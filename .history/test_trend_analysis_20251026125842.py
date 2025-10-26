#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试趋势分析工具修复
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utu.tools.financial_analysis_toolkit import FinancialAnalysisToolkit
import json


def test_trend_analysis():
    """
    测试趋势分析工具对不同数据格式的处理
    """
    # 初始化工具类
    toolkit = FinancialAnalysisToolkit()
    
    # 测试数据1：用户提供的第一种格式
    test_data1 = {
        "company_name": "陕西建工", 
        "stock_code": "600248.SH", 
        "financial_statements": {
            "income_statement": {"revenue": 573.88, "net_profit": 11.04, "gross_profit": 42.67}, 
            "balance_sheet": {"total_assets": 3472.98, "total_liabilities": 3081.05, "equity": 391.93}, 
            "cash_flow": {"operating_cash_flow": 7.18}
        }, 
        "financial_ratios": {
            "profitability": {"net_profit_margin": 1.92, "roe": 2.68, "gross_margin": 7.44}, 
            "liquidity": {"current_ratio": 1.12, "quick_ratio": 0.95}, 
            "solvency": {"debt_to_assets": 88.71}, 
            "efficiency": {"asset_turnover": 0.17, "inventory_turnover": 4.2}, 
            "growth": {"revenue_growth": 2.39, "net_profit_growth": 3.47, "asset_growth": 4.6}, 
            "cash_flow": {"operating_cash_flow_ratio": 0.65, "cash_flow_coverage": 1.05}
        }, 
        "health_assessment": {"score": 60.6, "risk_level": "中等风险"}
    }
    
    # 测试数据2：用户提供的第二种格式（包含historical_data）
    test_data2 = {
        "company_name": "陕西建工", 
        "stock_code": "600248.SH", 
        "historical_data": {
            "years": [2021, 2022, 2023, 2024], 
            "revenue": [520.45, 545.23, 560.78, 573.88], 
            "net_profit": [9.85, 10.23, 10.67, 11.04], 
            "total_assets": [3156.78, 3289.45, 3320.12, 3472.98], 
            "total_liabilities": [2789.34, 2901.56, 2945.23, 3081.05], 
            "equity": [367.44, 387.89, 374.89, 391.93], 
            "operating_cash_flow": [6.45, 6.78, 6.92, 7.18]
        }, 
        "current_period": {
            "revenue": 573.88, 
            "net_profit": 11.04, 
            "total_assets": 3472.98, 
            "total_liabilities": 3081.05, 
            "equity": 391.93, 
            "operating_cash_flow": 7.18
        }, 
        "financial_ratios": {
            "profitability": {"net_profit_margin": 1.92, "roe": 2.68, "gross_margin": 7.44}, 
            "liquidity": {"current_ratio": 1.12, "quick_ratio": 0.95}, 
            "solvency": {"debt_to_assets": 88.71}, 
            "efficiency": {"asset_turnover": 0.17, "inventory_turnover": 4.2}, 
            "growth": {"revenue_growth": 2.39, "net_profit_growth": 3.47, "asset_growth": 4.6}, 
            "cash_flow": {"operating_cash_flow_ratio": 0.65, "cash_flow_coverage": 1.05}
        }
    }
    
    # 测试数据3：用户提供的第三种格式（company, symbol, data结构）
    test_data3 = {
        "company": "陕西建工", 
        "symbol": "600248.SH", 
        "data": {
            "2021": {"revenue": 520.45, "net_profit": 9.85, "total_assets": 3156.78, "total_liabilities": 2789.34, "equity": 367.44, "operating_cash_flow": 6.45}, 
            "2022": {"revenue": 545.23, "net_profit": 10.23, "total_assets": 3289.45, "total_liabilities": 2901.56, "equity": 387.89, "operating_cash_flow": 6.78}, 
            "2023": {"revenue": 560.78, "net_profit": 10.67, "total_assets": 3320.12, "total_liabilities": 2945.23, "equity": 374.89, "operating_cash_flow": 6.92}, 
            "2024": {"revenue": 573.88, "net_profit": 11.04, "total_assets": 3472.98, "total_liabilities": 3081.05, "equity": 391.93, "operating_cash_flow": 7.18}
        }
    }
    
    # 测试数据4：多公司格式
    test_data4 = {
        "陕西建工": {
            "2021": {"revenue": 520.45, "net_profit": 9.85}, 
            "2022": {"revenue": 545.23, "net_profit": 10.23}, 
            "2023": {"revenue": 560.78, "net_profit": 10.67}, 
            "2024": {"revenue": 573.88, "net_profit": 11.04}
        },
        "对比公司": {
            "2021": {"revenue": 480.56, "net_profit": 12.34}, 
            "2022": {"revenue": 500.78, "net_profit": 13.56}, 
            "2023": {"revenue": 510.34, "net_profit": 14.78}, 
            "2024": {"revenue": 520.12, "net_profit": 15.90}
        }
    }
    
    # 测试不同数据格式
    print("=== 测试数据格式1 ===")
    result1 = toolkit.analyze_trends_tool(json.dumps(test_data1))
    print(f"结果类型: {type(result1)}")
    print(f"结果: {json.dumps(result1, ensure_ascii=False, indent=2)}")
    print()
    
    print("=== 测试数据格式2 ===")
    result2 = toolkit.analyze_trends_tool(json.dumps(test_data2))
    print(f"结果类型: {type(result2)}")
    print(f"结果: {json.dumps(result2, ensure_ascii=False, indent=2)}")
    print()
    
    print("=== 测试数据格式3 ===")
    result3 = toolkit.analyze_trends_tool(json.dumps(test_data3))
    print(f"结果类型: {type(result3)}")
    print(f"结果: {json.dumps(result3, ensure_ascii=False, indent=2)}")
    print()
    
    print("=== 测试数据格式4 (多公司) ===")
    result4 = toolkit.analyze_trends_tool(json.dumps(test_data4))
    print(f"结果类型: {type(result4)}")
    print(f"结果: {json.dumps(result4, ensure_ascii=False, indent=2)}")
    print()
    
    print("所有测试完成!")


if __name__ == "__main__":
    test_trend_analysis()