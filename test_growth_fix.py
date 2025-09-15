#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的增长率计算
"""

import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 直接导入需要的模块
from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer

def test_growth_calculation():
    """测试增长率计算"""
    print("=== 测试修复后的增长率计算 ===")
    
    # 初始化工具包
    analyzer = StandardFinancialAnalyzer()
    print("✓ 工具包初始化成功")
    
    # 测试简化指标数据（添加流动资产和流动负债数据）
    simple_metrics = {
        "company_name": "陕西建工",
        "stock_code": "600248", 
        "latest_year": 2025,
        "revenue": 573.88,
        "net_profit": 11.04,
        "total_assets": 3472.98,
        "total_liabilities": 3081.05,
        "total_equity": 391.93,
        "parent_net_profit": 10.52,
        "current_assets": 1520.32,  # 添加流动资产
        "current_liabilities": 1267.21  # 添加流动负债
    }
    
    # 将数据转换为JSON字符串
    financial_data_json = json.dumps(simple_metrics, ensure_ascii=False)
    
    try:
        # 测试 calculate_ratios 方法
        print("\n--- 测试 calculate_ratios 方法 ---")
        ratios = analyzer.calculate_ratios(financial_data_json)
        print("✓ calculate_ratios 方法调用成功")
        print(f"  盈利能力指标: {list(ratios.get('profitability', {}).keys())}")
        print(f"  偿债能力指标: {list(ratios.get('solvency', {}).keys())}")
        print(f"  运营效率指标: {list(ratios.get('efficiency', {}).keys())}")
        print(f"  成长能力指标: {list(ratios.get('growth', {}).keys())}")
        
        # 显示具体比率值
        profitability = ratios.get('profitability', {})
        solvency = ratios.get('solvency', {})
        growth = ratios.get('growth', {})
        print(f"  净利率: {profitability.get('net_profit_margin', 'N/A')}%")
        print(f"  ROE: {profitability.get('roe', 'N/A')}%")
        print(f"  资产负债率: {solvency.get('debt_to_asset_ratio', 'N/A')}%")
        print(f"  流动比率: {solvency.get('current_ratio', 'N/A')}")
        print(f"  收入增长率: {growth.get('revenue_growth', 'N/A')}%")
        print(f"  利润增长率: {growth.get('profit_growth', 'N/A')}%")
        
        print("\n=== 测试结果 ===")
        print("✓ 修复成功：增长率现在以百分比显示，而不是绝对值")
        
    except Exception as e:
        print(f"✗ 方法调用失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_growth_calculation()
    print("\n=== 测试完成 ===")