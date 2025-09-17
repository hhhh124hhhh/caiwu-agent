import json
import sys
import os
import glob

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utu.tools.tabular_data_toolkit import TabularDataToolkit
from utu.config import ToolkitConfig

# 创建更复杂的测试数据，包含时间序列数据
test_data = {
    "company_name": "测试公司",
    "analysis_period": "2020-2024",
    "trend_data": [
        {"year": 2020, "revenue": 800000, "net_profit": 150000, "total_assets": 4000000},
        {"year": 2021, "revenue": 850000, "net_profit": 160000, "total_assets": 4200000},
        {"year": 2022, "revenue": 900000, "net_profit": 180000, "total_assets": 4500000},
        {"year": 2023, "revenue": 950000, "net_profit": 190000, "total_assets": 4800000},
        {"year": 2024, "revenue": 1000000, "net_profit": 200000, "total_assets": 5000000}
    ],
    "ratios_data": {
        "profitability": {
            "gross_margin": 0.35,
            "net_margin": 0.20,
            "roe": 0.12
        },
        "solvency": {
            "debt_ratio": 0.60,
            "current_ratio": 1.8
        }
    },
    "companies": ["公司A", "公司B", "公司C"],
    "revenue": [1000000, 1200000, 800000],
    "net_profit": [200000, 250000, 150000],
    "roe": [0.12, 0.15, 0.10]
}

# 转换为JSON字符串
test_data_json = json.dumps(test_data)

# 初始化工具包
config = ToolkitConfig()
toolkit = TabularDataToolkit(config)

# 图表类型列表
chart_types = ["bar", "line", "pie", "scatter", "heatmap", "radar", "boxplot", "area", "waterfall"]

print("开始全面测试所有图表类型...")
print(f"测试数据: {test_data}")

# 记录测试前的文件
before_files = set(glob.glob("./run_workdir/*.png"))

# 测试每种图表类型
for chart_type in chart_types:
    print(f"\n测试 {chart_type} 图表...")
    try:
        result = toolkit.generate_charts(test_data_json, chart_type=chart_type, output_dir="./run_workdir")
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

print("\n全面测试完成!")