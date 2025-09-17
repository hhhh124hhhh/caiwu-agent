import json
import sys
import os
import glob

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utu.tools.tabular_data_toolkit import TabularDataToolkit
from utu.config import ToolkitConfig

# 创建测试数据
test_data = {
    'revenue': 1000000,
    'net_profit': 200000,
    'total_assets': 5000000,
    'total_liabilities': 3000000,
    'equity': 2000000,
    'roe': 0.1,
    'roa': 0.04,
    'debt_ratio': 0.6,
    'net_margin': 0.2
}

# 转换为JSON字符串
test_data_json = json.dumps(test_data)

# 初始化工具包
config = ToolkitConfig()
toolkit = TabularDataToolkit(config)

# 图表类型列表
chart_types = ["bar", "line", "pie", "scatter", "heatmap", "radar", "boxplot", "area", "waterfall"]

print("开始测试所有图表类型...")
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

print("\n测试完成!")