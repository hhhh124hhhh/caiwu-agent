import json
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utu.tools.tabular_data_toolkit import TabularDataToolkit

# 测试数据 - 公司对比数据
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
        },
        {
            "名称": "片仔癀",
            "净利润率": 26.92,
            "营收": 53.79
        },
        {
            "名称": "云南白药",
            "净利润率": 17.15,
            "营收": 212.57
        }
    ]
}

# 测试数据 - 利润率分布数据
profit_margin_distribution = {
    "利润率分布": [
        {
            "利润率区间": "40%+",
            "公司数量": 1
        },
        {
            "利润率区间": "30-40%",
            "公司数量": 2
        },
        {
            "利润率区间": "20-30%",
            "公司数量": 1
        },
        {
            "利润率区间": "10-20%",
            "公司数量": 1
        }
    ]
}

# 创建TabularDataToolkit实例
toolkit = TabularDataToolkit()

# 测试柱状图生成
print("测试生成柱状图...")
try:
    json_data = json.dumps(company_comparison_data, ensure_ascii=False)
    result = toolkit.generate_charts(
        data_json=json_data,
        chart_type="bar",
        output_dir="./run_workdir"
    )
    print(f"柱状图生成结果: {result}")
except Exception as e:
    print(f"柱状图生成失败: {e}")

# 测试饼图生成
print("\n测试生成饼图...")
try:
    json_data = json.dumps(profit_margin_distribution, ensure_ascii=False)
    result = toolkit.generate_charts(
        data_json=json_data,
        chart_type="pie",
        output_dir="./run_workdir"
    )
    print(f"饼图生成结果: {result}")
    
    if result["chart_files"]:
        print(f"生成的图表文件: {result['chart_files']}")
    else:
        print("未生成图表文件")
except Exception as e:
    print(f"饼图生成失败: {e}")