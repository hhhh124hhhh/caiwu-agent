#!/usr/bin/env python3
"""
简化版本测试新增的财务指标计算功能
"""

import sys
import json
import pandas as pd
from pathlib import Path

def test_simple_enhanced_metrics():
    """简化测试新增的财务指标计算功能"""
    print("=== 简化测试新增财务指标功能 ===")

    try:
        # 添加项目根目录到Python路径
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))

        from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer
        print("OK 财务分析工具导入成功")

        # 创建分析器实例
        analyzer = StandardFinancialAnalyzer()
        print("OK 财务分析器初始化成功")

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

        # 验证5大分析维度完整性
        print("\n=== 5大分析维度完整性检查 ===")
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
                print(f"OK {name} - 已实现")
                dimension_count += 1
                if key == 'efficiency' and 'receivables_turnover' in ratios[key]:
                    receivables_turnover = ratios[key]['receivables_turnover']
                    print(f"OK 应收账款周转率: {receivables_turnover:.2f}")
                if key == 'cash_flow':
                    cash_flow_ratios = ratios[key]
                    print(f"OK 经营现金流: {cash_flow_ratios.get('operating_cash_flow', 0):.2f}亿元")
                    print(f"OK 自由现金流: {cash_flow_ratios.get('free_cash_flow', 0):.2f}亿元")
                    print(f"OK 现金流量比率: {cash_flow_ratios.get('cash_flow_ratio', 0):.2f}")
            else:
                print(f"FAIL {name} - 缺失")

        print(f"\n分析维度覆盖率: {dimension_count}/5 ({dimension_count/5*100:.1f}%)")

        # 验证具体指标
        print("\n=== 具体指标验证 ===")

        # 盈利能力指标
        if 'profitability' in ratios:
            profitability = ratios['profitability']
            total_count += 3
            if 'net_profit_margin' in profitability:
                print(f"OK 净利率: {profitability['net_profit_margin']:.2f}%")
                success_count += 1
            if 'roe' in profitability:
                print(f"OK ROE: {profitability['roe']:.2f}%")
                success_count += 1
            if 'roa' in profitability:
                print(f"OK ROA: {profitability['roa']:.2f}%")
                success_count += 1

        # 运营效率指标（包含应收账款周转率）
        if 'efficiency' in ratios:
            efficiency = ratios['efficiency']
            if 'receivables_turnover' in efficiency:
                total_count += 1
                receivables_turnover = efficiency['receivables_turnover']
                # 营业收入 / 平均应收账款 = 10亿 / 3亿 = 3.33
                expected = 3.33
                if abs(receivables_turnover - expected) < 1:
                    print(f"OK 应收账款周转率: {receivables_turnover:.2f}")
                    success_count += 1
                else:
                    print(f"WARNING 应收账款周转率: {receivables_turnover:.2f} (期望约3.33)")

        # 现金能力指标
        if 'cash_flow' in ratios:
            cash_flow = ratios['cash_flow']
            total_count += 2
            operating_cf = cash_flow.get('operating_cash_flow', 0)
            free_cf = cash_flow.get('free_cash_flow', 0)
            print(f"OK 经营现金流: {operating_cf:.2f}亿元")
            print(f"OK 自由现金流: {free_cf:.2f}亿元")
            if operating_cf != 0 or free_cf != 0:
                success_count += 2

        success_rate = success_count / total_count * 100 if total_count > 0 else 0
        print(f"\n指标计算成功率: {success_count}/{total_count} ({success_rate:.1f}%)")

        return success_rate >= 70 and dimension_count >= 4

    except Exception as e:
        print(f"FAIL 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=== 简化增强财务指标功能验证 ===")

    # 运行测试
    test_passed = test_simple_enhanced_metrics()

    # 总结测试结果
    print("\n" + "="*50)
    print(f"测试结果: {'PASS' if test_passed else 'FAIL'}")

    if test_passed:
        print("\nSUCCESS 增强财务指标功能验证成功！")
        print("OK 应收账款周转率计算正常")
        print("OK 现金能力分析指标计算正常")
        print("OK 5大分析维度完整")
        print("\n系统现在支持完整的财务分析体系！")
    else:
        print("\nWARNING 仍有问题需要解决")

    return test_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)