"""
统一错误处理模块
为多智能体系统提供结构化的错误处理和恢复机制
"""

import logging
import traceback
import time
from typing import Dict, Any, Optional, Callable, List, Union
from dataclasses import dataclass, field
from enum import Enum
import functools
import asyncio

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """错误类别"""
    DATA_FORMAT = "data_format"
    TOOL_EXECUTION = "tool_execution"
    NETWORK = "network"
    VALIDATION = "validation"
    SYSTEM = "system"
    USER_INPUT = "user_input"
    UNKNOWN = "unknown"


@dataclass
class ErrorInfo:
    """错误信息数据类"""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    can_retry: bool = True
    suggested_actions: List[str] = field(default_factory=list)


class RetryableError(Exception):
    """可重试错误"""
    def __init__(self, message: str, max_retries: int = 3, delay: float = 1.0):
        super().__init__(message)
        self.max_retries = max_retries
        self.delay = delay


class FatalError(Exception):
    """致命错误（不可重试）"""
    def __init__(self, message: str, category: ErrorCategory = ErrorCategory.SYSTEM):
        super().__init__(message)
        self.category = category


class ErrorHandler:
    """错误处理器"""

    def __init__(self):
        self.error_history: List[ErrorInfo] = []
        self.error_callbacks: Dict[ErrorCategory, List[Callable]] = {}

    def register_callback(self, category: ErrorCategory, callback: Callable):
        """注册错误回调函数"""
        if category not in self.error_callbacks:
            self.error_callbacks[category] = []
        self.error_callbacks[category].append(callback)

    def create_error_info(self, exception: Exception, context: Dict[str, Any] = None) -> ErrorInfo:
        """创建错误信息"""
        import uuid
        error_id = str(uuid.uuid4())[:8]

        # 确定错误类别
        category = self._categorize_error(exception)

        # 确定严重程度
        severity = self._determine_severity(exception, category)

        # 生成建议操作
        suggested_actions = self._generate_suggested_actions(exception, category)

        # 获取堆栈跟踪
        stack_trace = traceback.format_exc() if not isinstance(exception, RetryableError) else None

        return ErrorInfo(
            error_id=error_id,
            category=category,
            severity=severity,
            message=str(exception),
            details={"exception_type": type(exception).__name__},
            stack_trace=stack_trace,
            context=context or {},
            suggested_actions=suggested_actions,
            can_retry=not isinstance(exception, FatalError)
        )

    def _categorize_error(self, exception: Exception) -> ErrorCategory:
        """错误分类"""
        error_message = str(exception).lower()
        exception_type = type(exception).__name__.lower()

        if any(keyword in error_message for keyword in ["dataframe", "json", "format", "parse"]):
            return ErrorCategory.DATA_FORMAT
        elif any(keyword in error_message for keyword in ["tool", "function", "call"]):
            return ErrorCategory.TOOL_EXECUTION
        elif any(keyword in error_message for keyword in ["network", "connection", "timeout"]):
            return ErrorCategory.NETWORK
        elif any(keyword in error_message for keyword in ["validation", "invalid", "missing"]):
            return ErrorCategory.VALIDATION
        elif any(keyword in exception_type for keyword in ["filenotfound", "permission", "io"]):
            return ErrorCategory.SYSTEM
        elif any(keyword in error_message for keyword in ["name", "variable", "defined"]):
            return ErrorCategory.USER_INPUT
        else:
            return ErrorCategory.UNKNOWN

    def _determine_severity(self, exception: Exception, category: ErrorCategory) -> ErrorSeverity:
        """确定错误严重程度"""
        if isinstance(exception, FatalError):
            return ErrorSeverity.CRITICAL
        elif isinstance(exception, RetryableError):
            return ErrorSeverity.MEDIUM
        elif category in [ErrorCategory.SYSTEM, ErrorCategory.DATA_FORMAT]:
            return ErrorSeverity.HIGH
        elif category in [ErrorCategory.TOOL_EXECUTION, ErrorCategory.VALIDATION]:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW

    def _generate_suggested_actions(self, exception: Exception, category: ErrorCategory) -> List[str]:
        """生成建议操作"""
        actions = []

        if category == ErrorCategory.DATA_FORMAT:
            actions.extend([
                "检查数据格式是否符合要求",
                "验证JSON字符串是否正确",
                "确认所有必需字段都存在"
            ])
        elif category == ErrorCategory.TOOL_EXECUTION:
            actions.extend([
                "检查工具参数是否正确",
                "验证输入数据类型",
                "确认工具是否可用"
            ])
        elif category == ErrorCategory.VALIDATION:
            actions.extend([
                "检查输入数据的有效性",
                "验证数据范围和约束",
                "确认数据完整性"
            ])
        elif category == ErrorCategory.USER_INPUT:
            actions.extend([
                "检查变量名是否正确",
                "确认变量已正确定义",
                "验证作用域是否正确"
            ])

        # 基于异常类型的特定建议
        error_message = str(exception).lower()
        if "dataframe" in error_message:
            actions.append("确保DataFrame构造器参数正确")
        elif "not defined" in error_message:
            actions.append("在使用变量前先进行定义")
        elif "json" in error_message:
            actions.append("检查JSON字符串格式是否正确")
        elif "index" in error_message:
            actions.append("检查数据索引设置是否正确")

        return actions

    def handle_error(self, exception: Exception, context: Dict[str, Any] = None) -> ErrorInfo:
        """处理错误"""
        error_info = self.create_error_info(exception, context)
        self.error_history.append(error_info)

        # 记录错误日志
        log_message = f"[{error_info.category.value.upper()}] {error_info.message}"
        if error_info.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, extra={"error_info": error_info.__dict__})
        elif error_info.severity == ErrorSeverity.HIGH:
            logger.error(log_message, extra={"error_info": error_info.__dict__})
        elif error_info.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message, extra={"error_info": error_info.__dict__})
        else:
            logger.info(log_message, extra={"error_info": error_info.__dict__})

        # 调用注册的回调函数
        if error_info.category in self.error_callbacks:
            for callback in self.error_callbacks[error_info.category]:
                try:
                    callback(error_info)
                except Exception as e:
                    logger.error(f"错误回调函数执行失败: {str(e)}")

        return error_info

    def can_retry(self, error_info: ErrorInfo) -> bool:
        """判断是否可以重试"""
        return (
            error_info.can_retry and
            error_info.retry_count < error_info.max_retries and
            error_info.severity != ErrorSeverity.CRITICAL
        )

    def get_error_summary(self) -> Dict[str, Any]:
        """获取错误摘要"""
        if not self.error_history:
            return {"total_errors": 0, "by_category": {}, "by_severity": {}}

        by_category = {}
        by_severity = {}

        for error in self.error_history:
            category = error.category.value
            severity = error.severity.value

            by_category[category] = by_category.get(category, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1

        return {
            "total_errors": len(self.error_history),
            "by_category": by_category,
            "by_severity": by_severity,
            "latest_errors": [
                {
                    "error_id": error.error_id,
                    "category": error.category.value,
                    "severity": error.severity.value,
                    "message": error.message,
                    "timestamp": error.timestamp
                }
                for error in self.error_history[-5:]
            ]
        }


# 全局错误处理器实例
global_error_handler = ErrorHandler()


def handle_error(exception: Exception, context: Dict[str, Any] = None) -> ErrorInfo:
    """全局错误处理函数"""
    return global_error_handler.handle_error(exception, context)


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    重试装饰器

    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间
        backoff: 退避倍数
    """
    def decorator(func):
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_error = None
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    error_info = handle_error(e, {
                        "function": func.__name__,
                        "attempt": attempt + 1,
                        "max_retries": max_retries + 1
                    })

                    if attempt < max_retries and global_error_handler.can_retry(error_info):
                        logger.warning(f"函数 {func.__name__} 执行失败，{current_delay:.1f}秒后重试 (尝试 {attempt + 1}/{max_retries + 1})")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        break

            raise last_error

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_error = None
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    error_info = handle_error(e, {
                        "function": func.__name__,
                        "attempt": attempt + 1,
                        "max_retries": max_retries + 1,
                        "async": True
                    })

                    if attempt < max_retries and global_error_handler.can_retry(error_info):
                        logger.warning(f"异步函数 {func.__name__} 执行失败，{current_delay:.1f}秒后重试 (尝试 {attempt + 1}/{max_retries + 1})")
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        break

            raise last_error

        # 根据函数类型返回对应的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def safe_execute(func: Callable, *args, default_return=None, **kwargs):
    """
    安全执行函数

    Args:
        func: 要执行的函数
        default_return: 发生错误时的默认返回值
        *args: 函数参数
        **kwargs: 函数关键字参数

    Returns:
        函数执行结果或默认返回值
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_info = handle_error(e, {
            "function": func.__name__ if hasattr(func, '__name__') else str(func),
            "safe_execute": True
        })

        if default_return is not None:
            return default_return
        raise


def validate_and_execute(validation_func: Callable, func: Callable, *args, **kwargs):
    """
    验证并执行函数

    Args:
        validation_func: 验证函数
        func: 要执行的函数
        *args: 函数参数
        **kwargs: 函数关键字参数

    Returns:
        函数执行结果
    """
    try:
        # 执行验证
        validation_result = validation_func(*args, **kwargs)
        if hasattr(validation_result, 'is_valid') and not validation_result.is_valid:
            raise ValueError(f"验证失败: {'; '.join(validation_result.errors)}")

        # 执行函数
        return func(*args, **kwargs)

    except Exception as e:
        error_info = handle_error(e, {
            "function": func.__name__ if hasattr(func, '__name__') else str(func),
            "validation_func": validation_func.__name__ if hasattr(validation_func, '__name__') else str(validation_func)
        })
        raise


# 错误处理工具函数
def format_error_message(error_info: ErrorInfo) -> str:
    """格式化错误消息"""
    message = f"[{error_info.category.value.upper()}] {error_info.message}"

    if error_info.suggested_actions:
        message += f"\n建议操作:\n"
        for i, action in enumerate(error_info.suggested_actions, 1):
            message += f"  {i}. {action}\n"

    return message


def log_error_context(error_info: ErrorInfo, additional_context: Dict[str, Any] = None):
    """记录错误上下文"""
    context = error_info.context.copy()
    if additional_context:
        context.update(additional_context)

    logger.info(f"错误上下文 [{error_info.error_id}]: {context}")


def create_data_format_error(message: str, details: Dict[str, Any] = None) -> DataValidationError:
    """创建数据格式错误"""
    error = DataValidationError(message)
    if details:
        error.details = details
    return error