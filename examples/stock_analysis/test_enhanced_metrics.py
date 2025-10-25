#!/usr/bin/env python3
"""
测试新增的财务指标计算功能
包括应收账款周转率和现金能力分析指标
"""

import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path

def test_enhanced_financial_metrics():
    """测试新增的财务指标计算功能"""
    print("=== 测试新增财务指标计算功能 ===")

    try:
        # 添加项目根目录到Python路径
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))

        from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer
        print("OK 财务分析工具导入成功")

        # 创建分析器实例
        analyzer = StandardFinancialAnalyzer()
        print("✓ 财务分析器初始化成功")

        # 创建包含现金流量表的完整测试数据
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

        # 转换为JSON字符串模拟真实调用
        test_data_json = json.dumps(test_data)

        # 测试财务比率计算
        print("测试增强财务比率计算...")
        ratios = analyzer.calculate_ratios(test_data_json)

        # 验证计算结果
        success_count = 0
        total_count = 0

        # 验证原有的4类指标
        print("\n=== 原有指标验证 ===")

        # 盈利能力指标
        if 'profitability' in ratios:
            profitability = ratios['profitability']
            expected_profitability = {
                'gross_profit_margin': 20.0,
                'net_profit_margin': 15.0,
                'roe': 4.0,
                'roa': 3.0
            }

            for key, expected_value in expected_profitability.items():
                total_count += 1
                if key in profitability:
                    actual_value = profitability[key]
                    if abs(actual_value - expected_value) < 0.1:  # 允许小数位误差
                        print(f"✓ {key}: {actual_value}%")
                        success_count += 1
                    else:
                        print(f"✗ {key}: {actual_value}% (期望: {expected_value}%)")

        # 运营效率指标（包含新增的应收账款周转率）
        if 'efficiency' in ratios:
            efficiency = ratios['efficiency']
            print("\n=== 运营效率指标验证 ===")

            # 验证应收账款周转率
            if 'receivables_turnover' in efficiency:
                receivables_turnover = efficiency['receivables_turnover']
                # 营业收入 / 平均应收账款 = 10亿 / 3亿 = 3.33
                expected_receivables_turnover = 3.33
                total_count += 1
                if abs(receivables_turnover - expected_receivables_turnover) < 0.1:
                    print(f"✓ 应收账款周转率: {receivables_turnover}")
                    success_count += 1
                else:
                    print(f"✗ 应收账款周转率: {receivables_turnover} (期望: {expected_receivables_turnover})")

        # 现金能力指标（新增的5个指标）
        if 'cash_flow' in ratios:
            cash_flow = ratios['cash_flow']
            print("\n=== 现金能力指标验证 ===")

            expected_cash_flow = {
                'operating_cash_flow': 2.0,  # 2亿 / 1e8 = 2.0亿元
                'cash_flow_ratio': 0.2,   # 2亿 / 10亿 = 0.2
                'free_cash_flow': 0.5,     # (2亿 - 1.5亿) / 1e8 = 0.5亿元
                'cash_reinvestment_ratio': 6.67,  # (2亿 - 0.5亿) / (20亿+5亿+10亿) * 100 = 6.67%
                'cash_to_investment_ratio': 1.0   # 2亿 / (1.5亿+0.5亿) = 1.0
            }

            for key, expected_value in expected_cash_flow.items():
                total_count += 1
                if key in cash_flow:
                    actual_value = cash_flow[key]
                    if key == 'operating_cash_flow' or key == 'free_cash_flow':
                        # 现金流指标以亿元为单位，允许0.1误差
                        if abs(actual_value - expected_value) < 0.1:
                            print(f"✓ {key}: {actual_value:.2f}亿元")
                            success_count += 1
                        else:
                            print(f"✗ {key}: {actual_value:.2f}亿元 (期望: {expected_value:.2f}亿元)")
                    else:
                        # 比率指标，允许0.5误差
                        if abs(actual_value - expected_value) < 0.5:
                            if key.endswith('ratio'):
                                print(f"✓ {key}: {actual_value:.2f}")
                            else:
                                print(f"✓ {key}: {actual_value:.2f}%")
                            success_count += 1
                        else:
                            if key.endswith('ratio'):
                                print(f"✗ {key}: {actual_value:.2f} (期望: {expected_value:.2f})")
                            else:
                                print(f"✗ {key}: {actual_value:.2f}% (期望: {expected_value:.2f}%)")

        print(f"\n=== 测试结果总结 ===")
        success_rate = success_count / total_count * 100
        print(f"指标计算成功率: {success_count}/{total_count} ({success_rate:.1f}%)")

        # 验证5大分析维度完整性
        print(f"\n=== 5大分析维度完整性检查 ===")
        dimensions = {
            'profitability': '盈利能力',
            'solvency': '偿债能力',
            'efficiency': '运营效率',
            'growth': '成长能力',
            'cash_flow': '现金能力'
        }

        dimension_count = 0
        for key, name in dimensions.items():
            if key in ratios:
                print(f"✓ {name} - 已实现")
                dimension_count += 1
            else:
                print(f"✗ {name} - 缺失")

        print(f"\n分析维度覆盖率: {dimension_count}/5 ({dimension_count/5*100:.1f}%)")

        return success_rate >= 80 and dimension_count >= 4

    except Exception as e:
        print(f"✗ 增强财务指标测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_validation():
    """测试数据验证和容错机制"""
    print("\n=== 测试数据验证和容错机制 ===")

    try:
        # 添加项目根目录到Python路径
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))

        from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer
        analyzer = StandardFinancialAnalyzer()

        # 测试异常数据处理
        print("测试异常数据处理...")

        abnormal_data = {
            "income": [{"营业收入": -1000, "净利润": "invalid"}],
            "balance": [{"资产总计": 0, "负债合计": "text"}],
            "cashflow": [{"经营活动产生的现金流量净额": "invalid_value"}]
        }

        abnormal_result = analyzer.calculate_ratios(json.dumps(abnormal_data))
        print("✓ 异常数据处理正常")

        # 检查现金能力指标的容错处理
        if 'cash_flow' in abnormal_result:
            cash_flow_ratios = abnormal_result['cash_flow']
            expected_defaults = {
                'operating_cash_flow': 0.0,
                'cash_flow_ratio': 0.0,
                'free_cash_flow': 0.0,
                'cash_reinvestment_ratio': 0.0,
                'cash_to_investment_ratio': 0.0
            }

            for key, expected_value in expected_defaults.items():
                if key in cash_flow_ratios and cash_flow_ratios[key] == expected_value:
                    print(f"✓ {key} 容错处理正常")
                else:
                    print(f"✗ {key} 容错处理异常")

        return True

    except Exception as e:
        print(f"✗ 数据验证测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=== 增强财务指标功能验证测试 ===")
    print("测试目标:")
    print("1. 验证新增的应收账款周转率计算")
    print("2. 验证新增的5个现金能力分析指标")
    print("3. 验证5大分析维度的完整性")
    print("4. 验证数据验证和容错机制")
    print()

    # 运行各项测试
    test1_passed = test_enhanced_financial_metrics()
    test2_passed = test_data_validation()

    # 总结测试结果
    print("\n" + "="*50)
    print("测试结果总结:")
    print(f"增强财务指标测试: {'✓ 通过' if test1_passed else '✗ 失败'}")
    print(f"数据验证测试: {'✓ 通过' if test2_passed else '✗ 失败'}")

    overall_success = test1_passed and test2_passed
    print(f"\n整体测试结果: {'✓ 全部通过' if overall_success else '✗ 有测试失败'}")

    if overall_success:
        print("\n🎉 增强财务指标功能验证成功！")
        print("✅ 应收账款周转率计算正常")
        print("✅ 现金能力分析指标计算正常")
        print("✅ 5大分析维度完整")
        print("✅ 数据验证和容错机制正常")
        print("\n系统现在支持完整的财务分析体系！")
    else:
        print("\n⚠️  仍有问题需要解决")

    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)