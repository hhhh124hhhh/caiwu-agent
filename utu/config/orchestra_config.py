"""
Orchestra配置管理器
统一管理OrchestraAgent和相关组件的配置
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import os


@dataclass
class LoggingConfig:
    """日志配置"""
    enabled: bool = True
    log_level: str = "INFO"
    log_dir: str = "./logs"
    max_file_size_mb: int = 100
    max_files: int = 7
    console_output: bool = True
    json_format: bool = True
    include_traceback: bool = True
    log_tool_calls: bool = True
    log_performance_metrics: bool = True


@dataclass
class ExecutionConfig:
    """执行配置"""
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout_per_task: float = 300.0
    fail_fast: bool = False
    checkpoint_interval: int = 3
    enable_checkpoints: bool = True
    parallel_execution: bool = False
    max_concurrent_tasks: int = 3


@dataclass
class MonitoringConfig:
    """监控配置"""
    enable_performance_monitoring: bool = True
    track_memory_usage: bool = True
    track_tool_usage: bool = True
    save_intermediate_results: bool = False
    enable_error_analysis: bool = True
    metrics_retention_days: int = 30


@dataclass
class OrchestraConfig:
    """完整的Orchestra配置"""
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)

    # 环境配置
    workspace_root: Optional[str] = None
    temp_dir: Optional[str] = None

    def __post_init__(self):
        """后处理配置"""
        if self.workspace_root is None:
            self.workspace_root = os.getenv("UTU_WORKSPACE_ROOT", "./workspace")

        if self.temp_dir is None:
            self.temp_dir = os.getenv("UTU_TEMP_DIR", "./temp")

        # 确保目录存在
        Path(self.workspace_root).mkdir(parents=True, exist_ok=True)
        Path(self.temp_dir).mkdir(parents=True, exist_ok=True)
        Path(self.logging.log_dir).mkdir(parents=True, exist_ok=True)


class OrchestraConfigManager:
    """Orchestra配置管理器"""

    @staticmethod
    def load_from_env() -> OrchestraConfig:
        """从环境变量加载配置"""
        return OrchestraConfig(
            logging=LoggingConfig(
                enabled=os.getenv("UTU_LOGGING_ENABLED", "true").lower() == "true",
                log_level=os.getenv("UTU_LOG_LEVEL", "INFO"),
                log_dir=os.getenv("UTU_LOG_DIR", "./logs"),
                max_file_size_mb=int(os.getenv("UTU_LOG_MAX_FILE_SIZE_MB", "100")),
                max_files=int(os.getenv("UTU_LOG_MAX_FILES", "7")),
                console_output=os.getenv("UTU_LOG_CONSOLE", "true").lower() == "true",
                json_format=os.getenv("UTU_LOG_JSON", "true").lower() == "true",
                include_traceback=os.getenv("UTU_LOG_TRACEBACK", "true").lower() == "true",
                log_tool_calls=os.getenv("UTU_LOG_TOOL_CALLS", "true").lower() == "true",
                log_performance_metrics=os.getenv("UTU_LOG_PERFORMANCE", "true").lower() == "true"
            ),
            execution=ExecutionConfig(
                max_retries=int(os.getenv("UTU_MAX_RETRIES", "3")),
                retry_delay=float(os.getenv("UTU_RETRY_DELAY", "1.0")),
                timeout_per_task=float(os.getenv("UTU_TASK_TIMEOUT", "300.0")),
                fail_fast=os.getenv("UTU_FAIL_FAST", "false").lower() == "true",
                checkpoint_interval=int(os.getenv("UTU_CHECKPOINT_INTERVAL", "3")),
                enable_checkpoints=os.getenv("UTU_ENABLE_CHECKPOINTS", "true").lower() == "true",
                parallel_execution=os.getenv("UTU_PARALLEL_EXECUTION", "false").lower() == "true",
                max_concurrent_tasks=int(os.getenv("UTU_MAX_CONCURRENT_TASKS", "3"))
            ),
            monitoring=MonitoringConfig(
                enable_performance_monitoring=os.getenv("UTU_ENABLE_MONITORING", "true").lower() == "true",
                track_memory_usage=os.getenv("UTU_TRACK_MEMORY", "true").lower() == "true",
                track_tool_usage=os.getenv("UTU_TRACK_TOOLS", "true").lower() == "true",
                save_intermediate_results=os.getenv("UTU_SAVE_INTERMEDIATE", "false").lower() == "true",
                enable_error_analysis=os.getenv("UTU_ENABLE_ERROR_ANALYSIS", "true").lower() == "true",
                metrics_retention_days=int(os.getenv("UTU_METRICS_RETENTION_DAYS", "30"))
            )
        )

    @staticmethod
    def load_from_dict(config_dict: Dict[str, Any]) -> OrchestraConfig:
        """从字典加载配置"""
        return OrchestraConfig(
            logging=LoggingConfig(**config_dict.get("logging", {})),
            execution=ExecutionConfig(**config_dict.get("execution", {})),
            monitoring=MonitoringConfig(**config_dict.get("monitoring", {})),
            workspace_root=config_dict.get("workspace_root"),
            temp_dir=config_dict.get("temp_dir")
        )

    @staticmethod
    def create_default() -> OrchestraConfig:
        """创建默认配置"""
        return OrchestraConfig()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "logging": {
                "enabled": self.logging.enabled,
                "log_level": self.logging.log_level,
                "log_dir": self.logging.log_dir,
                "max_file_size_mb": self.logging.max_file_size_mb,
                "max_files": self.logging.max_files,
                "console_output": self.logging.console_output,
                "json_format": self.logging.json_format,
                "include_traceback": self.logging.include_traceback,
                "log_tool_calls": self.logging.log_tool_calls,
                "log_performance_metrics": self.logging.log_performance_metrics
            },
            "execution": {
                "max_retries": self.execution.max_retries,
                "retry_delay": self.execution.retry_delay,
                "timeout_per_task": self.execution.timeout_per_task,
                "fail_fast": self.execution.fail_fast,
                "checkpoint_interval": self.execution.checkpoint_interval,
                "enable_checkpoints": self.execution.enable_checkpoints,
                "parallel_execution": self.execution.parallel_execution,
                "max_concurrent_tasks": self.execution.max_concurrent_tasks
            },
            "monitoring": {
                "enable_performance_monitoring": self.monitoring.enable_performance_monitoring,
                "track_memory_usage": self.monitoring.track_memory_usage,
                "track_tool_usage": self.monitoring.track_tool_usage,
                "save_intermediate_results": self.monitoring.save_intermediate_results,
                "enable_error_analysis": self.monitoring.enable_error_analysis,
                "metrics_retention_days": self.monitoring.metrics_retention_days
            },
            "workspace_root": self.workspace_root,
            "temp_dir": self.temp_dir
        }

    def save_to_file(self, file_path: str) -> None:
        """保存配置到文件"""
        import json
        config_dict = self.to_dict()

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)

    @staticmethod
    def load_from_file(file_path: str) -> OrchestraConfig:
        """从文件加载配置"""
        import json

        with open(file_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)

        return OrchestraConfigManager.load_from_dict(config_dict)

    def validate(self) -> List[str]:
        """验证配置，返回错误列表"""
        errors = []

        # 验证日志配置
        if self.logging.max_file_size_mb <= 0:
            errors.append("日志文件大小必须大于0")
        if self.logging.max_files <= 0:
            errors.append("日志文件数量必须大于0")
        if self.logging.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            errors.append(f"无效的日志级别: {self.logging.log_level}")

        # 验证执行配置
        if self.execution.max_retries < 0:
            errors.append("最大重试次数不能为负数")
        if self.execution.retry_delay < 0:
            errors.append("重试延迟不能为负数")
        if self.execution.timeout_per_task <= 0:
            errors.append("任务超时时间必须大于0")
        if self.execution.checkpoint_interval <= 0:
            errors.append("检查点间隔必须大于0")
        if self.execution.max_concurrent_tasks <= 0:
            errors.append("最大并发任务数必须大于0")

        # 验证监控配置
        if self.monitoring.metrics_retention_days <= 0:
            errors.append("指标保留天数必须大于0")

        return errors

    def get_logging_config_for_logger(self) -> Dict[str, Any]:
        """获取适用于日志记录器的配置"""
        return {
            "log_dir": self.logging.log_dir,
            "log_level": self.logging.log_level,
            "enabled": self.logging.enabled,
            "max_file_size_mb": self.logging.max_file_size_mb,
            "max_files": self.logging.max_files
        }

    def get_tool_logging_config(self) -> Dict[str, Any]:
        """获取工具日志配置"""
        return {
            "tool_logging_enabled": self.logging.log_tool_calls,
            "log_level": self.logging.log_level,
            "performance_logging": self.logging.log_performance_metrics
        }


# 全局配置实例
_global_config: Optional[OrchestraConfig] = None


def get_orchestra_config() -> OrchestraConfig:
    """获取全局Orchestra配置"""
    global _global_config
    if _global_config is None:
        _global_config = OrchestraConfigManager.load_from_env()
    return _global_config


def configure_orchestra(config: OrchestraConfig) -> None:
    """配置全局Orchestra设置"""
    global _global_config
    _global_config = config


def configure_orchestra_from_env() -> None:
    """从环境变量配置Orchestra"""
    configure_orchestra(OrchestraConfigManager.load_from_env())