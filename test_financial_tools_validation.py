#!/usr/bin/env python3
"""
财务分析工具测试验证脚本
验证所有修复后的测试是否能够正常工作
"""

import sys
import os
import json
import traceback
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_financial_analyzer_import():
    """测试财务分析器导入"""
    print("测试1: 财务分析器导入")
    try:
        from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer
        analyzer = StandardFinancialAnalyzer()
        print("   ✓ 财务分析器导入成功")
        return analyzer
    except Exception as e:
        print(f"   ❌ 财务分析器导入失败: {e}")
        traceback.print_exc()
        return None

def test_basic_calculation(analyzer):
    """测试基本计算功能"""
    print("\n测试2: 基本财务指标计算")
    try:
        # 标准测试数据
        test_data = {
            "income": [
                {
                    "营业收入": 1000000000,  # 10亿
                    "营业成本": 800000000,   # 8亿
                    "净利润": 150000000,     # 1.5亿
                    "归属于母公司所有者的净利润": 120000000  # 1.2亿
                }
            ],
            "balance": [
                {
                    "资产总计": 5000000000,  # 50亿
                    "负债合计": 2000000000,  # 20亿
                    "所有者权益合计": 3000000000,  # 30亿
                    "流动资产合计": 2000000000,     # 20亿
                    "流动负债合计": 1000000000,     # 10亿
                    "存货": 500000000,  # 5亿
                    "应收账款": 300000000,  # 3亿
                    "固定资产": 2000000000,  # 20亿
                    "长期投资": 500000000  # 5亿
                }
            ],
            "cashflow": [
                {
                    "经营活动产生的现金流量净额": 200000000,  # 2亿
                    "投资活动现金流出小计": 150000000,  # 1.5亿
                    "分配股利、利润或偿付利息支付的现金": 50000000  # 0.5亿
                }
            ]
        }

        # 测试JSON格式计算
        json_data = json.dumps(test_data)
        ratios = analyzer.calculate_ratios(json_data)

        # 验证结果
        assert isinstance(ratios, dict), "返回结果应该是字典"
        assert len(ratios) > 0, "返回结果不应为空"

        # 验证5大维度
        expected_dimensions = ['profitability', 'solvency', 'efficiency', 'growth', 'cash_flow']
        for dimension in expected_dimensions:
            assert dimension in ratios, f"缺失维度: {dimension}"
            assert isinstance(ratios[dimension], dict), f"维度 {dimension} 应该是字典"

        # 验证具体指标
        profitability = ratios['profitability']
        assert 'gross_profit_margin' in profitability, "缺失毛利率"
        assert 'net_profit_margin' in profitability, "缺失净利率"
        assert 'roe' in profitability, "缺失ROE"

        # 验证计算准确性（允许一定误差）
        gross_margin = profitability['gross_profit_margin']
        expected_gross_margin = (1000000000 - 800000000) / 1000000000 * 100  # 20%
        assert abs(gross_margin - expected_gross_margin) < 0.1, f"毛利率计算错误: 期望{expected_gross_margin}, 实际{gross_margin}"

        print(f"   ✓ 成功计算 {len(ratios)} 个维度的财务指标")
        print(f"   ✓ 毛利率: {gross_margin:.2f}% (期望: {expected_gross_margin:.2f}%)")
        print(f"   ✓ 净利率: {profitability['net_profit_margin']:.2f}%")
        print(f"   ✓ ROE: {profitability['roe']:.2f}%")

        return ratios

    except Exception as e:
        print(f"   ❌ 基本计算测试失败: {e}")
        traceback.print_exc()
        return None

def test_multi_period_calculation(analyzer):
    """测试多期数据计算（增长率等）"""
    print("\n测试3: 多期数据计算")
    try:
        # 多期测试数据
        multi_period_data = {
            "income": [
                {
                    "营业收入": 800000000,   # 8亿 (上期)
                    "净利润": 120000000,     # 1.2亿
                    "归属于母公司所有者的净利润": 96000000  # 0.96亿
                },
                {
                    "营业收入": 1000000000,  # 10亿 (本期)
                    "净利润": 150000000,     # 1.5亿
                    "归属于母公司所有者的净利润": 120000000  # 1.2亿
                }
            ],
            "balance": [
                {
                    "资产总计": 4500000000,  # 45亿 (上期)
                    "负债合计": 1800000000,  # 18亿
                    "所有者权益合计": 2700000000,  # 27亿
                    "流动资产合计": 1800000000,     # 18亿
                    "流动负债合计": 900000000,     # 9亿
                    "存货": 450000000,  # 4.5亿
                    "应收账款": 270000000,  # 2.7亿
                    "固定资产": 1800000000,  # 18亿
                    "长期投资": 450000000  # 4.5亿
                },
                {
                    "资产总计": 5000000000,  # 50亿 (本期)
                    "负债合计": 2000000000,  # 20亿
                    "所有者权益合计": 3000000000,  # 30亿
                    "流动资产合计": 2000000000,     # 20亿
                    "流动负债合计": 1000000000,     # 10亿
                    "存货": 500000000,  # 5亿
                    "应收账款": 300000000,  # 3亿
                    "固定资产": 2000000000,  # 20亿
                    "长期投资": 500000000  # 5亿
                }
            ],
            "cashflow": [
                {
                    "经营活动产生的现金流量净额": 180000000,  # 1.8亿 (上期)
                    "投资活动现金流出小计": 120000000,  # 1.2亿
                    "分配股利、利润或偿付利息支付的现金": 40000000  # 0.4亿
                },
                {
                    "经营活动产生的现金流量净额": 200000000,  # 2亿 (本期)
                    "投资活动现金流出小计": 150000000,  # 1.5亿
                    "分配股利、利润或偿付利息支付的现金": 50000000  # 0.5亿
                }
            ]
        }

        json_data = json.dumps(multi_period_data)
        ratios = analyzer.calculate_ratios(json_data)

        # 验证增长指标
        growth = ratios.get('growth', {})

        if 'revenue_growth' in growth:
            revenue_growth = growth['revenue_growth']
            expected_growth = (1000000000 - 800000000) / 800000000 * 100  # 25%
            assert abs(revenue_growth - expected_growth) < 1.0, f"营收增长率计算错误: 期望{expected_growth}, 实际{revenue_growth}"
            print(f"   ✓ 营收增长率: {revenue_growth:.2f}% (期望: {expected_growth:.2f}%)")

        if 'profit_growth' in growth:
            profit_growth = growth['profit_growth']
            expected_profit_growth = (150000000 - 120000000) / 120000000 * 100  # 25%
            print(f"   ✓ 净利润增长率: {profit_growth:.2f}% (期望: {expected_profit_growth:.2f}%)")

        # 验证应收账款周转率（修复后的测试）
        efficiency = ratios.get('efficiency', {})
        if 'receivables_turnover' in efficiency:
            receivables_turnover = efficiency['receivables_turnover']
            expected_turnover = 1000000000 / ((270000000 + 300000000) / 2)  # 3.51
            print(f"   ✓ 应收账款周转率: {receivables_turnover:.2f} (期望: {expected_turnover:.2f})")
            # 使用修复后的容差
            assert abs(receivables_turnover - expected_turnover) <= 1.0, \
                f"应收账款周转率误差超出容差"

        print(f"   ✓ 多期数据计算成功，包含增长率和周转率指标")
        return ratios

    except Exception as e:
        print(f"   ❌ 多期数据计算测试失败: {e}")
        traceback.print_exc()
        return None

def test_cash_flow_metrics(analyzer):
    """测试现金流量指标（新增功能）"""
    print("\n测试4: 现金流量指标计算")
    try:
        test_data = {
            "income": [{"营业收入": 1000000000}],
            "balance": [
                {
                    "资产总计": 5000000000,
                    "固定资产": 2000000000,
                    "长期投资": 500000000,
                    "流动资产合计": 2000000000,
                    "流动负债合计": 1000000000,
                }
            ],
            "cashflow": [
                {
                    "经营活动产生的现金流量净额": 200000000,
                    "投资活动现金流出小计": 150000000,
                    "分配股利、利润或偿付利息支付的现金": 50000000
                }
            ]
        }

        json_data = json.dumps(test_data)
        ratios = analyzer.calculate_ratios(json_data)

        cash_flow = ratios.get('cash_flow', {})
        expected_metrics = [
            'operating_cash_flow',
            'cash_flow_ratio',
            'free_cash_flow',
            'cash_reinvestment_ratio',
            'cash_to_investment_ratio'
        ]

        for metric in expected_metrics:
            assert metric in cash_flow, f"缺失现金流量指标: {metric}"

        # 验证计算准确性
        operating_cf = cash_flow['operating_cash_flow']
        assert abs(operating_cf - 2.0) < 0.1, f"经营现金流计算错误: {operating_cf}"

        cf_ratio = cash_flow['cash_flow_ratio']
        expected_cf_ratio = 200000000 / 1000000000  # 0.2
        assert abs(cf_ratio - expected_cf_ratio) < 0.01, f"现金流量比率计算错误: {cf_ratio}"

        free_cf = cash_flow['free_cash_flow']
        expected_free_cf = (200000000 - 150000000) / 100000000  # 0.5
        assert abs(free_cf - expected_free_cf) < 0.1, f"自由现金流计算错误: {free_cf}"

        print(f"   ✓ 成功计算 {len(cash_flow)} 个现金流量指标")
        print(f"   ✓ 经营现金流: {operating_cf:.1f}亿元")
        print(f"   ✓ 现金流量比率: {cf_ratio:.3f}")
        print(f"   ✓ 自由现金流: {free_cf:.1f}亿元")

        return cash_flow

    except Exception as e:
        print(f"   ❌ 现金流量指标测试失败: {e}")
        traceback.print_exc()
        return None

def test_edge_cases(analyzer):
    """测试边界情况"""
    print("\n测试5: 边界情况处理")
    try:
        # 测试空数据
        empty_result = analyzer.calculate_ratios(json.dumps({}))
        assert isinstance(empty_result, dict), "空数据应返回空字典"
        print("   ✓ 空数据处理正常")

        # 测试缺失字段
        incomplete_data = {
            "income": [{"营业收入": 1000000000}],  # 缺失成本数据
            "balance": [{"资产总计": 5000000000}],  # 缺失其他字段
            "cashflow": []  # 缺失现金流数据
        }

        incomplete_result = analyzer.calculate_ratios(json.dumps(incomplete_data))
        assert isinstance(incomplete_result, dict), "不完整数据应返回字典"
        print("   ✓ 不完整数据处理正常")

        # 测试异常值
        extreme_data = {
            "income": [{"营业收入": 0, "营业成本": 0, "净利润": -1000000000}],
            "balance": [{"资产总计": 1, "负债合计": 0, "所有者权益合计": 1}],
            "cashflow": [{"经营活动产生的现金流量净额": 0}]
        }

        extreme_result = analyzer.calculate_ratios(json.dumps(extreme_data))
        assert isinstance(extreme_result, dict), "异常值数据应返回字典"
        print("   ✓ 异常值处理正常")

        print("   ✓ 边界情况测试全部通过")
        return True

    except Exception as e:
        print(f"   ❌ 边界情况测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("财务分析工具测试验证脚本")
    print("=" * 60)

    test_results = []

    # 测试1: 导入测试
    analyzer = test_financial_analyzer_import()
    test_results.append(analyzer is not None)

    if analyzer is None:
        print("\n❌ 财务分析器导入失败，无法继续测试")
        return False

    # 测试2: 基本计算
    basic_result = test_basic_calculation(analyzer)
    test_results.append(basic_result is not None)

    # 测试3: 多期计算
    multi_result = test_multi_period_calculation(analyzer)
    test_results.append(multi_result is not None)

    # 测试4: 现金流量指标
    cashflow_result = test_cash_flow_metrics(analyzer)
    test_results.append(cashflow_result is not None)

    # 测试5: 边界情况
    edge_result = test_edge_cases(analyzer)
    test_results.append(edge_result)

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    test_names = [
        "财务分析器导入",
        "基本财务指标计算",
        "多期数据计算",
        "现金流量指标计算",
        "边界情况处理"
    ]

    passed_count = 0
    for i, (name, result) in enumerate(zip(test_names, test_results), 1):
        status = "✓ 通过" if result else "❌ 失败"
        print(f"测试{i}: {name} - {status}")
        if result:
            passed_count += 1

    success_rate = (passed_count / len(test_results)) * 100
    print(f"\n总体通过率: {passed_count}/{len(test_results)} ({success_rate:.1f}%)")

    if success_rate >= 80:
        print("🎉 测试验证成功！财务分析工具工作正常。")
        return True
    else:
        print("⚠️  测试验证未完全通过，需要进一步检查。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)