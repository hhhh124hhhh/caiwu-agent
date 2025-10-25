#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试财务比率计算功能修复
验证中英文列名映射是否正确工作
"""

import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer

def test_financial_ratios():
    """
    测试财务比率计算功能
    使用英文键名的数据进行测试
    """
    print("开始测试财务比率计算功能...")
    
    # 创建测试数据（使用英文键名）
    test_data = {
        "revenue": 1000000000,  # 10亿元
        "net_profit": 100000000,  # 1亿元
        "gross_profit": 300000000,  # 3亿元
        "operating_profit": 200000000,  # 2亿元
        "cost_of_goods_sold": 700000000,  # 7亿元
        "total_assets": 5000000000,  # 50亿元
        "total_liabilities": 3000000000,  # 30亿元
        "total_equity": 2000000000,  # 20亿元
        "current_assets": 2000000000,  # 20亿元
        "current_liabilities": 1500000000,  # 15亿元
        "inventory": 500000000,  # 5亿元
        "accounts_receivable": 300000000,  # 3亿元
        "operating_cash_flow": 150000000,  # 1.5亿元
        "investing_cash_flow": -500000000,  # -5亿元
        "financing_cash_flow": -100000000  # -1亿元
    }
    
    print("测试数据:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    
    # 初始化工具
    toolkit = StandardFinancialAnalyzer()
    
    # 将测试数据转换为JSON字符串
    test_data_json = json.dumps(test_data)
    
    # 计算财务比率
    print("\n计算财务比率...")
    ratios = toolkit.calculate_ratios(test_data_json)
    
    # 打印结果
    print("\n财务比率计算结果:")
    
    # 盈利能力指标
    print("\n盈利能力指标:")
    profitability = ratios.get('profitability', {})
    for ratio_name, ratio_value in profitability.items():
        print(f"  {ratio_name}: {ratio_value}")
    
    # 偿债能力指标
    print("\n偿债能力指标:")
    solvency = ratios.get('solvency', {})
    for ratio_name, ratio_value in solvency.items():
        print(f"  {ratio_name}: {ratio_value}")
    
    # 验证关键指标是否正确计算（不为零）
    print("\n验证关键指标:")
    success = True
    
    # 检查毛利率
    if 'gross_profit_margin' in profitability and profitability['gross_profit_margin'] > 0:
        print(f"  ✓ 毛利率计算成功: {profitability['gross_profit_margin']}%")
    else:
        print("  ✗ 毛利率计算失败，值为零或未计算")
        success = False
    
    # 检查净利率
    if 'net_profit_margin' in profitability and profitability['net_profit_margin'] > 0:
        print(f"  ✓ 净利率计算成功: {profitability['net_profit_margin']}%")
    else:
        print("  ✗ 净利率计算失败，值为零或未计算")
        success = False
    
    # 检查ROE
    if 'roe' in profitability and profitability['roe'] > 0:
        print(f"  ✓ ROE计算成功: {profitability['roe']}%")
    else:
        print("  ✗ ROE计算失败，值为零或未计算")
        success = False
    
    # 检查资产负债率
    if 'debt_to_asset_ratio' in solvency and solvency['debt_to_asset_ratio'] > 0:
        print(f"  ✓ 资产负债率计算成功: {solvency['debt_to_asset_ratio']}%")
    else:
        print("  ✗ 资产负债率计算失败，值为零或未计算")
        success = False
    
    # 检查流动比率
    if 'current_ratio' in solvency and solvency['current_ratio'] > 0:
        print(f"  ✓ 流动比率计算成功: {solvency['current_ratio']}")
    else:
        print("  ✗ 流动比率计算失败，值为零或未计算")
        success = False
    
    # 打印总结
    print("\n测试总结:")
    if success:
        print("✅ 所有关键财务比率计算成功！修复有效。")
        return 0
    else:
        print("❌ 部分财务比率计算失败，请检查修复。")
        return 1

if __name__ == "__main__":
    sys.exit(test_financial_ratios())