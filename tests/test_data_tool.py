#!/usr/bin/env python3
"""
Tests for the financial data tool
"""

import sys
import os
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from financial_tools.akshare_financial_tool import AKShareFinancialDataTool


def test_tool_initialization():
    """Test tool initialization"""
    print("Testing tool initialization...")
    try:
        tool = AKShareFinancialDataTool()
        print("✓ Tool initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Tool initialization failed: {e}")
        return False


def test_get_financial_reports():
    """Test getting financial reports"""
    print("Testing financial reports retrieval...")
    try:
        tool = AKShareFinancialDataTool()
        # Test with a well-known company
        data = tool.get_financial_reports("600519", "贵州茅台")
        
        if data and isinstance(data, dict):
            print("✓ Financial reports retrieved successfully")
            print(f"  Data keys: {list(data.keys())}")
            return True
        else:
            print("✗ Failed to retrieve financial reports")
            return False
    except Exception as e:
        print(f"✗ Error retrieving financial reports: {e}")
        return False


def test_get_key_metrics():
    """Test getting key metrics"""
    print("Testing key metrics extraction...")
    try:
        tool = AKShareFinancialDataTool()
        data = tool.get_financial_reports("600519", "贵州茅台")
        
        if data:
            metrics = tool.get_key_metrics(data)
            if metrics and isinstance(metrics, dict):
                print("✓ Key metrics extracted successfully")
                print(f"  Metrics keys: {list(metrics.keys())}")
                return True
            else:
                print("✗ Failed to extract key metrics")
                return False
        else:
            print("✗ No data available for metrics extraction")
            return False
    except Exception as e:
        print(f"✗ Error extracting key metrics: {e}")
        return False


def test_cache_functionality():
    """Test cache functionality"""
    print("Testing cache functionality...")
    try:
        tool = AKShareFinancialDataTool()
        
        # Get data first time (should fetch from network)
        data1 = tool.get_financial_reports("600519", "贵州茅台")
        
        # Get data second time (should fetch from cache)
        data2 = tool.get_financial_reports("600519", "贵州茅台")
        
        if data1 and data2:
            # Check if data is consistent
            income1_len = len(data1.get('income', pd.DataFrame()))
            income2_len = len(data2.get('income', pd.DataFrame()))
            
            if income1_len == income2_len:
                print("✓ Cache functionality working correctly")
                return True
            else:
                print("✗ Cache data inconsistency detected")
                return False
        else:
            print("✗ Failed to test cache functionality")
            return False
    except Exception as e:
        print(f"✗ Error testing cache functionality: {e}")
        return False


def main():
    """Run all tests"""
    print("=== Financial Data Tool Tests ===\n")
    
    tests = [
        test_tool_initialization,
        test_get_financial_reports,
        test_get_key_metrics,
        test_cache_functionality
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