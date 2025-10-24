"""
工具日志包装器
为工具调用添加自动日志记录功能
"""

import time
import functools
from typing import Dict, Any, Callable, Optional
from ..utils.orchestrated_logger import get_orchestra_logger


def log_tool_calls(tool_name: Optional[str] = None):
    """工具调用日志装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            logger = get_orchestra_logger()

            # 确定工具名称
            actual_tool_name = tool_name or func.__name__

            # 获取智能体名称（从self类名推断）
            agent_name = self.__class__.__name__.replace('Toolkit', '').replace('Tool', '')
            if agent_name == 'DateTime':
                agent_name = 'DateTimeToolkit'
            elif agent_name == 'AKShareFinancial':
                agent_name = 'DataAgent'

            start_time = time.time()

            # 准备输入数据
            tool_input = {
                "args": {str(i): str(arg)[:100] for i, arg in enumerate(args)},
                "kwargs": {k: str(v)[:100] for k, v in kwargs.items()}
            }

            # 尝试获取trace_id（通常在kwargs中）
            trace_id = kwargs.get("trace_id")

            # 记录工具调用开始
            logger.log_agent_event(
                agent_name=agent_name,
                event_type="tool_call_start",
                status="started",
                input_data={
                    "tool_name": actual_tool_name,
                    "input": tool_input
                },
                trace_id=trace_id
            )

            try:
                # 执行工具函数
                result = func(self, *args, **kwargs)

                # 计算执行时间
                duration_ms = int((time.time() - start_time) * 1000)

                # 处理输出数据
                processed_output = None
                if result is not None:
                    if isinstance(result, dict):
                        processed_output = {k: str(v)[:200] for k, v in result.items()}
                    elif isinstance(result, list):
                        processed_output = {"list_length": len(result), "preview": str(result)[:200]}
                    else:
                        processed_output = {"result": str(result)[:200]}

                # 记录成功调用
                logger.log_tool_usage(
                    agent_name=agent_name,
                    tool_name=actual_tool_name,
                    tool_input=tool_input,
                    tool_output=processed_output,
                    duration_ms=duration_ms,
                    trace_id=trace_id
                )

                return result

            except Exception as e:
                # 计算执行时间
                duration_ms = int((time.time() - start_time) * 1000)

                # 记录错误
                error_info = {
                    "type": type(e).__name__,
                    "message": str(e)
                }

                logger.log_tool_usage(
                    agent_name=agent_name,
                    tool_name=actual_tool_name,
                    tool_input=tool_input,
                    tool_output=None,
                    duration_ms=duration_ms,
                    error_info=error_info,
                    trace_id=trace_id
                )

                # 重新抛出异常
                raise

        return wrapper
    return decorator


def log_async_tool_calls(tool_name: Optional[str] = None):
    """异步工具调用日志装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            logger = get_orchestra_logger()

            # 确定工具名称
            actual_tool_name = tool_name or func.__name__

            # 获取智能体名称
            agent_name = self.__class__.__name__.replace('Toolkit', '').replace('Tool', '')
            if agent_name == 'DateTime':
                agent_name = 'DateTimeToolkit'
            elif agent_name == 'AKShareFinancial':
                agent_name = 'DataAgent'

            start_time = time.time()

            # 准备输入数据
            tool_input = {
                "args": {str(i): str(arg)[:100] for i, arg in enumerate(args)},
                "kwargs": {k: str(v)[:100] for k, v in kwargs.items()}
            }

            # 尝试获取trace_id
            trace_id = kwargs.get("trace_id")

            # 记录工具调用开始
            logger.log_agent_event(
                agent_name=agent_name,
                event_type="tool_call_start",
                status="started",
                input_data={
                    "tool_name": actual_tool_name,
                    "input": tool_input
                },
                trace_id=trace_id
            )

            try:
                # 执行异步工具函数
                result = await func(self, *args, **kwargs)

                # 计算执行时间
                duration_ms = int((time.time() - start_time) * 1000)

                # 处理输出数据
                processed_output = None
                if result is not None:
                    if isinstance(result, dict):
                        processed_output = {k: str(v)[:200] for k, v in result.items()}
                    elif isinstance(result, list):
                        processed_output = {"list_length": len(result), "preview": str(result)[:200]}
                    else:
                        processed_output = {"result": str(result)[:200]}

                # 记录成功调用
                logger.log_tool_usage(
                    agent_name=agent_name,
                    tool_name=actual_tool_name,
                    tool_input=tool_input,
                    tool_output=processed_output,
                    duration_ms=duration_ms,
                    trace_id=trace_id
                )

                return result

            except Exception as e:
                # 计算执行时间
                duration_ms = int((time.time() - start_time) * 1000)

                # 记录错误
                error_info = {
                    "type": type(e).__name__,
                    "message": str(e)
                }

                logger.log_tool_usage(
                    agent_name=agent_name,
                    tool_name=actual_tool_name,
                    tool_input=tool_input,
                    tool_output=None,
                    duration_ms=duration_ms,
                    error_info=error_info,
                    trace_id=trace_id
                )

                # 重新抛出异常
                raise

        return wrapper
    return decorator


class LoggingMixin:
    """为工具类提供日志功能的混入类"""

    def _log_tool_call(self, tool_name: str, tool_input: Dict[str, Any],
                      tool_output: Any, duration_ms: int,
                      error: Optional[Exception] = None, trace_id: Optional[str] = None):
        """记录工具调用的辅助方法"""
        logger = get_orchestra_logger()

        # 获取智能体名称
        agent_name = self.__class__.__name__.replace('Toolkit', '').replace('Tool', '')
        if agent_name == 'DateTime':
            agent_name = 'DateTimeToolkit'
        elif agent_name == 'AKShareFinancial':
            agent_name = 'DataAgent'

        # 处理输出数据
        processed_output = None
        if tool_output is not None:
            if isinstance(tool_output, dict):
                processed_output = {k: str(v)[:200] for k, v in tool_output.items()}
            elif isinstance(tool_output, list):
                processed_output = {"list_length": len(tool_output), "preview": str(tool_output)[:200]}
            else:
                processed_output = {"result": str(tool_output)[:200]}

        # 处理错误信息
        error_info = None
        if error:
            error_info = {
                "type": type(error).__name__,
                "message": str(error)
            }

        logger.log_tool_usage(
            agent_name=agent_name,
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=processed_output,
            duration_ms=duration_ms,
            error_info=error_info,
            trace_id=trace_id
        )

    def _get_agent_name(self) -> str:
        """获取当前工具对应的智能体名称"""
        class_name = self.__class__.__name__

        # 映射规则
        mapping = {
            'DateTimeToolkit': 'DateTimeToolkit',
            'AKShareFinancialDataTool': 'DataAgent',
            'FinancialAnalysisToolkit': 'DataAnalysisAgent',
            'EnhancedPythonExecutorToolkit': 'ChartGeneratorAgent',
            'ReportSaverToolkit': 'ReportAgent'
        }

        return mapping.get(class_name, class_name.replace('Toolkit', '').replace('Tool', 'Agent'))


# 创建一个全局的日志配置
def configure_tool_logging(config: Optional[Dict[str, Any]] = None):
    """配置工具日志系统"""
    logger_config = {
        "log_dir": "./logs",
        "log_level": "INFO",
        "enabled": config.get("tool_logging_enabled", True) if config else True
    }

    if config:
        logger_config.update(config)

    return logger_config