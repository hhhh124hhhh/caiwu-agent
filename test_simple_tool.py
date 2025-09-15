#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试工具包方法
"""

import pandas as pd
import os
from utu.tools.tabular_data_toolkit import TabularDataToolkit
from utu.config import ToolkitConfig

def test_tools():
    print("=== 简单测试工具包方法 ===")
    
    # 初始化工具包
    config = ToolkitConfig()
    tabular_tool = TabularDataToolkit(config=config)
    
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
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_tools()