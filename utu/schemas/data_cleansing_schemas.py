"""
数据清洗专用数据模型
扩展现有agent_schemas.py，添加数据清洗相关的数据类型和结构
"""

from typing import Dict, Any, List, Optional, Union, Literal
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime

# 导入现有的数据模型
from .agent_schemas import DataType, AgentMessage


class DataCleansingDataType(Enum):
    """数据清洗专用数据类型枚举"""
    RAW_FINANCIAL_DATA = "raw_financial_data"                # 原始财务数据
    VALIDATED_DATA = "validated_data"                        # 已验证数据
    TRANSFORMED_DATA = "transformed_data"                    # 已转换数据
    CLEANSED_DATA = "cleansed_data"                          # 已清洗数据
    QUALITY_ASSESSED_DATA = "quality_assessed_data"        # 已质量评估数据
    
    # 中间处理数据类型
    NORMALIZED_DATA = "normalized_data"                      # 标准化数据
    MAPPED_DATA = "mapped_data"                              # 字段映射数据
    TYPE_CONVERTED_DATA = "type_converted_data"            # 类型转换数据
    
    # 错误和状态数据类型
    VALIDATION_ERROR = "validation_error"                    # 验证错误
    TRANSFORMATION_ERROR = "transformation_error"            # 转换错误
    QUALITY_ISSUE = "quality_issue"                         # 质量问题


class ProcessingStage(Enum):
    """数据处理阶段枚举"""
    INITIAL = "initial"                                     # 初始阶段
    VALIDATION = "validation"                               # 验证阶段
    TRANSFORMATION = "transformation"                       # 转换阶段
    QUALITY_ASSESSMENT = "quality_assessment"               # 质量评估阶段
    FINALIZATION = "finalization"                           # 最终化阶段


class QualityLevel(Enum):
    """数据质量等级枚举"""
    EXCELLENT = "excellent"                                 # 优秀 (90-100分)
    GOOD = "good"                                           # 良好 (75-89分)
    ACCEPTABLE = "acceptable"                               # 可接受 (60-74分)
    POOR = "poor"                                           # 差 (0-59分)
    UNKNOWN = "unknown"                                     # 未知


class IssueSeverity(Enum):
    """问题严重程度枚举"""
    CRITICAL = "critical"                                   # 严重 - 必须修复
    HIGH = "high"                                           # 高 - 建议修复
    MEDIUM = "medium"                                       # 中 - 可选修复
    LOW = "low"                                             # 低 - 提示信息


@dataclass
class QualityMetrics:
    """数据质量指标"""
    overall_score: float = 0.0
    completeness_score: float = 0.0
    accuracy_score: float = 0.0
    consistency_score: float = 0.0
    validity_score: float = 0.0
    timeliness_score: float = 0.0
    uniqueness_score: float = 0.0
    
    # 详细统计
    total_records: int = 0
    valid_records: int = 0
    missing_values: int = 0
    duplicate_records: int = 0
    outlier_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'overall_score': self.overall_score,
            'completeness_score': self.completeness_score,
            'accuracy_score': self.accuracy_score,
            'consistency_score': self.consistency_score,
            'validity_score': self.validity_score,
            'timeliness_score': self.timeliness_score,
            'uniqueness_score': self.uniqueness_score,
            'total_records': self.total_records,
            'valid_records': self.valid_records,
            'missing_values': self.missing_values,
            'duplicate_records': self.duplicate_records,
            'outlier_count': self.outlier_count
        }


@dataclass
class QualityIssue:
    """数据质量问题"""
    issue_id: str
    issue_type: str
    severity: IssueSeverity
    description: str
    affected_fields: List[str] = field(default_factory=list)
    affected_records: int = 0
    recommendation: str = ""
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'issue_id': self.issue_id,
            'issue_type': self.issue_type,
            'severity': self.severity.value,
            'description': self.description,
            'affected_fields': self.affected_fields,
            'affected_records': self.affected_records,
            'recommendation': self.recommendation,
            'detected_at': self.detected_at
        }


@dataclass
class DataValidationResult:
    """数据验证结果"""
    is_valid: bool
    data_type: str
    quality_score: float
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processing_suggestions: List[str] = field(default_factory=list)
    detected_issues: List[str] = field(default_factory=list)
    normalized_data: Optional[Dict[str, Any]] = None
    
    # 质量指标
    completeness_score: float = 0.0
    consistency_score: float = 0.0
    validity_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'is_valid': self.is_valid,
            'data_type': self.data_type,
            'quality_score': self.quality_score,
            'errors': self.errors,
            'warnings': self.warnings,
            'processing_suggestions': self.processing_suggestions,
            'detected_issues': self.detected_issues,
            'normalized_data': self.normalized_data,
            'completeness_score': self.completeness_score,
            'consistency_score': self.consistency_score,
            'validity_score': self.validity_score
        }


@dataclass
class DataTransformResult:
    """数据转换结果"""
    success: bool
    original_format: str
    target_format: str
    transformed_data: Optional[Dict[str, Any]] = None
    
    # 转换统计
    fields_transformed: int = 0
    fields_added: int = 0
    fields_removed: int = 0
    values_converted: int = 0
    conversion_rate: float = 0.0
    
    # 处理信息
    transformation_log: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'success': self.success,
            'original_format': self.original_format,
            'target_format': self.target_format,
            'transformed_data': self.transformed_data,
            'fields_transformed': self.fields_transformed,
            'fields_added': self.fields_added,
            'fields_removed': self.fields_removed,
            'values_converted': self.values_converted,
            'conversion_rate': self.conversion_rate,
            'transformation_log': self.transformation_log,
            'errors': self.errors,
            'warnings': self.warnings,
            'metadata': self.metadata
        }


@dataclass
class DataQualityReport:
    """数据质量报告"""
    data_id: str
    assessment_time: str
    metrics: QualityMetrics
    quality_level: QualityLevel = QualityLevel.UNKNOWN
    issues: List[QualityIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    processing_summary: Dict[str, Any] = field(default_factory=dict)
    
    def get_critical_issues(self) -> List[QualityIssue]:
        """获取严重问题"""
        return [issue for issue in self.issues if issue.severity == IssueSeverity.CRITICAL]
    
    def get_high_priority_issues(self) -> List[QualityIssue]:
        """获取高优先级问题"""
        return [issue for issue in self.issues if issue.severity in [IssueSeverity.CRITICAL, IssueSeverity.HIGH]]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'data_id': self.data_id,
            'assessment_time': self.assessment_time,
            'metrics': self.metrics.to_dict(),
            'quality_level': self.quality_level.value,
            'issues': [issue.to_dict() for issue in self.issues],
            'recommendations': self.recommendations,
            'processing_summary': self.processing_summary
        }


@dataclass
class DataCleansingResult:
    """数据清洗结果"""
    processing_id: str
    success: bool
    original_data_format: str
    target_format: str
    
    # 核心数据
    original_data: Optional[Dict[str, Any]] = None
    cleansed_data: Optional[Dict[str, Any]] = None
    
    # 质量信息
    quality_score: float = 0.0
    quality_level: QualityLevel = QualityLevel.UNKNOWN
    quality_metrics: Optional[QualityMetrics] = None
    
    # 处理信息
    validation_result: Optional[DataValidationResult] = None
    transform_result: Optional[DataTransformResult] = None
    quality_report: Optional[DataQualityReport] = None
    
    # 统计和日志
    processing_time: float = 0.0
    issues_found: int = 0
    critical_issues: int = 0
    recommendations: List[str] = field(default_factory=list)
    processing_log: Dict[str, Any] = field(default_factory=dict)
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'processing_id': self.processing_id,
            'success': self.success,
            'original_data_format': self.original_data_format,
            'target_format': self.target_format,
            'original_data': self.original_data,
            'cleansed_data': self.cleansed_data,
            'quality_score': self.quality_score,
            'quality_level': self.quality_level.value,
            'quality_metrics': self.quality_metrics.to_dict() if self.quality_metrics else None,
            'validation_result': self.validation_result.to_dict() if self.validation_result else None,
            'transform_result': self.transform_result.to_dict() if self.transform_result else None,
            'quality_report': self.quality_report.to_dict() if self.quality_report else None,
            'processing_time': self.processing_time,
            'issues_found': self.issues_found,
            'critical_issues': self.critical_issues,
            'recommendations': self.recommendations,
            'processing_log': self.processing_log,
            'metadata': self.metadata
        }


@dataclass
class DataCleansingMessage(AgentMessage):
    """数据清洗专用消息格式"""
    
    # 扩展字段
    processing_stage: ProcessingStage = ProcessingStage.INITIAL
    cleansing_result: Optional[DataCleansingResult] = None
    quality_requirements: Dict[str, Any] = field(default_factory=dict)
    processing_options: Dict[str, Any] = field(default_factory=dict)
    
    def to_cleansing_dict(self) -> Dict[str, Any]:
        """转换为数据清洗专用格式"""
        base_dict = self.to_dict()
        cleansing_dict = {
            **base_dict,
            'processing_stage': self.processing_stage.value,
            'cleansing_result': self.cleansing_result.to_dict() if self.cleansing_result else None,
            'quality_requirements': self.quality_requirements,
            'processing_options': self.processing_options
        }
        return cleansing_dict


class DataCleansingMessageFactory:
    """数据清洗消息工厂"""
    
    @staticmethod
    def create_validation_request(data: Dict[str, Any], 
                                receiver: str,
                                options: Optional[Dict[str, Any]] = None) -> DataCleansingMessage:
        """创建验证请求消息"""
        return DataCleansingMessage(
            sender="DataCleanserAgent",
            receiver=receiver,
            data_type=DataType.RAW_FINANCIAL_DATA,
            content=data,
            processing_stage=ProcessingStage.VALIDATION,
            processing_options=options or {},
            metadata={
                'message_type': 'validation_request',
                'created_at': datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def create_transformation_request(data: Dict[str, Any],
                                     receiver: str,
                                     target_format: str,
                                     options: Optional[Dict[str, Any]] = None) -> DataCleansingMessage:
        """创建转换请求消息"""
        return DataCleansingMessage(
            sender="DataCleanserAgent",
            receiver=receiver,
            data_type=DataCleansingDataType.TRANSFORMED_DATA,
            content=data,
            processing_stage=ProcessingStage.TRANSFORMATION,
            processing_options={
                'target_format': target_format,
                **(options or {})
            },
            metadata={
                'message_type': 'transformation_request',
                'target_format': target_format,
                'created_at': datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def create_cleansed_data_message(cleansed_result: DataCleansingResult,
                                     receiver: str) -> DataCleansingMessage:
        """创建已清洗数据消息"""
        return DataCleansingMessage(
            sender="DataCleanserAgent",
            receiver=receiver,
            data_type=DataCleansingDataType.CLEANSED_DATA,
            content=cleansed_result.cleansed_data or {},
            processing_stage=ProcessingStage.FINALIZATION,
            cleansing_result=cleansed_result,
            metadata={
                'message_type': 'cleansed_data_delivery',
                'quality_score': cleansed_result.quality_score,
                'quality_level': cleansed_result.quality_level.value,
                'processing_id': cleansed_result.processing_id,
                'created_at': datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def create_quality_report_message(quality_report: DataQualityReport,
                                     receiver: str) -> DataCleansingMessage:
        """创建质量报告消息"""
        return DataCleansingMessage(
            sender="DataCleanserAgent",
            receiver=receiver,
            data_type=DataCleansingDataType.QUALITY_ASSESSED_DATA,
            content=quality_report.to_dict(),
            processing_stage=ProcessingStage.QUALITY_ASSESSMENT,
            metadata={
                'message_type': 'quality_report',
                'data_id': quality_report.data_id,
                'quality_level': quality_report.quality_level.value,
                'created_at': datetime.now().isoformat()
            }
        )


# 数据格式标准定义
class DataFormatStandards:
    """数据格式标准"""
    
    # 支持的原始数据格式
    SUPPORTED_INPUT_FORMATS = [
        "chinese_financial_format",      # 中文财务数据格式
        "standard_financial_format",     # 标准英文财务数据格式
        "user_custom_format",           # 用户自定义格式
        "historical_data_format",       # 历史数据格式
        "mixed_financial_format",       # 混合格式
        "array_format"                  # 数组格式
    ]
    
    # 支持的目标格式
    SUPPORTED_OUTPUT_FORMATS = [
        "data_analysis_agent_compatible",    # DataAnalysisAgent兼容格式
        "chart_generator_compatible",       # ChartGeneratorAgent兼容格式
        "report_agent_compatible",          # ReportAgent兼容格式
        "standard_financial_format"         # 标准财务数据格式
    ]
    
    # 质量等级定义
    QUALITY_LEVEL_THRESHOLDS = {
        QualityLevel.EXCELLENT: (90, 100),
        QualityLevel.GOOD: (75, 89),
        QualityLevel.ACCEPTABLE: (60, 74),
        QualityLevel.POOR: (0, 59)
    }
    
    # 必需字段定义
    REQUIRED_FIELDS = {
        'income_statement': ['revenue', 'net_profit'],
        'balance_sheet': ['total_assets', 'total_liabilities', 'total_equity'],
        'cash_flow': ['operating_cash_flow']
    }
    
    # 字段名映射
    FIELD_MAPPINGS = {
        'income_statement': {
            '营业收入': ['revenue', 'operating_revenue', 'sales_revenue'],
            '净利润': ['net_profit', 'net_income'],
            '营业利润': ['operating_profit', 'operating_income']
        },
        'balance_sheet': {
            '总资产': ['total_assets', 'assets'],
            '总负债': ['total_liabilities', 'liabilities'],
            '所有者权益': ['total_equity', 'shareholders_equity']
        },
        'cash_flow': {
            '经营活动现金流量净额': ['operating_cash_flow', 'ocf'],
            '投资活动现金流量净额': ['investing_cash_flow', 'icf'],
            '筹资活动现金流量净额': ['financing_cash_flow', 'fcf']
        }
    }


# 便捷函数
def create_cleansing_message(message_type: str,
                          data: Any,
                          receiver: str,
                          **kwargs) -> DataCleansingMessage:
    """
    创建数据清洗消息的便捷函数
    
    Args:
        message_type: 消息类型
        data: 数据内容
        receiver: 接收方
        **kwargs: 其他参数
        
    Returns:
        DataCleansingMessage: 数据清洗消息
    """
    factory = DataCleansingMessageFactory()
    
    if message_type == "validation_request":
        return factory.create_validation_request(data, receiver, kwargs.get('options'))
    elif message_type == "transformation_request":
        return factory.create_transformation_request(
            data, receiver, 
            kwargs.get('target_format', 'data_analysis_agent_compatible'),
            kwargs.get('options')
        )
    elif message_type == "cleansed_data":
        return factory.create_cleansed_data_message(data, receiver)
    elif message_type == "quality_report":
        return factory.create_quality_report_message(data, receiver)
    else:
        # 默认创建基本消息
        return DataCleansingMessage(
            sender="DataCleanserAgent",
            receiver=receiver,
            data_type=DataType.RAW_FINANCIAL_DATA,
            content=data,
            metadata=kwargs
        )


def determine_quality_level(score: float) -> QualityLevel:
    """
    根据分数确定质量等级
    
    Args:
        score: 质量分数
        
    Returns:
        QualityLevel: 质量等级
    """
    for level, (min_score, max_score) in DataFormatStandards.QUALITY_LEVEL_THRESHOLDS.items():
        if min_score <= score <= max_score:
            return level
    return QualityLevel.UNKNOWN