#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证图表生成工具的修复方案
用于修复Terminal#589-602中的图表生成错误
"""

import json
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from utu.tools.tabular_data_toolkit import TabularDataToolkit

def create_shanxi_jiankong_trend_data():
    """
    创建陕西建工财务趋势数据，使用正确的通用图表格式
    包含title、x_axis和series必需字段
    """
    # 使用正确的通用图表格式
    trend_data = {
        "title": "陕西建工2024-2025年财务趋势分析",
        "x_axis": ["2024年", "2025年"],
        "series": [
            {
                "name": "营业收入（亿元）",
                "data": [500, 190]  # 模拟下降62.03%的数据
            },
            {
                "name": "净利润（亿元）",
                "data": [34, 10.4]  # 模拟下降69.43%的数据
            }
        ]
    }
    return trend_data

def create_company_comparison_data():
    """
    创建公司对比数据格式（备用）
    """
    comparison_data = {
        "companies": ["陕西建工", "行业平均"],
        "revenue": [190, 300],
        "net_profit": [10.4, 20],
        "profit_margin": [5.47, 6.67],
        "roe": [8.2, 12.5]
    }
    return comparison_data

def test_chart_generation(data_type="generic"):
    """
    测试图表生成
    
    Args:
        data_type: 数据类型，"generic"表示通用图表格式，"comparison"表示公司对比格式
    """
    print("开始测试图表生成修复方案...")
    
    # 初始化图表生成工具
    toolkit = TabularDataToolkit()
    
    # 创建输出目录
    output_dir = os.path.join(os.getcwd(), "chart_test_output")
    os.makedirs(output_dir, exist_ok=True)
    
    # 根据数据类型选择数据
    if data_type == "generic":
        data = create_shanxi_jiankong_trend_data()
        print("使用通用图表格式进行测试...")
    else:
        data = create_company_comparison_data()
        print("使用公司对比格式进行测试...")
    
    # 打印数据格式用于调试
    print("\n测试数据格式:")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    
    # 转换为JSON字符串
    data_json = json.dumps(data)
    
    try:
        # 生成折线图
        print("\n生成折线图...")
        result_line = toolkit.generate_charts(data_json, chart_type="trend", output_dir=output_dir)
        print(f"折线图结果: {result_line['success']}")
        if result_line['success']:
            print(f"生成的图表文件: {', '.join(result_line['files'])}")
        else:
            print(f"错误信息: {result_line.get('message')}")
        
        # 生成柱状图
        print("\n生成柱状图...")
        result_bar = toolkit.generate_charts(data_json, chart_type="bar", output_dir=output_dir)
        print(f"柱状图结果: {result_bar['success']}")
        if result_bar['success']:
            print(f"生成的图表文件: {', '.join(result_bar['files'])}")
        else:
            print(f"错误信息: {result_bar.get('message')}")
            
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n测试完成，图表保存在: {output_dir}")

if __name__ == "__main__":
    # 默认使用通用图表格式测试
    test_chart_generation(data_type="generic")
    
    # 如果需要测试公司对比格式，可以取消下面这行的注释
    # test_chart_generation(data_type="comparison")