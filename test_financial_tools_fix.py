#!/usr/bin/env python3
"""
财务分析工具修复验证测试脚本
测试 calculate_ratios 和 analyze_trends_tool 的修复效果
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer

def test_calculate_ratios_fixes():
    """测试财务比率计算修复"""
    print("🔍 测试 calculate_ratios 工具修复...")

    analyzer = StandardFinancialAnalyzer()

    # 测试用例1：比亚迪扁平化数据
    test_case_1 = {
        "company": "比亚迪",
        "revenue": 371281000000,
        "net_profit": 16039000000,
        "total_assets": 846343000000,
        "total_liabilities": 601592000000,
        "equity": 244751000000,
        "current_assets": 400000000000,
        "current_liabilities": 350000000000,
        "inventory": 100000000000,
        "cash": 80000000000,
        "receivables": 150000000000,
        "operating_cash_flow": 25000000000,
        "prev_revenue": 170360000000,
        "prev_net_profit": 9443000000
    }

    result1 = analyzer.calculate_ratios(json.dumps(test_case_1))

    print("  📊 测试用例1 - 比亚迪扁平化数据:")
    print(f"    盈利能力: {result1.get('profitability', {})}")
    print(f"    偿债能力: {result1.get('solvency', {})}")
    print(f"    运营效率: {result1.get('efficiency', {})}")
    print(f"    成长能力: {result1.get('growth', {})}")

    # 验证关键字段是否被计算
    assert 'profitability' in result1, "盈利能力字段缺失"
    assert 'solvency' in result1, "偿债能力字段缺失"
    assert 'efficiency' in result1, "运营效率字段缺失"
    assert 'growth' in result1, "成长能力字段缺失"

    # 验证具体指标
    profitability = result1.get('profitability', {})
    assert len(profitability) > 0, "盈利能力指标为空"
    assert profitability.get('net_profit_margin', 0) > 0, "净利率计算错误"

    solvency = result1.get('solvency', {})
    assert len(solvency) > 0, "偿债能力指标为空"
    assert solvency.get('debt_to_asset_ratio', 0) > 0, "资产负债率计算错误"

    print("    ✅ 测试用例1 通过\n")

    # 测试用例2：嵌套结构数据
    test_case_2 = {
        "income_statement": {
            "revenue": 283072000000,
            "net_profit": 52297000000,
            "gross_profit": 80000000000,
            "operating_profit": 60000000000
        },
        "balance_sheet": {
            "total_assets": 896082000000,
            "total_liabilities": 548900000000,
            "total_equity": 347182000000,
            "current_assets": 400000000000,
            "current_liabilities": 300000000000,
            "cash_and_equivalents": 150000000000,
            "inventory": 80000000000,
            "accounts_receivable": 120000000000
        }
    }

    result2 = analyzer.calculate_ratios(json.dumps(test_case_2))

    print("  📊 测试用例2 - 嵌套结构数据:")
    print(f"    盈利能力: {result2.get('profitability', {})}")
    print(f"    偿债能力: {result2.get('solvency', {})}")
    print(f"    运营效率: {result2.get('efficiency', {})}")

    # 验证嵌套结构解析
    profitability = result2.get('profitability', {})
    solvency = result2.get('solvency', {})
    assert len(profitability) > 0, "嵌套结构盈利能力解析失败"
    assert len(solvency) > 0, "嵌套结构偿债能力解析失败"

    print("    ✅ 测试用例2 通过\n")

    return True

def test_analyze_trends_fixes():
    """测试趋势分析修复"""
    print("🔍 测试 analyze_trends_tool 工具修复...")

    analyzer = StandardFinancialAnalyzer()

    # 测试用例1：多公司多年数据
    test_case_1 = {
        "宁德时代": {
            "2024": {
                "营业收入": 2000,
                "净利润": 400
            },
            "2025": {
                "营业收入": 2830.72,
                "净利润": 522.97
            }
        },
        "比亚迪": {
            "2024": {
                "营业收入": 1703.60,
                "净利润": 94.43
            },
            "2025": {
                "营业收入": 3712.81,
                "净利润": 160.39
            }
        }
    }

    result1 = analyzer.analyze_trends_tool(json.dumps(test_case_1), 2)

    print("  📈 测试用例1 - 多公司多年数据:")
    print(f"    收入趋势: 趋势={result1['revenue']['trend']}, 平均增长率={result1['revenue']['average_growth']}%")
    print(f"    利润趋势: 趋势={result1['profit']['trend']}, 平均增长率={result1['profit']['average_growth']}%")
    print(f"    收入数据点数量: {len(result1['revenue']['data'])}")
    print(f"    利润数据点数量: {len(result1['profit']['data'])}")

    # 验证趋势分析结果
    assert 'revenue' in result1, "收入趋势字段缺失"
    assert 'profit' in result1, "利润趋势字段缺失"
    assert len(result1['revenue']['data']) > 0, "收入趋势数据为空"
    assert len(result1['profit']['data']) > 0, "利润趋势数据为空"
    assert result1['revenue']['average_growth'] != 0 or result1['profit']['average_growth'] != 0, "增长率计算异常"

    print("    ✅ 测试用例1 通过\n")

    # 测试用例2：简单历史数据对比
    test_case_2 = {
        "company": "测试公司",
        "revenue": 1000,
        "net_profit": 100,
        "prev_revenue": 800,
        "prev_net_profit": 60
    }

    result2 = analyzer.analyze_trends_tool(json.dumps(test_case_2), 2)

    print("  📈 测试用例2 - 简单历史数据对比:")
    print(f"    收入增长率: {result2['revenue']['average_growth']}%")
    print(f"    利润增长率: {result2['profit']['average_growth']}%")
    print(f"    收入数据点: {result2['revenue']['data']}")
    print(f"    利润数据点: {result2['profit']['data']}")

    # 验证简单对比分析
    assert result2['revenue']['average_growth'] > 0, "收入增长率计算错误"
    assert result2['profit']['average_growth'] > 0, "利润增长率计算错误"
    assert len(result2['revenue']['data']) >= 1, "收入数据点生成错误"
    assert len(result2['profit']['data']) >= 1, "利润数据点生成错误"

    print("    ✅ 测试用例2 通过\n")

    return True

def test_error_handling():
    """测试错误处理"""
    print("🔍 测试错误处理机制...")

    analyzer = StandardFinancialAnalyzer()

    # 测试无效JSON
    result1 = analyzer.calculate_ratios("invalid json")
    print(f"  ❌ 无效JSON处理: {result1}")

    # 测试空数据
    result2 = analyzer.calculate_ratios(json.dumps({}))
    print(f"  📝 空数据处理: {result2}")

    # 测试错误数据类型
    result3 = analyzer.analyze_trends_tool("invalid json", 2)
    print(f"  ❌ 无效JSON趋势分析: {result3}")

    print("    ✅ 错误处理测试完成\n")
    return True

def main():
    """主测试函数"""
    print("🚀 开始财务分析工具修复验证测试\n")

    try:
        # 运行所有测试
        test_results = []

        test_results.append(test_calculate_ratios_fixes())
        test_results.append(test_analyze_trends_fixes())
        test_results.append(test_error_handling())

        # 统计结果
        passed_tests = sum(test_results)
        total_tests = len(test_results)

        print("📊 测试结果汇总:")
        print(f"    总测试数: {total_tests}")
        print(f"    通过测试: {passed_tests}")
        print(f"    失败测试: {total_tests - passed_tests}")
        print(f"    通过率: {(passed_tests/total_tests)*100:.1f}%")

        if passed_tests == total_tests:
            print("\n🎉 所有测试通过！财务分析工具修复成功！")
            return True
        else:
            print(f"\n⚠️  有 {total_tests - passed_tests} 个测试失败，需要进一步修复")
            return False

    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)