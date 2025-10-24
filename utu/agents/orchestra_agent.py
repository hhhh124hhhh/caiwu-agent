import asyncio
import json
import time

from agents import AgentUpdatedStreamEvent, trace
from agents._run_impl import QueueCompleteSentinel
from agents.tracing import function_span

from ..config import AgentConfig, ConfigLoader
from ..utils import AgentsUtils, get_logger
from .base_agent import BaseAgent
from .orchestra import (
    AnalysisResult,
    BaseWorkerAgent,
    CreatePlanResult,
    OrchestraStreamEvent,
    OrchestraTaskRecorder,
    PlannerAgent,
    ReporterAgent,
    SimpleWorkerAgent,
    Subtask,
    WorkerResult,
)
from .orchestra.logger import get_orchestra_agent_logger, OrchestraAgentLogger

logger = get_logger(__name__)


class OrchestraAgent(BaseAgent):
    def __init__(self, config: AgentConfig | str):
        """Initialize the orchestra agent"""
        if isinstance(config, str):
            config = ConfigLoader.load_agent_config(config)
        self.config = config

        # 初始化日志记录器
        self.orchestra_logger = get_orchestra_agent_logger()

        # init subagents
        self.planner_agent = PlannerAgent(config)
        self.worker_agents = self._setup_workers()
        self.reporter_agent = ReporterAgent(config)

    def set_planner(self, planner: PlannerAgent):
        self.planner_agent = planner

    def _setup_workers(self) -> dict[str, BaseWorkerAgent]:
        workers = {}
        for name, config in self.config.workers.items():
            assert config.type == "simple", f"Only support SimpleAgent as worker in orchestra agent, get {config}"
            workers[name] = SimpleWorkerAgent(config=config)
        return workers

    async def build(self):
        await self.planner_agent.build()
        for worker_agent in self.worker_agents.values():
            await worker_agent.build()
        await self.reporter_agent.build()

    async def run(self, input: str, trace_id: str = None) -> OrchestraTaskRecorder:
        """Run the orchestra agent

        1. plan
        2. sequentially execute subtasks
        3. report
        """
        # setup
        trace_id = trace_id or AgentsUtils.gen_trace_id()
        logger.info(f"> trace_id: {trace_id}")

        # 开始orchestra会话日志记录
        session_trace_id = self.orchestra_logger.start_session(input, trace_id)

        # TODO: error_tracing
        task_recorder = OrchestraTaskRecorder(task=input, trace_id=trace_id)

        try:
            with trace(workflow_name="orchestra_agent", trace_id=trace_id):
                # 1. 计划阶段
                await self.plan(task_recorder)

                # 2. 执行阶段
                for task in task_recorder.plan.todo:
                    await self.work(task_recorder, task)

                # 3. 报告阶段
                result = await self.report(task_recorder)
                task_recorder.set_final_output(result.output)

                # 结束会话日志记录
                self.orchestra_logger.end_session(
                    final_output=result.output,
                    status="completed"
                )

                return task_recorder

        except Exception as e:
            # 记录错误和结束会话
            self.orchestra_logger.log_error(
                agent_name="OrchestraAgent",
                error=e,
                context={
                    "input": input[:200],
                    "stage": "orchestra_execution",
                    "trace_id": trace_id
                },
                trace_id=session_trace_id
            )

            self.orchestra_logger.end_session(
                final_output=f"Error: {str(e)}",
                status="failed"
            )

            raise

    def run_streamed(self, input: str, trace_id: str = None) -> OrchestraTaskRecorder:
        trace_id = trace_id or AgentsUtils.gen_trace_id()
        logger.info(f"> trace_id: {trace_id}")

        with trace(workflow_name="orchestra_agent", trace_id=trace_id):
            task_recorder = OrchestraTaskRecorder(task=input, trace_id=trace_id)
            # Kick off the actual agent loop in the background and return the streamed result object.
            task_recorder._run_impl_task = asyncio.create_task(self._start_streaming(task_recorder))
        return task_recorder

    async def _start_streaming(self, task_recorder: OrchestraTaskRecorder):
        task_recorder._event_queue.put_nowait(AgentUpdatedStreamEvent(new_agent=self.planner_agent))
        plan = await self.plan(task_recorder)
        task_recorder._event_queue.put_nowait(OrchestraStreamEvent(name="plan", item=plan))
        for task in task_recorder.plan.todo:
            # print(f"> processing {task}")
            # DONOT send this event because Runner will send it
            # task_recorder._event_queue.put_nowait(
            #     AgentUpdatedStreamEvent(new_agent=self.worker_agents[task.agent_name])
            # )
            worker_agent = self.worker_agents[task.agent_name]
            result_streaming = worker_agent.work_streamed(task_recorder, task)
            async for event in result_streaming.stream.stream_events():
                task_recorder._event_queue.put_nowait(event)
            result_streaming.output = result_streaming.stream.final_output
            result_streaming.trajectory = AgentsUtils.get_trajectory_from_agent_result(result_streaming.stream)
            task_recorder.add_worker_result(result_streaming)
            # print(f"< processed {task}")
        task_recorder._event_queue.put_nowait(AgentUpdatedStreamEvent(new_agent=self.reporter_agent))
        result = await self.report(task_recorder)
        task_recorder.set_final_output(result.output)
        task_recorder._event_queue.put_nowait(OrchestraStreamEvent(name="report", item=result))
        task_recorder._event_queue.put_nowait(QueueCompleteSentinel())
        task_recorder._is_complete = True

    async def plan(self, task_recorder: OrchestraTaskRecorder) -> CreatePlanResult:
        """Step1: Plan"""
        # 记录计划开始
        planning_trace_id = self.orchestra_logger.log_planning_start(task_recorder.task)
        start_time = time.time()

        try:
            with function_span("planner") as span_planner:
                plan = await self.planner_agent.create_plan(task_recorder)
                assert all(t.agent_name in self.worker_agents for t in plan.todo), (
                    f"agent_name in plan.todo must be in worker_agents, get {plan.todo}"
                )
                task_recorder.set_plan(plan)
                span_planner.span_data.input = json.dumps({"input": task_recorder.task}, ensure_ascii=False)
                span_planner.span_data.output = plan.to_dict()

            # 记录计划完成
            self.orchestra_logger.log_planning_end(
                plan_result={
                    "input_question": task_recorder.task,
                    "analysis": plan.analysis[:500] if plan.analysis else "",
                    "todo_count": len(plan.todo),
                    "todo_items": [{"agent": t.agent_name, "task": t.task[:100]} for t in plan.todo]
                },
                start_time=start_time,
                trace_id=planning_trace_id
            )

            return plan

        except Exception as e:
            # 记录计划失败
            self.orchestra_logger.log_error(
                agent_name="PlannerAgent",
                error=e,
                context={
                    "input_task": task_recorder.task[:200],
                    "stage": "planning"
                },
                trace_id=planning_trace_id
            )
            raise

    async def work(self, task_recorder: OrchestraTaskRecorder, task: Subtask) -> WorkerResult:
        """Step2: Work"""
        # 记录Worker开始
        worker_trace_id = self.orchestra_logger.log_worker_start(task, task.agent_name)
        start_time = time.time()

        try:
            worker_agent = self.worker_agents[task.agent_name]
            result = await worker_agent.work(task_recorder, task)
            task_recorder.add_worker_result(result)

            # 记录Worker完成
            self.orchestra_logger.log_worker_end(
                subtask=task,
                worker_name=task.agent_name,
                result=result,
                start_time=start_time,
                trace_id=worker_trace_id
            )

            return result

        except Exception as e:
            # 记录Worker失败
            self.orchestra_logger.log_worker_error(
                subtask=task,
                worker_name=task.agent_name,
                error=e,
                start_time=start_time,
                trace_id=worker_trace_id
            )
            raise

    async def report(self, task_recorder: OrchestraTaskRecorder) -> AnalysisResult:
        """Step3: Report"""
        # 记录报告开始
        reporting_trace_id = self.orchestra_logger.log_reporting_start(task_recorder)
        start_time = time.time()

        try:
            with function_span("reporter") as span_fn:
                analysis_result = await self.reporter_agent.report(task_recorder)
                task_recorder.add_reporter_result(analysis_result)
                span_fn.span_data.input = json.dumps(
                    {
                        "input": task_recorder.task,
                        "task_records": [{"task": r.task, "output": r.output} for r in task_recorder.task_records],
                    },
                    ensure_ascii=False,
                )
                span_fn.span_data.output = analysis_result.to_dict()

            # 记录报告完成
            self.orchestra_logger.log_reporting_end(
                final_output=analysis_result.output,
                start_time=start_time,
                trace_id=reporting_trace_id
            )

            return analysis_result

        except Exception as e:
            # 记录报告失败
            self.orchestra_logger.log_error(
                agent_name="ReporterAgent",
                error=e,
                context={
                    "input_task": task_recorder.task[:200],
                    "task_count": len(task_recorder.task_records),
                    "stage": "reporting"
                },
                trace_id=reporting_trace_id
            )
            raise

    def get_session_summary(self) -> dict:
        """获取当前会话的日志摘要"""
        return self.orchestra_logger.get_session_summary()

    def get_recent_logs(self, limit: int = 50) -> list:
        """获取最近的日志记录"""
        return self.orchestra_logger.logger.get_session_logs(limit)
