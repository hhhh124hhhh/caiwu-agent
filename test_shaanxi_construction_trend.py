#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试陕西建工财务趋势分析修复
"""

import json
from utu.tools.financial_analysis_toolkit import FinancialAnalysisToolkit

def test_shaanxi_construction_trend():
    """测试陕西建工数据格式的趋势分析"""
    print("开始测试陕西建工财务趋势分析修复...")
    
    # 使用用户提供的陕西建工数据格式
    shaanxi_data = {
        "company_name": "陕西建工",
        "stock_code": "600248.SH",
        "financial_data": {
            "income_statement": {
                "records": 102,
                "latest": {
                    "revenue": 573.88,
                    "net_profit": 11.04,
                    "gross_profit": None,
                    "operating_profit": None
                },
                "previous_year": {
                    "revenue": 1511.39,
                    "net_profit": 36.11
                }
            },
            "balance_sheet": {
                "records": 101,
                "latest": {
                    "total_assets": 3472.98,
                    "total_liabilities": 3081.05,
                    "equity": 391.93,
                    "current_assets": 2000,
                    "current_liabilities": 1800,
                    "receivables": 800
                }
            },
            "cash_flow": {
                "records": 97
            },
            "key_ratios": {
                "profit_margin": 1.92,
                "roe": 2.68,
                "debt_to_asset_ratio": 88.71,
                "current_ratio": 1.11,
                "asset_turnover": 0.17,
                "receivables_turnover": 0.72
            }
        },
        "time_periods": {
            "current": "2025",
            "previous": "2024",
            "data_freshness": "部分期间数据"
        }
    }
    
    # 转换为JSON字符串
    financial_data_json = json.dumps(shaanxi_data, ensure_ascii=False)
    
    # 初始化工具
    toolkit = FinancialAnalysisToolkit()
    
    # 调用修复后的函数
    print("调用analyze_trends_tool...")
    result = toolkit.analyze_trends_tool(financial_data_json)
    
    # 打印结果
    print("\n分析结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 验证结果是否包含有效数据
    if result.get('revenue', {}).get('average_growth') is not None or \
       result.get('profit', {}).get('average_growth') is not None:
        print("\n✅ 测试成功! 趋势分析工具现在可以正确处理陕西建工数据格式。")
        
        # 计算预期增长率进行验证
        current_revenue = shaanxi_data['financial_data']['income_statement']['latest']['revenue']
        prev_revenue = shaanxi_data['financial_data']['income_statement']['previous_year']['revenue']
        expected_revenue_growth = ((current_revenue - prev_revenue) / prev_revenue) * 100
        
        current_profit = shaanxi_data['financial_data']['income_statement']['latest']['net_profit']
        prev_profit = shaanxi_data['financial_data']['income_statement']['previous_year']['net_profit']
        expected_profit_growth = ((current_profit - prev_profit) / prev_profit) * 100
        
        print(f"\n预期收入增长率: {expected_revenue_growth:.2f}%")
        print(f"预期利润增长率: {expected_profit_growth:.2f}%")
        
    else:
        print("\n❌ 测试失败! 趋势分析工具仍然无法正确处理陕西建工数据格式。")

if __name__ == "__main__":
    test_shaanxi_construction_trend()