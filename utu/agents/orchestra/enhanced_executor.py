"""
增强的Orchestra执行器
提供更好的错误处理、任务调度和性能监控
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .common import OrchestraTaskRecorder, Subtask, WorkerResult
from ..utils.orchestrated_logger import get_orchestra_logger


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TaskExecution:
    """任务执行记录"""
    subtask: Subtask
    status: TaskStatus
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    result: Optional[WorkerResult] = None
    error: Optional[Exception] = None
    retry_count: int = 0
    trace_id: Optional[str] = None

    @property
    def duration_ms(self) -> Optional[int]:
        """获取执行时间（毫秒）"""
        if self.start_time and self.end_time:
            return int((self.end_time - self.start_time) * 1000)
        return None


class EnhancedOrchestraExecutor:
    """增强的Orchestra执行器"""

    def __init__(self, worker_agents: Dict[str, Any], max_retries: int = 3,
                 retry_delay: float = 1.0, timeout_per_task: float = 300.0):
        self.worker_agents = worker_agents
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout_per_task = timeout_per_task
        self.logger = get_orchestra_logger()

    async def execute_tasks_enhanced(self, task_recorder: OrchestraTaskRecorder,
                                    fail_fast: bool = False) -> Tuple[List[WorkerResult], List[Exception]]:
        """
        增强的任务执行方法

        Args:
            task_recorder: 任务记录器
            fail_fast: 是否在遇到错误时立即停止

        Returns:
            Tuple[成功的结果列表, 异常列表]
        """
        if not task_recorder.plan or not task_recorder.plan.todo:
            return [], []

        # 创建任务执行记录
        task_executions = []
        for subtask in task_recorder.plan.todo:
            execution = TaskExecution(
                subtask=subtask,
                status=TaskStatus.PENDING
            )
            task_executions.append(execution)

        results = []
        errors = []

        # 执行任务
        for i, execution in enumerate(task_executions):
            try:
                # 执行单个任务
                result = await self._execute_single_task(execution, i + 1, len(task_executions))
                if result:
                    results.append(result)
                    task_recorder.add_worker_result(result)

                # 如果是fail_fast模式且遇到错误，停止执行
                if fail_fast and errors:
                    break

            except Exception as e:
                errors.append(e)
                self.logger.log_error(
                    agent_name="EnhancedExecutor",
                    error=e,
                    context={
                        "task": execution.subtask.task,
                        "agent": execution.subtask.agent_name,
                        "position": f"{i + 1}/{len(task_executions)}"
                    },
                    trace_id=execution.trace_id
                )

                if fail_fast:
                    break

        return results, errors

    async def _execute_single_task(self, execution: TaskExecution,
                                  position: int, total: int) -> Optional[WorkerResult]:
        """执行单个任务，支持重试机制"""
        worker_agent = self.worker_agents.get(execution.subtask.agent_name)
        if not worker_agent:
            raise ValueError(f"Worker agent not found: {execution.subtask.agent_name}")

        # 生成trace_id
        execution.trace_id = self.logger.generate_trace_id(f"task_{position:02d}")

        for attempt in range(self.max_retries + 1):
            try:
                # 记录任务开始
                self.logger.log_agent_event(
                    agent_name=execution.subtask.agent_name,
                    event_type="task_execution",
                    status="started",
                    input_data={
                        "task": execution.subtask.task,
                        "position": f"{position}/{total}",
                        "attempt": attempt + 1
                    },
                    trace_id=execution.trace_id
                )

                execution.status = TaskStatus.RUNNING
                execution.start_time = time.time()

                # 执行任务（带超时）
                try:
                    result = await asyncio.wait_for(
                        worker_agent.work(None, execution.subtask),
                        timeout=self.timeout_per_task
                    )
                except asyncio.TimeoutError:
                    raise TimeoutError(f"Task execution timed out after {self.timeout_per_task} seconds")

                execution.end_time = time.time()
                execution.status = TaskStatus.COMPLETED
                execution.result = result

                # 记录任务完成
                self.logger.log_agent_event(
                    agent_name=execution.subtask.agent_name,
                    event_type="task_execution",
                    status="completed",
                    duration_ms=execution.duration_ms,
                    input_data={
                        "task": execution.subtask.task,
                        "position": f"{position}/{total}",
                        "attempt": attempt + 1
                    },
                    output_data={
                        "result_length": len(result.output) if result.output else 0,
                        "result_preview": (result.output or "")[:200]
                    },
                    trace_id=execution.trace_id
                )

                return result

            except Exception as e:
                execution.retry_count = attempt
                execution.error = e

                # 记录错误
                self.logger.log_error(
                    agent_name=execution.subtask.agent_name,
                    error=e,
                    context={
                        "task": execution.subtask.task,
                        "position": f"{position}/{total}",
                        "attempt": attempt + 1,
                        "max_retries": self.max_retries
                    },
                    trace_id=execution.trace_id
                )

                # 如果是最后一次尝试，标记为失败
                if attempt == self.max_retries:
                    execution.status = TaskStatus.FAILED
                    execution.end_time = time.time()
                    raise

                # 等待重试
                if self.retry_delay > 0:
                    await asyncio.sleep(self.retry_delay)

        return None

    async def execute_with_checkpoints(self, task_recorder: OrchestraTaskRecorder,
                                      checkpoint_interval: int = 3) -> Tuple[List[WorkerResult], List[Exception]]:
        """
        带检查点的任务执行

        Args:
            task_recorder: 任务记录器
            checkpoint_interval: 检查点间隔（任务数）

        Returns:
            Tuple[成功的结果列表, 异常列表]
        """
        if not task_recorder.plan or not task_recorder.plan.todo:
            return [], []

        all_results = []
        all_errors = []
        total_tasks = len(task_recorder.plan.todo)

        # 分批执行任务
        for start_idx in range(0, total_tasks, checkpoint_interval):
            end_idx = min(start_idx + checkpoint_interval, total_tasks)
            current_batch = task_recorder.plan.todo[start_idx:end_idx]

            # 创建临时任务记录器
            batch_recorder = OrchestraTaskRecorder(
                task=f"{task_recorder.task} (batch {start_idx//checkpoint_interval + 1})",
                trace_id=f"{task_recorder.trace_id}_batch_{start_idx//checkpoint_interval + 1}"
            )
            batch_recorder.plan = type(task_recorder.plan)(
                analysis=task_recorder.plan.analysis,
                todo=current_batch
            )

            # 记录检查点开始
            self.logger.log_agent_event(
                agent_name="EnhancedExecutor",
                event_type="checkpoint_start",
                status="started",
                input_data={
                    "batch_range": f"{start_idx + 1}-{end_idx}",
                    "total_tasks": total_tasks,
                    "batch_size": len(current_batch)
                },
                trace_id=batch_recorder.trace_id
            )

            try:
                # 执行当前批次
                batch_results, batch_errors = await self.execute_tasks_enhanced(
                    batch_recorder, fail_fast=False
                )

                all_results.extend(batch_results)
                all_errors.extend(batch_errors)

                # 记录检查点完成
                self.logger.log_agent_event(
                    agent_name="EnhancedExecutor",
                    event_type="checkpoint_complete",
                    status="completed",
                    input_data={
                        "batch_range": f"{start_idx + 1}-{end_idx}",
                        "results_count": len(batch_results),
                        "errors_count": len(batch_errors)
                    },
                    trace_id=batch_recorder.trace_id
                )

                # 如果有错误但不致命，记录警告
                if batch_errors and not self._should_abort_on_errors(batch_errors):
                    self.logger.log_agent_event(
                        agent_name="EnhancedExecutor",
                        event_type="checkpoint_warning",
                        status="warning",
                        input_data={
                            "batch_range": f"{start_idx + 1}-{end_idx}",
                            "errors": [str(e)[:100] for e in batch_errors[:3]]
                        },
                        trace_id=batch_recorder.trace_id
                    )

            except Exception as e:
                # 记录检查点失败
                self.logger.log_error(
                    agent_name="EnhancedExecutor",
                    error=e,
                    context={
                        "batch_range": f"{start_idx + 1}-{end_idx}",
                        "completed_batches": start_idx // checkpoint_interval
                    },
                    trace_id=batch_recorder.trace_id
                )
                raise

        return all_results, all_errors

    def _should_abort_on_errors(self, errors: List[Exception]) -> bool:
        """判断是否应该因错误而中止执行"""
        # 检查是否有严重错误
        critical_errors = [
            "TimeoutError",
            "ConnectionError",
            "AuthenticationError",
            "PermissionError"
        ]

        for error in errors:
            if any(critical_error in str(type(error)) for critical_error in critical_errors):
                return True

        # 如果错误数量过多，也中止执行
        if len(errors) > 3:
            return True

        return False

    def get_execution_summary(self, task_executions: List[TaskExecution]) -> Dict[str, Any]:
        """获取执行摘要"""
        if not task_executions:
            return {"total_tasks": 0}

        status_counts = {}
        total_duration = 0
        completed_count = 0

        for execution in task_executions:
            status = execution.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

            if execution.status == TaskStatus.COMPLETED:
                completed_count += 1
                if execution.duration_ms:
                    total_duration += execution.duration_ms

        return {
            "total_tasks": len(task_executions),
            "completed": completed_count,
            "failed": status_counts.get("failed", 0),
            "skipped": status_counts.get("skipped", 0),
            "success_rate": completed_count / len(task_executions) * 100,
            "total_duration_ms": total_duration,
            "average_duration_ms": total_duration / completed_count if completed_count > 0 else 0,
            "status_breakdown": status_counts
        }