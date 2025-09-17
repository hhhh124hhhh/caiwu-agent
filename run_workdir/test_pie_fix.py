import json
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the TabularDataToolkit
from utu.tools.tabular_data_toolkit import TabularDataToolkit

# 测试数据 - 分布数据（用于饼图）
distribution_data = {
    "利润率分布": [
        {"利润率区间": "40%+", "公司数量": 1},
        {"利润率区间": "30-40%", "公司数量": 1},
        {"利润率区间": "20-30%", "公司数量": 1}
    ]
}

def test_pie_fix():
    print("=== 测试饼图修复 ===")
    
    # 创建TabularDataToolkit实例
    toolkit = TabularDataToolkit()
    
    print("测试饼图生成...")
    try:
        result = toolkit.generate_charts(
            data_json=json.dumps(distribution_data, ensure_ascii=False),
            chart_type="pie",
            output_dir="./run_workdir"
        )
        print(f"结果: {result}")
        
        if result.get("chart_files"):
            print(f"生成的图表文件: {result['chart_files']}")
        else:
            print("未生成图表文件")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pie_fix()