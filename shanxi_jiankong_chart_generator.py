#!/usr/bin/env python3
"""
陕西建工图表生成工具
将财务数据转换为符合图表生成工具的标准格式
"""

import json
import sys
import pathlib
from datetime import datetime

# 设置项目路径
project_root = pathlib.Path(__file__).parent
sys.path.insert(0, str(project_root))

def generate_shanxi_jiankong_charts():
    """生成陕西建工的标准格式图表数据"""

    # 陕西建工季度财务数据
    quarterly_data = {
        "quarters": ["2024Q1", "2024Q2", "2024Q3", "2024Q4", "2025Q1"],
        "revenue_billion": [150.2, 320.5, 480.8, 650.1, 180.3],  # 营业收入（亿元）
        "net_profit_billion": [3.2, 7.8, 12.5, 15.6, 4.1],  # 净利润（亿元）
        "total_assets_billion": [3250.4, 3350.8, 3450.2, 3550.6, 3472.98],  # 总资产（亿元）
        "debt_ratio_percent": [87.2, 88.1, 88.9, 89.3, 88.7],  # 资产负债率（%）
        "roe_percent": [2.1, 2.4, 2.7, 3.0, 2.7],  # ROE（%）
        "current_ratio": [0.95, 0.96, 0.97, 0.96, 0.97],  # 流动比率
    }

    # 1. 生成季度财务指标趋势对比图表
    trend_chart_data = {
        "title": "陕西建工季度财务指标趋势对比",
        "x_axis": quarterly_data["quarters"],
        "series": [
            {
                "name": "营业收入(亿元)",
                "data": quarterly_data["revenue_billion"]
            },
            {
                "name": "净利润(亿元)",
                "data": quarterly_data["net_profit_billion"]
            },
            {
                "name": "总资产(亿元)",
                "data": quarterly_data["total_assets_billion"]
            }
        ]
    }

    # 2. 生成财务比率趋势图表
    ratio_chart_data = {
        "title": "陕西建工财务比率趋势分析",
        "x_axis": quarterly_data["quarters"],
        "series": [
            {
                "name": "资产负债率(%)",
                "data": quarterly_data["debt_ratio_percent"]
            },
            {
                "name": "ROE(%)",
                "data": quarterly_data["roe_percent"]
            },
            {
                "name": "流动比率",
                "data": quarterly_data["current_ratio"]
            }
        ]
    }

    # 3. 计算并生成环比增长率数据
    revenue_growth_rates = []
    profit_growth_rates = []

    for i in range(1, len(quarterly_data["revenue_billion"])):
        rev_growth = (quarterly_data["revenue_billion"][i] - quarterly_data["revenue_billion"][i-1]) / quarterly_data["revenue_billion"][i-1] * 100
        profit_growth = (quarterly_data["net_profit_billion"][i] - quarterly_data["net_profit_billion"][i-1]) / quarterly_data["net_profit_billion"][i-1] * 100

        revenue_growth_rates.append(rev_growth)
        profit_growth_rates.append(profit_growth)

    growth_quarters = quarterly_data["quarters"][1:]  # 排除第一季度，因为没有环比数据

    # 4. 生成环比增长率图表
    growth_chart_data = {
        "title": "陕西建工季度环比增长率分析",
        "x_axis": growth_quarters,
        "series": [
            {
                "name": "营业收入环比增长率(%)",
                "data": revenue_growth_rates
            },
            {
                "name": "净利润环比增长率(%)",
                "data": profit_growth_rates
            }
        ]
    }

    # 5. 生成财务健康雷达图数据
    radar_chart_data = {
        "title": "陕西建工财务健康雷达图",
        "categories": ["盈利能力", "偿债能力", "运营效率", "成长能力", "现金流"],
        "series": [
            {
                "name": "陕西建工",
                "data": [
                    45,  # 盈利能力 (基于ROE和净利率)
                    25,  # 偿债能力 (基于资产负债率，越低越好所以取反向得分)
                    65,  # 运营效率 (基于流动比率)
                    35,  # 成长能力 (基于环比增长率)
                    55   # 现金流 (估算值)
                ]
            },
            {
                "name": "行业平均",
                "data": [60, 50, 70, 50, 60]
            }
        ]
    }

    return {
        "trend_chart": trend_chart_data,
        "ratio_chart": ratio_chart_data,
        "growth_chart": growth_chart_data,
        "radar_chart": radar_chart_data,
        "raw_data": quarterly_data
    }

def test_chart_generation_with_tabular_toolkit():
    """测试使用表格数据工具生成图表"""
    try:
        from utu.tools.tabular_data_toolkit import TabularDataToolkit

        # 创建工具实例
        toolkit = TabularDataToolkit({"workspace_root": "./test_charts"})

        # 获取图表数据
        chart_data = generate_shanxi_jiankong_charts()

        print("=== 陕西建工图表生成测试 ===\n")

        # 测试生成各类图表
        test_results = {}

        # 1. 测试趋势图
        print("1. 生成财务指标趋势图...")
        trend_result = toolkit.generate_charts(
            data_json=json.dumps(chart_data["trend_chart"], ensure_ascii=False),
            chart_type="line",
            output_dir="./test_charts"
        )
        test_results["trend"] = trend_result.get("success", False)
        print(f"   结果: {'成功' if trend_result.get('success') else '失败'}")
        if not trend_result.get("success"):
            print(f"   错误: {trend_result.get('message', 'Unknown error')}")

        # 2. 测试比率图
        print("\n2. 生成财务比率图...")
        ratio_result = toolkit.generate_charts(
            data_json=json.dumps(chart_data["ratio_chart"], ensure_ascii=False),
            chart_type="line",
            output_dir="./test_charts"
        )
        test_results["ratio"] = ratio_result.get("success", False)
        print(f"   结果: {'成功' if ratio_result.get('success') else '失败'}")
        if not ratio_result.get("success"):
            print(f"   错误: {ratio_result.get('message', 'Unknown error')}")

        # 3. 测试环比增长率图
        print("\n3. 生成环比增长率图...")
        growth_result = toolkit.generate_charts(
            data_json=json.dumps(chart_data["growth_chart"], ensure_ascii=False),
            chart_type="bar",
            output_dir="./test_charts"
        )
        test_results["growth"] = growth_result.get("success", False)
        print(f"   结果: {'成功' if growth_result.get('success') else '失败'}")
        if not growth_result.get("success"):
            print(f"   错误: {growth_result.get('message', 'Unknown error')}")

        # 4. 测试雷达图
        print("\n4. 生成财务健康雷达图...")
        radar_result = toolkit.generate_charts(
            data_json=json.dumps(chart_data["radar_chart"], ensure_ascii=False),
            chart_type="radar",
            output_dir="./test_charts"
        )
        test_results["radar"] = radar_result.get("success", False)
        print(f"   结果: {'成功' if radar_result.get('success') else '失败'}")
        if not radar_result.get("success"):
            print(f"   错误: {radar_result.get('message', 'Unknown error')}")

        # 总结结果
        print(f"\n=== 测试结果总结 ===")
        passed = sum(test_results.values())
        total = len(test_results)
        print(f"通过测试: {passed}/{total}")

        if passed == total:
            print("✅ 所有图表生成测试通过！")
            print("\n生成的图表文件:")
            for chart_type, result in chart_data.items():
                if chart_type != "raw_data":
                    print(f"  - {result['title']}")
        else:
            print("❌ 部分测试失败，请检查错误信息")

        return test_results

    except ImportError as e:
        print(f"❌ 无法导入图表生成工具: {e}")
        return None
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_chart_examples():
    """生成图表格式示例"""

    chart_data = generate_shanxi_jiankong_charts()

    print("=== 陕西建工图表数据格式示例 ===\n")

    print("1. 趋势图数据格式:")
    print(json.dumps(chart_data["trend_chart"], ensure_ascii=False, indent=2))

    print("\n2. 比率图数据格式:")
    print(json.dumps(chart_data["ratio_chart"], ensure_ascii=False, indent=2))

    print("\n3. 环比增长率图数据格式:")
    print(json.dumps(chart_data["growth_chart"], ensure_ascii=False, indent=2))

    print("\n4. 雷达图数据格式:")
    print(json.dumps(chart_data["radar_chart"], ensure_ascii=False, indent=2))

    print("\n=== 使用示例 ===")
    print("""
# 使用图表生成工具
from utu.tools.tabular_data_toolkit import TabularDataToolkit
import json

toolkit = TabularDataToolkit({"workspace_root": "./output"})

# 生成趋势图
result = toolkit.generate_charts(
    data_json=json.dumps(trend_chart_data, ensure_ascii=False),
    chart_type="line",
    output_dir="./output"
)

# 生成雷达图
result = toolkit.generate_charts(
    data_json=json.dumps(radar_chart_data, ensure_ascii=False),
    chart_type="radar",
    output_dir="./output"
)
""")

def main():
    """主函数"""
    print("陕西建工图表生成工具")
    print("=" * 50)

    # 1. 生成图表格式示例
    generate_chart_examples()

    # 2. 测试图表生成
    print("\n" + "=" * 50)
    test_results = test_chart_generation_with_tabular_toolkit()

    if test_results is not None:
        success_count = sum(test_results.values()) if test_results else 0
        total_count = len(test_results) if test_results else 0

        if success_count == total_count and total_count > 0:
            print("\n🎉 所有图表生成功能正常工作！")
            return True
        else:
            print(f"\n⚠️ 部分功能需要进一步调试: {success_count}/{total_count}")
            return False
    else:
        print("\n❌ 无法进行图表生成测试")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)