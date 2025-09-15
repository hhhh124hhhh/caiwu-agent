#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试表格数据工具包集成效果
"""

import asyncio
import pandas as pd
import json
import os

# 创建测试数据
def create_test_financial_data():
    """创建测试财务数据文件"""
    # 创建测试CSV文件
    test_data = {
        '年份': [2020, 2021, 2022, 2023],
        '营业收入(亿元)': [100, 120, 135, 150],
        '净利润(亿元)': [8, 10, 12, 13.5],
        '总资产(亿元)': [80, 90, 100, 110],
        '总负债(亿元)': [50, 55, 60, 65]
    }
    
    df = pd.DataFrame(test_data)
    
    # 确保目录存在
    os.makedirs("run_workdir", exist_ok=True)
    
    # 保存为CSV文件
    csv_file_path = "run_workdir/test_financial_data.csv"
    df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')
    
    print(f"测试数据已保存到: {csv_file_path}")
    return csv_file_path

async def test_tabular_tools():
    """测试表格数据工具"""
    # 创建测试数据
    csv_file_path = create_test_financial_data()
    
    # 导入工具包
    from utu.tools.tabular_data_toolkit import TabularDataToolkit
    from utu.config import ToolkitConfig
    
    # 初始化工具包
    config = ToolkitConfig()
    toolkit = TabularDataToolkit(config=config)
    
    print("=== 测试表格数据工具包 ===")
    
    # 测试1: 获取表格列信息
    print("\n1. 测试获取表格列信息...")
    try:
        columns_info = toolkit.get_tabular_columns(csv_file_path)
        print("列信息:")
        print(columns_info)
    except Exception as e:
        print(f"获取列信息失败: {e}")
    
    # 测试2: 智能分析列含义
    print("\n2. 测试智能分析列含义...")
    try:
        column_analysis = await toolkit.get_column_info(csv_file_path)
        print("列含义分析:")
        print(column_analysis)
    except Exception as e:
        print(f"分析列含义失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_tabular_tools())