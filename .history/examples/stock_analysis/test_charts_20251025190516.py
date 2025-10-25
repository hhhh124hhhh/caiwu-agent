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
    
    # 测试3: 资产结构饼图
    print("\n测试3: 生成资产结构饼图...")
    data3 = {
        "title": "陕西建工资产结构分析",
        "x_axis": ["流动资产", "非流动资产"],
        "series": [{"name": "资产结构", "data": [2800.45, 672.53]}]
    }
    
    response3 = toolkit.generate_charts(
        data_json=data3,
        chart_type='pie',
        output_dir=output_dir
    )
    print(f"资产结构图表生成结果: {response3}")
    
    print("\n图表生成测试完成！")


if __name__ == "__main__":
    test_chart_generation()