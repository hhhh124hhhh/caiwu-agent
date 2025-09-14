#!/usr/bin/env python3
"""
Comprehensive analysis example for multiple stocks
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from financial_tools.akshare_financial_tool import AKShareFinancialDataTool
from financial_tools.financial_analysis_toolkit import StandardFinancialAnalyzer
import pandas as pd


def compare_companies(stock_list):
    """Compare multiple companies"""
    data_tool = AKShareFinancialDataTool()
    analyzer = StandardFinancialAnalyzer()
    
    comparison_data = []
    
    for stock_code, stock_name in stock_list:
        print(f"Analyzing {stock_name} ({stock_code})...")
        
        try:
            # Get financial data
            financial_data = data_tool.get_financial_reports(stock_code, stock_name)
            
            if not financial_data:
                print(f"  Failed to get data for {stock_name}")
                continue
            
            # Calculate metrics
            metrics = data_tool.get_key_metrics(financial_data)
            ratios = analyzer.calculate_financial_ratios(financial_data)
            trends = analyzer.analyze_trends(financial_data)
            health = analyzer.assess_financial_health(ratios, trends)
            
            # Collect comparison data
            company_data = {
                'Company': stock_name,
                'Stock Code': stock_code,
                'Revenue (Billion)': metrics.get('revenue_billion', 0),
                'Net Profit (Billion)': metrics.get('net_profit_billion', 0),
                'ROE (%)': ratios.get('profitability', {}).get('roe', 0),
                'Debt to Asset (%)': ratios.get('solvency', {}).get('debt_to_asset_ratio', 0),
                'Health Score': health.get('overall_score', 0),
                'Risk Level': health.get('risk_level', 'Unknown')
            }
            
            comparison_data.append(company_data)
            print(f"  Analysis completed for {stock_name}")
            
        except Exception as e:
            print(f"  Error analyzing {stock_name}: {e}")
    
    # Create comparison DataFrame
    if comparison_data:
        df = pd.DataFrame(comparison_data)
        print("\n=== Company Comparison ===")
        print(df.to_string(index=False))
        
        # Save to CSV
        df.to_csv('./company_comparison.csv', index=False, encoding='utf-8-sig')
        print("\nComparison data saved to company_comparison.csv")
    
    return comparison_data


def industry_analysis(industry_stocks):
    """Analyze companies in the same industry"""
    print("=== Industry Analysis ===")
    
    # Compare companies
    comparison_data = compare_companies(industry_stocks)
    
    if not comparison_data:
        print("No data available for industry analysis")
        return
    
    # Calculate industry averages
    df = pd.DataFrame(comparison_data)
    
    print("\n=== Industry Averages ===")
    numeric_columns = ['Revenue (Billion)', 'Net Profit (Billion)', 'ROE (%)', 
                      'Debt to Asset (%)', 'Health Score']
    
    for col in numeric_columns:
        if col in df.columns:
            avg = df[col].mean()
            print(f"{col}: {avg:.2f}")


def main():
    # Example stock list (company code, company name)
    sample_stocks = [
        ("600519", "贵州茅台"),
        ("000858", "五粮液"),
        ("002304", "洋河股份")
    ]
    
    print("Starting comprehensive financial analysis...")
    
    # Compare companies
    compare_companies(sample_stocks)
    
    # Industry analysis (liquor industry)
    industry_analysis(sample_stocks)
    
    print("\nComprehensive analysis completed!")


if __name__ == "__main__":
    main()