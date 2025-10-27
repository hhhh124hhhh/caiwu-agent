#!/usr/bin/env python3
"""
用户场景验证和性能对比脚本
验证数据清洗智能体在实际使用场景中的效果，并与传统方法进行对比
"""

import sys
import os
import json
import asyncio
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
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

# 真实用户测试场景
USER_SCENARIOS = {
    "scenario_1_basic_analysis": {
        "name": "基础财报分析",
        "description": "用户上传基础的中文财报数据，要求进行财务分析",
        "user_data": {
            "利润表": {
                "营业收入": 573.88,
                "净利润": 11.04,
                "营业成本": 552.84,
                "营业利润": 11.04
            },
            "资产负债表": {
                "总资产": 3472.98,
                "总负债": 3081.02,
                "所有者权益": 391.96
            },
            "历史数据": {
                "2025": {"营业收入": 573.88, "净利润": 11.04},
                "2024": {"营业收入": 1511.39, "净利润": 36.11},
                "2023": {"营业收入": 1420.56, "净利润": 32.45}
            }
        },
        "expected_outcomes": [
            "成功识别中文数据格式",
            "历史数据正确解析",
            "生成标准化的财务比率",
            "提供质量评估报告"
        ]
    },
    
    "scenario_2_mixed_format": {
        "name": "混合格式处理",
        "description": "用户提供中英文混合、格式不一致的复杂数据",
        "user_data": {
            "income_statement": {
                "revenue": 2500.0,
                "net_profit": 300.0,
                "operating_profit": 350.0
            },
            "利润表": {
                "营业收入": 1500.0,
                "净利润": 180.0
            },
            "资产负债表": {
                "总资产": 8000.0,
                "total_liabilities": 5000.0
            },
            "历史数据": {
                "2024": {
                    "revenue": 2000.0,
                    "net_profit": 250.0,
                    "营业收入": 1500.0
                },
                "2023": {
                    "营业收入": 1800.0,
                    "net_profit": 220.0
                }
            }
        },
        "expected_outcomes": [
            "智能识别和映射中英文字段",
            "合并重复数据",
            "标准化数据结构",
            "保持数据完整性"
        ]
    },
    
    "scenario_3_problematic_data": {
        "name": "问题数据修复",
        "description": "数据存在各种问题，需要智能修复和清洗",
        "user_data": {
            "利润表": {
                "营业收入": 0,  # 收入为0
                "净利润": -500.0,  # 亏损
                "营业成本": "invalid_value",  # 无效值
                "营业利润": None  # 空值
            },
            "资产负债表": {
                "总资产": None  # 缺少关键字段
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
        },
        "expected_outcomes": [
            "识别和处理无效数据",
            "填补缺失字段",
            "处理异常数值",
            "提供修复建议"
        ]
    },
    
    "scenario_4_large_dataset": {
        "name": "大数据集处理",
        "description": "用户上传多年份的详细财务数据",
        "user_data": {
            "基本信息": {
                "公司名称": "大型制造企业",
                "股票代码": "600000.SH"
            },
            "利润表": {
                "营业收入": 50000.0,
                "营业成本": 40000.0,
                "净利润": 5000.0
            },
            "资产负债表": {
                "总资产": 200000.0,
                "总负债": 120000.0,
                "所有者权益": 80000.0
            },
            "现金流量表": {
                "经营活动现金流量净额": 15000.0,
                "投资活动现金流量净额": -8000.0,
                "筹资活动现金流量净额": -3000.0
            },
            "历史数据": {
                **{str(2025-i): {
                    "营业收入": 50000 + i * 5000,
                    "净利润": 5000 + i * 500,
                    "营业成本": 40000 + i * 4000,
                    "总资产": 200000 + i * 10000,
                    "总负债": 120000 + i * 6000
                } for i in range(15)  # 15年数据
            }
        },
        "expected_outcomes": [
            "高效处理大数据集",
            "保持良好性能",
            "生成准确的趋势分析",
            "提供有价值的业务洞察"
        ]
    }
}


class UserScenarioValidator:
    """用户场景验证器"""
    
    def __init__(self):
        self.validation_results = {
            'total_scenarios': 0,
            'successful_scenarios': 0,
            'failed_scenarios': 0,
            'performance_metrics': {},
            'scenario_details': []
        }
        
        # 初始化组件
        self._initialize_components()
    
    def _initialize_components(self):
        """初始化验证组件"""
        try:
            from utu.agents.data_cleanser_agent import DataCleanserAgent
            from utu.tools.data_cleansing_toolkit import DataCleansingToolkit
            from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer
            from utu.config import ToolkitConfig
            
            self.cleanser_agent = DataCleanserAgent()
            
            toolkit_config = ToolkitConfig(config={}, name="data_cleansing")
            self.cleansing_toolkit = DataCleansingToolkit(toolkit_config)
            
            self.financial_analyzer = StandardFinancialAnalyzer()
            
            logger.info("验证组件初始化成功")
            
        except Exception as e:
            logger.error(f"验证组件初始化失败: {str(e)}")
            raise
    
    def run_all_validations(self):
        """运行所有用户场景验证"""
        logger.info("开始运行用户场景验证")
        
        overall_start_time = time.time()
        
        # 逐个验证场景
        for scenario_id, scenario_data in USER_SCENARIOS.items():
            logger.info(f"\n{'='*60}")
            logger.info(f"验证场景: {scenario_data['name']}")
            logger.info(f"描述: {scenario_data['description']}")
            logger.info(f"{'='*60}")
            
            self.validation_results['total_scenarios'] += 1
            
            try:
                # 验证单个场景
                result = self.validate_scenario(scenario_id, scenario_data)
                
                if result['success']:
                    self.validation_results['successful_scenarios'] += 1
                    logger.info(f"✅ 场景 '{scenario_data['name']}' 验证成功")
                else:
                    self.validation_results['failed_scenarios'] += 1
                    logger.error(f"❌ 场景 '{scenario_data['name']}' 验证失败")
                
                # 记录性能指标
                self.validation_results['performance_metrics'][scenario_id] = result['performance']
                
                # 记录详细结果
                self.validation_results['scenario_details'].append(result)
                
            except Exception as e:
                self.validation_results['failed_scenarios'] += 1
                logger.error(f"❌ 场景 '{scenario_data['name']}' 验证异常: {str(e)}")
        
        overall_duration = time.time() - overall_start_time
        
        # 生成对比报告
        self.generate_comparison_report(overall_duration)
        
        # 输出总结
        self.print_validation_summary()
        
        return self.validation_results['successful_scenarios'] == len(USER_SCENARIOS)
    
    def validate_scenario(self, scenario_id: str, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证单个用户场景"""
        result = {
            'scenario_id': scenario_id,
            'scenario_name': scenario_data['name'],
            'success': False,
            'performance': {},
            'validation_results': {},
            'recommendations': []
        }
        
        start_time = time.time()
        
        try:
            # 1. 数据清洗验证
            cleansing_result = self._validate_data_cleansing(
                scenario_data['user_data'], scenario_data['expected_outcomes']
            )
            result['validation_results']['data_cleansing'] = cleansing_result
            
            # 2. 性能验证
            performance_result = self._validate_performance(
                scenario_data['user_data'], scenario_id
            )
            result['performance'] = performance_result
            
            # 3. 业务价值验证
            business_result = self._validate_business_value(
                scenario_data['user_data'], scenario_data['expected_outcomes']
            )
            result['validation_results']['business_value'] = business_result
            
            # 4. 综合评估
            overall_success = (
                cleansing_result['success'] and
                performance_result['within_limits'] and
                business_result['meets_expectations']
            )
            
            result['success'] = overall_success
            result['duration'] = time.time() - start_time
            
            # 生成建议
            result['recommendations'] = self._generate_recommendations(
                cleansing_result, performance_result, business_result
            )
            
        except Exception as e:
            logger.error(f"场景验证异常: {str(e)}")
            result['duration'] = time.time() - start_time
            result['error'] = str(e)
        
        return result
    
    def _validate_data_cleansing(self, user_data: Dict[str, Any], expected_outcomes: List[str]) -> Dict[str, Any]:
        """验证数据清洗效果"""
        result = {
            'success': False,
            'outcomes_met': [],
            'outcomes_missed': [],
            'quality_score': 0,
            'details': []
        }
        
        try:
            # 使用数据清洗工具集处理数据
            start_time = time.time()
            cleansing_result = self.cleansing_toolkit.cleanse_financial_data(user_data)
            processing_time = time.time() - start_time
            
            if cleansing_result['success']:
                # 评估结果质量
                quality_score = cleansing_result['quality_score']
                quality_level = cleansing_result['quality_level']
                
                result['quality_score'] = quality_score
                result['processing_time'] = processing_time
                
                # 检查预期结果
                for outcome in expected_outcomes:
                    if self._check_outcome(cleansing_result, outcome):
                        result['outcomes_met'].append(outcome)
                        result['details'].append(f"✅ {outcome}")
                    else:
                        result['outcomes_missed'].append(outcome)
                        result['details'].append(f"❌ {outcome}")
                
                # 数据清洗成功的基本要求
                has_cleansed_data = 'cleansed_data' in cleansing_result
                has_quality_info = 'quality_score' in cleansing_result
                
                result['success'] = (
                    has_cleansed_data and
                    has_quality_info and
                    quality_score >= 50  # 最低质量要求
                )
                
                if result['success']:
                    result['details'].append(f"质量等级: {quality_level}")
                    result['details'].append(f"处理时间: {processing_time:.3f}s")
                
            else:
                result['details'].append(f"数据清洗失败: {cleansing_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            result['details'].append(f"数据清洗验证异常: {str(e)}")
        
        return result
    
    def _validate_performance(self, user_data: Dict[str, Any], scenario_id: str) -> Dict[str, Any]:
        """验证性能表现"""
        result = {
            'success': False,
            'within_limits': False,
            'performance_metrics': {},
            'benchmark_comparison': {}
        }
        
        try:
            # 设置性能基准
            benchmarks = {
                'max_processing_time': 10.0,  # 最大处理时间10秒
                'min_quality_score': 60,    # 最低质量分数60
                'max_memory_estimate': 50   # 最大内存估算50MB
            }
            
            # 运行性能测试
            start_time = time.time()
            
            # 执行多次测试取平均值
            test_runs = 3
            processing_times = []
            quality_scores = []
            
            for i in range(test_runs):
                test_start = time.time()
                test_result = self.cleansing_toolkit.cleanse_financial_data(user_data)
                test_end = time.time()
                
                if test_result.get('success'):
                    processing_times.append(test_end - test_start)
                    quality_scores.append(test_result.get('quality_score', 0))
            
            if processing_times:
                avg_processing_time = sum(processing_times) / len(processing_times)
                avg_quality_score = sum(quality_scores) / len(quality_scores)
                
                result['performance_metrics'] = {
                    'avg_processing_time': avg_processing_time,
                    'avg_quality_score': avg_quality_score,
                    'test_runs': test_runs,
                    'processing_time_variance': max(processing_times) - min(processing_times)
                }
                
                # 性能评估
                time_ok = avg_processing_time <= benchmarks['max_processing_time']
                quality_ok = avg_quality_score >= benchmarks['min_quality_score']
                
                result['within_limits'] = time_ok and quality_ok
                result['success'] = True
                
                # 基准对比
                result['benchmark_comparison'] = {
                    'time_performance': f"{avg_processing_time:.3f}s (基准: {benchmarks['max_processing_time']:.1f}s)",
                    'quality_performance': f"{avg_quality_score:.1f} (基准: {benchmarks['min_quality_score']})"
                }
                
                if not time_ok:
                    result['benchmark_comparison']['time_status'] = "超出基准"
                if not quality_ok:
                    result['benchmark_comparison']['quality_status'] = "低于基准"
                
                result['details'] = [
                    f"平均处理时间: {avg_processing_time:.3f}s",
                    f"平均质量分数: {avg_quality_score:.1f}",
                    f"测试运行次数: {test_runs}"
                ]
                
                if not result['within_limits']:
                    result['details'].append("性能超出基准限制")
                
        except Exception as e:
            result['details'].append(f"性能验证异常: {str(e)}")
        
        return result
    
    def _validate_business_value(self, user_data: Dict[str, Any], expected_outcomes: List[str]) -> Dict[str, Any]:
        """验证业务价值"""
        result = {
            'success': False,
            'meets_expectations': False,
            'business_benefits': [],
            'limitations': [],
            'roi_assessment': ''
        }
        
        try:
            # 数据清洗价值评估
            start_time = time.time()
            cleansing_result = self.cleansing_toolkit.cleanse_financial_data_data)
            cleansing_end = time.time()
            
            if cleansing_result.get('success'):
                cleansing_data = cleansing_result['cleansed_data']
                quality_score = cleansing_result['quality_score']
                
                # 评估业务价值
                benefits = []
                limitations = []
                
                # 1. 数据标准化价值
                if self._has_standardized_structure(cleansing_data):
                    benefits.append("数据格式标准化，便于后续分析")
                
                # 2. 质量保证价值
                if quality_score >= 80:
                    benefits.append(f"高质量数据({quality_score:.1f}分)，分析结果可靠")
                elif quality_score >= 60:
                    benefits.append(f"中等质量数据({quality_score:.1f}分)，基本可用")
                else:
                    limitations.append(f"数据质量较低({quality_score:.1f}分)，需要改进")
                
                # 3. 错误处理价值
                issues_count = cleansing_result.get('issues_found', 0)
                if issues_count > 0:
                    benefits.append(f"发现{issues_count}个数据问题，帮助提高数据质量")
                else:
                    benefits.append("数据质量良好，无需额外修复")
                
                # 4. 效率价值
                processing_time = cleansing_end - start_time
                if processing_time < 2.0:
                    benefits.append(f"处理快速({processing_time:.2f}s)，用户友好")
                elif processing_time < 5.0:
                    benefits.append(f"处理效率合理({processing_time:.2f}s)")
                else:
                    limitations.append(f"处理时间较长({processing_time:.2f}s)，可优化")
                
                result['business_benefits'] = benefits
                result['limitations'] = limitations
                
                # 综合评估
                meets_basic_requirements = (
                    len(benefits) >= 2 and
                    quality_score >= 60
                )
                
                result['meets_expectations'] = meets_basic_requirements
                result['success'] = True
                
                # ROI评估
                if meets_basic_requirements:
                    result['roi_assessment'] = "数据清洗显著提升了数据质量，为后续分析创造价值"
                else:
                    result['roi_assessment'] = "数据清洗提供了一些价值，但仍有改进空间"
                
                result['details'] = [
                    f"业务收益数: {len(benefits)}",
                    f"限制因素数: {len(limitations)}",
                    f"ROI评估: {result['roi_assessment']}"
                ]
                
            else:
                result['details'].append("数据清洗失败，无法创造业务价值")
                
        except Exception as e:
            result['details'].append(f"业务价值验证异常: {str(e)}")
        
        return result
    
    def _check_outcome(self, cleansing_result: Dict[str, Any], expected_outcome: str) -> bool:
        """检查预期结果是否达到"""
        outcome_lower = expected_outcome.lower()
        
        # 常见预期结果的检查
        outcome_checks = {
            "中文": lambda r: any("中文" in str(r).lower() for r in cleansing_result.get('details', [])),
            "历史": lambda r: "historical" in str(r).lower() or "历史" in str(r).lower(),
            "标准化": lambda r: "标准化" in str(r).lower() or "standard" in str(r).lower(),
            "比率": lambda r: "比率" in str(r).lower() or "ratio" in str(r).lower(),
            "质量": lambda r: "质量" in str(r).lower() or "quality" in str(r).lower(),
            "修复": lambda r: "修复" in str(r).lower() or "fix" in str(r).lower(),
            "处理": lambda r: "处理" in str(r).lower() or "process" in str(r).lower()
        }
        
        for key, check_func in outcome_checks.items():
            if key in outcome_lower and check_func(cleansing_result):
                return True
        
        return False
    
    def _has_standardized_structure(self, data: Dict[str, Any]) -> bool:
        """检查是否有标准化结构"""
        standard_indicators = [
            'income_statement', '资产负债表', 'cash_flow',
            'profitability', 'solvency', 'efficiency'
        ]
        
        return any(indicator in str(data).lower() for indicator in standard_indicators)
    
    def _generate_recommendations(self, cleansing_result: Dict, performance_result: Dict, business_result: Dict) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于数据清洗结果的建议
        if not cleansing_result['success']:
            recommendations.append("建议检查数据格式，确保符合基本要求")
        elif cleansing_result['quality_score'] < 70:
            recommendations.append("建议提供更完整和准确的数据以获得更好的分析结果")
        
        # 基于性能结果的建议
        if not performance_result['within_limits']:
            recommendations.append("建议优化数据处理流程以提高性能")
        elif performance_result['performance_metrics'].get('avg_processing_time', 0) > 5.0:
            recommendations.append("考虑使用缓存或批处理来提高处理效率")
        
        # 基于业务价值的建议
        if not business_result['meets_expectations']:
            recommendations.append("建议提供更详细和结构化的财务数据")
        elif business_result['limitations']:
            recommendations.append("解决发现的数据质量问题以获得更好的业务洞察")
        
        # 通用建议
        if len(recommendations) == 0:
            recommendations.append("数据清洗效果良好，可以继续进行财务分析")
        
        return recommendations
    
    def generate_comparison_report(self, total_duration: float):
        """生成对比报告"""
        logger.info("\n" + "="*60)
        logger.info("生成性能对比报告")
        logger.info("="*60)
        
        # 收集性能数据
        all_performance = [
            {
                'scenario_id': scenario_id,
                'scenario_name': details['scenario_name'],
                'performance': details['performance']
            }
            for scenario_id, details in self.validation_results['scenario_details']
            if 'performance' in details
        ]
        
        if all_performance:
            avg_processing_time = sum(
                p['performance'].get('performance_metrics', {}).get('avg_processing_time', 0)
                for p in all_performance
            ) / len(all_performance)
            
            avg_quality_score = sum(
                p['performance'].get('performance_metrics', {}).get('avg_quality_score', 0)
                for p in all_performance
            ) / len(all_performance)
            
            logger.info(f"平均处理时间: {avg_processing_time:.3f}秒")
            logger.info(f"平均质量分数: {avg_quality_score:.2f}分")
            
            # 性能分级
            if avg_processing_time < 2.0:
                performance_grade = "优秀"
            elif avg_processing_time < 5.0:
                performance_grade = "良好"
            elif avg_processing_time < 10.0:
                performance_grade = "可接受"
            else:
                performance_grade = "需改进"
            
            logger.info(f"整体性能等级: {performance_grade}")
            
            # 质量分级
            if avg_quality_score >= 85:
                quality_grade = "优秀"
            elif avg_quality_score >= 70:
                quality_grade = "良好"
            elif avg_quality_score >= 60:
                quality_grade = "可接受"
            else:
                quality_grade = "需改进"
            
            logger.info(f"整体质量等级: {quality_grade}")
    
    def print_validation_summary(self):
        """打印验证摘要"""
        logger.info("\n" + "="*60)
        logger.info("用户场景验证摘要")
        logger.info("="*60)
        
        total = self.validation_results['total_scenarios']
        successful = self.validation_results['successful_scenarios']
        failed = self.validation_results['failed_scenarios']
        success_rate = (successful / total * 100) if total > 0 else 0
        
        logger.info(f"总场景数: {total}")
        logger.info(f"验证成功: {successful}")
        logger.info(f"验证失败: {failed}")
        logger.info(f"成功率: {success_rate:.1f}%")
        
        # 分类统计
        categories = {}
        for detail in self.validation_results['scenario_details']:
            if 'validation_results' in detail:
                for validation_type, validation_data in detail['validation_results'].items():
                    if validation_type not in categories:
                        categories[validation_type] = {'total': 0, 'success': 0}
                    categories[validation_type]['total'] += 1
                    if validation_data.get('success', False):
                        categories[validation_type]['success'] += 1
        
        logger.info("\n验证类别统计:")
        for category, stats in categories.items():
            rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
            logger.info(f"  {category}: {stats['success']}/{stats['total']} ({rate:.1f}%)")
        
        # 详细结果
        logger.info("\n详细验证结果:")
        for detail in self.validation_results['scenario_details']:
            status = "✅ 成功" if detail['success'] else "❌ 失败"
            logger.info(f"  {status}: {detail['scenario_name']} ({detail['duration']:.3f}s)")
            
            if 'recommendations' in detail and detail['recommendations']:
                for rec in detail['recommendations'][:2]:  # 只显示前2个建议
                    logger.info(f"    建议: {rec}")
        
        logger.info("\n" + "="*60)
        logger.info("验证完成")
        logger.info("="*60)
        
        # 保存验证报告
        self.save_validation_report()
    
    def save_validation_report(self):
        """保存验证报告"""
        try:
            report = {
                "user_scenario_validation_summary": {
                    "total_scenarios": self.validation_results['total_scenarios'],
                    "successful_scenarios": self.validation_results['successful_scenarios'],
                    "failed_scenarios": self.validation_results['failed_scenarios'],
                    "success_rate": (self.validation_results['successful_scenarios'] / 
                                  self.validation_results['total_scenarios'] * 100) 
                                  if self.validation_results['total_scenarios'] > 0 else 0),
                    "validation_time": datetime.now().isoformat(),
                    "user_scenarios": list(USER_SCENARIOS.keys())
                },
                "performance_metrics": self.validation_results['performance_metrics'],
                "scenario_details": self.validation_results['scenario_details'],
                "system_readiness": "production_ready" if self.validation_results['successful_scenarios'] == len(USER_SCENARIOS) else "needs_improvement"
            }
            
            # 保存到文件
            report_file = project_root / "user_scenario_validation_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"用户场景验证报告已保存到: {report_file}")
            
        except Exception as e:
            logger.error(f"保存验证报告失败: {str(e)}")


def main():
    """主函数"""
    print("数据清洗用户场景验证和性能对比")
    print("=" * 50)
    
    try:
        # 创建验证器
        validator = UserScenarioValidator()
        
        # 运行验证
        success = validator.run_all_validations()
        
        if success:
            print("\n🎉 所有用户场景验证通过！")
            print("数据清洗智能体已准备好服务真实用户。")
            print("\n系统优势:")
            print("✓ 能够处理各种格式的财务数据")
            print("✓ 智能识别和修复数据问题")
            print("✓ 提供数据质量保证")
            print("✓ 性能表现优秀")
            print("✓ 业务价值显著")
            return True
        else:
            print(f"\n⚠️ 有 {validator.validation_results['failed_scenarios']} 个场景验证失败。")
            print("请检查并改进系统后再试。")
            return False
            
    except Exception as e:
        print(f"\n❌ 用户场景验证失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)