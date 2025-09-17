import json
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the TabularDataToolkit
from utu.tools.tabular_data_toolkit import TabularDataToolkit
import numpy as np

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

def debug_chart_generation():
    # 创建TabularDataToolkit实例
    toolkit = TabularDataToolkit()
    
    print("=== 调试柱状图数据处理 ===")
    try:
        json_data = json.dumps(company_comparison_data, ensure_ascii=False)
        print(f"输入数据: {json_data}")
        
        # 直接调用数据处理函数来查看中间结果
        data = json.loads(json_data)
        print(f"解析后的数据: {data}")
        
        # 检查数据扁平化过程
        if isinstance(data, list):
            flattened_data = toolkit._flatten_financial_list_data(data)
        else:
            flattened_data = toolkit._flatten_financial_data(data)
        
        print(f"扁平化后的数据: {flattened_data}")
        
        # 检查过滤后的数据
        filtered_data = {}
        for key, value in flattened_data.items():
            if isinstance(value, (int, float)) and not (np.isnan(value) or np.isinf(value)):
                if '毛利率' in key and value <= 100 and value >= 0:
                    filtered_data[key] = value
                elif '净利率' in key and value <= 100 and value >= -100:
                    filtered_data[key] = value
                elif '资产负债率' in key and value <= 100 and value >= 0:
                    filtered_data[key] = value
                elif 'ROE' in key and abs(value) <= 100:
                    filtered_data[key] = value
                elif not any(keyword in key for keyword in ['毛利率', '净利率', '资产负债率', 'ROE']):
                    filtered_data[key] = value
        
        print(f"过滤后的数据: {filtered_data}")
        
        # 检查最终用于图表的数据
        keys = list(filtered_data.keys())
        values = list(filtered_data.values())
        print(f"图表键: {keys}")
        print(f"图表值: {values}")
        
    except Exception as e:
        print(f"调试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== 调试折线图数据处理 ===")
    try:
        json_data = json.dumps(trend_data, ensure_ascii=False)
        print(f"输入数据: {json_data}")
        
        # 直接调用数据处理函数来查看中间结果
        data = json.loads(json_data)
        print(f"解析后的数据: {data}")
        
        # 检查数据扁平化过程
        if isinstance(data, list):
            flattened_data = toolkit._flatten_financial_list_data(data)
        else:
            flattened_data = toolkit._flatten_financial_data(data)
        
        print(f"扁平化后的数据: {flattened_data}")
        
        # 检查过滤后的数据
        filtered_data = {}
        for key, value in flattened_data.items():
            if isinstance(value, (int, float)) and not (np.isnan(value) or np.isinf(value)):
                if '毛利率' in key and value <= 100 and value >= 0:
                    filtered_data[key] = value
                elif '净利率' in key and value <= 100 and value >= -100:
                    filtered_data[key] = value
                elif '资产负债率' in key and value <= 100 and value >= 0:
                    filtered_data[key] = value
                elif 'ROE' in key and abs(value) <= 100:
                    filtered_data[key] = value
                elif not any(keyword in key for keyword in ['毛利率', '净利率', '资产负债率', 'ROE']):
                    filtered_data[key] = value
        
        print(f"过滤后的数据: {filtered_data}")
        
        # 检查最终用于图表的数据
        keys = list(filtered_data.keys())
        values = list(filtered_data.values())
        print(f"图表键: {keys}")
        print(f"图表值: {values}")
        
    except Exception as e:
        print(f"调试失败: {e}")
        import traceback
        traceback.print_exc()

# 运行调试
if __name__ == "__main__":
    debug_chart_generation()