"""
智能体数据流调试工具
用于调试、监控和分析智能体间的数据流转过程
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import traceback
import hashlib

from ..schemas import AgentMessage, DataType, AgentDataFormatter
from ..data_conversion import UniversalDataConverter
from ..context_compression import IntelligentContextCompressor

logger = logging.getLogger(__name__)

@dataclass
class DataFlowEvent:
    """数据流事件"""
    event_id: str                                     # 事件ID
    timestamp: str                                    # 时间戳
    event_type: str                                   # 事件类型
    source_agent: str                                 # 源智能体
    target_agent: Optional[str] = None               # 目标智能体
    data_type: DataType = DataType.TEXT_SUMMARY      # 数据类型
    data_size: int = 0                               # 数据大小
    processing_time: float = 0.0                     # 处理时间
    status: str = "success"                          # 状态
    error_message: Optional[str] = None              # 错误信息
    metadata: Dict[str, Any] = None                  # 元数据

@dataclass
class ConversionTrace:
    """数据转换追踪"""
    trace_id: str                                     # 追踪ID
    original_data: Dict[str, Any]                    # 原始数据
    converted_data: Dict[str, Any]                   # 转换后数据
    conversion_path: List[str]                       # 转换路径
    conversion_time: float                           # 转换耗时
    success: bool                                     # 是否成功
    errors: List[str]                                # 错误列表

@dataclass
class FlowAnalysis:
    """数据流分析结果"""
    total_messages: int                              # 总消息数
    data_types_distribution: Dict[str, int]          # 数据类型分布
    agent_interaction_graph: Dict[str, List[str]]    # 智能体交互图
    conversion_success_rate: float                   # 转换成功率
    average_processing_time: float                   # 平均处理时间
    bottleneck_analysis: Dict[str, Any]              # 瓶颈分析
    optimization_suggestions: List[str]              # 优化建议

class AgentDataFlowDebugger:
    """智能体数据流调试器"""
    
    def __init__(self):
        self.logger = logger
        self.universal_converter = UniversalDataConverter()
        self.context_compressor = IntelligentContextCompressor()
        
        # 事件追踪
        self.flow_events: List[DataFlowEvent] = []
        self.conversion_traces: List[ConversionTrace] = []
        
        # 调试配置
        self.debug_config = {
            "enable_detailed_logging": True,          # 启用详细日志
            "capture_raw_data": True,                 # 捕获原始数据
            "max_event_history": 1000,                # 最大事件历史数
            "enable_performance_monitoring": True,    # 启用性能监控
            "auto_diagnosis": True                    # 自动诊断
        }
        
        # 性能基准
        self.performance_benchmarks = {
            "max_conversion_time": 1.0,               # 最大转换时间（秒）
            "max_context_size": 8000,                 # 最大上下文大小
            "min_compression_ratio": 0.5,             # 最小压缩比
            "max_error_rate": 0.05                    # 最大错误率
        }
    
    def trace_data_conversion(self, source_data: Any, source_type: DataType,
                            target_agent: str, source_agent: str = None) -> ConversionTrace:
        """追踪数据转换过程"""
        trace_id = hashlib.md5(f"{source_agent}_{target_agent}_{datetime.now()}".encode()).hexdigest()[:8]
        
        start_time = datetime.now()
        
        try:
            self.logger.info(f"开始追踪数据转换: {source_type} → {target_agent}")
            
            # 创建原始消息
            original_message = AgentMessage(
                sender=source_agent or "unknown",
                data_type=source_type,
                content=source_data if isinstance(source_data, dict) else {"value": source_data}
            )
            
            # 执行转换
            target_type = self.universal_converter._infer_target_data_type(target_agent)
            converted_message = self.universal_converter.convert_message(
                original_message, target_type, target_agent
            )
            
            conversion_time = (datetime.now() - start_time).total_seconds()
            
            # 创建转换追踪
            trace = ConversionTrace(
                trace_id=trace_id,
                original_data=asdict(original_message),
                converted_data=asdict(converted_message),
                conversion_path=[source_type.value, target_type.value],
                conversion_time=conversion_time,
                success=converted_message.data_type != DataType.ERROR_INFO,
                errors=[] if converted_message.data_type != DataType.ERROR_INFO else [converted_message.content.get("error", "Unknown error")]
            )
            
            self.conversion_traces.append(trace)
            
            # 记录事件
            self._record_event(
                event_type="data_conversion",
                source_agent=source_agent or "unknown",
                target_agent=target_agent,
                data_type=target_type,
                processing_time=conversion_time,
                status="success" if trace.success else "failed",
                metadata={
                    "trace_id": trace_id,
                    "conversion_path": trace.conversion_path,
                    "data_size": len(json.dumps(source_data, ensure_ascii=False))
                }
            )
            
            self.logger.info(f"数据转换追踪完成: {trace_id}, 成功: {trace.success}, 耗时: {conversion_time:.3f}s")
            
            return trace
            
        except Exception as e:
            conversion_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"数据转换失败: {str(e)}"
            
            self.logger.error(error_msg)
            
            # 记录失败事件
            self._record_event(
                event_type="data_conversion",
                source_agent=source_agent or "unknown",
                target_agent=target_agent,
                data_type=source_type,
                processing_time=conversion_time,
                status="failed",
                error_message=error_msg,
                metadata={"trace_id": trace_id, "exception": traceback.format_exc()}
            )
            
            # 创建失败追踪
            trace = ConversionTrace(
                trace_id=trace_id,
                original_data={"raw_data": str(source_data)},
                converted_data={},
                conversion_path=[source_type.value],
                conversion_time=conversion_time,
                success=False,
                errors=[error_msg]
            )
            
            self.conversion_traces.append(trace)
            return trace
    
    def trace_context_flow(self, messages: List[AgentMessage], target_agent: str) -> Dict[str, Any]:
        """追踪上下文流转过程"""
        try:
            self.logger.info(f"开始追踪上下文流转，目标智能体: {target_agent}")
            
            flow_analysis = {
                "original_message_count": len(messages),
                "original_context_size": sum(len(msg.to_string()) for msg in messages),
                "data_types_distribution": {},
                "agent_interactions": [],
                "compression_analysis": {},
                "performance_metrics": {}
            }
            
            # 分析数据类型分布
            for msg in messages:
                data_type = msg.data_type.value
                flow_analysis["data_types_distribution"][data_type] = \
                    flow_analysis["data_types_distribution"].get(data_type, 0) + 1
            
            # 分析智能体交互
            for i, msg in enumerate(messages):
                flow_analysis["agent_interactions"].append({
                    "index": i,
                    "sender": msg.sender,
                    "receiver": msg.receiver,
                    "data_type": msg.data_type.value,
                    "timestamp": msg.timestamp
                })
            
            # 模拟上下文压缩（如果需要）
            if flow_analysis["original_context_size"] > self.performance_benchmarks["max_context_size"]:
                compressed_messages, metrics = self.context_compressor.compress_context(
                    messages, target_agent
                )
                
                flow_analysis["compression_analysis"] = {
                    "compressed": True,
                    "original_size": flow_analysis["original_context_size"],
                    "compressed_size": metrics.compressed_size,
                    "compression_ratio": metrics.compression_ratio,
                    "preserved_info_ratio": metrics.preserved_info_ratio,
                    "strategy_used": metrics.strategy_used
                }
            else:
                flow_analysis["compression_analysis"] = {
                    "compressed": False,
                    "reason": "Context size within limits"
                }
            
            # 记录事件
            self._record_event(
                event_type="context_flow",
                source_agent="OrchestraAgent",
                target_agent=target_agent,
                data_type=DataType.TEXT_SUMMARY,
                processing_time=0,
                status="success",
                metadata=flow_analysis
            )
            
            return flow_analysis
            
        except Exception as e:
            error_msg = f"上下文流转追踪失败: {str(e)}"
            self.logger.error(error_msg)
            
            self._record_event(
                event_type="context_flow",
                source_agent="OrchestraAgent",
                target_agent=target_agent,
                data_type=DataType.ERROR_INFO,
                processing_time=0,
                status="failed",
                error_message=error_msg
            )
            
            return {"error": error_msg}
    
    def diagnose_data_flow_issues(self) -> Dict[str, Any]:
        """诊断数据流问题"""
        try:
            self.logger.info("开始诊断数据流问题")
            
            diagnosis = {
                "overall_health": "healthy",
                "issues_found": [],
                "warnings": [],
                "performance_issues": [],
                "recommendations": []
            }
            
            # 检查转换成功率
            if self.conversion_traces:
                successful_conversions = sum(1 for trace in self.conversion_traces if trace.success)
                total_conversions = len(self.conversion_traces)
                success_rate = successful_conversions / total_conversions
                
                if success_rate < (1 - self.performance_benchmarks["max_error_rate"]):
                    diagnosis["issues_found"].append(
                        f"数据转换成功率过低: {success_rate:.2%} (期望: >{(1-self.performance_benchmarks['max_error_rate']):.2%})"
                    )
                    diagnosis["overall_health"] = "unhealthy"
                
                # 分析转换错误
                failed_traces = [trace for trace in self.conversion_traces if not trace.success]
                if failed_traces:
                    error_patterns = {}
                    for trace in failed_traces:
                        for error in trace.errors:
                            error_type = error.split(":")[0] if ":" in error else "unknown"
                            error_patterns[error_type] = error_patterns.get(error_type, 0) + 1
                    
                    diagnosis["issues_found"].append(f"常见转换错误: {error_patterns}")
            
            # 检查性能问题
            slow_conversions = [trace for trace in self.conversion_traces 
                              if trace.conversion_time > self.performance_benchmarks["max_conversion_time"]]
            if slow_conversions:
                diagnosis["performance_issues"].append(
                    f"发现 {len(slow_conversions)} 个慢转换 (> {self.performance_benchmarks['max_conversion_time']}s)"
                )
                diagnosis["overall_health"] = "degraded"
            
            # 检查上下文大小问题
            large_context_events = [event for event in self.flow_events 
                                  if event.data_size > self.performance_benchmarks["max_context_size"]]
            if large_context_events:
                diagnosis["performance_issues"].append(
                    f"发现 {len(large_context_events)} 个大上下文 (> {self.performance_benchmarks['max_context_size']} 字符)"
                )
            
            # 生成优化建议
            diagnosis["recommendations"] = self._generate_optimization_recommendations(diagnosis)
            
            # 记录诊断事件
            self._record_event(
                event_type="diagnosis",
                source_agent="DataFlowDebugger",
                data_type=DataType.TEXT_SUMMARY,
                processing_time=0,
                status="success",
                metadata=diagnosis
            )
            
            self.logger.info(f"数据流诊断完成，健康状态: {diagnosis['overall_health']}")
            
            return diagnosis
            
        except Exception as e:
            error_msg = f"数据流诊断失败: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg, "overall_health": "error"}
    
    def visualize_data_flow(self) -> Dict[str, Any]:
        """可视化数据流"""
        try:
            visualization = {
                "nodes": [],
                "edges": [],
                "metadata": {
                    "total_events": len(self.flow_events),
                    "time_range": {},
                    "data_flow_patterns": {}
                }
            }
            
            # 构建节点（智能体）
            agents = set()
            for event in self.flow_events:
                agents.add(event.source_agent)
                if event.target_agent:
                    agents.add(event.target_agent)
            
            for agent in agents:
                visualization["nodes"].append({
                    "id": agent,
                    "label": agent,
                    "type": "agent"
                })
            
            # 构建边（数据流）
            for event in self.flow_events:
                if event.target_agent:
                    visualization["edges"].append({
                        "from": event.source_agent,
                        "to": event.target_agent,
                        "data_type": event.data_type.value,
                        "status": event.status,
                        "timestamp": event.timestamp,
                        "size": event.data_size
                    })
            
            # 计算时间范围
            if self.flow_events:
                timestamps = [datetime.fromisoformat(event.timestamp) for event in self.flow_events]
                visualization["metadata"]["time_range"] = {
                    "start": min(timestamps).isoformat(),
                    "end": max(timestamps).isoformat()
                }
            
            return visualization
            
        except Exception as e:
            self.logger.error(f"数据流可视化失败: {e}")
            return {"error": str(e)}
    
    def export_debug_report(self, output_file: str = None) -> Dict[str, Any]:
        """导出调试报告"""
        try:
            report = {
                "generated_at": datetime.now().isoformat(),
                "summary": {
                    "total_events": len(self.flow_events),
                    "total_conversions": len(self.conversion_traces),
                    "debug_config": self.debug_config
                },
                "flow_events": [asdict(event) for event in self.flow_events[-100:]],  # 最近100个事件
                "conversion_traces": [asdict(trace) for trace in self.conversion_traces[-50:]],  # 最近50个转换
                "diagnosis": self.diagnose_data_flow_issues(),
                "visualization": self.visualize_data_flow(),
                "performance_analysis": self._analyze_performance()
            }
            
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)
                self.logger.info(f"调试报告已导出到: {output_file}")
            
            return report
            
        except Exception as e:
            error_msg = f"导出调试报告失败: {e}"
            self.logger.error(error_msg)
            return {"error": error_msg}
    
    def _record_event(self, event_type: str, source_agent: str, target_agent: str = None,
                     data_type: DataType = DataType.TEXT_SUMMARY, processing_time: float = 0,
                     status: str = "success", error_message: str = None,
                     metadata: Dict[str, Any] = None) -> None:
        """记录数据流事件"""
        if not self.debug_config["enable_detailed_logging"]:
            return
        
        event = DataFlowEvent(
            event_id=hashlib.md5(f"{event_type}_{datetime.now()}".encode()).hexdigest()[:8],
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            source_agent=source_agent,
            target_agent=target_agent,
            data_type=data_type,
            data_size=metadata.get("data_size", 0) if metadata else 0,
            processing_time=processing_time,
            status=status,
            error_message=error_message,
            metadata=metadata or {}
        )
        
        self.flow_events.append(event)
        
        # 限制事件历史大小
        if len(self.flow_events) > self.debug_config["max_event_history"]:
            self.flow_events = self.flow_events[-self.debug_config["max_event_history"]:]
    
    def _generate_optimization_recommendations(self, diagnosis: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if diagnosis["issues_found"]:
            recommendations.append("修复数据转换错误，提高转换成功率")
            recommendations.append("添加更完善的错误处理和降级策略")
        
        if diagnosis["performance_issues"]:
            recommendations.append("优化慢转换，考虑缓存和预处理")
            recommendations.append("实施智能上下文压缩，减少数据传输量")
        
        if not self.conversion_traces:
            recommendations.append("启用数据转换追踪以收集更多诊断信息")
        
        # 基于模式分析的建议
        data_types = {}
        for event in self.flow_events:
            data_type = event.data_type.value
            data_types[data_type] = data_types.get(data_type, 0) + 1
        
        if data_types:
            most_common_type = max(data_types, key=data_types.get)
            recommendations.append(f"针对最常见的 '{most_common_type}' 数据类型优化转换逻辑")
        
        return recommendations
    
    def _analyze_performance(self) -> Dict[str, Any]:
        """分析性能指标"""
        if not self.flow_events:
            return {"message": "暂无数据可供分析"}
        
        analysis = {
            "total_events": len(self.flow_events),
            "average_processing_time": 0,
            "slowest_event": None,
            "fastest_event": None,
            "error_rate": 0,
            "data_size_stats": {}
        }
        
        # 计算处理时间统计
        processing_times = [event.processing_time for event in self.flow_events]
        if processing_times:
            analysis["average_processing_time"] = sum(processing_times) / len(processing_times)
            analysis["slowest_event"] = max(self.flow_events, key=lambda x: x.processing_time).event_id
            analysis["fastest_event"] = min(self.flow_events, key=lambda x: x.processing_time).event_id
        
        # 计算错误率
        error_events = [event for event in self.flow_events if event.status == "failed"]
        analysis["error_rate"] = len(error_events) / len(self.flow_events)
        
        # 数据大小统计
        data_sizes = [event.data_size for event in self.flow_events if event.data_size > 0]
        if data_sizes:
            analysis["data_size_stats"] = {
                "average": sum(data_sizes) / len(data_sizes),
                "max": max(data_sizes),
                "min": min(data_sizes),
                "total": sum(data_sizes)
            }
        
        return analysis

# ===== 全局调试器实例 =====
data_flow_debugger = AgentDataFlowDebugger()

def debug_agent_data_flow(source_data: Any, source_type: DataType,
                         target_agent: str, source_agent: str = None) -> Dict[str, Any]:
    """
    便捷函数：调试智能体数据流
    
    Args:
        source_data: 源数据
        source_type: 源数据类型
        target_agent: 目标智能体
        source_agent: 源智能体
    
    Returns:
        调试结果
    """
    trace = data_flow_debugger.trace_data_conversion(
        source_data, source_type, target_agent, source_agent
    )
    
    diagnosis = data_flow_debugger.diagnose_data_flow_issues()
    
    return {
        "conversion_trace": asdict(trace),
        "diagnosis": diagnosis,
        "recommendations": diagnosis.get("recommendations", [])
    }

def generate_debug_report(output_file: str = None) -> Dict[str, Any]:
    """生成完整调试报告"""
    return data_flow_debugger.export_debug_report(output_file)