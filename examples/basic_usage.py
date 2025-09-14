#!/usr/bin/env python3
"""
Basic usage example for the financial analysis toolkit
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from financial_tools.akshare_financial_tool import AKShareFinancialDataTool
from financial_tools.financial_analysis_toolkit import StandardFinancialAnalyzer


def main():
    # Initialize tools
    print("Initializing financial data tool...")
    data_tool = AKShareFinancialDataTool()
    
    print("Initializing financial analyzer...")
    analyzer = StandardFinancialAnalyzer()
    
    # Example: Analyze Kweichow Moutai (600519)
    stock_code = "600519"
    stock_name = "贵州茅台"
    
    print(f"\nGetting financial data for {stock_name} ({stock_code})...")
    financial_data = data_tool.get_financial_reports(stock_code, stock_name)
    
    if not financial_data:
        print("Failed to get financial data")
        return
    
    print("Financial data retrieved successfully")
    
    # Calculate key metrics
    print("\nCalculating key metrics...")
    metrics = data_tool.get_key_metrics(financial_data)
    print("Key metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    
    # Calculate financial ratios
    print("\nCalculating financial ratios...")
    ratios = analyzer.calculate_financial_ratios(financial_data)
    print("Financial ratios calculated")
    
    # Analyze trends
    print("\nAnalyzing trends...")
    trends = analyzer.analyze_trends(financial_data)
    print("Trend analysis completed")
    
    # Assess financial health
    print("\nAssessing financial health...")
    health = analyzer.assess_financial_health(ratios, trends)
    print("Health assessment completed")
    
    # Generate comprehensive report
    print("\nGenerating comprehensive report...")
    report = analyzer.generate_analysis_report(financial_data, stock_name)
    
    print(f"\n=== Analysis Report for {report['company_name']} ===")
    print(f"Analysis Date: {report['analysis_date']}")
    print(f"Health Score: {report['health_assessment']['overall_score']}")
    print(f"Risk Level: {report['health_assessment']['risk_level']}")
    
    print("\nKey Metrics:")
    for key, value in report['key_metrics'].items():
        print(f"  {key}: {value}")
    
    print("\nRecommendations:")
    for rec in report['health_assessment']['recommendations']:
        print(f"  - {rec}")
    
    # Save data to CSV
    print("\nSaving data to CSV files...")
    data_tool.save_to_csv(financial_data, f"./{stock_code}_financial_data")
    print("Data saved successfully")


if __name__ == "__main__":
    main()