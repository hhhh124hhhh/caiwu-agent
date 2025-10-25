#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试图表生成功能
"""

import os
import json
from utu.tools.tabular_data_toolkit import TabularDataToolkit


def test_chart_generation():
    """
    测试图表生成功能
    """
    print("开始测试图表生成功能...")
    
    # 创建图表生成器实例
    chart_generator = TabularDataToolkit()
    
    # 测试数据 - 使用用户提供的财务数据样例
    test_data = {
        "title": "陕西建工盈利能力趋势分析",
        "x_axis": ["2022年", "2023年", "2024年", "2025年"],
        "series": [
            {"name": "营业收入(亿元)", "data": [450.89, 490.23, 520.45, 573.88]},
            {"name": "净利润(亿元)", "data": [7.23, 8.56, 9.85, 11.04]},
            {"name": "净利润率(%)", "data": [1.60, 1.75, 1.89, 1.92]},
            {"name": "ROE(%)", "data": [2.10, 2.35, 2.52, 2.68]}
        ]
    }
    
    # 测试折线图生成
    print("\n测试折线图生成...")
    result = chart_generator.generate_charts(
        data_json=json.dumps(test_data),
        chart_type="line",
        output_dir="./run_workdir"
    )
    
    print(f"\n测试结果:")
    print(f"成功: {result.get('success')}")
    print(f"消息: {result.get('message')}")
    
    if result.get('success'):
        print(f"生成的图表文件:")
        for file_path in result.get('files', []):
            if os.path.exists(file_path):
                print(f"  ✓ {file_path} (文件存在)")
            else:
                print(f"  ✗ {file_path} (文件不存在)")
    
    # 测试柱状图生成（可选）
    print("\n测试柱状图生成...")
    result_bar = chart_generator.generate_charts(
        data_json=json.dumps(test_data),
        chart_type="bar",
        output_dir="./run_workdir"
    )
    
    print(f"\n柱状图测试结果:")
    print(f"成功: {result_bar.get('success')}")
    print(f"消息: {result_bar.get('message')}")
    
    if result_bar.get('success'):
        print(f"生成的图表文件:")
        for file_path in result_bar.get('files', []):
            if os.path.exists(file_path):
                print(f"  ✓ {file_path} (文件存在)")
            else:
                print(f"  ✗ {file_path} (文件不存在)")
    
    print("\n测试完成！")
    
    # 返回最终结果
    return result.get('success') and result_bar.get('success')


if __name__ == "__main__":
    success = test_chart_generation()
    exit(0 if success else 1)