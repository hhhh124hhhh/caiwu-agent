import json
import sys
import os

# 添加项目路径
sys.path.append(r'f:\person\3-数字化集锦\caiwu-agent')

from utu.tools.tabular_data_toolkit import TabularDataToolkit
from utu.config import ToolkitConfig

def test_chart_generation():
    """测试图表生成功能"""
    # 创建工具实例
    config = ToolkitConfig()
    toolkit = TabularDataToolkit(config)
    
    # 测试数据 - 包含异常数据
    test_data = {
        "trend": [
            {"年份": "2024中期", "营业收入": 8202.83, "净利润": 224.61},
            {"年份": "2024年度", "营业收入": 11603.11, "净利润": 307.58},
            {"年份": "2025中期", "营业收入": 2492.83, "净利润": 65.59},
            {"年份": "2025三季度", "营业收入": 5125.02, "净利润": 131.42}  # 这个应该是未来的数据
        ]
    }
    
    # 正常数据
    normal_data = {
        "trend": [
            {"年份": "2023年度", "营业收入": 8202.83, "净利润": 224.61, "毛利率": 15.2},
            {"年份": "2024中期", "营业收入": 4500.00, "净利润": 120.00, "毛利率": 14.8},
            {"年份": "2024年度", "营业收入": 11603.11, "净利润": 307.58, "毛利率": 15.0}
        ]
    }
    
    print("测试1: 包含未来时间的数据")
    result1 = toolkit.generate_charts(json.dumps(test_data), chart_type="line")
    print(f"结果: {result1}")
    
    print("\n测试2: 正常时间范围的数据")
    result2 = toolkit.generate_charts(json.dumps(normal_data), chart_type="line")
    print(f"结果: {result2}")
    
    # 测试异常财务数据
    abnormal_data = {
        "trend": [
            {"年份": "2023年度", "营业收入": 8202.83, "净利润": 224.61, "毛利率": 100.0},  # 异常毛利率
            {"年份": "2024年度", "营业收入": 11603.11, "净利润": 307.58, "毛利率": 15.0}
        ]
    }
    
    print("\n测试3: 包含异常财务数据")
    result3 = toolkit.generate_charts(json.dumps(abnormal_data), chart_type="bar")
    print(f"结果: {result3}")

if __name__ == "__main__":
    test_chart_generation()