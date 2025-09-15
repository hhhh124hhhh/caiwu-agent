#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复的工具包功能
"""

import json
from utu.tools import TOOLKIT_MAP

def test_financial_analysis_toolkit():
    """测试财务分析工具包"""
    print("=== 测试财务分析工具包 ===")
    
    # 初始化工具包
    analyzer = TOOLKIT_MAP['financial_analysis']()
    print("✓ 工具包初始化成功")
    
    # 测试 generate_report 方法
    print("\n--- 测试 generate_report 方法 ---")
    
    # 创建简化指标数据
    simple_metrics = {
        "company_name": "陕西建工",
        "stock_code": "600248", 
        "latest_year": 2025,
        "revenue": 573.88,
        "net_profit": 11.04,
        "total_assets": 3472.98,
        "debt_ratio": 88.71,
        "roe": 2.68,
        "net_margin": 1.92
    }
    
    # 将数据转换为JSON字符串
    financial_data_json = json.dumps(simple_metrics, ensure_ascii=False)
    
    try:
        # 调用 generate_report 方法
        report = analyzer.generate_report(
            financial_data_json=financial_data_json,
            stock_name="陕西建工"
        )
        print("✓ generate_report 方法调用成功")
        print(f"  报告生成时间: {report.get('analysis_date', 'N/A')}")
        print(f"  公司名称: {report.get('company_name', 'N/A')}")
    except Exception as e:
        print(f"✗ generate_report 方法调用失败: {e}")

def test_akshare_financial_toolkit():
    """测试AKShare财务数据工具包"""
    print("\n=== 测试AKShare财务数据工具包 ===")
    
    # 初始化工具包
    data_tool = TOOLKIT_MAP['akshare_financial_data']()
    print("✓ 工具包初始化成功")
    
    # 测试工具方法是否存在
    tools = [method for method in dir(data_tool) if hasattr(getattr(data_tool, method), '_is_tool')]
    print(f"✓ 可用工具方法: {tools}")

if __name__ == "__main__":
    print("开始测试修复后的工具包功能...")
    
    try:
        test_financial_analysis_toolkit()
    except Exception as e:
        print(f"财务分析工具包测试出错: {e}")
    
    try:
        test_akshare_financial_toolkit()
    except Exception as e:
        print(f"AKShare财务数据工具包测试出错: {e}")
    
    print("\n=== 测试完成 ===")