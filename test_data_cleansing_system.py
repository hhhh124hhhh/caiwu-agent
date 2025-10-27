#!/usr/bin/env python3
"""
数据清洗系统独立测试套件
全面测试DataCleanserAgent和数据工程组件的功能和性能
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

# 测试数据
TEST_DATA_SAMPLES = {
    "chinese_financial_format": {
        "利润表": {
            "营业收入": 573.88,
            "净利润": 11.04,
            "营业成本": 552.84,
            "营业利润": 11.04
        },
        "资产负债表": {
            "总资产": 3472.98,
            "总负债": 3081.02,
            "所有者权益": 391.96,
            "流动资产": 2500.45
        },
        "现金流量表": {
            "经营活动现金流量净额": 25.67,
            "投资活动现金流量净额": -15.23,
            "筹资活动现金流量净额": -8.45
        },
        "历史数据": {
            "2025": {"营业收入": 573.88, "净利润": 11.04},
            "2024": {"营业收入": 1511.39, "净利润": 36.11},
            "2023": {"营业收入": 1420.56, "净利润": 32.45},
            "2022": {"营业收入": 1280.23, "净利润": 28.67}
        }
    },
    
    "standard_financial_format": {
        "income_statement": {
            "revenue": 1000.0,
            "net_profit": 150.0,
            "operating_profit": 200.0
        },
        "balance_sheet": {
            "total_assets": 5000.0,
            "total_liabilities": 3000.0,
            "total_equity": 2000.0
        },
        "cash_flow": {
            "operating_cash_flow": 300.0,
            "investing_cash_flow": -100.0,
            "financing_cash_flow": -50.0
        },
        "historical_data": {
            "2024": {"revenue": 900.0, "net_profit": 120.0},
            "2023": {"revenue": 800.0, "net_profit": 100.0}
        }
    },
    
    "mixed_format": {
        "income_statement": {
            "revenue": 800.0,
            "净利润": 100.0,
            "营业成本": 600.0
        },
        "资产负债表": {
            "总资产": 4000.0,
            "total_liabilities": 2500.0
        },
        "历史数据": {
            "2024": {"营业收入": 800.0, "净利润": 100.0},
            "2023": {"营业收入": 750.0, "净利润": 90.0}
        }
    },
    
    "incomplete_data": {
        "利润表": {
            "营业收入": 500.0
            # 缺少净利润
        },
        # 缺少资产负债表
        "历史数据": {
            "2024": {"营业收入": 500.0}
        }
    },
    
    "invalid_data": {
        "利润表": {
            "营业收入": "invalid_value",
            "净利润": None
        }
    }
}


class DataCleansingTestSuite:
    """数据清洗测试套件"""
    
    def __init__(self):
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }
        
        # 导入测试组件
        try:
            from utu.data_engineering.validation_pipeline import DataValidationPipeline
            from utu.data_engineering.transform_pipeline import DataTransformPipeline
            from utu.data_engineering.quality_monitor import DataQualityMonitor
            from utu.agents.data_cleanser_agent import DataCleanserAgent
            from utu.tools.data_cleansing_toolkit import DataCleansingToolkit
            from utu.config import ToolkitConfig
            
            # 初始化组件
            self.validation_pipeline = DataValidationPipeline()
            self.transform_pipeline = DataTransformPipeline()
            self.quality_monitor = DataQualityMonitor()
            self.cleanser_agent = DataCleanserAgent()
            
            # 初始化工具包
            toolkit_config = ToolkitConfig(config={}, name="data_cleansing")
            self.cleansing_toolkit = DataCleansingToolkit(toolkit_config)
            
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
    
    def run_all_tests(self):
        """运行所有测试"""
        logger.info("开始运行数据清洗系统测试套件")
        
        start_time = datetime.now()
        
        # 单元测试
        self.test_validation_pipeline()
        self.test_transform_pipeline()
        self.test_quality_monitor()
        
        # 集成测试
        self.test_data_cleanser_agent()
        self.test_data_cleansing_toolkit()
        
        # 端到端测试
        self.test_end_to_end_processing()
        
        # 性能测试
        self.test_performance()
        
        # 边界测试
        self.test_edge_cases()
        
        # 错误处理测试
        self.test_error_handling()
        
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        # 输出测试结果摘要
        self.print_test_summary(total_duration)
    
    def test_validation_pipeline(self):
        """测试数据验证管道"""
        logger.info("\n=== 测试数据验证管道 ===")
        
        test_cases = [
            ("chinese_financial_format", TEST_DATA_SAMPLES["chinese_financial_format"]),
            ("standard_financial_format", TEST_DATA_SAMPLES["standard_financial_format"]),
            ("incomplete_data", TEST_DATA_SAMPLES["incomplete_data"]),
            ("invalid_data", TEST_DATA_SAMPLES["invalid_data"])
        ]
        
        for case_name, test_data in test_cases:
            start_time = datetime.now()
            try:
                result = self.validation_pipeline.validate_financial_data_comprehensive(test_data)
                
                passed = (
                    hasattr(result, 'is_valid') and
                    hasattr(result, 'quality_score') and
                    hasattr(result, 'data_type')
                )
                
                details = f"数据类型: {result.data_type}, 质量分数: {result.quality_score:.2f}"
                if result.errors:
                    details += f", 错误数: {len(result.errors)}"
                if result.warnings:
                    details += f", 警告数: {len(result.warnings)}"
                
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test(f"验证管道_{case_name}", passed, details, duration)
                
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test(f"验证管道_{case_name}", False, f"异常: {str(e)}", duration)
    
    def test_transform_pipeline(self):
        """测试数据转换管道"""
        logger.info("\n=== 测试数据转换管道 ===")
        
        test_cases = [
            ("chinese_to_standard", TEST_DATA_SAMPLES["chinese_financial_format"]),
            ("standard_format", TEST_DATA_SAMPLES["standard_financial_format"]),
            ("mixed_format", TEST_DATA_SAMPLES["mixed_format"])
        ]
        
        target_formats = ["data_analysis_agent_compatible", "chart_generator_compatible"]
        
        for case_name, test_data in test_cases:
            for target_format in target_formats:
                start_time = datetime.now()
                try:
                    result = self.transform_pipeline.transform_financial_data(
                        test_data, target_format
                    )
                    
                    passed = result.success and result.transformed_data is not None
                    
                    details = f"目标格式: {target_format}, 转换率: {result.conversion_rate:.1f}%"
                    if result.fields_transformed > 0:
                        details += f", 字段转换: {result.fields_transformed}"
                    
                    duration = (datetime.now() - start_time).total_seconds()
                    self.record_test(
                        f"转换管道_{case_name}_{target_format}", 
                        passed, 
                        details, 
                        duration
                    )
                    
                except Exception as e:
                    duration = (datetime.now() - start_time).total_seconds()
                    self.record_test(
                        f"转换管道_{case_name}_{target_format}", 
                        False, 
                        f"异常: {str(e)}", 
                        duration
                    )
    
    def test_quality_monitor(self):
        """测试数据质量监控器"""
        logger.info("\n=== 测试数据质量监控器 ===")
        
        test_cases = [
            ("good_quality_data", TEST_DATA_SAMPLES["chinese_financial_format"]),
            ("standard_data", TEST_DATA_SAMPLES["standard_financial_format"]),
            ("incomplete_data", TEST_DATA_SAMPLES["incomplete_data"])
        ]
        
        for case_name, test_data in test_cases:
            start_time = datetime.now()
            try:
                report = self.quality_monitor.assess_data_quality(test_data)
                
                passed = (
                    hasattr(report, 'metrics') and
                    hasattr(report, 'quality_level') and
                    report.metrics.overall_score >= 0
                )
                
                details = f"质量等级: {report.metrics.quality_level}, 分数: {report.metrics.overall_score:.2f}"
                details += f", 问题数: {len(report.issues)}"
                
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test(f"质量监控_{case_name}", passed, details, duration)
                
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test(f"质量监控_{case_name}", False, f"异常: {str(e)}", duration)
    
    def test_data_cleanser_agent(self):
        """测试数据清洗智能体"""
        logger.info("\n=== 测试数据清洗智能体 ===")
        
        test_cases = [
            ("chinese_data_cleansing", TEST_DATA_SAMPLES["chinese_financial_format"]),
            ("standard_data_cleansing", TEST_DATA_SAMPLES["standard_financial_format"]),
            ("mixed_data_cleansing", TEST_DATA_SAMPLES["mixed_format"])
        ]
        
        for case_name, test_data in test_cases:
            start_time = datetime.now()
            try:
                result = asyncio.run(
                    self.cleanser_agent.cleanse_financial_data(test_data)
                )
                
                passed = result.get('success', False) and 'cleansed_data' in result
                
                details = f"质量分数: {result.get('quality_score', 0):.2f}"
                if result.get('issues_found', 0) > 0:
                    details += f", 问题数: {result['issues_found']}"
                if result.get('transformation_summary'):
                    summary = result['transformation_summary']
                    details += f", 转换字段: {summary.get('fields_transformed', 0)}"
                
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test(f"智能体_{case_name}", passed, details, duration)
                
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test(f"智能体_{case_name}", False, f"异常: {str(e)}", duration)
    
    def test_data_cleansing_toolkit(self):
        """测试数据清洗工具集"""
        logger.info("\n=== 测试数据清洗工具集 ===")
        
        test_cases = [
            ("cleanse_financial_data", TEST_DATA_SAMPLES["chinese_financial_format"]),
            ("quick_cleanse_data", TEST_DATA_SAMPLES["mixed_format"]),
            ("validate_data_format", TEST_DATA_SAMPLES["standard_financial_format"])
        ]
        
        for case_name, test_data in test_cases:
            start_time = datetime.now()
            try:
                if case_name == "cleanse_financial_data":
                    result = self.cleansing_toolkit.cleanse_financial_data(test_data)
                    passed = result.get('success', False)
                    details = f"质量分数: {result.get('quality_score', 0):.2f}"
                    
                elif case_name == "quick_cleanse_data":
                    result = self.cleansing_toolkit.quick_cleanse_data(test_data)
                    passed = result.get('success', False)
                    details = f"质量等级: {result.get('quality_level', 'unknown')}"
                    
                elif case_name == "validate_data_format":
                    result = self.cleansing_toolkit.validate_data_format(test_data)
                    passed = result.get('success', False)
                    details = f"验证通过: {result.get('success', False)}"
                
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test(f"工具集_{case_name}", passed, details, duration)
                
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test(f"工具集_{case_name}", False, f"异常: {str(e)}", duration)
    
    def test_end_to_end_processing(self):
        """测试端到端处理"""
        logger.info("\n=== 测试端到端处理 ===")
        
        test_data = TEST_DATA_SAMPLES["chinese_financial_format"]
        start_time = datetime.now()
        
        try:
            # 完整处理流程
            # 1. 验证
            validation_result = self.validation_pipeline.validate_financial_data_comprehensive(test_data)
            
            # 2. 转换
            transform_result = self.transform_pipeline.transform_financial_data(
                test_data, "data_analysis_agent_compatible"
            )
            
            # 3. 质量评估
            quality_report = self.quality_monitor.assess_data_quality(
                transform_result.transformed_data or {}
            )
            
            # 4. 智能体清洗
            cleansing_result = asyncio.run(
                self.cleanser_agent.cleanse_financial_data(test_data)
            )
            
            # 检查所有步骤都成功
            passed = (
                validation_result.is_valid and
                transform_result.success and
                quality_report.metrics.overall_score > 0 and
                cleansing_result.get('success', False)
            )
            
            details = f"验证: {validation_result.is_valid}, 转换: {transform_result.success}"
            details += f", 质量: {quality_report.metrics.overall_score:.2f}"
            details += f", 清洗: {cleansing_result.get('success', False)}"
            
            duration = (datetime.now() - start_time).total_seconds()
            self.record_test("端到端处理", passed, details, duration)
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.record_test("端到端处理", False, f"异常: {str(e)}", duration)
    
    def test_performance(self):
        """测试性能"""
        logger.info("\n=== 测试性能 ===")
        
        # 性能测试用例
        performance_cases = [
            ("大数据集处理", self._generate_large_dataset(1000)),
            ("中等数据集处理", self._generate_large_dataset(100)),
            ("小数据集处理", self._generate_large_dataset(10))
        ]
        
        for case_name, test_data in performance_cases:
            start_time = datetime.now()
            try:
                result = asyncio.run(
                    self.cleanser_agent.cleanse_financial_data(test_data)
                )
                
                duration = (datetime.now() - start_time).total_seconds()
                
                # 性能要求：处理时间不超过5秒
                passed = result.get('success', False) and duration < 5.0
                
                details = f"处理时间: {duration:.3f}秒, 数据大小: {len(json.dumps(test_data))}字符"
                
                self.record_test(f"性能_{case_name}", passed, details, duration)
                
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test(f"性能_{case_name}", False, f"异常: {str(e)}", duration)
    
    def test_edge_cases(self):
        """测试边界情况"""
        logger.info("\n=== 测试边界情况 ===")
        
        edge_cases = [
            ("空数据", {}),
            ("只有中文键名", {"利润表": {"营业收入": 100}}),
            ("只有英文键名", {"income_statement": {"revenue": 100}}),
            ("字符串数值", {"利润表": {"营业收入": "100.5", "净利润": "50.2"}}),
            ("负数值", {"利润表": {"营业收入": 1000, "净利润": -50}}),
            ("零值", {"利润表": {"营业收入": 0, "净利润": 0}}),
            ("极大值", {"利润表": {"营业收入": 1e15, "净利润": 1e12}}),
            ("极小值", {"利润表": {"营业收入": 0.001, "净利润": 0.0001}})
        ]
        
        for case_name, test_data in edge_cases:
            start_time = datetime.now()
            try:
                result = self.cleansing_toolkit.quick_cleanse_data(test_data)
                
                passed = result.get('success', False)
                details = f"处理结果: {'成功' if passed else '失败'}"
                
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test(f"边界_{case_name}", passed, details, duration)
                
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test(f"边界_{case_name}", False, f"异常: {str(e)}", duration)
    
    def test_error_handling(self):
        """测试错误处理"""
        logger.info("\n=== 测试错误处理 ===")
        
        error_cases = [
            ("无效JSON字符串", "{invalid json string"),
            ("非字典数据", [1, 2, 3]),
            ("None值", None),
            ("无限大值", {"利润表": {"营业收入": float('inf')}}),
            ("NaN值", {"利润表": {"营业收入": float('nan')}})
        ]
        
        for case_name, test_data in error_cases:
            start_time = datetime.now()
            try:
                result = self.cleansing_toolkit.validate_data_format(test_data)
                
                # 错误情况下应该返回success: False但有有意义的错误信息
                passed = not result.get('success', True) and 'error' in result
                
                details = f"正确处理错误: {passed}"
                if 'error' in result:
                    details += f", 错误信息: {result['error'][:50]}..."
                
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test(f"错误处理_{case_name}", passed, details, duration)
                
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                self.record_test(f"错误处理_{case_name}", False, f"异常: {str(e)}", duration)
    
    def _generate_large_dataset(self, size: int) -> Dict[str, Any]:
        """生成大型数据集用于性能测试"""
        data = {
            "利润表": {},
            "资产负债表": {},
            "现金流量表": {},
            "历史_data": {}
        }
        
        # 生成历史数据
        for i in range(size):
            year = 2020 + (i % 5)
            data["历史数据"][str(year)] = {
                "营业收入": 1000 + i * 10,
                "净利润": 100 + i,
                "营业成本": 800 + i * 8
            }
        
        return data
    
    def print_test_summary(self, total_duration: float):
        """打印测试摘要"""
        logger.info("\n" + "="*60)
        logger.info("测试摘要")
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
        
        if failed > 0:
            logger.info("\n失败的测试:")
            for test in self.test_results['test_details']:
                if "失败" in test['status']:
                    logger.info(f"   - {test['name']}: {test['details']}")
        
        logger.info("\n所有测试详情:")
        for test in self.test_results['test_details']:
            logger.info(f"   {test['status']}: {test['name']} ({test['duration']:.3f}s)")
        
        logger.info("="*60)
        
        # 保存测试报告
        self.save_test_report(total_duration, success_rate)
    
    def save_test_report(self, total_duration: float, success_rate: float):
        """保存测试报告"""
        try:
            report = {
                "test_summary": {
                    "total_tests": self.test_results['total_tests'],
                    "passed_tests": self.test_results['passed_tests'],
                    "failed_tests": self.test_results['failed_tests'],
                    "success_rate": success_rate,
                    "total_duration": total_duration,
                    "test_time": datetime.now().isoformat()
                },
                "test_details": self.test_results['test_details']
            }
            
            # 保存到文件
            report_file = project_root / "test_data_cleansing_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"测试报告已保存到: {report_file}")
            
        except Exception as e:
            logger.error(f"保存测试报告失败: {str(e)}")


def main():
    """主函数"""
    print("数据清洗系统独立测试套件")
    print("=" * 50)
    
    try:
        # 创建测试套件
        test_suite = DataCleansingTestSuite()
        
        # 运行所有测试
        test_suite.run_all_tests()
        
        # 检查结果
        if test_suite.test_results['failed_tests'] == 0:
            print("\n🎉 所有测试通过！数据清洗系统功能正常。")
            return True
        else:
            print(f"\n⚠️ 有 {test_suite.test_results['failed_tests']} 个测试失败，请检查问题。")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试套件执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)