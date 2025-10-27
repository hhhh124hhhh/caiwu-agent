"""
智能体标准化数据格式定义
定义每个智能体的标准输入输出格式和数据类型标记
"""

from typing import Dict, Any, List, Optional, Union, Literal
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime

class DataType(Enum):
    """数据类型枚举"""
    RAW_FINANCIAL_DATA = "raw_financial_data"           # 原始财务数据
    FINANCIAL_RATIOS = "financial_ratios"               # 财务比率数据
    FINANCIAL_ANALYSIS = "financial_analysis"           # 财务分析结果
    CHART_DATA = "chart_data"                          # 图表数据格式
    ANALYSIS_INSIGHTS = "analysis_insights"             # 分析洞察
    REPORT_DATA = "report_data"                        # 报告数据
    TEXT_SUMMARY = "text_summary"                      # 文本摘要
    ERROR_INFO = "error_info"                          # 错误信息

@dataclass
class AgentMessage:
    """标准化智能体消息格式"""
    sender: str                                        # 发送方智能体名称
    receiver: Optional[str] = None                     # 接收方智能体名称
    data_type: DataType = DataType.TEXT_SUMMARY        # 数据类型
    content: Dict[str, Any] = field(default_factory=dict)  # 数据内容
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0"                               # 格式版本
    
    def to_string(self) -> str:
        """转换为字符串格式，用于上下文传递"""
        return f"<AGENT_MESSAGE>{json.dumps(self.to_dict(), ensure_ascii=False)}</AGENT_MESSAGE>"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "data_type": self.data_type.value,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "version": self.version
        }
    
    @classmethod
    def from_string(cls, message_str: str) -> 'AgentMessage':
        """从字符串解析消息"""
        if "<AGENT_MESSAGE>" not in message_str:
            # 兼容旧格式
            return cls(
                sender="unknown",
                data_type=DataType.TEXT_SUMMARY,
                content={"raw_output": message_str}
            )
        
        try:
            json_str = message_str.replace("<AGENT_MESSAGE>", "").replace("</AGENT_MESSAGE>", "")
            data = json.loads(json_str)
            return cls(
                sender=data.get("sender", "unknown"),
                receiver=data.get("receiver"),
                data_type=DataType(data.get("data_type", "text_summary")),
                content=data.get("content", {}),
                metadata=data.get("metadata", {}),
                timestamp=data.get("timestamp"),
                version=data.get("version", "1.0")
            )
        except Exception:
            return cls(
                sender="unknown",
                data_type=DataType.TEXT_SUMMARY,
                content={"raw_output": message_str, "parse_error": True}
            )

# ===== 智能体标准化Schema定义 =====

@dataclass
class DataAgentInput:
    """DataAgent输入格式"""
    company_name: str                                 # 公司名称
    analysis_period: Optional[str] = None            # 分析期间
    data_sources: List[str] = field(default_factory=lambda: ["akshare"])  # 数据源
    report_types: List[str] = field(default_factory=lambda: ["income", "balance", "cashflow"])  # 报表类型

@dataclass 
class DataAgentOutput:
    """DataAgent输出格式"""
    status: Literal["success", "error"]             # 执行状态
    company_name: str                               # 公司名称
    period: str                                     # 数据期间
    data_files: Dict[str, str] = field(default_factory=dict)  # 数据文件路径
    raw_data: Optional[Dict[str, Any]] = None       # 原始数据内容
    warnings: List[str] = field(default_factory=list)  # 警告信息
    errors: List[str] = field(default_factory=list)  # 错误信息

@dataclass
class DataAnalysisAgentInput:
    """DataAnalysisAgent输入格式"""
    company_name: str                               # 公司名称
    financial_data: Dict[str, Any]                  # 财务数据
    analysis_types: List[str] = field(default_factory=lambda: ["ratios", "trends", "health"])  # 分析类型
    comparison_benchmark: Optional[str] = None       # 对比基准

@dataclass
class DataAnalysisAgentOutput:
    """DataAnalysisAgent输出格式"""
    status: Literal["success", "error"]             # 执行状态
    company_name: str                               # 公司名称
    analysis_period: str                            # 分析期间
    
    # 财务比率分析
    profitability: Optional[Dict[str, float]] = None    # 盈利能力指标
    solvency: Optional[Dict[str, float]] = None         # 偿债能力指标
    efficiency: Optional[Dict[str, float]] = None       # 运营效率指标
    growth: Optional[Dict[str, float]] = None           # 成长能力指标
    cash_flow: Optional[Dict[str, float]] = None        # 现金流指标
    
    # 趋势分析
    trend_analysis: Optional[Dict[str, Any]] = None    # 趋势分析结果
    
    # 健康评估
    health_assessment: Optional[Dict[str, Any]] = None # 健康评估结果
    
    warnings: List[str] = field(default_factory=list)  # 警告信息
    errors: List[str] = field(default_factory=list)    # 错误信息

@dataclass
class FinancialAnalysisAgentInput:
    """FinancialAnalysisAgent输入格式"""
    company_name: str                               # 公司名称
    financial_ratios: Dict[str, Any]                # 财务比率数据
    trend_data: Optional[Dict[str, Any]] = None     # 趋势数据
    health_assessment: Optional[Dict[str, Any]] = None # 健康评估
    industry_context: Optional[str] = None          # 行业背景
    analysis_focus: List[str] = field(default_factory=lambda: ["investment", "risk"])  # 分析重点

@dataclass
class FinancialAnalysisAgentOutput:
    """FinancialAnalysisAgent输出格式"""
    status: Literal["success", "error"]             # 执行状态
    company_name: str                               # 公司名称
    
    # 分析结果
    performance_analysis: Dict[str, str]            # 业绩分析
    risk_assessment: Dict[str, str]                 # 风险评估
    investment_opportunities: List[str]             # 投资机会
    investment_risks: List[str]                     # 投资风险
    
    # 建议和结论
    recommendation: str                             # 总体建议
    confidence_level: float                         # 置信度 (0-1)
    key_insights: List[str]                         # 关键洞察
    
    supporting_data: Dict[str, Any] = field(default_factory=dict)  # 支撑数据

@dataclass
class ChartGeneratorAgentInput:
    """ChartGeneratorAgent输入格式"""
    company_name: str                               # 公司名称
    analysis_data: Dict[str, Any]                   # 分析数据（可能包含多种格式）
    chart_requirements: Optional[Dict[str, Any]] = None  # 图表要求
    output_format: str = "png"                      # 输出格式
    chart_types: List[str] = field(default_factory=lambda: ["auto"])  # 图表类型

@dataclass
class ChartGeneratorAgentOutput:
    """ChartGeneratorAgent输出格式"""
    status: Literal["success", "error"]             # 执行状态
    company_name: str                               # 公司名称
    
    # 生成的图表
    charts: List[Dict[str, Any]] = field(default_factory=list)  # 图表列表
    chart_files: List[str] = field(default_factory=list)        # 图表文件路径
    
    # 图表说明
    chart_descriptions: Dict[str, str] = field(default_factory=dict)  # 图表说明
    data_summary: Dict[str, Any] = field(default_factory=dict)        # 数据摘要
    
    errors: List[str] = field(default_factory=list)    # 错误信息

@dataclass
class ReportAgentInput:
    """ReportAgent输入格式"""
    company_name: str                               # 公司名称
    analysis_results: Dict[str, Any]                # 所有分析结果
    charts: List[Dict[str, Any]]                   # 图表数据
    report_format: List[str] = field(default_factory=lambda: ["pdf", "html"])  # 报告格式
    template_style: Optional[str] = None           # 模板样式

@dataclass
class ReportAgentOutput:
    """ReportAgent输出格式"""
    status: Literal["success", "error"]             # 执行状态
    company_name: str                               # 公司名称
    report_summary: str                             # 报告摘要
    
    # 生成的报告
    report_files: Dict[str, str] = field(default_factory=dict)  # 报告文件路径
    
    # 关键内容
    key_findings: List[str] = field(default_factory=list)      # 主要发现
    recommendations: List[str] = field(default_factory=list)   # 建议列表
    risk_warnings: List[str] = field(default_factory=list)     # 风险提示
    
    errors: List[str] = field(default_factory=list)    # 错误信息

# ===== 数据格式转换器 =====

class AgentDataFormatter:
    """智能体数据格式转换器"""
    
    @staticmethod
    def format_data_agent_input(raw_input: Dict[str, Any]) -> DataAgentInput:
        """格式化DataAgent输入"""
        return DataAgentInput(
            company_name=raw_input.get("company_name", ""),
            analysis_period=raw_input.get("period"),
            data_sources=raw_input.get("data_sources", ["akshare"]),
            report_types=raw_input.get("report_types", ["income", "balance", "cashflow"])
        )
    
    @staticmethod
    def create_agent_message(sender: str, data: Any, data_type: DataType, 
                           receiver: str = None, metadata: Dict = None) -> AgentMessage:
        """创建标准化智能体消息"""
        return AgentMessage(
            sender=sender,
            receiver=receiver,
            data_type=data_type,
            content=data if isinstance(data, dict) else {"value": data},
            metadata=metadata or {}
        )
    
    @staticmethod
    def extract_financial_ratios(message: AgentMessage) -> Optional[Dict[str, Any]]:
        """从消息中提取财务比率数据"""
        if message.data_type == DataType.FINANCIAL_RATIOS:
            return message.content
        
        # 尝试从文本摘要中解析财务比率
        if message.data_type == DataType.TEXT_SUMMARY:
            content = message.content.get("raw_output", "")
            # 这里可以添加更智能的解析逻辑
            try:
                if "{" in content and "}" in content:
                    import re
                    json_match = re.search(r'\\{[^}]*\\}', content)
                    if json_match:
                        return json.loads(json_match.group())
            except Exception:
                pass
        
        return None
    
    @staticmethod
    def compress_trajectory(trajectory: List[AgentMessage], max_tokens: int = 2000) -> List[AgentMessage]:
        """压缩历史轨迹，保留关键信息"""
        if not trajectory:
            return []
        
        # 按重要性排序消息类型
        priority_map = {
            DataType.FINANCIAL_RATIOS: 5,
            DataType.CHART_DATA: 4,
            DataType.FINANCIAL_ANALYSIS: 4,
            DataType.RAW_FINANCIAL_DATA: 3,
            DataType.ANALYSIS_INSIGHTS: 2,
            DataType.REPORT_DATA: 1,
            DataType.TEXT_SUMMARY: 1,
            DataType.ERROR_INFO: 0
        }
        
        # 按优先级排序
        sorted_messages = sorted(trajectory, 
                               key=lambda x: priority_map.get(x.data_type, 1), 
                               reverse=True)
        
        # 简单截断，实际应用中可以更智能
        compressed = sorted_messages[:max_tokens//100]  # 假设每条消息约100 tokens
        
        return compressed

# ===== 使用示例 =====

if __name__ == "__main__":
    # 示例：创建标准化消息
    ratios_data = {
        "profitability": {"roe": 0.15, "roa": 0.08},
        "solvency": {"debt_ratio": 0.6}
    }
    
    message = AgentDataFormatter.create_agent_message(
        sender="DataAnalysisAgent",
        data=ratios_data,
        data_type=DataType.FINANCIAL_RATIOS,
        receiver="ChartGeneratorAgent",
        metadata={"company": "陕西建工", "period": "2024"}
    )
    
    print("标准化消息格式:")
    print(message.to_string())
    
    # 示例：解析消息
    parsed_message = AgentMessage.from_string(message.to_string())
    print("\n解析结果:")
    print(f"发送方: {parsed_message.sender}")
    print(f"数据类型: {parsed_message.data_type}")
    print(f"内容: {parsed_message.content}")