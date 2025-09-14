#!/usr/bin/env python3
"""
Tests for the financial analyzer
"""

import sys
import os
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from financial_tools.financial_analysis_toolkit import StandardFinancialAnalyzer


def create_mock_data():
    """Create mock financial data for testing"""
    # Create mock income statement
    mock_income = pd.DataFrame({
        'REPORT_DATE': pd.date_range('2020-12-31', periods=4, freq='Y'),
        'TOTAL_OPERATE_INCOME': [100000000, 120000000, 135000000, 150000000],
        'NETPROFIT': [8000000, 10000000, 12000000, 13500000],
        'PARENT_NETPROFIT': [7500000, 9500000, 11500000, 13000000],
        'TOTAL_OPERATE_COST': [70000000, 85000000, 95000000, 105000000]
    })
    
    # Create mock balance sheet
    mock_balance = pd.DataFrame({
        'REPORT_DATE': pd.date_range('2020-12-31', periods=4, freq='Y'),
        'TOTAL_ASSETS': [80000000, 90000000, 100000000, 110000000],
        'TOTAL_LIABILITIES': [50000000, 55000000, 60000000, 65000000],
        'TOTAL_EQUITY': [30000000, 35000000, 40000000, 45000000],
        'TOTAL_CURRENT_ASSETS': [40000000, 45000000, 50000000, 55000000],
        'TOTAL_CURRENT_LIABILITIES': [30000000, 32000000, 35000000, 38000000]
    })
    
    return {
        'income': mock_income,
        'balance': mock_balance
    }


def test_analyzer_initialization():
    """Test analyzer initialization"""
    print("Testing analyzer initialization...")
    try:
        analyzer = StandardFinancialAnalyzer()
        print("✓ Analyzer initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Analyzer initialization failed: {e}")
        return False


def test_ratio_calculation():
    """Test financial ratio calculation"""
    print("Testing financial ratio calculation...")
    try:
        analyzer = StandardFinancialAnalyzer()
        mock_data = create_mock_data()
        
        ratios = analyzer.calculate_financial_ratios(mock_data)
        
        if ratios and isinstance(ratios, dict):
            print("✓ Financial ratios calculated successfully")
            print(f"  Ratio categories: {list(ratios.keys())}")
            return True
        else:
            print("✗ Failed to calculate financial ratios")
            return False
    except Exception as e:
        print(f"✗ Error calculating financial ratios: {e}")
        return False


def test_trend_analysis():
    """Test trend analysis"""
    print("Testing trend analysis...")
    try:
        analyzer = StandardFinancialAnalyzer()
        mock_data = create_mock_data()
        
        trends = analyzer.analyze_trends(mock_data)
        
        if trends and isinstance(trends, dict):
            print("✓ Trend analysis completed successfully")
            print(f"  Trend categories: {list(trends.keys())}")
            return True
        else:
            print("✗ Failed to complete trend analysis")
            return False
    except Exception as e:
        print(f"✗ Error in trend analysis: {e}")
        return False


def test_health_assessment():
    """Test financial health assessment"""
    print("Testing financial health assessment...")
    try:
        analyzer = StandardFinancialAnalyzer()
        mock_data = create_mock_data()
        
        # First calculate ratios and trends
        ratios = analyzer.calculate_financial_ratios(mock_data)
        trends = analyzer.analyze_trends(mock_data)
        
        # Then assess health
        health = analyzer.assess_financial_health(ratios, trends)
        
        if health and isinstance(health, dict):
            print("✓ Financial health assessment completed successfully")
            print(f"  Health score: {health.get('overall_score', 'N/A')}")
            print(f"  Risk level: {health.get('risk_level', 'N/A')}")
            return True
        else:
            print("✗ Failed to complete health assessment")
            return False
    except Exception as e:
        print(f"✗ Error in health assessment: {e}")
        return False


def test_report_generation():
    """Test report generation"""
    print("Testing report generation...")
    try:
        analyzer = StandardFinancialAnalyzer()
        mock_data = create_mock_data()
        
        report = analyzer.generate_analysis_report(mock_data, "Test Company")
        
        if report and isinstance(report, dict):
            print("✓ Analysis report generated successfully")
            print(f"  Report keys: {list(report.keys())}")
            return True
        else:
            print("✗ Failed to generate analysis report")
            return False
    except Exception as e:
        print(f"✗ Error generating analysis report: {e}")
        return False


def main():
    """Run all tests"""
    print("=== Financial Analyzer Tests ===\n")
    
    tests = [
        test_analyzer_initialization,
        test_ratio_calculation,
        test_trend_analysis,
        test_health_assessment,
        test_report_generation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print(f"=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False


if __name__ == "__main__":
    main()