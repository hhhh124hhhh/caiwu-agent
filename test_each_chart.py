import json
import sys
import os
import glob

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utu.tools.tabular_data_toolkit import TabularDataToolkit
from utu.config import ToolkitConfig

# 为每种图表类型创建专门的测试数据
chart_tests = {
    "bar": {"revenue": 1000000, "net_profit": 200000, "assets": 5000000},
    "line": {"2020_revenue": 800000, "2021_revenue": 850000, "2022_revenue": 900000, "2023_revenue": 950000, "2024_revenue": 1000000},
    "pie": {"product_a": 400000, "product_b": 300000, "product_c": 200000, "product_d": 100000},
    "scatter": {"revenue": 1000000, "profit": 200000, "assets": 5000000, "liabilities": 3000000},
    "heatmap": {"Q1_revenue": 250000, "Q2_revenue": 250000, "Q3_revenue": 250000, "Q4_revenue": 250000, "Q1_profit": 50000, "Q2_profit": 50000, "Q3_profit": 50000, "Q4_profit": 50000},
    "radar": {"profitability": 0.8, "solvency": 0.7, "efficiency": 0.6, "growth": 0.75, "market_share": 0.65},
    "boxplot": {"jan": 100000, "feb": 120000, "mar": 110000, "apr": 130000, "may": 125000, "jun": 135000, "jul": 140000, "aug": 138000, "sep": 142000, "oct": 145000, "nov": 148000, "dec": 150000},
    "area": {"Q1": 250000, "Q2": 500000, "Q3": 750000, "Q4": 1000000},
    "waterfall": {"starting_value": 1000000, "revenue": 500000, "expenses": -300000, "taxes": -50000, "net_income": 150000}
}

# 初始化工具包
config = ToolkitConfig()
toolkit = TabularDataToolkit(config)

print("开始逐个测试图表类型...")

# 记录测试前的文件
before_files = set(glob.glob("./run_workdir/*.png"))

# 测试每种图表类型
for chart_type, data in chart_tests.items():
    print(f"\n测试 {chart_type} 图表...")
    try:
        data_json = json.dumps(data)
        result = toolkit.generate_charts(data_json, chart_type=chart_type, output_dir="./run_workdir")
        if result["success"]:
            print(f"✓ {chart_type} 图表生成成功: {result['chart_files']}")
        else:
            print(f"✗ {chart_type} 图表生成失败: {result.get('error', '未知错误')}")
    except Exception as e:
        print(f"✗ {chart_type} 图表生成异常: {str(e)}")

# 显示新增的文件
after_files = set(glob.glob("./run_workdir/*.png"))
new_files = after_files - before_files
print(f"\n新增的图表文件: {new_files}")

print("\n逐个测试完成!")