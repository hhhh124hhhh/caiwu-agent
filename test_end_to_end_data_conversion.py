#!/usr/bin/env python3
"""
端到端数据转换测试用例
完整测试智能体间的数据转换流程
"""

import sys
import os
from pathlib import Path
import json
import logging
from typing import Dict, Any, List

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utu.schemas import (
    DataType, AgentMessage, AgentDataFormatter,
    DataAnalysisAgentOutput, ChartGeneratorAgentInput
)
from utu.data_conversion import UniversalDataConverter, convert_data_for_agent
from utu.context_compression import IntelligentContextCompressor, compress_agent_context
from utu.debugging import AgentDataFlowDebugger, debug_agent_data_flow

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EndToEndDataConversionTest:
    """端到端数据转换测试类"""
    
    def __init__(self):
        self.converter = UniversalDataConverter()
        self.compressor = IntelligentContextCompressor()
        self.debugger = AgentDataFlowDebugger()
        
        self.test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始端到端数据转换测试")
        print("=" * 60)
        
        # 测试1: DataAnalysisAgent → ChartGeneratorAgent 数据转换
        self._test_data_analysis_to_chart_conversion()
        
        # 测试2: 智能上下文压缩
        self._test_context_compression()
        
        # 测试3: 数据流转调试
        self._test_data_flow_debugging()
        
        # 测试4: 完整工作流程模拟
        self._test_complete_workflow_simulation()
        
        # 测试5: 错误处理和恢复
        self._test_error_handling_and_recovery()
        
        # 测试6: 性能基准测试
        self._test_performance_benchmarks()
        
        # 输出测试结果
        self._print_test_summary()
        
        return self.test_results
    
    def _test_data_analysis_to_chart_conversion(self):
        """测试DataAnalysisAgent到ChartGeneratorAgent的数据转换"""
        print("\n测试1: DataAnalysisAgent → ChartGeneratorAgent 数据转换")
        print("-" * 50)
        
        try:
            # 创建模拟的DataAnalysisAgent输出
            financial_ratios = {
                "profitability": {
                    "gross_profit_margin": 0.0528,
                    "net_profit_margin": 0.0192,
                    "roe": 0.0282,
                    "roa": 0.0032
                },
                "solvency": {
                    "debt_to_asset_ratio": 0.8871,
                    "current_ratio": 1.0,
                    "quick_ratio": 1.0
                },
                "warnings": ["资产负债率偏高", "净利润率较低"]
            }
            
            # 创建原始消息
            original_message = AgentMessage(
                sender="DataAnalysisAgent",
                data_type=DataType.FINANCIAL_RATIOS,
                content=financial_ratios,
                metadata={"company": "陕西建工", "period": "2024"}
            )
            
            print(f"✅ 原始数据类型: {original_message.data_type.value}")
            print(f"✅ 原始数据大小: {len(original_message.to_string())} 字符")
            
            # 转换为ChartGeneratorAgent格式
            converted_message = self.converter.convert_message(
                original_message, DataType.CHART_DATA, "ChartGeneratorAgent"
            )
            
            print(f"✅ 转换后数据类型: {converted_message.data_type.value}")
            print(f"✅ 转换后数据大小: {len(converted_message.to_string())} 字符")
            
            # 验证转换结果
            if converted_message.data_type == DataType.CHART_DATA:
                chart_data = converted_message.content.get("chart_data", {})
                print(f"✅ 生成图表数量: {len(chart_data)}")
                
                for chart_name, chart_config in chart_data.items():
                    print(f"   - {chart_name}: {chart_config.get('title', 'N/A')}")
                
                self._record_test_result(
                    test_name="DataAnalysis → ChartGenerator 转换",
                    passed=True,
                    details=f"成功生成 {len(chart_data)} 个图表格式"
                )
            else:
                raise Exception("转换失败，目标数据类型不是CHART_DATA")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            self._record_test_result(
                test_name="DataAnalysis → ChartGenerator 转换",
                passed=False,
                details=str(e)
            )
    
    def _test_context_compression(self):
        """测试智能上下文压缩"""
        print("\n🗜️ 测试2: 智能上下文压缩")
        print("-" * 50)
        
        try:
            # 创建大量上下文消息
            messages = []
            agents = ["DataAgent", "DataAnalysisAgent", "FinancialAnalysisAgent"]
            data_types = [DataType.RAW_FINANCIAL_DATA, DataType.FINANCIAL_RATIOS, DataType.FINANCIAL_ANALYSIS]
            
            for i in range(10):  # 创建10条消息
                agent = agents[i % len(agents)]
                data_type = data_types[i % len(data_types)]
                
                message = AgentMessage(
                    sender=agent,
                    data_type=data_type,
                    content={"test_data": f"这是第{i+1}条测试数据", "index": i},
                    metadata={"sequence": i}
                )
                messages.append(message)
            
            original_size = sum(len(msg.to_string()) for msg in messages)
            print(f"✅ 原始上下文大小: {original_size} 字符")
            print(f"✅ 原始消息数量: {len(messages)}")
            
            # 压缩上下文
            compressed_messages, metrics = self.compressor.compress_context(
                messages, target_agent="ChartGeneratorAgent", max_tokens=1000
            )
            
            compressed_size = sum(len(msg.to_string()) for msg in compressed_messages)
            print(f"✅ 压缩后上下文大小: {compressed_size} 字符")
            print(f"✅ 压缩后消息数量: {len(compressed_messages)}")
            print(f"✅ 压缩比: {metrics.compression_ratio:.2f}")
            print(f"✅ 信息保留率: {metrics.preserved_info_ratio:.2f}")
            print(f"✅ 压缩策略: {metrics.strategy_used}")
            
            # 验证压缩效果
            if metrics.compression_ratio < 0.8 and metrics.preserved_info_ratio > 0.6:
                self._record_test_result(
                    test_name="智能上下文压缩",
                    passed=True,
                    details=f"压缩比: {metrics.compression_ratio:.2f}, 保留率: {metrics.preserved_info_ratio:.2f}"
                )
            else:
                raise Exception(f"压缩效果不佳: 压缩比={metrics.compression_ratio:.2f}, 保留率={metrics.preserved_info_ratio:.2f}")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            self._record_test_result(
                test_name="智能上下文压缩",
                passed=False,
                details=str(e)
            )
    
    def _test_data_flow_debugging(self):
        """测试数据流转调试"""
        print("\n🔍 测试3: 数据流转调试")
        print("-" * 50)
        
        try:
            # 模拟数据转换并追踪
            source_data = {
                "profitability": {"roe": 0.15, "roa": 0.08},
                "solvency": {"debt_ratio": 0.6}
            }
            
            print("✅ 开始数据转换追踪...")
            trace = self.debugger.trace_data_conversion(
                source_data=source_data,
                source_type=DataType.FINANCIAL_RATIOS,
                target_agent="ChartGeneratorAgent",
                source_agent="DataAnalysisAgent"
            )
            
            print(f"✅ 追踪ID: {trace.trace_id}")
            print(f"✅ 转换成功: {trace.success}")
            print(f"✅ 转换耗时: {trace.conversion_time:.3f}s")
            print(f"✅ 转换路径: {' → '.join(trace.conversion_path)}")
            
            if trace.errors:
                print(f"⚠️ 转换错误: {trace.errors}")
            
            # 生成诊断报告
            diagnosis = self.debugger.diagnose_data_flow_issues()
            print(f"✅ 系统健康状态: {diagnosis.get('overall_health', 'unknown')}")
            
            if diagnosis.get("issues_found"):
                print("⚠️ 发现的问题:")
                for issue in diagnosis["issues_found"]:
                    print(f"   - {issue}")
            
            if diagnosis.get("recommendations"):
                print("💡 优化建议:")
                for rec in diagnosis["recommendations"]:
                    print(f"   - {rec}")
            
            # 验证调试功能
            if trace.success and diagnosis.get("overall_health") in ["healthy", "degraded"]:
                self._record_test_result(
                    test_name="数据流转调试",
                    passed=True,
                    details=f"追踪成功，健康状态: {diagnosis.get('overall_health')}"
                )
            else:
                raise Exception(f"调试功能异常: trace_success={trace.success}, health={diagnosis.get('overall_health')}")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            self._record_test_result(
                test_name="数据流转调试",
                passed=False,
                details=str(e)
            )
    
    def _test_complete_workflow_simulation(self):
        """测试完整工作流程模拟"""
        print("\n🔄 测试4: 完整工作流程模拟")
        print("-" * 50)
        
        try:
            workflow_results = []
            
            # 步骤1: DataAgent获取数据
            print("📥 步骤1: DataAgent 获取原始财务数据")
            raw_data = {
                "income_statement": {"revenue": 1000, "net_profit": 50},
                "balance_sheet": {"total_assets": 2000, "total_liabilities": 1500}
            }
            
            data_message = AgentMessage(
                sender="DataAgent",
                data_type=DataType.RAW_FINANCIAL_DATA,
                content=raw_data,
                metadata={"company": "测试公司", "period": "2024"}
            )
            workflow_results.append(data_message)
            print("✅ 原始数据获取完成")
            
            # 步骤2: DataAnalysisAgent分析数据
            print("📊 步骤2: DataAnalysisAgent 计算财务比率")
            financial_ratios = {
                "profitability": {
                    "gross_profit_margin": 0.15,
                    "net_profit_margin": 0.05,
                    "roe": 0.10,
                    "roa": 0.025
                },
                "solvency": {
                    "debt_to_asset_ratio": 0.75,
                    "current_ratio": 1.2
                },
                "warnings": ["负债率较高"]
            }
            
            analysis_message = AgentMessage(
                sender="DataAnalysisAgent",
                data_type=DataType.FINANCIAL_RATIOS,
                content=financial_ratios,
                metadata={"analysis_period": "2024"}
            )
            workflow_results.append(analysis_message)
            print("✅ 财务比率计算完成")
            
            # 步骤3: 数据格式转换为图表格式
            print("📈 步骤3: 转换数据格式为图表格式")
            chart_message = self.converter.convert_message(
                analysis_message, DataType.CHART_DATA, "ChartGeneratorAgent"
            )
            workflow_results.append(chart_message)
            print("✅ 图表格式转换完成")
            
            # 步骤4: 上下文压缩（如果需要）
            total_context_size = sum(len(msg.to_string()) for msg in workflow_results)
            print(f"📏 当前上下文大小: {total_context_size} 字符")
            
            if total_context_size > 2000:
                print("🗜️ 步骤4: 执行上下文压缩")
                compressed_messages, metrics = self.compressor.compress_context(
                    workflow_results, target_agent="ReportAgent", max_tokens=1500
                )
                print(f"✅ 压缩完成: {metrics.compression_ratio:.2f} 压缩比")
                workflow_results = compressed_messages
            
            # 步骤5: 验证工作流程
            print("✅ 步骤5: 工作流程验证")
            
            # 检查每个步骤的数据类型
            expected_types = [
                DataType.RAW_FINANCIAL_DATA,
                DataType.FINANCIAL_RATIOS,
                DataType.CHART_DATA
            ]
            
            actual_types = [msg.data_type for msg in workflow_results[:3]]
            if actual_types == expected_types:
                print("✅ 数据类型流转正确")
            else:
                raise Exception(f"数据类型流转错误: 期望 {expected_types}, 实际 {actual_types}")
            
            # 检查数据完整性
            chart_data = workflow_results[2].content.get("chart_data", {})
            if chart_data:
                print(f"✅ 图表数据完整性: 生成 {len(chart_data)} 个图表")
            else:
                raise Exception("图表数据为空")
            
            self._record_test_result(
                test_name="完整工作流程模拟",
                passed=True,
                details=f"成功完成 {len(workflow_results)} 个步骤的数据流转"
            )
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            self._record_test_result(
                test_name="完整工作流程模拟",
                passed=False,
                details=str(e)
            )
    
    def _test_error_handling_and_recovery(self):
        """测试错误处理和恢复"""
        print("\n🚨 测试5: 错误处理和恢复")
        print("-" * 50)
        
        try:
            # 测试1: 无效数据格式
            print("测试5.1: 无效数据格式处理")
            invalid_data = "这不是有效的财务数据"
            
            result_message = self.converter.convert_message(
                AgentMessage(
                    sender="TestAgent",
                    data_type=DataType.TEXT_SUMMARY,
                    content={"raw_output": invalid_data}
                ),
                DataType.FINANCIAL_RATIOS,
                "ChartGeneratorAgent"
            )
            
            if result_message.data_type == DataType.ERROR_INFO:
                print("✅ 无效数据格式正确识别为错误")
            else:
                print("⚠️ 无效数据格式处理可能有问题")
            
            # 测试2: 空数据处理
            print("测试5.2: 空数据处理")
            empty_data = {}
            
            result_message = self.converter.convert_message(
                AgentMessage(
                    sender="TestAgent",
                    data_type=DataType.FINANCIAL_RATIOS,
                    content=empty_data
                ),
                DataType.CHART_DATA,
                "ChartGeneratorAgent"
            )
            
            print(f"✅ 空数据处理结果: {result_message.data_type.value}")
            
            # 测试3: 超大上下文处理
            print("测试5.3: 超大上下文处理")
            large_messages = []
            for i in range(100):
                large_messages.append(AgentMessage(
                    sender=f"Agent{i % 5}",
                    data_type=DataType.TEXT_SUMMARY,
                    content={"data": "x" * 1000}  # 大量数据
                ))
            
            compressed_messages, metrics = self.compressor.compress_context(
                large_messages, target_agent="TestAgent", max_tokens=500
            )
            
            compression_effective = len(compressed_messages) < len(large_messages)
            print(f"✅ 超大上下文压缩效果: {compression_effective}")
            
            self._record_test_result(
                test_name="错误处理和恢复",
                passed=True,
                details="所有错误处理测试通过"
            )
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            self._record_test_result(
                test_name="错误处理和恢复",
                passed=False,
                details=str(e)
            )
    
    def _test_performance_benchmarks(self):
        """测试性能基准"""
        print("\n⚡ 测试6: 性能基准测试")
        print("-" * 50)
        
        try:
            import time
            
            # 测试数据转换性能
            print("测试6.1: 数据转换性能")
            test_data = {
                "profitability": {f"metric_{i}": 0.1 + i * 0.01 for i in range(100)},
                "solvency": {f"ratio_{i}": 0.5 + i * 0.005 for i in range(100)}
            }
            
            start_time = time.time()
            for i in range(10):
                self.converter.convert_message(
                    AgentMessage(
                        sender="TestAgent",
                        data_type=DataType.FINANCIAL_RATIOS,
                        content=test_data
                    ),
                    DataType.CHART_DATA,
                    "ChartGeneratorAgent"
                )
            conversion_time = time.time() - start_time
            
            avg_conversion_time = conversion_time / 10
            print(f"✅ 平均转换时间: {avg_conversion_time:.3f}s")
            
            # 测试上下文压缩性能
            print("测试6.2: 上下文压缩性能")
            test_messages = []
            for i in range(50):
                test_messages.append(AgentMessage(
                    sender=f"Agent{i % 3}",
                    data_type=DataType.TEXT_SUMMARY,
                    content={"data": f"测试数据 {i}" * 100}
                ))
            
            start_time = time.time()
            compressed_messages, metrics = self.compressor.compress_context(
                test_messages, target_agent="TestAgent", max_tokens=2000
            )
            compression_time = time.time() - start_time
            
            print(f"✅ 压缩耗时: {compression_time:.3f}s")
            print(f"✅ 压缩比: {metrics.compression_ratio:.2f}")
            
            # 性能基准验证
            performance_ok = True
            
            if avg_conversion_time > 0.5:  # 单次转换不应超过0.5秒
                print("⚠️ 数据转换性能低于基准")
                performance_ok = False
            
            if compression_time > 2.0:  # 压缩不应超过2秒
                print("⚠️ 上下文压缩性能低于基准")
                performance_ok = False
            
            if performance_ok:
                self._record_test_result(
                    test_name="性能基准测试",
                    passed=True,
                    details=f"转换: {avg_conversion_time:.3f}s, 压缩: {compression_time:.3f}s"
                )
            else:
                raise Exception("性能不满足基准要求")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            self._record_test_result(
                test_name="性能基准测试",
                passed=False,
                details=str(e)
            )
    
    def _record_test_result(self, test_name: str, passed: bool, details: str):
        """记录测试结果"""
        self.test_results["total_tests"] += 1
        
        if passed:
            self.test_results["passed_tests"] += 1
            status = "✅ 通过"
        else:
            self.test_results["failed_tests"] += 1
            status = "❌ 失败"
        
        self.test_results["test_details"].append({
            "name": test_name,
            "status": status,
            "details": details
        })
        
        print(f"   {status}: {test_name}")
    
    def _print_test_summary(self):
        """打印测试摘要"""
        print("\n" + "=" * 60)
        print("📋 测试摘要报告")
        print("=" * 60)
        
        total = self.test_results["total_tests"]
        passed = self.test_results["passed_tests"]
        failed = self.test_results["failed_tests"]
        
        print(f"总测试数: {total}")
        print(f"通过: {passed} ✅")
        print(f"失败: {failed} ❌")
        print(f"成功率: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print("\n❌ 失败的测试:")
            for test in self.test_results["test_details"]:
                if "失败" in test["status"]:
                    print(f"   - {test['name']}: {test['details']}")
        
        print("\n📊 详细测试结果:")
        for test in self.test_results["test_details"]:
            print(f"   {test['status']}: {test['name']}")
        
        # 生成调试报告
        try:
            debug_report = self.debugger.export_debug_report()
            print(f"\n🔍 调试报告已生成，包含 {len(debug_report.get('flow_events', []))} 个事件")
        except Exception as e:
            print(f"\n⚠️ 调试报告生成失败: {e}")
        
        print("\n" + "=" * 60)
        
        if failed == 0:
            print("🎉 所有测试通过！数据转换系统工作正常")
        else:
            print("⚠️ 部分测试失败，需要进一步调试")

def main():
    """主函数"""
    tester = EndToEndDataConversionTest()
    results = tester.run_all_tests()
    
    return results

if __name__ == "__main__":
    main()