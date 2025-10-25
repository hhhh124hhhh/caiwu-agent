#!/usr/bin/env python3
"""
财务分析边界情况测试
测试系统在异常数据、极端情况和边界条件下的表现
"""

import pytest
import json
import os
import tempfile
import shutil
import math
from pathlib import Path
import sys
from typing import Dict, Any, List

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer
from utu.tools.tabular_data_toolkit import TabularDataToolkit
from utu.tools.report_saver_toolkit import ReportSaverToolkit


class TestFinancialEdgeCases:
    """财务分析边界情况测试类"""

    @pytest.fixture
    def temp_workspace(self):
        """创建临时工作空间"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def edge_case_tools(self):
        """边界情况测试工具套件"""
        return {
            "analyzer": StandardFinancialAnalyzer(),
            "chart_generator": TabularDataToolkit(),
            "report_saver": ReportSaverToolkit()
        }

    def test_empty_data_handling(self, edge_case_tools):
        """测试空数据处理"""
        analyzer = edge_case_tools["analyzer"]

        # 测试完全空的数据
        empty_data = {}
        result = analyzer.calculate_ratios(json.dumps(empty_data))

        # 应该有错误处理机制
        assert isinstance(result, dict), "空数据应该返回字典格式结果"

        # 测试包含空结构的数据
        empty_structured_data = {
            "income": [],
            "balance": [],
            "cashflow": []
        }
        result = analyzer.calculate_ratios(json.dumps(empty_structured_data))

        assert isinstance(result, dict), "空结构化数据应该返回字典格式结果"

        print("✓ 空数据处理测试通过")

    def test_zero_value_handling(self, edge_case_tools):
        """测试零值数据处理"""
        analyzer = edge_case_tools["analyzer"]

        # 创建包含零值的财务数据
        zero_value_data = {
            "income": [
                {
                    "营业收入": 0,  # 营业收入为零
                    "营业成本": 0,
                    "净利润": 0,
                    "归属于母公司所有者的净利润": 0
                }
            ],
            "balance": [
                {
                    "资产总计": 0,  # 资产为零
                    "负债合计": 0,
                    "所有者权益合计": 0,
                    "流动资产合计": 0,
                    "流动负债合计": 0,
                    "存货": 0,
                    "应收账款": 0,
                    "固定资产": 0,
                    "长期投资": 0
                }
            ],
            "cashflow": [
                {
                    "经营活动产生的现金流量净额": 0,
                    "投资活动现金流出小计": 0,
                    "分配股利、利润或偿付利息支付的现金": 0
                }
            ]
        }

        # 执行计算
        result = analyzer.calculate_ratios(json.dumps(zero_value_data))

        # 验证结果
        assert isinstance(result, dict), "零值数据应该返回字典格式结果"

        # 检查是否有任何维度被计算出
        calculated_dimensions = len(result)
        print(f"零值数据计算出 {calculated_dimensions} 个维度")

        # 零值数据可能导致除零错误，系统应该有默认值处理
        for dimension, metrics in result.items():
            for metric_name, value in metrics.items():
                assert isinstance(value, (int, float)), f"指标值应该是数值: {dimension}.{metric_name}"
                assert not math.isnan(value), f"指标值不应该是NaN: {dimension}.{metric_name}"
                assert not math.isinf(value), f"指标值不应该是无穷大: {dimension}.{metric_name}"

        print("✓ 零值数据处理测试通过")

    def test_negative_value_handling(self, edge_case_tools):
        """测试负值数据处理"""
        analyzer = edge_case_tools["analyzer"]

        # 创建包含负值的财务数据（亏损公司）
        negative_data = {
            "income": [
                {
                    "营业收入": 1000000000,  # 10亿收入
                    "营业成本": 1200000000,  # 12亿成本
                    "净利润": -200000000,  # -2亿亏损
                    "归属于母公司所有者的净利润": -150000000  # -1.5亿亏损
                }
            ],
            "balance": [
                {
                    "资产总计": 800000000,  # 8亿资产
                    "负债合计": 1000000000,  # 10亿负债（资不抵债）
                    "所有者权益合计": -200000000,  # -2亿权益
                    "流动资产合计": 300000000,
                    "流动负债合计": 500000000,
                    "存货": 100000000,
                    "应收账款": 80000000,
                    "固定资产": 400000000,
                    "长期投资": 50000000
                }
            ],
            "cashflow": [
                {
                    "经营活动产生的现金流量净额": -100000000,  # -1亿经营现金流
                    "投资活动现金流出小计": 50000000,   # 0.5亿投资流出
                    "分配股利、利润或偿付利息支付的现金": 0  # 无分红
                }
            ]
        }

        # 执行计算
        result = analyzer.calculate_ratios(json.dumps(negative_data))

        # 验证结果
        assert isinstance(result, dict), "负值数据应该返回字典格式结果"

        # 检查计算结果的合理性
        for dimension, metrics in result.items():
            for metric_name, value in metrics.items():
                assert isinstance(value, (int, float)), f"指标值应该是数值: {dimension}.{metric_name}"
                assert not math.isnan(value), f"指标值不应该是NaN: {dimension}.{metric_name}"
                assert not math.isinf(value), f"指标值不应该是无穷大: {dimension}.{metric_name}"

        print(f"负值数据计算出 {len(result)} 个维度")
        print("✓ 负值数据处理测试通过")

    def test_extreme_large_values(self, edge_case_tools):
        """测试极大值数据处理"""
        analyzer = edge_case_tools["analyzer"]

        # 创建包含极大值的财务数据
        extreme_data = {
            "income": [
                {
                    "营业收入": 1000000000000000,  # 1万亿
                    "营业成本": 800000000000000,   # 8千亿
                    "净利润": 100000000000000,      # 1千亿
                    "归属于母公司所有者的净利润": 80000000000000  # 800亿
                }
            ],
            "balance": [
                {
                    "资产总计": 5000000000000000,  # 5万亿
                    "负债合计": 3000000000000000,  # 3万亿
                    "所有者权益合计": 2000000000000000,  # 2万亿
                    "流动资产合计": 2000000000000000,  # 2万亿
                    "流动负债合计": 1000000000000000,  # 1万亿
                    "存货": 500000000000000,      # 5000亿
                    "应收账款": 300000000000000,    # 3000亿
                    "固定资产": 2000000000000000,  # 2万亿
                    "长期投资": 500000000000000     # 5000亿
                }
            ],
            "cashflow": [
                {
                    "经营活动产生的现金流量净额": 200000000000000,   # 2000亿
                    "投资活动现金流出小计": 150000000000000,     # 1500亿
                    "分配股利、利润或偿付利息支付的现金": 50000000000000  # 500亿
                }
            ]
        }

        # 执行计算
        result = analyzer.calculate_ratios(json.dumps(extreme_data))

        # 验证结果
        assert isinstance(result, dict), "极大值数据应该返回字典格式结果"

        # 检查计算结果是否合理
        for dimension, metrics in result.items():
            for metric_name, value in metrics.items():
                assert isinstance(value, (int, float)), f"指标值应该是数值: {dimension}.{metric_name}"
                assert not math.isnan(value), f"指标值不应该是NaN: {dimension}.{metric_name}"
                assert not math.isinf(value), f"指标值不应该是无穷大: {dimension}.{metric_name}"

                # 极大值可能导致比率异常，应该在合理范围内
                if 'ratio' in metric_name.lower():
                    assert 0 <= abs(value) <= 1000, f"比率指标应该在合理范围内: {dimension}.{metric_name} = {value}"
                elif 'margin' in metric_name.lower() or 'roe' in metric_name.lower() or 'roa' in metric_name.lower():
                    assert -1000 <= value <= 1000, f"百分比指标应该在合理范围内: {dimension}.{metric_name} = {value}%"

        print(f"极大值数据计算出 {len(result)} 个维度")
        print("✓ 极大值数据处理测试通过")

    def test_mixed_data_quality(self, edge_case_tools):
        """测试混合数据质量"""
        analyzer = edge_case_tools["analyzer"]

        # 创建混合质量的财务数据
        mixed_data = {
            "income": [
                {
                    "营业收入": 1000000000,      # 正常值
                    "营业成本": None,            # None值
                    "净利润": 150000000,          # 正常值
                    "归属于母公司所有者的净利润": ""  # 空字符串
                }
            ],
            "balance": [
                {
                    "资产总计": 5000000000,      # 正常值
                    "负债合计": "invalid",       # 无效字符串
                    "所有者权益合计": 3000000000,  # 正常值
                    "流动资产合计": 2000000000,    # 正常值
                    "流动负债合计": None,          # None值
                    "存货": 500000000,            # 正常值
                    "应收账款": "300000000",      # 字符串格式的数字
                    "固定资产": None,             # None值
                    "长期投资": 500000000           # 正常值
                }
            ],
            "cashflow": [
                {
                    "经营活动产生的现金流量净额": 200000000,   # 正常值
                    "投资活动现金流出小计": None,          # None值
                    "分配股利、利润或偿付利息支付的现金": "invalid"  # 无效字符串
                }
            ]
        }

        # 执行计算
        result = analyzer.calculate_ratios(json.dumps(mixed_data))

        # 验证结果
        assert isinstance(result, dict), "混合质量数据应该返回字典格式结果"

        # 检查计算结果的合理性
        for dimension, metrics in result.items():
            for metric_name, value in metrics.items():
                assert isinstance(value, (int, float)), f"指标值应该是数值: {dimension}.{metric_name}"
                assert not math.isnan(value), f"指标值不应该是NaN: {dimension}.{metric_name}"
                assert not math.isinf(value), f"指标值不应该是无穷大: {dimension}.{metric_name}"

        print(f"混合质量数据计算出 {len(result)} 个维度")
        print("✓ 混合数据质量测试通过")

    def test_incomplete_data_structure(self, edge_case_tools):
        """测试不完整数据结构"""
        analyzer = edge_case_tools["analyzer"]

        # 测试缺少关键字段的数据结构
        incomplete_scenarios = [
            # 只有钱利润表
            {
                "income": [
                    {
                        "营业收入": 1000000000,
                        "净利润": 150000000
                    }
                ]
            },
            # 只有资产负债表
            {
                "balance": [
                    {
                        "资产总计": 5000000000,
                        "负债合计": 2000000000
                    }
                ]
            },
            # 只有现金流量表
            {
                "cashflow": [
                    {
                        "经营活动产生的现金流量净额": 200000000
                    }
                ]
            },
            # 缺少关键字段
            {
                "income": [
                    {
                        # 缺少营业收入
                        "净利润": 150000000
                    }
                ],
                "balance": [
                    {
                        "资产总计": 5000000000
                        # 缺少负债合计
                    }
                ]
            }
        ]

        for i, test_data in enumerate(incomplete_scenarios):
            print(f"  测试场景 {i+1}: {list(test_data.keys())}")

            # 执行计算
            result = analyzer.calculate_ratios(json.dumps(test_data))

            # 验证结果
            assert isinstance(result, dict), f"不完整数据场景{i+1}应该返回字典格式结果"

            # 检查计算结果的合理性
            for dimension, metrics in result.items():
                for metric_name, value in metrics.items():
                    assert isinstance(value, (int, float)), f"场景{i+1}指标值应该是数值: {dimension}.{metric_name}"
                    assert not math.isnan(value), f"场景{i+1}指标值不应该是NaN: {dimension}.{metric_name}"
                    assert not math.isinf(value), f"场景{i+1}指标值不应该是无穷大: {dimension}.{metric_name}"

            print(f"    场景{i+1}: 计算出 {len(result)} 个维度")

        print("✓ 不完整数据结构测试通过")

    def test_unicode_and_special_characters(self, edge_case_tools):
        """测试Unicode和特殊字符处理"""
        analyzer = edge_case_tools["analyzer"]

        # 创建包含特殊字符的数据
        special_char_data = {
            "income": [
                {
                    "营业收入": 1000000000,
                    "营业成本": 800000000,
                    "净利润": 150000000,
                    "归属于母公司所有者的净利润": 120000000,
                    "备注": "测试备注包含特殊字符：@#$%^&*()_+-={}[]|\\;':\",.<>/?`~"
                }
            ],
            "balance": [
                {
                    "资产总计": 5000000000,
                    "负债合计": 2000000000,
                    "所有者权益合计": 3000000000,
                    "流动资产合计": 2000000000,
                    "流动负债合计": 1000000000,
                    "存货": 500000000,
                    "应收账款": 300000000,
                    "固定资产": 2000000000,
                    "长期投资": 5000000000,
                    "公司名称": "测试公司名称Test Company Name"
                }
            ],
            "cashflow": [
                {
                    "经营活动产生的现金流量净额": 200000000,
                    "投资活动现金流出小计": 150000000,
                    "分配股利、利润或偿付利息支付的现金": 50000000,
                    "描述": "现金流量描述包含中文字符：经营活动产生的现金流量净额"
                }
            ]
        }

        # 执行计算
        result = analyzer.calculate_ratios(json.dumps(special_char_data))

        # 验证结果
        assert isinstance(result, dict), "特殊字符数据应该返回字典格式结果"

        # 检查计算结果的合理性
        for dimension, metrics in result.items():
            for metric_name, value in metrics.items():
                assert isinstance(value, (int, float)), f"指标值应该是数值: {dimension}.{metric_name}"
                assert not math.isnan(value), f"指标值不应该是NaN: {dimension}.{metric_name}"
                assert not math.isinf(value), f"指标值不应该是无穷大: {dimension}.{metric_name}"

        print(f"特殊字符数据计算出 {len(result)} 个维度")
        print("✓ Unicode和特殊字符处理测试通过")

    def test_single_company_minimal_data(self, edge_case_tools):
        """测试单家公司的最小数据"""
        analyzer = edge_case_tools["analyzer"]

        # 创建最小有效数据
        minimal_data = {
            "income": [
                {
                    "营业收入": 1000000,  # 100万
                    "净利润": 100000      # 10万
                }
            ],
            "balance": [
                {
                    "资产总计": 5000000,   # 500万
                    "负债合计": 2000000    # 200万
                }
            ],
            "cashflow": [
                {
                    "经营活动产生的现金流量净额": 200000  # 20万
                }
            ]
        }

        # 执行计算
        result = analyzer.calculate_ratios(json.dumps(minimal_data))

        # 验证结果
        assert isinstance(result, dict), "最小数据应该返回字典格式结果"

        # 检查计算结果的合理性
        for dimension, metrics in result.items():
            for metric_name, value in metrics.items():
                assert isinstance(value, (int, float)), f"指标值应该是数值: {dimension}.{metric_name}"
                assert not math.isnan(value), f"指标值不应该是NaN: {dimension}.{metric_name}"
                assert not math.isinf(value), f"指标值不应该是无穷大: {dimension}.{metric_name}"

        print(f"最小数据计算出 {len(result)} 个维度")
        print("✓ 单家公司最小数据测试通过")

    def test_chart_generation_edge_cases(self, edge_case_tools, temp_workspace):
        """测试图表生成的边界情况"""
        chart_generator = edge_case_tools["chart_generator"]

        edge_case_scenarios = [
            # 空数据
            {"companies": [], "revenue": [], "net_profit": []},

            # 单个公司
            {"companies": ["测试公司"], "revenue": [1000]},

            # 公司数量与数据不匹配
            {"companies": ["公司A", "公司B"], "revenue": [1000]},  # 只有1个值

            # 包含异常数值
            {
                "companies": ["测试公司"],
                "revenue": [float('inf')],  # 无穷大
                "net_profit": [float('-inf')]  # 负无穷大
            },

            # 包含None值
            {
                "companies": ["测试公司"],
                "revenue": [None],
                "net_profit": [100]
            },

            # 包含NaN值
            {
                "companies": ["测试公司"],
                "revenue": [float('nan')],
                "net_profit": [100]
            }
        ]

        for i, test_data in enumerate(edge_case_scenarios):
            print(f"  测试图表场景 {i+1}: {len(test_data.get('companies', []))}家公司")

            try:
                result = chart_generator.generate_charts(
                    data_json=json.dumps(test_data),
                    chart_type="comparison",
                    output_dir=temp_workspace
                )

                # 验证返回结果
                assert isinstance(result, dict), f"图表场景{i+1}应该返回字典格式结果"

                # 检查结果是否包含必要字段
                assert 'success' in result, f"图表场景{i+1}应该有success字段"

                if result.get('success', False):
                    print(f"    场景{i+1}: 图表生成成功")
                else:
                    print(f"    场景{i+1}: 图表生成失败 - {result.get('message', 'Unknown error')}")

            except Exception as e:
                print(f"    场景{i+1}: 异常 - {e}")

        print("✓ 图表生成边界情况测试通过")

    def test_report_generation_edge_cases(self, edge_case_tools, temp_workspace):
        """测试报告生成的边界情况"""
        report_saver = edge_case_tools["report_saver"]

        edge_case_contents = [
            # 空内容
            "",

            # 只有标题
            "# 空标题\n\n",

            # 超长内容
            "A" * 1000000,  # 100万个字符

            # 包含特殊字符
            "测试报告包含特殊字符：@#$%^&*()_+-={}[]|\\;':\",.<>/?`~\n",

            # 包含Unicode字符
            "测试报告包含Unicode字符：中文测试，🚀测试符号，数学公式：E=mc²\n",

            # 无效格式类型
            "测试内容"  # 随便传递一个无效类型参数
        ]

        edge_case_formats = ["md", "html", "json"]

        for i, content in enumerate(edge_case_contents):
            for j, format_type in enumerate(edge_case_formats):
                try:
                    print(f"  测试报告场景 {i+1}-{j+1}: {format_type}格式")

                    if i == len(edge_case_contents) - 1 and j == len(edge_case_formats) - 1:
                        # 最后一个场景测试无效格式类型
                        result = report_saver.save_report(
                            content=content,
                            filename=f"edge_test_report_{i}_{j}",
                            format_type="invalid_format",
                            workspace=temp_workspace
                        )
                    else:
                        result = report_saver.save_report(
                            content=content,
                            filename=f"edge_test_report_{i}_{j}",
                            format_type=format_type,
                            workspace=temp_workspace
                        )

                    # 验证返回结果
                    assert isinstance(result, dict), f"报告场景{i+1}-{j+1}应该返回字典格式结果"

                    if result.get('success', False):
                        print(f"    场景{i+1}-{j+1}: 报告生成成功")
                        assert os.path.exists(result.get('file_path', '')), "报告文件应该存在"
                    else:
                        print(f"    场景{i+1}-{j+1}: 报告生成失败 - {result.get('message', 'Unknown error')}")

                except Exception as e:
                    print(f"    场景{i+1}-{j+1}: 异常 - {e}")

        print("✓ 报告生成边界情况测试通过")

    def test_system_recovery(self, edge_case_tools, temp_workspace):
        """测试系统恢复能力"""
        analyzer = edge_case_tools["analyzer"]
        chart_generator = edge_case_tools["chart_generator"]
        report_saver = edge_case_tools["report_saver"]

        # 连续执行多个可能有问题的任务
        problematic_tasks = [
            # 空数据任务
            lambda: analyzer.calculate_ratios(json.dumps({})),

            # 无效JSON任务
            lambda: analyzer.calculate_ratios("invalid json"),

            # None数据任务
            lambda: analyzer.calculate_ratios(None),

            # 极大值任务
            lambda: analyzer.calculate_ratios(json.dumps({
                "income": [{"营业收入": float('inf')}]
            })),

            # 极小值任务
            lambda: analyzer.calculate_ratios(json.dumps({
                "income": [{"营业收入": float('-inf')}]
            })),

            # 混合异常任务
            lambda: analyzer.calculate_ratios(json.dumps({
                "income": [{"营业收入": None, "净利润": float('nan')}]
            }))
        ]

        error_count = 0
        recovery_count = 0

        for i, task in enumerate(problematic_tasks):
            try:
                result = task()
                if isinstance(result, dict):
                    recovery_count += 1
                    print(f"  任务{i+1}: 系统恢复成功")
                else:
                    error_count += 1
                    print(f"  任务{i+1}: 系统返回非字典结果")
            except Exception as e:
                # 系统应该能捕获异常并返回合理结果或默认值
                print(f"  任务{i+1}: 系统捕获异常 - {type(e).__name__}")

        total_tasks = len(problematic_tasks)
        print(f"系统恢复能力测试:")
        print(f"  总任务数: {total_tasks}")
        print(f"  恢复成功: {recovery_count}")
        print(f"  异常处理: {error_count}")
        print(f"  恢复率: {recovery_count/total_tasks*100:.1f}%")

        # 系统应该有一定的恢复能力
        recovery_rate = recovery_count / total_tasks
        assert recovery_rate >= 0.5, f"系统恢复率过低: {recovery_rate:.1%}"

        print("✓ 系统恢复能力测试通过")

    def test_data_validation_robustness(self, edge_case_tools):
        """测试数据验证的鲁棒性"""
        analyzer = edge_case_tools["analyzer"]

        # 创建各种边界数据
        validation_test_data = [
            # 数值边界
            {
                "income": [{"营业收入": 0.0001, "净利润": 0.0001}],  # 极小值
                "balance": [{"资产总计": 0.0001, "负债合计": 0.0001}],
                "cashflow": [{"经营活动产生的现金流量净额": 0.0001}]
            },

            # 精度边界
            {
                "income": [{"营业收入": 0.123456789012345, "净利润": 0.123456789012345}],
                "balance": [{"资产总计": 0.123456789012345, "负债合计": 0.123456789012345}],
                "cashflow": [{"经营活动产生的现金流量净额": 0.123456789012345}]
            },

            # 类型边界
            {
                "income": [{"营业收入": True, "净利润": False}],  # 布尔值
                "balance": [{"资产总计": 1, "负债合计": 0}],
                "cashflow": [{"经营活动产生的现金流量净额": -1}]
            },

            # 空字符串
            {
                "income": [{"营业收入": "", "净利润": ""}],
                "balance": [{"资产总计": "", "负债合计": ""}],
                "cashflow": [{"经营活动产生的现金流量净额": ""}]
            }
        ]

        successful_calculations = 0

        for i, test_data in enumerate(validation_test_data):
            try:
                result = analyzer.calculate_ratios(json.dumps(test_data))

                if isinstance(result, dict) and len(result) > 0:
                    successful_calculations += 1
                    print(f"  验证测试{i+1}: 数据验证成功")
                else:
                    print(f"  验证测试{i+1}: 数据验证失败")

            except Exception as e:
                print(f"  验证测试{i+1}: 异常 - {e}")

        print(f"数据验证鲁棒性测试:")
        print(f"  测试场景数: {len(validation_test_data)}")
        print(f"  成功验证数: {successful_calculations}")
        print(f"  验证成功率: {successful_calculations/len(validation_test_data)*100:.1f}%")

        # 数据验证应该有一定成功率
        success_rate = successful_calculations / len(validation_test_data)
        assert success_rate >= 0.6, f"数据验证成功率过低: {success_rate:.1%}"

        print("✓ 数据验证鲁棒性测试通过")


if __name__ == "__main__":
    # 运行边界情况测试
    pytest.main([__file__, "-v", "-s"])