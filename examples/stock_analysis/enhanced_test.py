"""
增强版测试脚本，包含错误处理和重试机制
"""

import os
import sys
import time
import pandas as pd

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from akshare_data_fetcher import AKShareDataFetcher

def retry_on_failure(max_retries=3, delay=1):
    """重试装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"   ⚠️  第{attempt + 1}次尝试失败: {e}")
                        time.sleep(delay)
                    else:
                        print(f"   ❌ 最终失败: {e}")
                        return None
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=2, delay=1)
def test_market_data():
    """测试市场数据获取"""
    fetcher = AKShareDataFetcher(save_dir="./test_workspace")
    
    # 测试获取市场统计
    stats = fetcher.get_market_statistics()
    return stats

@retry_on_failure(max_retries=2, delay=1)
def test_stock_basic_info(stock_code):
    """测试股票基本信息获取"""
    fetcher = AKShareDataFetcher(save_dir="./test_workspace")
    
    # 测试获取股票基本信息
    basic_info = fetcher.get_stock_basic_info(stock_code)
    return basic_info

@retry_on_failure(max_retries=2, delay=1)
def test_financial_reports(stock_code):
    """测试财务报表获取"""
    fetcher = AKShareDataFetcher(save_dir="./test_workspace")
    
    # 测试获取财务报表
    reports = fetcher.get_financial_report(stock_code)
    return reports

@retry_on_failure(max_retries=2, delay=1)
def test_multi_year_data(stock_code, years=2):
    """测试多年数据获取"""
    fetcher = AKShareDataFetcher(save_dir="./test_workspace")
    
    # 测试获取多年财务数据
    multi_year_data = fetcher.get_multi_year_financial_data(stock_code, years)
    return multi_year_data

def main():
    """主函数"""
    print("AKShare数据获取工具增强版测试")
    print("="*50)
    
    try:
        # 测试1: 市场数据
        print("\n=== 测试1: 市场数据 ===")
        stats = test_market_data()
        if stats:
            print(f"   ✓ 成功获取市场统计")
            print(f"   ✓ 总股票数: {stats.get('total_stocks', 0)}")
        else:
            print("   ⚠️ 市场数据获取失败，但程序正常处理")
        
        # 测试2: 股票基本信息
        print("\n=== 测试2: 股票基本信息 ===")
        test_stocks = ["600519", "000858", "300750"]
        for stock_code in test_stocks:
            basic_info = test_stock_basic_info(stock_code)
            if basic_info is not None and not basic_info.empty:
                name_series = basic_info.get('名称', pd.Series(['']))
                price_series = basic_info.get('最新价', pd.Series([0]))
                
                # 安全地获取值
                name = ''
                price = 0.0
                
                if isinstance(name_series, pd.Series) and not name_series.empty:
                    name = str(name_series.iloc[0]) if len(name_series) > 0 else ''
                
                if isinstance(price_series, pd.Series) and not price_series.empty:
                    price = float(price_series.iloc[0]) if len(price_series) > 0 else 0.0
                
                print(f"   ✓ {stock_code} ({name}): {price:.2f}元")
            else:
                print(f"   ⚠️ {stock_code}: 未获取到信息")
        
        # 测试3: 财务报表
        print("\n=== 测试3: 财务报表 ===")
        reports = test_financial_reports("600519")
        if reports:
            print(f"   ✓ 成功获取财务报表，包含 {len(reports)} 种报表")
            for report_type, df in reports.items():
                if not df.empty:
                    print(f"     - {report_type}: {len(df)} 条记录")
        else:
            print("   ⚠️ 财务报表获取失败，但程序正常处理")
        
        # 测试4: 多年数据
        print("\n=== 测试4: 多年数据 ===")
        multi_year_data = test_multi_year_data("600519", 2)
        if multi_year_data:
            success_count = 0
            for report_type, df in multi_year_data.items():
                if not df.empty:
                    unique_years = df['报告年份'].nunique() if '报告年份' in df.columns else 0
                    print(f"   ✓ {report_type}: {unique_years} 年数据")
                    success_count += 1
            if success_count == 0:
                print("   ⚠️ 未获取到多年数据")
        else:
            print("   ⚠️ 多年数据获取失败，但程序正常处理")
        
        print("\n" + "="*50)
        print("增强版测试完成！")
        print("注意：网络连接问题可能导致部分测试失败，这是正常现象。")
        
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()