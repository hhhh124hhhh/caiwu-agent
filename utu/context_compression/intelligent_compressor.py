"""
智能上下文压缩功能
优化智能体间的上下文传递，减少冗余信息，提高效率
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import re
import hashlib

from ..schemas import AgentMessage, DataType, AgentDataFormatter

logger = logging.getLogger(__name__)

@dataclass
class CompressionMetrics:
    """压缩指标"""
    original_size: int                               # 原始大小（字符数）
    compressed_size: int                             # 压缩后大小
    compression_ratio: float                         # 压缩比
    preserved_info_ratio: float                      # 信息保留比例
    compression_time: float                          # 压缩耗时（秒）
    strategy_used: str                               # 使用的压缩策略

@dataclass
class ContextSummary:
    """上下文摘要"""
    key_points: List[str]                           # 关键点
    data_summary: Dict[str, Any]                    # 数据摘要
    agent_insights: Dict[str, str]                  # 智能体洞察
    timeline: List[Dict[str, Any]]                  # 时间线
    compression_metadata: Dict[str, Any]            # 压缩元数据

class IntelligentContextCompressor:
    """智能上下文压缩器"""
    
    def __init__(self):
        self.logger = logger
        
        # 压缩策略配置
        self.compression_strategies = {
            "selective_preservation": self._selective_preservation,
            "semantic_compression": self._semantic_compression,
            "data_extraction": self._data_extraction,
            "temporal_compression": self._temporal_compression,
            "hierarchical_compression": self._hierarchical_compression
        }
        
        # 数据类型优先级（越高越重要）
        self.data_type_priority = {
            DataType.FINANCIAL_RATIOS: 10,
            DataType.CHART_DATA: 9,
            DataType.FINANCIAL_ANALYSIS: 8,
            DataType.RAW_FINANCIAL_DATA: 7,
            DataType.ANALYSIS_INSIGHTS: 6,
            DataType.REPORT_DATA: 5,
            DataType.ERROR_INFO: 4,
            DataType.TEXT_SUMMARY: 3
        }
        
        # 智能体重要性权重
        self.agent_importance = {
            "DataAnalysisAgent": 1.0,
            "FinancialAnalysisAgent": 0.9,
            "ChartGeneratorAgent": 0.8,
            "DataAgent": 0.7,
            "ReportAgent": 0.6
        }
        
        # 压缩阈值配置
        self.compression_thresholds = {
            "max_token_limit": 4000,                   # 最大token限制
            "compression_trigger_ratio": 0.7,         # 触发压缩的比率
            "min_compression_ratio": 0.3,             # 最小压缩比
            "info_loss_threshold": 0.2                 # 信息损失阈值
        }
    
    def compress_context(self, messages: List[AgentMessage], 
                        target_agent: str = None,
                        max_tokens: int = None,
                        preserve_strategy: str = "auto") -> Tuple[List[AgentMessage], CompressionMetrics]:
        """
        压缩上下文消息
        
        Args:
            messages: 原始消息列表
            target_agent: 目标智能体
            max_tokens: 最大token限制
            preserve_strategy: 保留策略
            
        Returns:
            压缩后的消息列表和压缩指标
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(f"开始压缩上下文，原始消息数: {len(messages)}")
            
            # 计算原始大小
            original_size = sum(len(msg.to_string()) for msg in messages)
            
            # 确定压缩目标
            max_tokens = max_tokens or self.compression_thresholds["max_token_limit"]
            estimated_tokens = original_size // 4  # 粗略估计token数
            
            if estimated_tokens <= max_tokens:
                self.logger.info("上下文大小在限制范围内，无需压缩")
                return messages, CompressionMetrics(
                    original_size=original_size,
                    compressed_size=original_size,
                    compression_ratio=1.0,
                    preserved_info_ratio=1.0,
                    compression_time=0,
                    strategy_used="no_compression"
                )
            
            # 选择压缩策略
            strategy = self._select_compression_strategy(messages, max_tokens, preserve_strategy)
            
            # 执行压缩
            compressed_messages = self.compression_strategies[strategy](messages, target_agent, max_tokens)
            
            # 计算压缩指标
            compressed_size = sum(len(msg.to_string()) for msg in compressed_messages)
            compression_time = (datetime.now() - start_time).total_seconds()
            
            metrics = CompressionMetrics(
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compressed_size / original_size,
                preserved_info_ratio=self._calculate_info_preservation(messages, compressed_messages),
                compression_time=compression_time,
                strategy_used=strategy
            )
            
            self.logger.info(f"上下文压缩完成: {metrics.compression_ratio:.2f} 压缩比, "
                           f"信息保留率: {metrics.preserved_info_ratio:.2f}")
            
            return compressed_messages, metrics
            
        except Exception as e:
            self.logger.error(f"上下文压缩失败: {e}")
            return messages, CompressionMetrics(
                original_size=len(messages),
                compressed_size=len(messages),
                compression_ratio=1.0,
                preserved_info_ratio=1.0,
                compression_time=0,
                strategy_used="failed"
            )
    
    def _select_compression_strategy(self, messages: List[AgentMessage], 
                                   max_tokens: int, preserve_strategy: str) -> str:
        """选择压缩策略"""
        if preserve_strategy != "auto":
            return preserve_strategy
        
        # 分析消息特征
        has_financial_data = any(msg.data_type == DataType.FINANCIAL_RATIOS for msg in messages)
        has_multiple_agents = len(set(msg.sender for msg in messages)) > 2
        temporal_span = self._calculate_temporal_span(messages)
        
        # 策略选择逻辑
        if has_financial_data and has_multiple_agents:
            return "hierarchical_compression"
        elif temporal_span and temporal_span > timedelta(hours=1):
            return "temporal_compression"
        elif any(msg.data_type in [DataType.FINANCIAL_RATIOS, DataType.CHART_DATA] for msg in messages):
            return "data_extraction"
        elif len(messages) > 5:
            return "semantic_compression"
        else:
            return "selective_preservation"
    
    def _selective_preservation(self, messages: List[AgentMessage], 
                              target_agent: str, max_tokens: int) -> List[AgentMessage]:
        """选择性保留压缩策略"""
        # 按重要性排序消息
        scored_messages = []
        
        for msg in messages:
            # 计算消息重要性分数
            priority_score = self.data_type_priority.get(msg.data_type, 1)
            agent_score = self.agent_importance.get(msg.sender, 0.5)
            recency_score = self._calculate_recency_score(msg)
            
            total_score = priority_score * agent_score * recency_score
            
            scored_messages.append((msg, total_score))
        
        # 按分数排序
        scored_messages.sort(key=lambda x: x[1], reverse=True)
        
        # 选择最重要的消息直到达到token限制
        selected_messages = []
        current_tokens = 0
        
        for msg, score in scored_messages:
            msg_tokens = len(msg.to_string()) // 4
            
            if current_tokens + msg_tokens <= max_tokens:
                selected_messages.append(msg)
                current_tokens += msg_tokens
            else:
                # 尝试压缩这条消息
                compressed_msg = self._compress_single_message(msg, max_tokens - current_tokens)
                if compressed_msg:
                    selected_messages.append(compressed_msg)
                break
        
        return selected_messages
    
    def _semantic_compression(self, messages: List[AgentMessage], 
                            target_agent: str, max_tokens: int) -> List[AgentMessage]:
        """语义压缩策略"""
        compressed_messages = []
        
        # 按发送方分组消息
        agent_groups = {}
        for msg in messages:
            if msg.sender not in agent_groups:
                agent_groups[msg.sender] = []
            agent_groups[msg.sender].append(msg)
        
        # 为每个智能体创建语义摘要
        for agent, agent_messages in agent_groups.items():
            if len(agent_messages) == 1:
                compressed_messages.extend(agent_messages)
            else:
                # 合并同类型消息
                merged_message = self._merge_similar_messages(agent_messages)
                if merged_message:
                    compressed_messages.append(merged_message)
        
        # 如果仍然超过限制，应用选择性保留
        total_tokens = sum(len(msg.to_string()) // 4 for msg in compressed_messages)
        if total_tokens > max_tokens:
            compressed_messages, _ = self._selective_preservation(compressed_messages, target_agent, max_tokens)
        
        return compressed_messages
    
    def _data_extraction(self, messages: List[AgentMessage], 
                        target_agent: str, max_tokens: int) -> List[AgentMessage]:
        """数据提取压缩策略"""
        compressed_messages = []
        
        for msg in messages:
            if msg.data_type in [DataType.FINANCIAL_RATIOS, DataType.CHART_DATA, DataType.RAW_FINANCIAL_DATA]:
                # 保留完整数据内容
                compressed_msg = AgentMessage(
                    sender=msg.sender,
                    receiver=target_agent,
                    data_type=msg.data_type,
                    content=self._extract_key_data(msg.content),
                    metadata={**msg.metadata, "compressed": True}
                )
                compressed_messages.append(compressed_msg)
            else:
                # 压缩文本内容
                summary = self._create_text_summary(msg.content)
                compressed_msg = AgentMessage(
                    sender=msg.sender,
                    receiver=target_agent,
                    data_type=DataType.TEXT_SUMMARY,
                    content={"summary": summary, "original_type": msg.data_type.value},
                    metadata={**msg.metadata, "compressed": True}
                )
                compressed_messages.append(compressed_msg)
        
        return compressed_messages
    
    def _temporal_compression(self, messages: List[AgentMessage], 
                            target_agent: str, max_tokens: int) -> List[AgentMessage]:
        """时间压缩策略"""
        # 按时间排序
        sorted_messages = sorted(messages, key=lambda x: x.timestamp)
        
        # 创建时间线摘要
        timeline_summary = self._create_timeline_summary(sorted_messages)
        
        # 保留关键时间点的消息
        key_messages = self._select_key_temporal_messages(sorted_messages, max_tokens)
        
        # 添加时间线摘要
        timeline_msg = AgentMessage(
            sender="ContextCompressor",
            receiver=target_agent,
            data_type=DataType.TEXT_SUMMARY,
            content={"timeline_summary": timeline_summary},
            metadata={"compression_type": "temporal"}
        )
        
        return [timeline_msg] + key_messages
    
    def _hierarchical_compression(self, messages: List[AgentMessage], 
                                target_agent: str, max_tokens: int) -> List[AgentMessage]:
        """分层压缩策略"""
        # 按数据类型分层
        layers = {
            DataType.FINANCIAL_RATIOS: [],
            DataType.CHART_DATA: [],
            DataType.FINANCIAL_ANALYSIS: [],
            DataType.RAW_FINANCIAL_DATA: [],
            DataType.ANALYSIS_INSIGHTS: [],
            DataType.TEXT_SUMMARY: [],
            DataType.ERROR_INFO: []
        }
        
        for msg in messages:
            layers[msg.data_type].append(msg)
        
        compressed_messages = []
        allocated_tokens = 0
        
        # 按重要性分配token
        for data_type, type_messages in sorted(layers.items(), 
                                             key=lambda x: self.data_type_priority.get(x[0], 0), 
                                             reverse=True):
            if not type_messages:
                continue
            
            # 为该层分配token
            layer_priority = self.data_type_priority.get(data_type, 1)
            layer_tokens = int((layer_priority / sum(self.data_type_priority.values())) * max_tokens)
            
            if allocated_tokens + layer_tokens > max_tokens:
                layer_tokens = max_tokens - allocated_tokens
            
            if layer_tokens <= 0:
                break
            
            # 压缩该层消息
            layer_compressed = self._compress_layer(type_messages, layer_tokens)
            compressed_messages.extend(layer_compressed)
            allocated_tokens += sum(len(msg.to_string()) // 4 for msg in layer_compressed)
        
        return compressed_messages
    
    def _compress_single_message(self, message: AgentMessage, max_tokens: int) -> Optional[AgentMessage]:
        """压缩单条消息"""
        if len(message.to_string()) // 4 <= max_tokens:
            return message
        
        # 尝试提取关键信息
        if message.data_type == DataType.TEXT_SUMMARY:
            summary = self._summarize_text(message.content.get("raw_output", ""), max_tokens * 3)
            return AgentMessage(
                sender=message.sender,
                receiver=message.receiver,
                data_type=DataType.TEXT_SUMMARY,
                content={"summary": summary},
                metadata={**message.metadata, "compressed": True}
            )
        elif message.data_type == DataType.FINANCIAL_RATIOS:
            # 保留最重要的财务比率
            key_ratios = self._extract_key_ratios(message.content)
            return AgentMessage(
                sender=message.sender,
                receiver=message.receiver,
                data_type=DataType.FINANCIAL_RATIOS,
                content=key_ratios,
                metadata={**message.metadata, "compressed": True}
            )
        
        return None
    
    def _merge_similar_messages(self, messages: List[AgentMessage]) -> Optional[AgentMessage]:
        """合并相似消息"""
        if not messages:
            return None
        
        # 按数据类型合并
        data_types = list(set(msg.data_type for msg in messages))
        if len(data_types) > 1:
            # 不同类型，分别处理
            return None
        
        data_type = data_types[0]
        
        if data_type == DataType.FINANCIAL_RATIOS:
            # 合并财务比率数据
            merged_content = {}
            for msg in messages:
                merged_content.update(msg.content)
            
            return AgentMessage(
                sender=messages[0].sender,
                receiver=messages[0].receiver,
                data_type=data_type,
                content=merged_content,
                metadata={"merged_from": [msg.sender for msg in messages], "compressed": True}
            )
        
        return None
    
    def _extract_key_data(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """提取关键数据"""
        if not isinstance(content, dict):
            return content
        
        key_data = {}
        
        # 财务比率数据的关键字段
        if "profitability" in content:
            key_data["profitability"] = content["profitability"]
        if "solvency" in content:
            key_data["solvency"] = content["solvency"]
        if "warnings" in content:
            key_data["warnings"] = content["warnings"]
        
        # 图表数据的关键字段
        if "chart_data" in content:
            key_data["chart_data"] = content["chart_data"]
        
        return key_data
    
    def _create_text_summary(self, content: Any, max_length: int = 500) -> str:
        """创建文本摘要"""
        if isinstance(content, dict):
            text = content.get("raw_output", "") or str(content)
        else:
            text = str(content)
        
        # 简单的文本摘要算法
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if len(text) <= max_length:
            return text
        
        # 选择前几个重要句子
        summary_sentences = []
        current_length = 0
        
        for sentence in sentences:
            if current_length + len(sentence) + 1 <= max_length:
                summary_sentences.append(sentence)
                current_length += len(sentence) + 1
            else:
                break
        
        return '. '.join(summary_sentences) + '.'
    
    def _calculate_recency_score(self, message: AgentMessage) -> float:
        """计算消息新近度分数"""
        try:
            msg_time = datetime.fromisoformat(message.timestamp)
            time_diff = datetime.now() - msg_time
            
            # 越新的消息分数越高
            if time_diff.total_seconds() < 300:  # 5分钟内
                return 1.0
            elif time_diff.total_seconds() < 3600:  # 1小时内
                return 0.8
            elif time_diff.total_seconds() < 86400:  # 1天内
                return 0.6
            else:
                return 0.4
        except Exception:
            return 0.5
    
    def _calculate_temporal_span(self, messages: List[AgentMessage]) -> Optional[timedelta]:
        """计算消息时间跨度"""
        if not messages:
            return None
        
        try:
            timestamps = []
            for msg in messages:
                timestamps.append(datetime.fromisoformat(msg.timestamp))
            
            return max(timestamps) - min(timestamps)
        except Exception:
            return None
    
    def _create_timeline_summary(self, messages: List[AgentMessage]) -> Dict[str, Any]:
        """创建时间线摘要"""
        timeline = []
        
        for msg in messages:
            try:
                msg_time = datetime.fromisoformat(msg.timestamp)
                timeline.append({
                    "time": msg_time.isoformat(),
                    "agent": msg.sender,
                    "type": msg.data_type.value,
                    "summary": self._create_message_summary(msg)
                })
            except Exception:
                continue
        
        return {
            "events": timeline,
            "total_events": len(timeline),
            "agents_involved": list(set(msg["agent"] for msg in timeline))
        }
    
    def _select_key_temporal_messages(self, messages: List[AgentMessage], max_tokens: int) -> List[AgentMessage]:
        """选择关键时间点消息"""
        # 选择每个智能体的最后一条消息
        agent_last_messages = {}
        
        for msg in messages:
            if msg.sender not in agent_last_messages:
                agent_last_messages[msg.sender] = msg
            else:
                try:
                    existing_time = datetime.fromisoformat(agent_last_messages[msg.sender].timestamp)
                    current_time = datetime.fromisoformat(msg.timestamp)
                    if current_time > existing_time:
                        agent_last_messages[msg.sender] = msg
                except Exception:
                    continue
        
        return list(agent_last_messages.values())
    
    def _compress_layer(self, messages: List[AgentMessage], max_tokens: int) -> List[AgentMessage]:
        """压缩特定层的消息"""
        if len(messages) == 1:
            return messages
        
        # 根据消息数量选择策略
        if len(messages) <= 3:
            return messages  # 少量消息不需要压缩
        elif len(messages) <= 10:
            # 合并相似消息
            merged = self._merge_similar_messages(messages)
            return [merged] if merged else messages[:1]
        else:
            # 选择代表性消息
            return self._select_representative_messages(messages, max_tokens)
    
    def _select_representative_messages(self, messages: List[AgentMessage], max_tokens: int) -> List[AgentMessage]:
        """选择代表性消息"""
        # 简单策略：均匀选择消息
        if len(messages) <= max_tokens // 100:  # 假设每条消息约100 tokens
            return messages
        
        step = len(messages) // (max_tokens // 100)
        selected = [messages[i] for i in range(0, len(messages), step)]
        
        return selected[:max_tokens // 100]
    
    def _create_message_summary(self, message: AgentMessage) -> str:
        """创建消息摘要"""
        if message.data_type == DataType.TEXT_SUMMARY:
            content = message.content.get("raw_output", "")[:100]
            return f"文本消息: {content}..."
        elif message.data_type == DataType.FINANCIAL_RATIOS:
            categories = list(message.content.keys())
            return f"财务比率数据: {', '.join(categories)}"
        elif message.data_type == DataType.CHART_DATA:
            chart_count = len(message.content.get("chart_data", {}))
            return f"图表数据: {chart_count} 个图表"
        else:
            return f"{message.data_type.value} 消息"
    
    def _summarize_text(self, text: str, max_length: int) -> str:
        """文本摘要"""
        if len(text) <= max_length:
            return text
        
        # 简单截断
        return text[:max_length-3] + "..."
    
    def _extract_key_ratios(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """提取关键财务比率"""
        key_ratios = {}
        
        # 优先保留的指标
        priority_indicators = {
            "profitability": ["roe", "roa", "net_profit_margin"],
            "solvency": ["debt_to_asset_ratio", "current_ratio"],
            "efficiency": ["asset_turnover"],
            "growth": ["revenue_growth"]
        }
        
        for category, indicators in priority_indicators.items():
            if category in content:
                category_data = content[category]
                if isinstance(category_data, dict):
                    filtered_data = {}
                    for indicator in indicators:
                        if indicator in category_data:
                            filtered_data[indicator] = category_data[indicator]
                    if filtered_data:
                        key_ratios[category] = filtered_data
        
        return key_ratios
    
    def _calculate_info_preservation(self, original: List[AgentMessage], 
                                  compressed: List[AgentMessage]) -> float:
        """计算信息保留比例"""
        try:
            # 基于数据类型计算保留比例
            original_types = set(msg.data_type for msg in original)
            compressed_types = set(msg.data_type for msg in compressed)
            
            type_preservation = len(compressed_types & original_types) / len(original_types)
            
            # 基于智能体计算保留比例
            original_agents = set(msg.sender for msg in original)
            compressed_agents = set(msg.sender for msg in compressed)
            
            agent_preservation = len(compressed_agents & original_agents) / len(original_agents)
            
            # 综合计算
            return (type_preservation + agent_preservation) / 2
            
        except Exception:
            return 0.5  # 默认值

# ===== 全局压缩器实例 =====
context_compressor = IntelligentContextCompressor()

def compress_agent_context(messages: List[AgentMessage], 
                          target_agent: str = None,
                          max_tokens: int = 2000) -> List[AgentMessage]:
    """
    便捷函数：压缩智能体上下文
    
    Args:
        messages: 消息列表
        target_agent: 目标智能体
        max_tokens: 最大token数
        
    Returns:
        压缩后的消息列表
    """
    compressed_messages, metrics = context_compressor.compress_context(
        messages, target_agent, max_tokens
    )
    
    logger.info(f"上下文压缩完成: {metrics.compression_ratio:.2f} 压缩比")
    
    return compressed_messages