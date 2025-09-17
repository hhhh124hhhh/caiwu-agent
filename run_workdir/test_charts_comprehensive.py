import json
import sys
import os
import asyncio

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

# 测试数据 - 分布数据（用于饼图）
distribution_data = {
    "利润率分布": [
        {
            "利润率区间": "40%+",
            "公司数量": 1
        },
        {
            "利润率区间": "30-40%",
            "公司数量": 1
        },
        {
            "利润率区间": "20-30%",
            "公司数量": 1
        }
    ]
}

async def test_charts():
    # 创建TabularDataToolkit实例
    toolkit = TabularDataToolkit()
    
    print("=== 测试柱状图生成 ===")
    try:
        json_data = json.dumps(company_comparison_data, ensure_ascii=False)
        print(f"输入数据: {json_data[:100]}...")
        
        result = toolkit.generate_charts(
            data_json=json_data,
            chart_type="bar",
            output_dir="./run_workdir"
        )
        print(f"柱状图生成结果: {result}")
    except Exception as e:
        print(f"柱状图生成失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== 测试折线图生成 ===")
    try:
        json_data = json.dumps(trend_data, ensure_ascii=False)
        print(f"输入数据: {json_data[:100]}...")
        
        result = toolkit.generate_charts(
            data_json=json_data,
            chart_type="line",
            output_dir="./run_workdir"
        )
        print(f"折线图生成结果: {result}")
    except Exception as e:
        print(f"折线图生成失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== 测试饼图生成 ===")
    try:
        json_data = json.dumps(distribution_data, ensure_ascii=False)
        print(f"输入数据: {json_data[:100]}...")
        
        result = toolkit.generate_charts(
            data_json=json_data,
            chart_type="pie",
            output_dir="./run_workdir"
        )
        print(f"饼图生成结果: {result}")
    except Exception as e:
        print(f"饼图生成失败: {e}")
        import traceback
        traceback.print_exc()

# 运行测试
if __name__ == "__main__":
    asyncio.run(test_charts())