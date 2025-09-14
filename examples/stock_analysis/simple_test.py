"""
简化测试脚本，用于诊断AKShare数据获取工具的问题
"""

import os
import sys
import pandas as pd

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from akshare_data_fetcher import AKShareDataFetcher

def test_basic_functionality():
    """测试基础功能"""
    print("=== 测试基础功能 ===")
    
    fetcher = AKShareDataFetcher(save_dir="./test_workspace")
    
    # 测试获取市场数据
    print("\n1. 测试获取市场数据...")
    try:
        market_data = fetcher.get_market_overview()
        print(f"   ✓ 成功获取市场数据，包含 {len(market_data)} 个市场")
    except Exception as e:
        print(f"   ✗ 获取市场数据失败: {e}")
    
    # 测试获取市场统计
    print("\n2. 测试获取市场统计...")
    try:
        stats = fetcher.get_market_statistics()
        print(f"   ✓ 成功获取市场统计")
        print(f"   ✓ 总股票数: {stats.get('total_stocks', 0)}")
    except Exception as e:
        print(f"   ✗ 获取市场统计失败: {e}")
    
    print("\n基础功能测试完成！")

def test_financial_reports():
    """测试财务报表获取"""
    print("\n=== 测试财务报表获取 ===")
    
    fetcher = AKShareDataFetcher(save_dir="./test_workspace")
    
    # 测试获取新浪财务报表数据
    print("\n1. 测试获取新浪财务报表数据...")
    try:
        reports = fetcher.get_financial_report_sina("600519")
        if reports:
            print(f"   ✓ 成功获取新浪财务报表，包含 {len(reports)} 种报表")
            for report_type, df in reports.items():
                if not df.empty:
                    print(f"     - {report_type}: {len(df)} 条记录")
        else:
            print("   ✗ 未获取到新浪财务报表")
    except Exception as e:
        print(f"   ✗ 获取新浪财务报表失败: {e}")
    
    print("\n财务报表测试完成！")

def main():
    """主函数"""
    print("AKShare数据获取工具简化测试")
    print("="*50)
    
    try:
        # 运行测试
        test_basic_functionality()
        test_financial_reports()
        
        print("\n" + "="*50)
        print("简化测试完成！")
        
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()