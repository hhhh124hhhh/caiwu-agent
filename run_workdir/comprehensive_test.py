import json
import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.append(r'f:\person\3-数字化集锦\caiwu-agent')

from utu.tools.tabular_data_toolkit import TabularDataToolkit
from utu.config import ToolkitConfig

def test_time_validation():
    """测试时间验证功能"""
    # 创建工具实例
    config = ToolkitConfig()
    toolkit = TabularDataToolkit(config)
    
    # 获取当前时间
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    print(f"当前时间: {current_year}年{current_month}月")
    
    # 测试数据1: 包含未来时间的数据
    future_data = {
        "trend": [
            {"年份": "2024中期", "营业收入": 8202.83, "净利润": 224.61},
            {"年份": "2024年度", "营业收入": 11603.11, "净利润": 307.58},
            {"年份": f"{current_year}中期", "营业收入": 2492.83, "净利润": 65.59},
            {"年份": f"{current_year}三季度", "营业收入": 5125.02, "净利润": 131.42}  # 这个应该是未来的数据
        ]
    }
    
    print("\n测试1: 包含未来时间的数据")
    result1 = toolkit.generate_charts(json.dumps(future_data), chart_type="line", output_dir="./run_workdir")
    print(f"结果: {result1}")
    
    # 测试数据2: 正常时间范围的数据
    normal_data = {
        "trend": [
            {"年份": "2023年度", "营业收入": 8202.83, "净利润": 224.61, "毛利率": 15.2},
            {"年份": "2024中期", "营业收入": 4500.00, "净利润": 120.00, "毛利率": 14.8},
            {"年份": "2024年度", "营业收入": 11603.11, "净利润": 307.58, "毛利率": 15.0}
        ]
    }
    
    print("\n测试2: 正常时间范围的数据")
    result2 = toolkit.generate_charts(json.dumps(normal_data), chart_type="line", output_dir="./run_workdir")
    print(f"结果: {result2}")
    
    # 测试数据3: 包含异常财务数据
    abnormal_data = {
        "trend": [
            {"年份": "2023年度", "营业收入": 8202.83, "净利润": 224.61, "毛利率": 100.0},  # 异常毛利率
            {"年份": "2024年度", "营业收入": 11603.11, "净利润": 307.58, "毛利率": 15.0}
        ]
    }
    
    print("\n测试3: 包含异常财务数据")
    result3 = toolkit.generate_charts(json.dumps(abnormal_data), chart_type="bar", output_dir="./run_workdir")
    print(f"结果: {result3}")

if __name__ == "__main__":
    test_time_validation()