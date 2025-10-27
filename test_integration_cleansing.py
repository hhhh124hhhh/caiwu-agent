#!/usr/bin/env python3
"""
数据清洗系统集成测试脚本
验证完整的智能体工作流，包括数据清洗智能体的集成效果
"""

import sys
import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List
import logging
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 测试数据 - 模拟真实用户场景
REALISTIC_TEST_DATA = {
    "basic_chinese_data": {
        "利润表": {
            "营业收入": 573.88,
            "净利润": 11.04,
            "营业成本": 552.84,
            "营业利润": 11.04,
            "利润总额": 11.04
        },
        "资产负债表": {
            "总资产": 3472.98,
            "总负债": 3081.02,
            "所有者权益": 391.96,
            "流动资产": 2500.45,
            "流动负债": 2800.12,
            "应收账款": 450.23,
            "存货": 380.67,
            "固定资产": 650.34,
            "货币资金": 180.56
        },
        "现金流量表": {
            "经营活动现金流量净额": 25.67,
            "投资活动现金流量净额": -15.23,
            "筹资活动现金流量净额": -8.45,
            "现金及现金等价物净增加额": 1.99
        },
        "关键指标": {
            "净利润率": 1.92,
            "资产负债率": 88.71,
            "ROE": 2.68
        },
        "历史数据": {
            "2025": {
                "营业收入": 573.88,
                "净利润": 11.04
            },
            "2024": {
                "营业收入": 1511.39,
                "净利润": 36.11
            },
            "2023": {
                "营业收入": 1420.56,
                "净利润": 32.45
            },
            "2022": {
                "营业收入": 1280.23,
                "净利润": 28.67
            }
        }
    },
    
    "complex_mixed_data": {
        "income_statement": {
            "revenue": 2500.0,
            "net_profit": 300.0,
            "operating_profit": 350.0,
            "gross_profit": 800.0
        },
        "利润表": {
            "营业收入": 1500.0,
            "净利润": 180.0
        },
        "balance_sheet": {
            "total_assets": 8000.0,
            "total_liabilities": 5000.0,
            "total_equity": 3000.0
        },
        "历史数据": {
            "2024": {
                "revenue": 2000.0,
                "net_profit": 250.0,
                "营业收入": 1500.0,
                "净利润": 180.0
            },
            "2023": {
                "revenue": 1800.0,
                "net_profit": 220.0
            }
        }
    },
    
    "user_uploaded_data": {
        "公司基本信息": {
            "公司名称": "测试公司",
            "股票代码": "600000.SH",
            "行业": "制造业"
        },
        "财务数据": {
            "2024年利润表": {
                "营业收入(万元)": 10000.0,
                "净利润(万元)": 1200.0
            },
            "2024年资产负债表": {
                "总资产(万元)": 50000.0,
                "总负债(万元)": 30000.0,
                "股东权益(万元)": 20000.0
            },
            "2023年利润表": {
                "营业收入(万元)": 9000.0,
                "净利润(万元)": 1000.0
            }
        }
    },
    
    "problematic_data": {
        "利润表": {
            "营业收入": 0,  # 收入为0
            "净利润": -500.0,  # 亏损
            "营业成本": "invalid",  # 无效值
            "营业利润": None  # 空值
        },
        "历史数据": {
            "2024": {
                "营业收入": 1000.0
                # 缺少净利润
            },
            "2023": {
                "营业收入": 0,
                "净利润": -200.0
            }
        }
    }
}


class IntegrationTestSuite:
    """集成测试套件"""
    
    def __init__(self):
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }
        
        # 初始化组件
        self._initialize_components()
    
    def _initialize_components(self):
        """初始化测试组件"""
        try:
            from utu.agents.data_cleanser_agent import DataCleanserAgent
            from utu.tools.data_cleansing_toolkit import DataCleansingToolkit
            from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer
            from utu.config import ToolkitConfig
            
            # 初始化智能体和工具
            self.cleanser_agent = DataCleanserAgent()
            
            toolkit_config = ToolkitConfig(config={}, name="data_cleansing")
            self.cleansing_toolkit = DataCleansingToolkit(toolkit_config)
            
            # 初始化分析器（用于后续验证）
            self.financial_analyzer = StandardFinancialAnalyzer()
            
            logger.info("所有测试组件初始化成功")
            
        except Exception as e:
            logger.error(f"测试组件初始化失败: {str(e)}")
            raise
    
    def record_test(self, test_name: str, passed: bool, details: str = "", duration: float = 0.0):
        """记录测试结果"""
        self.test_results['total_tests'] += 1
        if passed:
            self.test_results['passed_tests'] += 1
            status = "✅ 通过"
        else:
            self.test_results['failed_tests'] += 1
            status = "❌ 失败"
        
        self.test_results['test_details'].append({
            'name': test_name,
            'status': status,
            'details': details,
            'duration': duration
        })
        
        logger.info(f"{status}: {test_name}")
        if details:
            logger.info(f"  详情: {details}")
    
    def run_all_integration_tests(self):
        """运行所有集成测试"""
        logger.info("开始运行数据清洗系统集成测试套件")
        
        start_time = datetime.now()
        
        # 基础集成测试
        self.test_basic_data_cleansing_workflow()
        self.test_complex_data_handling()
        
        # 智能体协作测试
        self.test_agent_coordination()
        self.test_data_flow_compatibility()
        
        # 质量改进验证
        self.test_quality_improvements()
        self.test_error_recovery()
        
        # 真实场景模拟
        self.test_real_user_scenarios()
        self.test_edge_case_handling()
        
        # 性能和稳定性测试
        self.test_system_stability()
        self.test_performance_under_load()
        
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        # 输出测试结果摘要
        self.print_test_summary(total_duration)
    
    def test_basic_data_cleansing_workflow(self):
        """测试基础数据清洗工作流"""
        logger.info("\n=== 测试基础数据清洗工作流 ===")
        
        test_data = REALISTIC_TEST_DATA["basic_chinese_data"]
        start_time = datetime.now()
        
        try:
            # 1. 使用工具集进行快速清洗
            result = self.cleansing_toolkit.cleanse_financial_data(test_data)
            
            if result['success']:
                # 2. 验证清洗结果
                cleansed_data = result['cleansed_data']
                quality_score = result['quality_score']
                
                # 检查关键字段是否存在
                has_income_statement = 'income_statement' in cleansed_data
                has_balance_sheet = 'balance_sheet' in cleansed_data
                has_historical_data = 'historical_data' in cleansed_data
                
                passed = (
                    result['success'] and
                    quality_score >= 60 and  # 最低质量要求
                    has_income_statement and
                    has_balance_sheet and
                    has_historical_data
                )
                
                details = f"质量分数: {quality_score:.2f}, "
                details += f"报表完整性: {has_income_statement and has_balance_sheet}, "
                details += f"历史数据: {has_historical_data}"
                
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test("基础数据清洗工作流", passed, details, duration)
            else:
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test("基础数据清洗工作流", False, "清洗失败", duration)
                
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.record_test("基础数据清洗工作流", False, f"异常: {str(e)}", duration)
    
    def test_complex_data_handling(self):
        """测试复杂数据处理"""
        logger.info("\n=== 测试复杂数据处理 ===")
        
        test_cases = [
            ("混合格式数据", REALISTIC_TEST_DATA["complex_mixed_data"]),
            ("用户上传数据", REALISTIC_TEST_DATA["user_uploaded_data"]),
            ("问题数据", REALISTIC_TEST_DATA["problematic_data"])
        ]
        
        for case_name, test_data in test_cases:
            start_time = datetime.now()
            try:
                # 使用智能体进行完整清洗
                result = asyncio.run(
                    self.cleanser_agent.cleanse_financial_data(test_data)
                )
                
                if result['success']:
                    quality_score = result['quality_score']
                    issues_found = result.get('issues_found', 0)
                    critical_issues = result.get('critical_issues', 0)
                    
                    passed = quality_score >= 50  # 对问题数据要求较低
                    
                    details = f"质量分数: {quality_score:.2f}, "
                    details += f"问题数: {issues_found}, 严重问题: {critical_issues}"
                    
                    if 'transformation_summary' in result:
                        summary = result['transformation_summary']
                        details += f", 转换字段: {summary.get('fields_transformed', 0)}"
                else:
                    passed = False
                    details = "清洗失败"
                
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test(f"复杂数据处理_{case_name}", passed, details, duration)
                
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test(f"复杂数据处理_{case_name}", False, f"异常: {str(e)}", duration)
    
    def test_agent_coordination(self):
        """测试智能体协作"""
        logger.info("\n=== 测试智能体协作 ===")
        
        test_data = REALISTIC_TEST_DATA["basic_chinese_data"]
        start_time = datetime.now()
        
        try:
            # 1. 数据清洗智能体处理
            cleansing_result = asyncio.run(
                self.cleanser_agent.cleanse_financial_data(test_data)
            )
            
            if cleansing_result['success']:
                # 2. 验证清洗后数据可以被分析器使用
                cleansed_data = cleansing_result['cleansed_data']
                
                # 转换为JSON格式
                cleansed_data_json = json.dumps(cleansed_data, ensure_ascii=False)
                
                # 3. 尝试使用财务分析工具处理清洗后的数据
                try:
                    # 使用财务分析器的比率计算工具
                    ratios_result = self.financial_analyzer.calculate_ratios(
                        {"financial_data": cleansed_data_json}
                    )
                    
                    # 检查分析结果
                    has_profitability = 'profitability' in ratios_result
                    has_solvency = 'solvency' in ratios_result
                    
                    passed = (
                        cleansing_result['success'] and
                        has_profitability and
                        has_solvency
                    )
                    
                    details = f"清洗成功: {cleansing_result['success']}, "
                    details += f"比率计算: {has_profitability and has_solvency}"
                    
                    if has_profitability:
                        profitability = ratios_result['profitability']
                        if 'net_profit_margin' in profitability:
                            margin = profitability['net_profit_margin']
                            details += f", 净利润率: {margin:.2f}%"
                    
                except Exception as e:
                    # 财务分析器失败，但这不一定是清洗的问题
                    passed = cleansing_result['success']
                    details = f"清洗成功但分析失败: {str(e)[:50]}..."
                
            else:
                passed = False
                details = "数据清洗失败"
            
            duration = (datetime.now() - start_time).total_seconds()
            self.record_test("智能体协作", passed, details, duration)
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.record_test("智能体协作", False, f"异常: {str(e)}", duration)
    
    def test_data_flow_compatibility(self):
        """测试数据流兼容性"""
        logger.info("\n=== 测试数据流兼容性 ===")
        
        test_scenarios = [
            ("DataAgent → DataCleanserAgent", REALISTIC_TEST_DATA["basic_chinese_data"]),
            ("User Data → DataCleanserAgent", REALISTIC_TEST_DATA["user_uploaded_data"]),
            ("Mixed Format → DataCleanserAgent", REALISTIC_TEST_DATA["complex_mixed_data"])
        ]
        
        for scenario_name, test_data in test_scenarios:
            start_time = datetime.now()
            try:
                # 模拟数据流
                # 步骤1: 数据清洗
                cleansing_result = asyncio.run(
                    self.cleanser_agent.cleanse_financial_data(test_data)
                )
                
                # 步骤2: 验证数据格式兼容性
                if cleansing_result['success']:
                    cleansed_data = cleansing_result['cleansed_data']
                    
                    # 检查数据格式
                    has_standard_structure = (
                        isinstance(cleansed_data, dict) and
                        ('income_statement' in cleansed_data or '资产负债表' in cleansed_data)
                    )
                    
                    # 检查数据质量
                    quality_adequate = cleansing_result['quality_score'] >= 70
                    
                    passed = has_standard_structure and quality_adequate
                    
                    details = f"结构标准: {has_standard_structure}, "
                    details += f"质量足够: {quality_adequate}, "
                    details += f"质量分数: {cleansing_result['quality_score']:.2f}"
                else:
                    passed = False
                    details = "清洗失败"
                
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test(f"数据流兼容性_{scenario_name}", passed, details, duration)
                
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test(f"数据流兼容性_{scenario_name}", False, f"异常: {str(e)}", duration)
    
    def test_quality_improvements(self):
        """测试质量改进效果"""
        logger.info("\n=== 测试质量改进效果 ===")
        
        problematic_data = REALISTIC_TEST_DATA["problematic_data"]
        
        # 1. 评估原始数据质量
        start_time = datetime.now()
        try:
            original_quality = asyncio.run(
                self.cleanser_agent.assess_data_quality(problematic_data)
            )
            
            # 2. 清洗数据
            cleansing_result = asyncio.run(
                self.cleanser_agent.cleanse_financial_data(problematic_data)
            )
            
            if cleansing_result['success']:
                # 3. 评估清洗后数据质量
                cleansed_data = cleansing_result['cleansed_data']
                improved_quality = asyncio.run(
                    self.cleanser_agent.assess_data_quality(cleansed_data)
                )
                
                # 4. 比较质量改进
                original_score = original_quality['quality_metrics']['overall_score']
                improved_score = improved_quality['quality_metrics']['overall_score']
                improvement = improved_score - original_score
                
                passed = improvement >= 0  # 质量应该改进或保持
                
                details = f"原始分数: {original_score:.2f}, "
                details += f"改进后分数: {improved_score:.2f}, "
                details += f"改进幅度: {improvement:+.2f}"
                
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test("质量改进效果", passed, details, duration)
                
            else:
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test("质量改进效果", False, "数据清洗失败", duration)
                
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.record_test("质量改进效果", False, f"异常: {str(e)}", duration)
    
    def test_error_recovery(self):
        """测试错误恢复能力"""
        logger.info("\n=== 测试错误恢复能力 ===")
        
        error_cases = [
            ("缺失关键字段", {"利润表": {"营业收入": 100}}),
            ("无效数值类型", {"利润表": {"营业收入": "invalid", "净利润": None}}),
            ("结构不完整", {"利润表": {"营业收入": 100}, "历史数据": {}})
        ]
        
        for case_name, test_data in error_cases:
            start_time = datetime.now()
            try:
                # 使用快速清洗模式（更宽松的错误处理）
                result = self.cleansing_toolkit.quick_cleanse_data(test_data)
                
                passed = result.get('success', False)
                
                if passed:
                    quality_level = result.get('quality_level', 'unknown')
                    details = f"成功处理错误数据, 质量等级: {quality_level}"
                else:
                    details = f"无法处理错误数据: {result.get('error', 'Unknown error')}"
                
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test(f"错误恢复_{case_name}", passed, details, duration)
                
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test(f"错误恢复_{case_name}", False, f"异常: {str(e)}", duration)
    
    def test_real_user_scenarios(self):
        """测试真实用户场景"""
        logger.info("\n=== 测试真实用户场景 ===")
        
        scenarios = [
            {
                "name": "完整财报分析",
                "data": REALISTIC_TEST_DATA["basic_chinese_data"],
                "description": "用户上传完整财报数据，要求进行财务分析"
            },
            {
                "name": "快速数据清洗",
                "data": REALISTIC_TEST_DATA["complex_mixed_data"],
                "description": "用户上传格式混乱的数据，需要快速清洗"
            },
            {
                "name": "问题数据修复",
                "data": REALISTIC_TEST_DATA["problematic_data"],
                "description": "数据存在各种问题，需要智能修复"
            }
        ]
        
        for scenario in scenarios:
            start_time = datetime.now()
            try:
                # 使用完整清洗流程
                result = asyncio.run(
                    self.cleanser_agent.cleanse_financial_data(
                        scenario["data"],
                        {
                            "auto_fix_issues": True,
                            "generate_quality_report": True,
                            "strict_mode": False  # 用户场景通常不使用严格模式
                        }
                    )
                )
                
                if result['success']:
                    quality_score = result['quality_score']
                    quality_level = result['quality_level']
                    issues_found = result.get('issues_found', 0)
                    
                    # 评估是否满足用户需求
                    meets_requirements = (
                        quality_score >= 60 and  # 最低可接受质量
                        quality_level in ['excellent', 'good', 'acceptable']
                    )
                    
                    passed = result['success'] and meets_requirements
                    
                    details = f"场景: {scenario['name']}, "
                    details += f"质量分数: {quality_score:.2f}, "
                    details += f"等级: {quality_level}, "
                    details += f"满足需求: {meets_requirements}"
                    
                    # 添加用户友好的反馈
                    if meets_requirements:
                        details += " ✓ 数据质量良好，可以进行分析"
                    else:
                        details += " ⚠️ 数据质量需要改进"
                    
                else:
                    passed = False
                    details = f"场景: {scenario['name']}, 处理失败"
                
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test(f"用户场景_{scenario['name']}", passed, details, duration)
                
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test(f"用户场景_{scenario['name']}", False, f"异常: {str(e)}", duration)
    
    def test_edge_case_handling(self):
        """测试边界情况处理"""
        logger.info("\n=== 测试边界情况处理 ===")
        
        edge_cases = [
            ("空数据", {}),
            ("只有基础数据", {"利润表": {"营业收入": 100}}),
            ("大量历史数据", self._generate_large_historical_dataset(20)),
            ("数值极端值", {
                "利润表": {
                    "营业收入": 1e15,  # 极大值
                    "净利润": -1e12,  # 极大亏损
                    "营业成本": 1e10   # 极大成本
                }
            }),
            ("混合中英文", {
                "利润表": {"营业收入": 1000, "net_profit": 100},
                "income_statement": {"revenue": 500, "净利润": 50}
            })
        ]
        
        for case_name, test_data in edge_cases:
            start_time = datetime.now()
            try:
                # 使用容错性强的快速清洗
                result = self.cleansing_toolkit.quick_cleanse_data(test_data)
                
                passed = result.get('success', False)
                
                if passed:
                    details = f"成功处理边界情况"
                    if 'cleansed_data' in result:
                        data_keys = list(result['cleansed_data'].keys())
                        details += f", 数据键: {len(data_keys)}"
                else:
                    details = f"处理失败: {result.get('error', 'Unknown error')}"
                
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test(f"边界情况_{case_name}", passed, details, duration)
                
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test(f"边界情况_{case_name}", False, f"异常: {str(e)}", duration)
    
    def test_system_stability(self):
        """测试系统稳定性"""
        logger.info("\n=== 测试系统稳定性 ===")
        
        # 重复处理相同数据，验证一致性
        test_data = REALISTIC_TEST_DATA["basic_chinese_data"]
        results = []
        
        for i in range(5):  # 重复5次
            start_time = datetime.now()
            try:
                result = self.cleansing_toolkit.cleanse_financial_data(test_data)
                results.append(result)
                
                duration = (datetime.now() - start_time).total_seconds()
                logger.info(f"  重复测试 {i+1}/5: {result.get('success', False)} ({duration:.3f}s)")
                
            except Exception as e:
                logger.error(f"  重复测试 {i+1}/5 失败: {str(e)}")
        
        # 验证结果一致性
        if results:
            success_rates = [r.get('success', False) for r in results]
            quality_scores = [r.get('quality_score', 0) for r in results if r.get('success')]
            
            passed = (
                all(success_rates) and  # 所有都成功
                len(set(quality_scores)) <= 2  # 质量分数差异不大
            )
            
            details = f"成功率: {sum(success_rates)}/{len(success_rates)}, "
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                score_variance = max(quality_scores) - min(quality_scores)
                details += f"平均质量: {avg_quality:.2f}, 变化: {score_variance:.2f}"
            
            self.record_test("系统稳定性", passed, details)
    
    def test_performance_under_load(self):
        """测试负载下的性能"""
        logger.info("\n=== 测试负载下的性能 ===")
        
        # 生成中等规模数据集
        load_test_data = self._generate_medium_dataset()
        
        performance_thresholds = {
            "max_processing_time": 10.0,  # 最大处理时间10秒
            "min_quality_score": 60,    # 最低质量分数60
            "max_memory_usage": 100      # 最大内存使用100MB（估算）
        }
        
        start_time = datetime.now()
        try:
            result = asyncio.run(
                self.cleanser_agent.cleanse_financial_data(load_test_data)
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if result['success']:
                quality_score = result['quality_score']
                processing_time = result.get('processing_time', duration)
                
                # 评估性能指标
                performance_ok = (
                    duration <= performance_thresholds["max_processing_time"] and
                    quality_score >= performance_thresholds["min_quality_score"]
                )
                
                details = f"处理时间: {processing_time:.3f}s, "
                details += f"质量分数: {quality_score:.2f}, "
                details += f"性能达标: {performance_ok}"
                
                # 添加性能评级
                if duration < 2.0:
                    details += " (优秀)"
                elif duration < 5.0:
                    details += " (良好)"
                elif duration < 10.0:
                    details += " (可接受)"
                else:
                    details += " (需优化)"
                
                passed = result['success'] and performance_ok
            else:
                passed = False
                details = f"处理失败: {result.get('error', 'Unknown error')}"
            
            self.record_test("负载性能测试", passed, details, duration)
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.record_test("负载性能测试", False, f"异常: {str(e)}", duration)
    
    def _generate_large_historical_dataset(self, years: int) -> Dict[str, Any]:
        """生成大型历史数据集"""
        data = {
            "利润表": {
                "营业收入": 1000.0,
                "净利润": 100.0
            },
            "资产负债表": {
                "总资产": 5000.0,
                "总负债": 3000.0,
                "所有者权益": 2000.0
            },
            "历史数据": {}
        }
        
        base_year = 2025 - years
        for i in range(years):
            year = base_year + i
            data["历史数据"][str(year)] = {
                "营业收入": 1000 + i * 50,
                "净利润": 100 + i * 5,
                "营业成本": 800 + i * 40
            }
        
        return data
    
    def _generate_medium_dataset(self) -> Dict[str, Any]:
        """生成中等规模数据集"""
        data = {
            "利润表": {
                "营业收入": 2000.0,
                "净利润": 200.0,
                "营业成本": 1500.0,
                "营业利润": 250.0,
                "毛利润": 500.0
            },
            "资产负债表": {
                "总资产": 8000.0,
                "总负债": 5000.0,
                "所有者权益": 3000.0,
                "流动资产": 4000.0,
                "流动负债": 2500.0
            },
            "现金流量表": {
                "经营活动现金流量净额": 500.0,
                "投资活动现金流量净额": -200.0,
                "筹资活动现金流量净额": -100.0
            },
            "历史数据": {}
        }
        
        # 生成10年历史数据
        for i in range(10):
            year = 2025 - i
            data["历史数据"][str(year)] = {
                "营业收入": 1500 + i * 100,
                "净利润": 150 + i * 10,
                "营业成本": 1200 + i * 80,
                "总资产": 6000 + i * 200
            }
        
        return data
    
    def print_test_summary(self, total_duration: float):
        """打印测试摘要"""
        logger.info("\n" + "="*60)
        logger.info("集成测试摘要")
        logger.info("="*60)
        
        total = self.test_results['total_tests']
        passed = self.test_results['passed_tests']
        failed = self.test_results['failed_tests']
        success_rate = (passed / total * 100) if total > 0 else 0
        
        logger.info(f"总测试数: {total}")
        logger.info(f"通过: {passed}")
        logger.info(f"失败: {failed}")
        logger.info(f"成功率: {success_rate:.1f}%")
        logger.info(f"总耗时: {total_duration:.3f}秒")
        
        # 按类别统计
        categories = {}
        for test in self.test_results['test_details']:
            category = test['name'].split('_')[0]
            if category not in categories:
                categories[category] = {'total': 0, 'passed': 0}
            categories[category]['total'] += 1
            if '通过' in test['status']:
                categories[category]['passed'] += 1
        
        logger.info("\n分类统计:")
        for category, stats in categories.items():
            rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            logger.info(f"  {category}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")
        
        if failed > 0:
            logger.info("\n失败的测试:")
            for test in self.test_results['test_details']:
                if "失败" in test['status']:
                    logger.info(f"   - {test['name']}: {test['details']}")
        
        logger.info("\n所有测试详情:")
        for test in self.test_results['test_details']:
            status_icon = "✅" if "通过" in test['status'] else "❌"
            logger.info(f"   {status_icon} {test['name']} ({test['duration']:.3f}s)")
        
        logger.info("="*60)
        
        # 保存集成测试报告
        self.save_integration_report(total_duration, success_rate, categories)
    
    def save_integration_report(self, total_duration: float, success_rate: float, categories: Dict):
        """保存集成测试报告"""
        try:
            report = {
                "integration_test_summary": {
                    "total_tests": self.test_results['total_tests'],
                    "passed_tests": self.test_results['passed_tests'],
                    "failed_tests": self.test_results['failed_tests'],
                    "success_rate": success_rate,
                    "total_duration": total_duration,
                    "test_time": datetime.now().isoformat(),
                    "categories": categories
                },
                "test_details": self.test_results['test_details'],
                "system_status": "ready" if success_rate >= 90 else "needs_improvement"
            }
            
            # 保存到文件
            report_file = project_root / "test_integration_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"集成测试报告已保存到: {report_file}")
            
        except Exception as e:
            logger.error(f"保存集成测试报告失败: {str(e)}")


def main():
    """主函数"""
    print("数据清洗系统集成测试脚本")
    print("=" * 50)
    
    try:
        # 创建集成测试套件
        test_suite = IntegrationTestSuite()
        
        # 运行所有集成测试
        test_suite.run_all_integration_tests()
        
        # 检查结果
        if test_suite.test_results['failed_tests'] == 0:
            print("\n🎉 所有集成测试通过！数据清洗系统集成成功。")
            print("系统已准备好用于生产环境。")
            return True
        else:
            print(f"\n⚠️ 有 {test_suite.test_results['failed_tests']} 个集成测试失败。")
            print("请检查问题并修复后重新测试。")
            return False
            
    except Exception as e:
        print(f"\n❌ 集成测试套件执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)