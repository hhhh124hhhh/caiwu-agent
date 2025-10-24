"""
多智能体结构化日志系统
提供JSON格式的结构化日志记录，便于调试和分析
"""

import json
import logging
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
import uuid
import threading


@dataclass
class LogEntry:
    """日志条目数据结构"""
    timestamp: str
    trace_id: str
    session_id: str
    agent_name: str
    event_type: str
    status: str
    duration_ms: Optional[int] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    tools_used: Optional[list] = None
    error_info: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class OrchestraLogger:
    """多智能体专用日志记录器"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

        # 日志配置
        self.log_dir = Path(self.config.get("log_dir", "./logs"))
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.log_file = self.log_dir / f"orchestra_{datetime.now().strftime('%Y%m%d')}.json"
        self.session_id = str(uuid.uuid4())
        self.trace_counter = {}

        # 日志级别
        self.log_level = self.config.get("log_level", "INFO").upper()
        self.enabled = self.config.get("enabled", True)

        # 线程安全
        self._lock = threading.Lock()

        # 创建标准日志记录器用于基本输出
        self.logger = logging.getLogger("orchestra")
        self.logger.setLevel(getattr(logging, self.log_level))

        # 添加控制台处理器
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def generate_trace_id(self, prefix: str = "trace") -> str:
        """生成唯一的trace_id"""
        with self._lock:
            self.trace_counter[prefix] = self.trace_counter.get(prefix, 0) + 1
            return f"{prefix}_{self.trace_counter[prefix]:06d}_{uuid.uuid4().hex[:8]}"

    def log_agent_event(
        self,
        agent_name: str,
        event_type: str,
        status: str = "started",
        duration_ms: Optional[int] = None,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        tools_used: Optional[list] = None,
        error_info: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None
    ) -> str:
        """记录智能体事件"""
        if not self.enabled:
            return trace_id or ""

        # 生成trace_id（如果未提供）
        if not trace_id:
            trace_id = self.generate_trace_id("agent")

        # 创建日志条目
        log_entry = LogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            trace_id=trace_id,
            session_id=self.session_id,
            agent_name=agent_name,
            event_type=event_type,
            status=status,
            duration_ms=duration_ms,
            input_data=input_data,
            output_data=output_data,
            tools_used=tools_used,
            error_info=error_info,
            metadata=metadata or {}
        )

        # 写入日志文件
        self._write_log_entry(log_entry)

        # 根据状态输出到控制台
        console_level = logging.INFO if status in ["started", "completed"] else logging.ERROR
        if status == "failed":
            self.logger.error(
                f"[{agent_name}] {event_type} - {status}" +
                (f" - Error: {error_info.get('message', 'Unknown error')}" if error_info else "")
            )
        else:
            self.logger.log(
                console_level,
                f"[{agent_name}] {event_type} - {status}" +
                (f" ({duration_ms}ms)" if duration_ms else "")
            )

        return trace_id

    def log_plan_creation(
        self,
        agent_name: str = "PlannerAgent",
        input_question: str = "",
        plan_result: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
        trace_id: Optional[str] = None
    ) -> str:
        """记录计划创建事件"""
        if not trace_id:
            trace_id = self.generate_trace_id("plan")

        return self.log_agent_event(
            agent_name=agent_name,
            event_type="plan_creation",
            status="completed",
            duration_ms=duration_ms,
            input_data={"question": input_question},
            output_data={
                "plan_items": len(plan_result.get("todo", [])) if plan_result else 0,
                "analysis_length": len(plan_result.get("analysis", "")) if plan_result else 0
            },
            trace_id=trace_id
        )

    def log_task_execution(
        self,
        agent_name: str,
        task: str,
        status: str = "started",
        result: Optional[str] = None,
        duration_ms: Optional[int] = None,
        tools_used: Optional[list] = None,
        error_info: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None
    ) -> str:
        """记录任务执行事件"""
        if not trace_id:
            trace_id = self.generate_trace_id("task")

        return self.log_agent_event(
            agent_name=agent_name,
            event_type="task_execution",
            status=status,
            duration_ms=duration_ms,
            input_data={"task": task},
            output_data={"result": result[:500] if result else None} if result else None,  # 限制输出长度
            tools_used=tools_used,
            error_info=error_info,
            trace_id=trace_id
        )

    def log_report_generation(
        self,
        agent_name: str = "ReporterAgent",
        input_question: str = "",
        report_result: Optional[str] = None,
        duration_ms: Optional[int] = None,
        trace_id: Optional[str] = None
    ) -> str:
        """记录报告生成事件"""
        if not trace_id:
            trace_id = self.generate_trace_id("report")

        return self.log_agent_event(
            agent_name=agent_name,
            event_type="report_generation",
            status="completed",
            duration_ms=duration_ms,
            input_data={"question": input_question},
            output_data={
                "report_length": len(report_result) if report_result else 0,
                "report_preview": report_result[:200] if report_result else None
            },
            trace_id=trace_id
        )

    def log_orchestra_session(
        self,
        session_type: str = "orchestra_run",
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
        trace_id: Optional[str] = None
    ) -> str:
        """记录整个orchestra会话"""
        if not trace_id:
            trace_id = self.generate_trace_id("session")

        return self.log_agent_event(
            agent_name="OrchestraAgent",
            event_type=session_type,
            status="completed",
            duration_ms=duration_ms,
            input_data=input_data,
            output_data=output_data,
            metadata={
                "session_type": session_type,
                "log_file": str(self.log_file)
            },
            trace_id=trace_id
        )

    def log_tool_usage(
        self,
        agent_name: str,
        tool_name: str,
        tool_input: Optional[Dict[str, Any]] = None,
        tool_output: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
        error_info: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None
    ) -> str:
        """记录工具使用事件"""
        if not trace_id:
            trace_id = self.generate_trace_id("tool")

        status = "completed" if not error_info else "failed"

        return self.log_agent_event(
            agent_name=agent_name,
            event_type="tool_usage",
            status=status,
            duration_ms=duration_ms,
            input_data={"tool_name": tool_name, "input": tool_input},
            output_data={"output": tool_output},
            error_info=error_info,
            metadata={"tool_name": tool_name},
            trace_id=trace_id
        )

    def log_error(
        self,
        agent_name: str,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None
    ) -> str:
        """记录错误事件"""
        if not trace_id:
            trace_id = self.generate_trace_id("error")

        error_info = {
            "type": type(error).__name__,
            "message": str(error),
            "traceback": traceback.format_exc()
        }

        return self.log_agent_event(
            agent_name=agent_name,
            event_type="error",
            status="failed",
            input_data=context,
            error_info=error_info,
            trace_id=trace_id
        )

    def _write_log_entry(self, log_entry: LogEntry):
        """写入日志条目到文件"""
        try:
            with self._lock:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    json.dump(asdict(log_entry), f, ensure_ascii=False, default=str)
                    f.write('\n')
        except Exception as e:
            self.logger.error(f"Failed to write log entry: {e}")

    def get_session_logs(self, limit: int = 100) -> list[Dict[str, Any]]:
        """获取当前会话的日志"""
        logs = []
        try:
            if self.log_file.exists():
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            log_entry = json.loads(line.strip())
                            if log_entry.get("session_id") == self.session_id:
                                logs.append(log_entry)
                                if len(logs) >= limit:
                                    break
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            self.logger.error(f"Failed to read session logs: {e}")

        return logs

    def get_trace_logs(self, trace_id: str) -> list[Dict[str, Any]]:
        """获取特定trace的日志"""
        logs = []
        try:
            if self.log_file.exists():
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            log_entry = json.loads(line.strip())
                            if log_entry.get("trace_id") == trace_id:
                                logs.append(log_entry)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            self.logger.error(f"Failed to read trace logs: {e}")

        return logs

    def clear_old_logs(self, days: int = 7):
        """清理旧的日志文件"""
        try:
            cutoff_date = datetime.now().replace(tzinfo=timezone.utc) - timedelta(days=days)
            for log_file in self.log_dir.glob("orchestra_*.json"):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    log_file.unlink()
                    self.logger.info(f"Deleted old log file: {log_file}")
        except Exception as e:
            self.logger.error(f"Failed to clear old logs: {e}")


# 全局日志记录器实例
_global_logger: Optional[OrchestraLogger] = None


def get_orchestra_logger(config: Optional[Dict[str, Any]] = None) -> OrchestraLogger:
    """获取全局orchestra日志记录器实例"""
    global _global_logger
    if _global_logger is None:
        _global_logger = OrchestraLogger(config)
    return _global_logger


def configure_orchestra_logging(config: Dict[str, Any]):
    """配置orchestra日志系统"""
    global _global_logger
    _global_logger = OrchestraLogger(config)


# 装饰器用于自动记录函数执行
def log_execution(
    agent_name: str,
    event_type: str = "function_execution",
    log_input: bool = True,
    log_output: bool = True,
    log_tools: bool = False
):
    """函数执行日志装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_orchestra_logger()
            start_time = datetime.now()

            # 提取trace_id（通常在kwargs中）
            trace_id = kwargs.get("trace_id")

            # 准备输入数据
            input_data = None
            if log_input:
                input_data = {
                    "args": str(args)[:200],  # 限制长度
                    "kwargs": {k: str(v)[:100] for k, v in kwargs.items() if k != "trace_id"}
                }

            # 记录开始
            if trace_id:
                logger.log_agent_event(
                    agent_name=agent_name,
                    event_type=event_type,
                    status="started",
                    input_data=input_data,
                    trace_id=trace_id
                )

            try:
                # 执行函数
                result = func(*args, **kwargs)

                # 计算执行时间
                duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

                # 准备输出数据
                output_data = None
                if log_output:
                    output_data = {"result": str(result)[:200]}

                # 记录完成
                if trace_id:
                    logger.log_agent_event(
                        agent_name=agent_name,
                        event_type=event_type,
                        status="completed",
                        duration_ms=duration_ms,
                        output_data=output_data,
                        trace_id=trace_id
                    )

                return result

            except Exception as e:
                # 计算执行时间
                duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

                # 记录错误
                if trace_id:
                    logger.log_error(
                        agent_name=agent_name,
                        error=e,
                        context={"function": func.__name__, "input_data": input_data},
                        trace_id=trace_id
                    )

                raise

        return wrapper
    return decorator