#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试工具包方法
"""

import asyncio
import pandas as pd
import os
from utu.tools import get_toolkits_map
from typing import cast
from utu.tools.tabular_data_toolkit import TabularDataToolkit

async def test_tools():
    print("=== 测试工具包方法 ===")
    
    # 加载工具包
    toolkits = get_toolkits_map(['tabular'])
    tabular_tool = cast(TabularDataToolkit, toolkits.get('tabular'))
    
    if tabular_tool is None:
        print("错误: 无法加载表格数据工具包")
        return
    
    # 创建测试数据
    test_data = {'年份': [2020, 2021], '收入': [100, 120]}
    df = pd.DataFrame(test_data)
    os.makedirs('run_workdir', exist_ok=True)
    csv_path = 'run_workdir/test.csv'
    df.to_csv(csv_path, index=False)
    
    # 测试表格工具的方法
    print("\n1. 测试 get_tabular_columns 方法...")
    columns = tabular_tool.get_tabular_columns(csv_path)
    print("列信息:", columns[:100] + '...' if len(columns) > 100 else columns)
    
    # 测试异步方法
    print("\n2. 测试 get_column_info 方法...")
    try:
        column_info = await tabular_tool.get_column_info(csv_path)
        print("列分析: 可用")
        print("分析结果长度:", len(column_info))
    except Exception as e:
        print("列分析错误:", str(e))
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    asyncio.run(test_tools())