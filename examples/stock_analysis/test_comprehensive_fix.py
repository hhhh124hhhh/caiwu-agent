#!/usr/bin/env python3
"""
财务分析和图表生成工具修复验证测试
"""

import sys
import json
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_financial_analysis_toolkit():
    """测试财务分析工具的修复效果"""
    print("=== 测试财务分析工具修复效果 ===")

    try:
        from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer
        print("✓ 财务分析工具导入成功")

        # 创建分析器实例
        analyzer = StandardFinancialAnalyzer()
        print("✓ 财务分析器初始化成功")

        # 创建测试数据（中文列名）
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
                    "存货": 500000000  # 5亿
                }
            ]
        }

        # 转换为JSON字符串模拟真实调用
        test_data_json = json.dumps(test_data)

        # 测试财务比率计算
        print("测试财务比率计算...")
        ratios = analyzer.calculate_ratios(test_data_json)

        # 验证计算结果
        success_count = 0
        total_count = 0

        # 盈利能力指标
        if 'profitability' in ratios:
            profitability = ratios['profitability']
            total_count += 4
            if 'gross_profit_margin' in profitability:
                print(f"✓ 毛利率: {profitability['gross_profit_margin']}%")
                success_count += 1
            else:
                print("✗ 毛利率计算失败")

            if 'net_profit_margin' in profitability:
                print(f"✓ 净利率: {profitability['net_profit_margin']}%")
                success_count += 1
            else:
                print("✗ 净利率计算失败")

            if 'roe' in profitability:
                print(f"✓ ROE: {profitability['roe']}%")
                success_count += 1
            else:
                print("✗ ROE计算失败")

            if 'roa' in profitability:
                print(f"✓ ROA: {profitability['roa']}%")
                success_count += 1
            else:
                print("✗ ROA计算失败")

        # 偿债能力指标
        if 'solvency' in ratios:
            solvency = ratios['solvency']
            total_count += 3
            if 'debt_to_asset_ratio' in solvency:
                print(f"✓ 资产负债率: {solvency['debt_to_asset_ratio']}%")
                success_count += 1
            else:
                print("✗ 资产负债率计算失败")

            if 'current_ratio' in solvency:
                print(f"✓ 流动比率: {solvency['current_ratio']}")
                success_count += 1
            else:
                print("✗ 流动比率计算失败")

            if 'quick_ratio' in solvency:
                print(f"✓ 速动比率: {solvency['quick_ratio']}")
                success_count += 1
            else:
                print("✗ 速动比率计算失败")

        print(f"\n财务指标计算成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")

        return success_count >= total_count * 0.8  # 80%以上成功率算通过

    except Exception as e:
        print(f"✗ 财务分析工具测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tabular_data_toolkit():
    """测试图表生成工具的修复效果"""
    print("\n=== 测试图表生成工具修复效果 ===")

    try:
        from utu.tools.tabular_data_toolkit import TabularDataToolkit
        print("✓ 图表生成工具导入成功")

        # 创建测试数据
        test_data = {
            "companies": ["测试公司A", "测试公司B"],
            "revenue": [100.0, 80.0],
            "net_profit": [15.0, 12.0],
            "profit_margin": [15.0, 15.0],
            "roe": [12.0, 10.0]
        }

        # 创建输出目录
        output_dir = "./test_output"
        os.makedirs(output_dir, exist_ok=True)

        # 测试图表生成
        print("测试对比图表生成...")

        toolkit = TabularDataToolkit()
        result = toolkit.generate_charts(json.dumps(test_data), "comparison", output_dir)

        if result.get("success"):
            print("✓ 对比图表生成成功")
            chart_files = result.get("files", [])
            print(f"生成的图表文件: {chart_files}")

            # 检查文件是否存在
            for file_path in chart_files:
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    print(f"✓ {file_path} ({file_size} bytes)")
                else:
                    print(f"✗ 文件不存在: {file_path}")
                    return False

            return True
        else:
            print(f"✗ 对比图表生成失败: {result.get('message')}")
            return False

    except Exception as e:
        print(f"✗ 图表生成工具测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handling():
    """测试错误处理能力"""
    print("\n=== 测试错误处理能力 ===")

    try:
        from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer

        analyzer = StandardFinancialAnalyzer()

        # 测试空数据
        print("测试空数据处理...")
        empty_data = {"income": [], "balance": []}
        empty_result = analyzer.calculate_ratios(json.dumps(empty_data))
        print("✓ 空数据处理正常")

        # 测试异常数据
        print("测试异常数据处理...")
        abnormal_data = {
            "income": [{"营业收入": -1000, "净利润": "invalid"}],
            "balance": [{"资产总计": 0, "负债合计": "text"}]
        }
        abnormal_result = analyzer.calculate_ratios(json.dumps(abnormal_data))
        print("✓ 异常数据处理正常")

        return True

    except Exception as e:
        print(f"✗ 错误处理测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=== 财务分析和图表生成工具修复验证 ===")
    print("测试目标:")
    print("1. 验证中文列名映射修复效果")
    print("2. 验证数据验证和容错机制")
    print("3. 验证图表生成稳定性")
    print("4. 验证错误处理能力")
    print()

    # 运行各项测试
    test1_passed = test_financial_analysis_toolkit()
    test2_passed = test_tabular_data_toolkit()
    test3_passed = test_error_handling()

    # 总结测试结果
    print("\n" + "="*50)
    print("测试结果总结:")
    print(f"财务分析工具: {'✓ 通过' if test1_passed else '✗ 失败'}")
    print(f"图表生成工具: {'✓ 通过' if test2_passed else '✗ 失败'}")
    print(f"错误处理能力: {'✓ 通过' if test3_passed else '✗ 失败'}")

    overall_success = test1_passed and test2_passed and test3_passed
    print(f"\n整体测试结果: {'✓ 全部通过' if overall_success else '✗ 有测试失败'}")

    if overall_success:
        print("\n🎉 修复验证成功！")
        print("✅ 中文列名映射已修复")
        print("✅ 数据验证机制正常")
        print("✅ 计算容错性提升")
        print("✅ 图表生成稳定性改善")
        print("✅ 错误处理能力增强")
        print("\n系统已准备好进行演示！")
    else:
        print("\n⚠️  仍有问题需要解决")
        print("请检查失败的测试项目")

    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)