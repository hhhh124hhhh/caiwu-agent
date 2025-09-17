import json
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the TabularDataToolkit
from utu.tools.tabular_data_toolkit import TabularDataToolkit

# 测试数据 - 公司对比数据（用于柱状图）
company_comparison_data = {
    "公司对比": [
        {
            "名称": "药明康德",
            "净利润率": 41.64,
            "营收": 207.99
        },
        {
            "名称": "迈瑞医疗",
            "净利润率": 31.25,
            "营收": 167.43
        },
        {
            "名称": "恒瑞医药",
            "净利润率": 28.26,
            "营收": 157.61
        }
    ]
}

# 测试数据 - 趋势数据（用于折线图）
trend_data = {
    "趋势数据": [
        {
            "年份": "2021",
            "营收": 150.32,
            "净利润": 65.42
        },
        {
            "年份": "2022",
            "营收": 175.43,
            "净利润": 72.34
        },
        {
            "年份": "2023",
            "营收": 200.12,
            "净利润": 80.56
        },
        {
            "年份": "2024",
            "营收": 220.78,
            "净利润": 88.91
        },
        {
            "年份": "2025",
            "营收": 250.65,
            "净利润": 95.32
        }
    ]
}

def test_fix():
    # 创建TabularDataToolkit实例
    toolkit = TabularDataToolkit()
    
    print("=== 测试公司对比数据处理 ===")
    try:
        flattened_data = toolkit._flatten_financial_data(company_comparison_data)
        print(f"扁平化后的数据: {flattened_data}")
        
        # 检查是否有数据
        if flattened_data:
            print("数据处理成功!")
        else:
            print("数据处理失败，没有生成有效数据")
    except Exception as e:
        print(f"处理失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== 测试趋势数据处理 ===")
    try:
        flattened_data = toolkit._flatten_financial_data(trend_data)
        print(f"扁平化后的数据: {flattened_data}")
        
        # 检查是否有数据
        if flattened_data:
            print("数据处理成功!")
        else:
            print("数据处理失败，没有生成有效数据")
    except Exception as e:
        print(f"处理失败: {e}")
        import traceback
        traceback.print_exc()

# 运行测试
if __name__ == "__main__":
    test_fix()