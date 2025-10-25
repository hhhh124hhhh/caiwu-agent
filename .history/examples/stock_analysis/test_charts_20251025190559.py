#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
图表生成测试脚本
"""

import sys
sys.path.append('d:\\caiwu-agent')

from utu.tools.tabular_data_toolkit import TabularDataToolkit
import os


def test_chart_generation():
    """测试图表生成功能"""
    print("开始测试图表生成功能...")
    
    # 创建图表工具实例
    toolkit = TabularDataToolkit()
    
    # 确保输出目录存在
    output_dir = './run_workdir'
    os.makedirs(output_dir, exist_ok=True)
    
    # 测试1: 盈利能力柱状图
    print("\n测试1: 生成盈利能力柱状图...")
    data1 = {
        "title": "陕西建工盈利能力指标",
        "x_axis": ["毛利率", "净利率", "ROE", "ROA"],
        "series": [{"name": "数值(%)", "data": [12.0, 1.92, 2.82, 0.32]}]
    }
    
    response1 = toolkit.generate_charts(
        data_json=data1,
        chart_type='bar',
        output_dir=output_dir
    )
    print(f"盈利能力图表生成结果: {response1}")
    
    # 测试2: 偿债能力柱状图
    print("\n测试2: 生成偿债能力柱状图...")
    data2 = {
        "title": "陕西建工偿债能力指标",
        "x_axis": ["资产负债率", "流动比率", "速动比率"],
        "series": [{"name": "数值", "data": [78.5, 1.23, 0.95]}]
    }
    
    response2 = toolkit.generate_charts(
        data_json=data2,
        chart_type='bar',
        output_dir=output_dir
    )
    print(f"偿债能力图表生成结果: {response2}")
    
    # 测试3: 财务健康雷达图
    print("\n测试3: 生成财务健康雷达图（使用公司对比格式）...")
    # 雷达图需要使用公司对比格式
    data3 = {
        "companies": ["陕西建工"],
        "profit_margin": [1.92],  # 净利率
        "roe": [2.82],
        "debt_ratio": [78.5],  # 资产负债率
        "current_ratio": [1.23],
        "asset_turnover": [0.42]  # 资产周转率
    }
    
    response3 = toolkit.generate_charts(
        data_json=data3,
        chart_type='radar',
        output_dir=output_dir
    )
    print(f"财务健康雷达图生成结果: {response3}")
    
    # 测试4: 趋势图
    print("\n测试4: 生成盈利能力趋势图...")
    data4 = {
        "title": "陕西建工盈利能力趋势",
        "x_axis": ["2020年", "2021年", "2022年", "2023年", "2024年"],
        "series": [
            {"name": "毛利率(%)", "data": [11.5, 12.2, 11.8, 12.0, 12.0]},
            {"name": "净利率(%)", "data": [2.1, 2.05, 1.98, 1.95, 1.92]}
        ]
    }
    
    response4 = toolkit.generate_charts(
        data_json=data4,
        chart_type='line',
        output_dir=output_dir
    )
    print(f"盈利能力趋势图生成结果: {response4}")
    
    print("\n图表生成测试完成！")


if __name__ == "__main__":
    test_chart_generation()