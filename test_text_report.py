#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文字报告生成功能
"""

import json
from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer

def test_text_report_generation():
    """测试文字报告生成功能"""
    print("=== 测试文字报告生成功能 ===")
    
    # 初始化分析器
    analyzer = StandardFinancialAnalyzer()
    print("✓ 分析器初始化成功")
    
    # 创建简化指标数据
    simple_metrics = {
        "company_name": "陕西建工",
        "stock_code": "600248", 
        "latest_year": 2025,
        "revenue": 573.88,
        "net_profit": 11.04,
        "parent_net_profit": 10.52,
        "total_assets": 3472.98,
        "total_liabilities": 3081.05,
        "total_equity": 391.93,
        "debt_ratio": 88.71,
        "roe": 2.68,
        "net_margin": 1.92
    }
    
    # 将数据转换为JSON字符串
    financial_data_json = json.dumps(simple_metrics, ensure_ascii=False)
    
    try:
        # 调用 generate_text_report 方法
        text_report = analyzer.generate_text_report(
            financial_data_json=financial_data_json,
            stock_name="陕西建工"
        )
        print("✓ 文字报告生成成功")
        print("\n=== 生成的文字报告 ===")
        print(text_report)
        print("=== 报告结束 ===")
        
        # 保存报告到文件
        import os
        os.makedirs("run_workdir", exist_ok=True)
        with open("run_workdir/shaanxi_construction_text_report.txt", "w", encoding="utf-8") as f:
            f.write(text_report)
        print("✓ 报告已保存到 run_workdir/shaanxi_construction_text_report.txt")
        
    except Exception as e:
        print(f"✗ 文字报告生成失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_text_report_generation()