"""
智能通用数据格式转换器
实现不同智能体间的自动数据格式转换
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import asdict
import re

from ..schemas import (
    DataType, AgentMessage, AgentDataFormatter,
    DataAnalysisAgentOutput, ChartGeneratorAgentInput
)
from ..tools.financial_data_converter import FinancialDataConverter

logger = logging.getLogger(__name__)

class UniversalDataConverter:
    """通用数据格式转换器"""
    
    def __init__(self):
        self.logger = logger
        self.financial_converter = FinancialDataConverter()
        
        # 数据类型映射规则
        self.conversion_rules = {
            # DataAnalysisAgent → ChartGeneratorAgent
            (DataType.FINANCIAL_RATIOS, DataType.CHART_DATA): self._convert_financial_ratios_to_chart,
            (DataType.RAW_FINANCIAL_DATA, DataType.CHART_DATA): self._convert_raw_financial_to_chart,
            (DataType.FINANCIAL_ANALYSIS, DataType.CHART_DATA): self._convert_analysis_to_chart,
            
            # 通用转换规则
            (DataType.TEXT_SUMMARY, DataType.FINANCIAL_RATIOS): self._extract_financial_ratios_from_text,
            (DataType.TEXT_SUMMARY, DataType.CHART_DATA): self._convert_text_to_chart,
        }
        
        # 智能体角色映射
        self.agent_role_mapping = {
            "DataAgent": "data_provider",
            "DataAnalysisAgent": "data_analyzer", 
            "FinancialAnalysisAgent": "financial_analyst",
            "ChartGeneratorAgent": "visualizer",
            "ReportAgent": "reporter"
        }
    
    def convert_message(self, message: AgentMessage, target_type: DataType, 
                       target_agent: str = None) -> AgentMessage:
        """
        转换消息到目标数据类型
        
        Args:
            message: 原始消息
            target_type: 目标数据类型
            target_agent: 目标智能体
            
        Returns:
            转换后的消息
        """
        try:
            self.logger.info(f"转换消息 {message.data_type} → {target_type}")
            
            # 查找转换规则
            conversion_key = (message.data_type, target_type)
            converter = self.conversion_rules.get(conversion_key)
            
            if converter:
                # 使用预定义转换规则
                converted_content = converter(message.content)
            else:
                # 尝试通用转换
                converted_content = self._auto_convert(message.content, target_type)
            
            # 创建转换后的消息
            converted_message = AgentMessage(
                sender=message.sender,
                receiver=target_agent,
                data_type=target_type,
                content=converted_content,
                metadata={
                    **message.metadata,
                    "converted_from": message.data_type.value,
                    "converted_by": "UniversalDataConverter",
                    "conversion_timestamp": message.timestamp
                }
            )
            
            self.logger.info(f"消息转换成功: {message.data_type} → {target_type}")
            return converted_message
            
        except Exception as e:
            self.logger.error(f"消息转换失败: {e}")
            # 返回错误消息
            return AgentMessage(
                sender=message.sender,
                receiver=target_agent,
                data_type=DataType.ERROR_INFO,
                content={
                    "error": str(e),
                    "original_content": message.content,
                    "original_type": message.data_type.value
                },
                metadata={"conversion_error": True}
            )
    
    def _convert_financial_ratios_to_chart(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """转换财务比率数据为图表格式"""
        try:
            # 使用已有的财务数据转换器
            chart_data_dict = self.financial_converter.convert_financial_ratios_to_chart_format(content)
            
            return {
                "chart_data": chart_data_dict,
                "data_summary": self._create_financial_summary(content),
                "suggested_charts": self._suggest_chart_types(content)
            }
        except Exception as e:
            self.logger.error(f"财务比率转换失败: {e}")
            raise
    
    def _convert_raw_financial_to_chart(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """转换原始财务数据为图表格式"""
        try:
            # 提取基础财务数据
            basic_data = self._extract_basic_financial_data(content)
            
            # 转换为图表格式
            chart_data_dict = self.financial_converter.convert_basic_financial_data_to_chart_format(basic_data)
            
            return {
                "chart_data": chart_data_dict,
                "data_summary": self._create_basic_data_summary(basic_data),
                "suggested_charts": ["bar", "pie", "comparison"]
            }
        except Exception as e:
            self.logger.error(f"原始财务数据转换失败: {e}")
            raise
    
    def _convert_analysis_to_chart(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """转换分析结果为图表格式"""
        try:
            # 从分析文本中提取关键数据点
            key_points = self._extract_key_points_from_analysis(content)
            
            # 创建适合可视化的数据结构
            chart_data = {
                "analysis_summary": {
                    "title": "财务分析要点",
                    "type": "bubble_chart",
                    "data": key_points
                }
            }
            
            return {
                "chart_data": chart_data,
                "data_summary": {"analysis_points_count": len(key_points)},
                "suggested_charts": ["bubble", "wordcloud"]
            }
        except Exception as e:
            self.logger.error(f"分析结果转换失败: {e}")
            raise
    
    def _extract_financial_ratios_from_text(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """从文本中提取财务比率数据"""
        try:
            text = content.get("raw_output", "") or str(content)
            
            # 使用正则表达式提取财务指标
            ratio_patterns = {
                "roe": r"(?:ROE|净资产收益率)[：:]\s*([0-9.]+)%",
                "roa": r"(?:ROA|总资产收益率)[：:]\s*([0-9.]+)%",
                "debt_ratio": r"(?:资产负债率|负债率)[：:]\s*([0-9.]+)%",
                "current_ratio": r"(?:流动比率)[：:]\s*([0-9.]+)",
                "gross_margin": r"(?:毛利率|销售毛利率)[：:]\s*([0-9.]+)%",
                "net_margin": r"(?:净利率|销售净利率)[：:]\s*([0-9.]+)%"
            }
            
            ratios = {}
            for key, pattern in ratio_patterns.items():
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    ratios[key] = float(match.group(1)) / 100 if "%" in pattern else float(match.group(1))
            
            if ratios:
                # 按类别分组
                categorized_ratios = {
                    "profitability": {},
                    "solvency": {},
                    "efficiency": {}
                }
                
                for key, value in ratios.items():
                    if key in ["roe", "roa", "gross_margin", "net_margin"]:
                        categorized_ratios["profitability"][key] = value
                    elif key in ["debt_ratio", "current_ratio"]:
                        categorized_ratios["solvency"][key] = value
                    else:
                        categorized_ratios["efficiency"][key] = value
                
                return categorized_ratios
            
            return {}
        except Exception as e:
            self.logger.error(f"文本财务比率提取失败: {e}")
            return {}
    
    def _convert_text_to_chart(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """转换文本为图表格式"""
        try:
            text = content.get("raw_output", "") or str(content)
            
            # 文本分析
            words = text.split()
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            
            # 创建简单的文本统计图表
            chart_data = {
                "text_statistics": {
                    "title": "文本统计分析",
                    "type": "bar",
                    "data": {
                        "总字数": len(words),
                        "总句数": len(sentences),
                        "平均句长": len(words) / len(sentences) if sentences else 0
                    }
                }
            }
            
            return {
                "chart_data": chart_data,
                "data_summary": {"text_length": len(text)},
                "suggested_charts": ["bar", "wordcloud"]
            }
        except Exception as e:
            self.logger.error(f"文本转图表失败: {e}")
            raise
    
    def _auto_convert(self, content: Dict[str, Any], target_type: DataType) -> Dict[str, Any]:
        """自动转换数据格式"""
        try:
            # 基于目标类型的通用转换逻辑
            if target_type == DataType.CHART_DATA:
                # 尝试将任何数据转换为图表格式
                return self._auto_convert_to_chart(content)
            elif target_type == DataType.TEXT_SUMMARY:
                # 转换为文本摘要
                return self._auto_convert_to_text(content)
            else:
                # 其他类型的转换
                return content
        except Exception as e:
            self.logger.error(f"自动转换失败: {e}")
            raise
    
    def _auto_convert_to_chart(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """自动转换为图表格式"""
        if isinstance(content, dict):
            # 检查是否已经是图表格式
            if any(key in content for key in ["title", "x_axis", "series", "data"]):
                return content
            
            # 尝试转换为标准图表格式
            if content:
                keys = list(content.keys())
                values = list(content.values())
                
                # 处理数值数据
                if values and isinstance(values[0], (int, float)):
                    return {
                        "title": "数据可视化",
                        "x_axis": keys,
                        "series": [{"name": "数值", "data": values}]
                    }
                elif values and isinstance(values[0], dict):
                    # 嵌套字典数据
                    return {
                        "title": "多维度数据分析",
                        "x_axis": list(values[0].keys()),
                        "series": [
                            {"name": key, "data": list(val.values()) if isinstance(val, dict) else [val]}
                            for key, val in content.items()
                        ]
                    }
        
        # 默认格式
        return {
            "title": "数据可视化",
            "type": "text",
            "content": str(content)
        }
    
    def _auto_convert_to_text(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """自动转换为文本格式"""
        if isinstance(content, dict):
            # 格式化字典为可读文本
            text_parts = ["数据摘要:"]
            for key, value in content.items():
                if isinstance(value, dict):
                    text_parts.append(f"{key}:")
                    for sub_key, sub_value in value.items():
                        text_parts.append(f"  {sub_key}: {sub_value}")
                else:
                    text_parts.append(f"{key}: {value}")
            
            return {"raw_output": "\\n".join(text_parts)}
        else:
            return {"raw_output": str(content)}
    
    def _extract_basic_financial_data(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """提取基础财务数据"""
        basic_data = {}
        
        # 常见财务字段映射
        field_mapping = {
            "revenue": ["营业收入", "总收入", "主营业务收入", "revenue"],
            "net_profit": ["净利润", "净收益", "net_profit", "net_income"],
            "total_assets": ["总资产", "资产总计", "total_assets"],
            "total_liabilities": ["总负债", "负债总计", "total_liabilities"],
            "total_equity": ["所有者权益", "股东权益", "total_equity"]
        }
        
        for target_field, possible_fields in field_mapping.items():
            for field in possible_fields:
                if field in content:
                    basic_data[target_field] = content[field]
                    break
        
        return basic_data
    
    def _create_financial_summary(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """创建财务数据摘要"""
        summary = {
            "data_type": "financial_ratios",
            "categories": list(content.keys()),
            "total_indicators": sum(len(category) if isinstance(category, dict) else 1 
                                  for category in content.values())
        }
        
        # 计算关键指标
        if "profitability" in content:
            summary["profitability_indicators"] = len(content["profitability"])
        if "solvency" in content:
            summary["solvency_indicators"] = len(content["solvency"])
        
        return summary
    
    def _create_basic_data_summary(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """创建基础数据摘要"""
        return {
            "data_type": "basic_financial_data",
            "available_metrics": list(content.keys()),
            "metrics_count": len(content)
        }
    
    def _suggest_chart_types(self, content: Dict[str, Any]) -> List[str]:
        """建议图表类型"""
        chart_types = []
        
        categories = list(content.keys())
        if "profitability" in categories:
            chart_types.extend(["bar", "radar"])
        if "solvency" in categories:
            chart_types.extend(["bar", "pie"])
        if len(categories) > 2:
            chart_types.append("radar")
        
        return list(set(chart_types))
    
    def _extract_key_points_from_analysis(self, content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从分析结果中提取关键点"""
        key_points = []
        
        # 从文本中提取关键信息
        text_fields = ["analysis", "summary", "conclusions", "insights"]
        for field in text_fields:
            if field in content:
                text = content[field]
                if isinstance(text, str):
                    # 简单的关键点提取
                    sentences = [s.strip() for s in text.split('.') if s.strip()]
                    for sentence in sentences[:5]:  # 取前5个句子
                        key_points.append({
                            "text": sentence,
                            "importance": 1.0,
                            "category": field
                        })
        
        return key_points
    
    def convert_trajectory(self, trajectory: List[AgentMessage], 
                         target_agent: str, target_data_type: DataType = None) -> List[AgentMessage]:
        """
        转换整个消息轨迹
        为特定目标智能体准备相关的历史消息
        """
        try:
            self.logger.info(f"转换消息轨迹，目标智能体: {target_agent}")
            
            converted_trajectory = []
            
            for message in trajectory:
                # 确定目标数据类型
                if target_data_type is None:
                    # 根据目标智能体自动推断
                    target_data_type = self._infer_target_data_type(target_agent)
                
                # 转换消息
                if message.data_type != target_data_type:
                    converted_message = self.convert_message(message, target_data_type, target_agent)
                    converted_trajectory.append(converted_message)
                else:
                    # 无需转换，直接添加
                    message.receiver = target_agent
                    converted_trajectory.append(message)
            
            self.logger.info(f"消息轨迹转换完成，共{len(converted_trajectory)}条消息")
            return converted_trajectory
            
        except Exception as e:
            self.logger.error(f"消息轨迹转换失败: {e}")
            return trajectory
    
    def _infer_target_data_type(self, agent_name: str) -> DataType:
        """根据智能体名称推断目标数据类型"""
        agent_type_mapping = {
            "ChartGeneratorAgent": DataType.CHART_DATA,
            "ReportAgent": DataType.REPORT_DATA,
            "FinancialAnalysisAgent": DataType.FINANCIAL_ANALYSIS,
            "DataAnalysisAgent": DataType.FINANCIAL_RATIOS,
            "DataAgent": DataType.RAW_FINANCIAL_DATA
        }
        
        return agent_type_mapping.get(agent_name, DataType.TEXT_SUMMARY)
    
    def analyze_data_compatibility(self, source_data: Dict[str, Any], 
                                 target_format: str) -> Dict[str, Any]:
        """分析数据兼容性"""
        try:
            compatibility_score = 0
            issues = []
            suggestions = []
            
            # 检查数据结构
            if isinstance(source_data, dict):
                compatibility_score += 30
                
                # 检查关键字段
                required_fields = {
                    "chart": ["title", "data"],
                    "financial": ["ratios", "period"],
                    "report": ["summary", "findings"]
                }
                
                if target_format in required_fields:
                    fields_found = sum(1 for field in required_fields[target_format] 
                                     if field in source_data)
                    field_score = (fields_found / len(required_fields[target_format])) * 40
                    compatibility_score += field_score
                    
                    if fields_found < len(required_fields[target_format]):
                        missing_fields = [field for field in required_fields[target_format] 
                                        if field not in source_data]
                        issues.append(f"缺少关键字段: {missing_fields}")
                        suggestions.append(f"建议添加字段: {missing_fields}")
                
                # 检查数据质量
                if any(value is None or value == "" for value in source_data.values()):
                    compatibility_score -= 20
                    issues.append("数据包含空值")
                    suggestions.append("建议清理空值数据")
            
            return {
                "compatibility_score": max(0, compatibility_score),
                "is_compatible": compatibility_score >= 70,
                "issues": issues,
                "suggestions": suggestions
            }
            
        except Exception as e:
            self.logger.error(f"数据兼容性分析失败: {e}")
            return {
                "compatibility_score": 0,
                "is_compatible": False,
                "issues": [f"分析失败: {str(e)}"],
                "suggestions": ["请检查数据格式"]
            }

# ===== 全局转换器实例 =====
universal_converter = UniversalDataConverter()

def convert_data_for_agent(source_data: Any, source_type: DataType, 
                          target_agent: str, source_agent: str = None) -> Dict[str, Any]:
    """
    便捷函数：为特定智能体转换数据
    
    Args:
        source_data: 源数据
        source_type: 源数据类型
        target_agent: 目标智能体
        source_agent: 源智能体
    
    Returns:
        转换后的数据
    """
    message = AgentMessage(
        sender=source_agent or "unknown",
        data_type=source_type,
        content=source_data if isinstance(source_data, dict) else {"value": source_data}
    )
    
    target_type = universal_converter._infer_target_data_type(target_agent)
    converted_message = universal_converter.convert_message(message, target_type, target_agent)
    
    return converted_message.content