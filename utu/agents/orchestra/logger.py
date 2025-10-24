"""
多智能体系统专用日志记录器
集成到OrchestraAgent中，提供智能体级别的日志记录
"""

import asyncio
import time
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

from ...utils.orchestrated_logger import OrchestraLogger, get_orchestra_logger
from .common import OrchestraTaskRecorder, Subtask, WorkerResult


class OrchestraAgentLogger:
    """OrchestraAgent专用日志记录器"""

    def __init__(self, logger: Optional[OrchestraLogger] = None):
        self.logger = logger or get_orchestra_logger()
        self.current_trace_id: Optional[str] = None
        self.start_time: Optional[float] = None

    def start_session(self, input_data: str, trace_id: Optional[str] = None) -> str:
        """开始一个新的orchestra会话"""
        self.current_trace_id = trace_id or self.logger.generate_trace_id("orchestra")
        self.start_time = time.time()

        self.logger.log_orchestra_session(
            session_type="orchestra_start",
            input_data={"input": input_data[:500]},  # 限制输入长度
            trace_id=self.current_trace_id
        )

        return self.current_trace_id

    def end_session(self, final_output: str, status: str = "completed") -> None:
        """结束orchestra会话"""
        if not self.current_trace_id or not self.start_time:
            return

        duration_ms = int((time.time() - self.start_time) * 1000)

        self.logger.log_orchestra_session(
            session_type="orchestra_end",
            input_data={"status": status},
            output_data={
                "final_output_length": len(final_output),
                "final_output_preview": final_output[:200] if final_output else None
            },
            duration_ms=duration_ms,
            trace_id=self.current_trace_id
        )

        self.current_trace_id = None
        self.start_time = None

    def log_planning_start(self, input_task: str) -> str:
        """记录计划开始"""
        trace_id = self.logger.generate_trace_id("planner")
        self.logger.log_agent_event(
            agent_name="PlannerAgent",
            event_type="planning_start",
            status="started",
            input_data={"task": input_task[:200]},
            trace_id=trace_id
        )
        return trace_id

    def log_planning_end(self, plan_result: Dict[str, Any], start_time: float, trace_id: str) -> None:
        """记录计划结束"""
        duration_ms = int((time.time() - start_time) * 1000)

        self.logger.log_plan_creation(
            input_question=plan_result.get("input_question", ""),
            plan_result=plan_result,
            duration_ms=duration_ms,
            trace_id=trace_id
        )

    def log_worker_start(self, subtask: Subtask, worker_name: str) -> str:
        """记录Worker开始任务"""
        trace_id = self.logger.generate_trace_id(f"worker_{worker_name.lower()}")

        self.logger.log_task_execution(
            agent_name=worker_name,
            task=subtask.task,
            status="started",
            trace_id=trace_id
        )

        return trace_id

    def log_worker_end(self, subtask: Subtask, worker_name: str,
                      result: WorkerResult, start_time: float, trace_id: str) -> None:
        """记录Worker完成任务"""
        duration_ms = int((time.time() - start_time) * 1000)

        # 提取使用的工具（从轨迹中）
        tools_used = []
        if hasattr(result, 'trajectory') and isinstance(result.trajectory, dict):
            trajectory = result.trajectory.get("trajectory", [])
            for step in trajectory:
                if isinstance(step, dict) and "tool_calls" in step:
                    tools_used.extend([call.get("function", "") for call in step.get("tool_calls", [])])

        self.logger.log_task_execution(
            agent_name=worker_name,
            task=subtask.task,
            status="completed",
            result=result.output[:500] if result.output else None,
            duration_ms=duration_ms,
            tools_used=tools_used if tools_used else None,
            trace_id=trace_id
        )

    def log_worker_error(self, subtask: Subtask, worker_name: str,
                         error: Exception, start_time: float, trace_id: str) -> None:
        """记录Worker执行错误"""
        duration_ms = int((time.time() - start_time) * 1000)

        self.logger.log_error(
            agent_name=worker_name,
            error=error,
            context={
                "task": subtask.task,
                "duration_ms": duration_ms
            },
            trace_id=trace_id
        )

    def log_reporting_start(self, task_recorder: OrchestraTaskRecorder) -> str:
        """记录报告生成开始"""
        trace_id = self.logger.generate_trace_id("reporter")

        self.logger.log_agent_event(
            agent_name="ReporterAgent",
            event_type="reporting_start",
            status="started",
            input_data={
                "task_count": len(task_recorder.task_records),
                "has_plan": task_recorder.plan is not None
            },
            trace_id=trace_id
        )

        return trace_id

    def log_reporting_end(self, final_output: str, start_time: float, trace_id: str) -> None:
        """记录报告生成结束"""
        duration_ms = int((time.time() - start_time) * 1000)

        self.logger.log_report_generation(
            input_question="",
            report_result=final_output,
            duration_ms=duration_ms,
            trace_id=trace_id
        )

    def log_tool_usage(self, agent_name: str, tool_name: str,
                      tool_input: Dict[str, Any], tool_output: Any,
                      duration_ms: int, error: Optional[Exception] = None) -> str:
        """记录工具使用"""
        trace_id = self.logger.generate_trace_id("tool")

        # 处理输出数据
        processed_output = None
        if tool_output is not None:
            if isinstance(tool_output, dict):
                processed_output = tool_output
            else:
                processed_output = {"result": str(tool_output)[:200]}

        error_info = None
        if error:
            error_info = {
                "type": type(error).__name__,
                "message": str(error)
            }

        self.logger.log_tool_usage(
            agent_name=agent_name,
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=processed_output,
            duration_ms=duration_ms,
            error_info=error_info,
            trace_id=trace_id
        )

        return trace_id

    def get_session_summary(self) -> Dict[str, Any]:
        """获取当前会话的摘要信息"""
        if not self.current_trace_id:
            return {"status": "no_active_session"}

        session_logs = self.logger.get_session_logs(limit=1000)

        # 统计信息
        agent_counts = {}
        total_duration = 0
        error_count = 0
        tool_usage = {}

        for log in session_logs:
            agent_name = log.get("agent_name", "unknown")
            agent_counts[agent_name] = agent_counts.get(agent_name, 0) + 1

            if log.get("duration_ms"):
                total_duration += log["duration_ms"]

            if log.get("status") == "failed":
                error_count += 1

            if log.get("event_type") == "tool_usage":
                tool_name = log.get("metadata", {}).get("tool_name", "unknown")
                tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1

        return {
            "session_id": self.logger.session_id,
            "trace_id": self.current_trace_id,
            "total_events": len(session_logs),
            "agent_events": agent_counts,
            "total_duration_ms": total_duration,
            "error_count": error_count,
            "tool_usage": tool_usage,
            "log_file": str(self.logger.log_file)
        }


class TimingContext:
    """用于计时和记录的上下文管理器"""

    def __init__(self, logger: OrchestraAgentLogger):
        self.logger = logger
        self.start_time: Optional[float] = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_ms = int((time.time() - self.start_time) * 1000)
            return duration_ms
        return None


@asynccontextmanager
async def async_timing_context(logger: OrchestraAgentLogger):
    """异步计时上下文管理器"""
    start_time = time.time()
    try:
        yield
    finally:
        duration_ms = int((time.time() - start_time) * 1000)
        # 记录时间信息到日志
        pass


# 全局日志记录器实例
_orchestra_logger: Optional[OrchestraAgentLogger] = None


def get_orchestra_agent_logger() -> OrchestraAgentLogger:
    """获取全局OrchestraAgent日志记录器实例"""
    global _orchestra_logger
    if _orchestra_logger is None:
        _orchestra_logger = OrchestraAgentLogger()
    return _orchestra_logger


def configure_orchestra_agent_logging(config: Optional[Dict[str, Any]] = None):
    """配置OrchestraAgent日志系统"""
    global _orchestra_logger
    base_logger = get_orchestra_logger(config)
    _orchestra_logger = OrchestraAgentLogger(base_logger)