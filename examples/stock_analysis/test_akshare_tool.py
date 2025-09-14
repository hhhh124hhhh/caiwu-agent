"""
AKShare数据获取工具测试脚本
验证所有功能是否正常工作
"""

import os
import sys
import pandas as pd
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from akshare_data_fetcher import AKShareDataFetcher

def test_basic_functionality():
    """测试基础功能"""
    print("=== 测试基础功能 ===")
    
    fetcher = AKShareDataFetcher(save_dir="./test_workspace")
    
    # 测试股票基本信息获取
    print("\n1. 测试股票基本信息获取...")
    test_stocks = ["600519", "000858", "300750", "688036", "832175"]
    
    for stock_code in test_stocks:
        try:
            basic_info = fetcher.get_stock_basic_info(stock_code)
            if not basic_info.empty:
                name = basic_info.get('名称', '').iloc[0]
                price = basic_info.get('最新价', '').iloc[0]
                print(f"   ✓ {stock_code} ({name}): {price:.2f}元")
            else:
                print(f"   ✗ {stock_code}: 未找到信息")
        except Exception as e:
            print(f"   ✗ {stock_code}: 错误 - {e}")
    
    print("\n基础功能测试完成！")

def test_financial_reports():
    """测试财务报表获取"""
    print("\n=== 测试财务报表获取 ===")
    
    fetcher = AKShareDataFetcher(save_dir="./test_workspace")
    
    # 测试财务报表获取
    print("\n1. 测试财务报表获取...")
    stock_code = "600519"
    
    try:
        reports = fetcher.get_financial_report(stock_code)
        if reports:
            for report_type, df in reports.items():
                if not df.empty:
                    print(f"   ✓ {report_type}: {len(df)} 条记录")
                else:
                    print(f"   ✗ {report_type}: 无数据")
        else:
            print("   ✗ 未获取到任何财务报表")
    except Exception as e:
        print(f"   ✗ 财务报表获取失败: {e}")
    
    print("\n财务报表测试完成！")

def test_multi_year_data():
    """测试多年数据获取"""
    print("\n=== 测试多年数据获取 ===")
    
    fetcher = AKShareDataFetcher(save_dir="./test_workspace")
    
    # 测试多年数据获取
    print("\n1. 测试多年数据获取...")
    stock_code = "600519"
    
    try:
        multi_year_data = fetcher.get_multi_year_financial_data(stock_code, years=2)
        for report_type, df in multi_year_data.items():
            if not df.empty:
                unique_years = df['报告年份'].nunique()
                print(f"   ✓ {report_type}: {unique_years} 年数据")
            else:
                print(f"   ✗ {report_type}: 无数据")
    except Exception as e:
        print(f"   ✗ 多年数据获取失败: {e}")
    
    print("\n多年数据测试完成！")

def test_market_data():
    """测试市场数据获取"""
    print("\n=== 测试市场数据获取 ===")
    
    fetcher = AKShareDataFetcher(save_dir="./test_workspace")
    
    # 测试市场统计
    print("\n1. 测试市场统计...")
    try:
        stats = fetcher.get_market_statistics()
        if stats:
            total_stocks = stats.get('total_stocks', 0)
            market_summary = stats.get('market_summary', {})
            print(f"   ✓ 总股票数: {total_stocks}")
            print(f"   ✓ 总市值: {market_summary.get('total_market_cap', 0)/1000000000000:.2f}万亿元")
            print(f"   ✓ 上涨家数: {market_summary.get('up_count', 0)}")
            print(f"   ✓ 下跌家数: {market_summary.get('down_count', 0)}")
        else:
            print("   ✗ 未获取到市场统计")
    except Exception as e:
        print(f"   ✗ 市场统计获取失败: {e}")
    
    print("\n市场数据测试完成！")

def test_financial_analysis():
    """测试财务分析功能"""
    print("\n=== 测试财务分析功能 ===")
    
    fetcher = AKShareDataFetcher(save_dir="./test_workspace")
    
    # 测试财务比率计算
    print("\n1. 测试财务比率计算...")
    stock_code = "600519"
    
    try:
        ratios = fetcher.calculate_financial_ratios(stock_code)
        if ratios:
            print(f"   ✓ ROE: {ratios.get('ROE', 0):.2f}%")
            print(f"   ✓ ROA: {ratios.get('ROA', 0):.2f}%")
            print(f"   ✓ 净利率: {ratios.get('net_profit_margin', 0):.2f}%")
            print(f"   ✓ 资产负债率: {ratios.get('debt_to_equity', 0):.2f}%")
        else:
            print("   ✗ 未获取到财务比率")
    except Exception as e:
        print(f"   ✗ 财务比率计算失败: {e}")
    
    # 测试财务摘要
    print("\n2. 测试财务摘要...")
    try:
        summary = fetcher.get_financial_summary(stock_code, years=2)
        if summary:
            trends = summary.get('financial_trends', {})
            risks = summary.get('risk_indicators', {})
            print(f"   ✓ 营收趋势: {trends.get('revenue_trend', '未知')}")
            print(f"   ✓ 利润趋势: {trends.get('profit_trend', '未知')}")
            print(f"   ✓ 整体风险: {risks.get('overall_risk', '未知')}")
        else:
            print("   ✗ 未获取到财务摘要")
    except Exception as e:
        print(f"   ✗ 财务摘要生成失败: {e}")
    
    print("\n财务分析测试完成！")

def test_comprehensive_report():
    """测试综合报告生成"""
    print("\n=== 测试综合报告生成 ===")
    
    fetcher = AKShareDataFetcher(save_dir="./test_workspace")
    
    # 测试综合报告生成
    print("\n1. 测试综合报告生成...")
    stock_code = "600519"
    
    try:
        report = fetcher.generate_comprehensive_report(stock_code, years=2)
        if report:
            print("   ✓ 综合报告生成成功")
            print(f"   ✓ 包含基本信息: {'是' if report.get('basic_info') is not None else '否'}")
            print(f"   ✓ 包含财务报表: {len(report.get('financial_reports', {}))} 种")
            print(f"   ✓ 包含财务比率: {'是' if report.get('calculated_ratios') else '否'}")
            print(f"   ✓ 同行业股票: {len(report.get('peers', []))} 只")
        else:
            print("   ✗ 综合报告生成失败")
    except Exception as e:
        print(f"   ✗ 综合报告生成失败: {e}")
    
    print("\n综合报告测试完成！")

def check_files_created():
    """检查生成的文件"""
    print("\n=== 检查生成的文件 ===")
    
    test_dir = "./test_workspace"
    if os.path.exists(test_dir):
        files = os.listdir(test_dir)
        print(f"\n在 {test_dir} 目录中找到 {len(files)} 个文件:")
        for file in files:
            file_path = os.path.join(test_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"   - {file} ({file_size} 字节)")
    else:
        print(f"   ✗ 目录 {test_dir} 不存在")

def main():
    """主函数"""
    print("AKShare数据获取工具功能测试")
    print("="*60)
    print("本脚本将测试所有主要功能是否正常工作")
    print("="*60 + "\n")
    
    try:
        # 运行所有测试
        test_basic_functionality()
        test_financial_reports()
        test_multi_year_data()
        test_market_data()
        test_financial_analysis()
        test_comprehensive_report()
        
        # 检查生成的文件
        check_files_created()
        
        print("\n" + "="*60)
        print("所有测试完成！")
        print("请查看上述测试结果，确认功能是否正常。")
        
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()