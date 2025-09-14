"""
增强版AKShare数据获取工具示例
展示完整的A股财务分析功能
"""

import sys
import os
import pandas as pd
from datetime import datetime
import json

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from akshare_data_fetcher import AKShareDataFetcher

def example_comprehensive_analysis():
    """综合分析示例"""
    print("=== A股财务分析综合示例 ===\n")
    
    # 创建数据获取器
    fetcher = AKShareDataFetcher(save_dir="./comprehensive_analysis_workspace")
    
    # 示例股票（涵盖不同市场类型）
    example_stocks = {
        '600519': '贵州茅台',  # 上海主板
        '000858': '五粮液',    # 深圳主板
        '300750': '宁德时代',  # 创业板
        '688036': '传音控股',  # 科创板
        '832175': '东方碳素'   # 北交所
    }
    
    for stock_code, stock_name in example_stocks.items():
        print(f"--- 分析 {stock_name}({stock_code}) ---")
        
        # 1. 获取基本信息
        print("\n1. 获取股票基本信息...")
        basic_info = fetcher.get_stock_basic_info(stock_code)
        if not basic_info.empty:
            print(f"   股票名称: {basic_info.get('名称', '').iloc[0]}")
            print(f"   最新价格: {basic_info.get('最新价', '').iloc[0]:.2f}元")
            print(f"   市盈率: {basic_info.get('市盈率-动态', '').iloc[0]:.2f}")
            print(f"   总市值: {basic_info.get('总市值', '').iloc[0]/100000000:.2f}亿元")
        
        # 2. 获取财务报表
        print("\n2. 获取最新财务报表...")
        reports = fetcher.get_financial_report(stock_code)
        if reports:
            for report_type, df in reports.items():
                if not df.empty:
                    print(f"   {report_type}: {len(df)} 条记录")
        
        # 3. 获取多年财务数据
        print("\n3. 获取多年财务数据...")
        multi_year_data = fetcher.get_multi_year_financial_data(stock_code, years=3)
        for report_type, df in multi_year_data.items():
            if not df.empty:
                unique_years = df['报告年份'].nunique()
                print(f"   {report_type}: {unique_years} 年数据")
        
        # 4. 计算财务比率
        print("\n4. 计算关键财务比率...")
        ratios = fetcher.calculate_financial_ratios(stock_code)
        if ratios:
            print(f"   ROE: {ratios.get('ROE', 0):.2f}%")
            print(f"   ROA: {ratios.get('ROA', 0):.2f}%")
            print(f"   净利率: {ratios.get('net_profit_margin', 0):.2f}%")
            print(f"   资产负债率: {ratios.get('debt_to_equity', 0):.2f}%")
        
        # 5. 获取财务摘要
        print("\n5. 生成财务分析摘要...")
        summary = fetcher.get_financial_summary(stock_code, years=3)
        if summary:
            trends = summary.get('financial_trends', {})
            print(f"   营收趋势: {trends.get('revenue_trend', '未知')}")
            print(f"   利润趋势: {trends.get('profit_trend', '未知')}")
            print(f"   负债水平: {trends.get('debt_level', '未知')}")
        
        print("\n" + "="*50 + "\n")

def example_market_analysis():
    """市场分析示例"""
    print("=== 市场分析示例 ===\n")
    
    fetcher = AKShareDataFetcher(save_dir="./market_analysis_workspace")
    
    # 1. 获取市场总览
    print("1. 获取市场总览数据...")
    market_data = fetcher.get_market_overview()
    for market_name, df in market_data.items():
        if not df.empty:
            print(f"   {market_name}: {len(df)} 只股票")
    
    print("\n" + "-"*30 + "\n")
    
    # 2. 获取市场统计
    print("2. 获取市场统计信息...")
    stats = fetcher.get_market_statistics()
    if stats:
        market_summary = stats.get('market_summary', {})
        print(f"   总股票数: {stats.get('total_stocks', 0)}")
        print(f"   总市值: {market_summary.get('total_market_cap', 0)/1000000000000:.2f}万亿元")
        print(f"   总成交额: {market_summary.get('total_turnover', 0)/100000000:.2f}亿元")
        print(f"   上涨家数: {market_summary.get('up_count', 0)}")
        print(f"   下跌家数: {market_summary.get('down_count', 0)}")
        print(f"   平盘家数: {market_summary.get('unchanged_count', 0)}")
        print(f"   平均市盈率: {market_summary.get('avg_pe_ratio', 0):.2f}")
        print(f"   平均市净率: {market_summary.get('avg_pb_ratio', 0):.2f}")
    
    print("\n" + "-"*30 + "\n")
    
    # 3. 显示涨幅榜
    print("3. 涨幅榜前10...")
    top_gainers = stats.get('top_gainers', [])
    for i, stock in enumerate(top_gainers[:5], 1):
        print(f"   {i}. {stock['名称']}({stock['代码']}): {stock['涨跌幅']:.2f}%")
    
    print("\n" + "-"*30 + "\n")
    
    # 4. 显示成交额榜
    print("4. 成交额榜前10...")
    most_active = stats.get('most_active', [])
    for i, stock in enumerate(most_active[:5], 1):
        print(f"   {i}. {stock['名称']}({stock['代码']}): {stock['成交额']/100000000:.2f}亿元")

def example_industry_analysis():
    """行业分析示例"""
    print("=== 行业分析示例 ===\n")
    
    fetcher = AKShareDataFetcher(save_dir="./industry_analysis_workspace")
    
    # 白酒行业主要股票
    liquor_stocks = ['600519', '000858', '002304', '000596', '000799', '603369', '603198']
    
    print("白酒行业财务对比分析：\n")
    
    industry_data = []
    for stock_code in liquor_stocks:
        print(f"--- 处理 {stock_code} ---")
        
        # 获取基本信息
        basic_info = fetcher.get_stock_basic_info(stock_code)
        if not basic_info.empty:
            stock_name = basic_info.get('名称', '').iloc[0]
            current_price = basic_info.get('最新价', '').iloc[0]
            market_cap = basic_info.get('总市值', '').iloc[0]
            
            # 获取最新财务报表
            reports = fetcher.get_financial_report(stock_code)
            revenue = 0
            net_profit = 0
            
            if reports and 'income_statement' in reports:
                income_df = reports['income_statement']
                if not income_df.empty and 'revenue' in income_df.columns:
                    revenue = income_df['revenue'].iloc[0]
                if not income_df.empty and 'net_profit' in income_df.columns:
                    net_profit = income_df['net_profit'].iloc[0]
            
            # 计算财务比率
            ratios = fetcher.calculate_financial_ratios(stock_code)
            
            industry_data.append({
                '股票代码': stock_code,
                '股票名称': stock_name,
                '当前价格': current_price,
                '市值(亿元)': market_cap/100000000,
                '营业收入(亿元)': revenue/100000000,
                '净利润(亿元)': net_profit/100000000,
                'ROE(%)': ratios.get('ROE', 0),
                '净利率(%)': ratios.get('net_profit_margin', 0),
                '资产负债率(%)': ratios.get('debt_to_equity', 0)
            })
    
    # 创建行业对比表
    if industry_data:
        industry_df = pd.DataFrame(industry_data)
        
        # 保存数据
        industry_file = os.path.join(fetcher.save_dir, "liquor_industry_analysis.csv")
        industry_df.to_csv(industry_file, index=False, encoding='utf-8-sig')
        print(f"\n行业分析数据已保存到: {industry_file}")
        
        # 显示行业对比结果
        print("\n白酒行业财务指标对比：")
        print(industry_df.to_string(index=False, float_format='%.2f'))
        
        # 计算行业平均值
        print("\n行业平均指标：")
        print(f"   平均ROE: {industry_df['ROE(%)'].mean():.2f}%")
        print(f"   平均净利率: {industry_df['net_profit_margin(%)'].mean():.2f}%")
        print(f"   平均资产负债率: {industry_df['资产负债率(%)'].mean():.2f}%")
        print(f"   总市值: {industry_df['市值(亿元)'].sum():.2f}亿元")

def example_financial_trend_analysis():
    """财务趋势分析示例"""
    print("=== 财务趋势分析示例 ===\n")
    
    fetcher = AKShareDataFetcher(save_dir="./trend_analysis_workspace")
    
    # 分析贵州茅台的财务趋势
    stock_code = "600519"
    stock_name = "贵州茅台"
    
    print(f"分析 {stock_name}({stock_code}) 的财务趋势...\n")
    
    # 获取多年财务数据
    multi_year_data = fetcher.get_multi_year_financial_data(stock_code, years=5)
    
    if multi_year_data['income_statement'].empty:
        print("未能获取到财务数据")
        return
    
    # 分析营收趋势
    income_df = multi_year_data['income_statement']
    if not income_df.empty and 'revenue' in income_df.columns:
        print("营收趋势分析：")
        income_sorted = income_df.sort_values('报告年份')
        for _, row in income_sorted.iterrows():
            year = row['报告年份']
            revenue = row['revenue']
            print(f"   {year}年: {revenue/100000000:.2f}亿元")
        
        # 计算增长率
        if len(income_sorted) >= 2:
            latest_revenue = income_sorted.iloc[-1]['revenue']
            earliest_revenue = income_sorted.iloc[0]['revenue']
            growth_rate = (latest_revenue - earliest_revenue) / earliest_revenue * 100
            print(f"\n   {income_sorted.iloc[-1]['报告年份']}年较{income_sorted.iloc[0]['报告年份']}年增长: {growth_rate:.2f}%")
    
    print("\n" + "-"*30 + "\n")
    
    # 分析利润趋势
    if not income_df.empty and 'net_profit' in income_df.columns:
        print("净利润趋势分析：")
        income_sorted = income_df.sort_values('报告年份')
        for _, row in income_sorted.iterrows():
            year = row['报告年份']
            net_profit = row['net_profit']
            print(f"   {year}年: {net_profit/100000000:.2f}亿元")
    
    print("\n" + "-"*30 + "\n")
    
    # 分析资产趋势
    balance_df = multi_year_data['balance_sheet']
    if not balance_df.empty and 'total_assets' in balance_df.columns:
        print("总资产趋势分析：")
        balance_sorted = balance_df.sort_values('报告年份')
        for _, row in balance_sorted.iterrows():
            year = row['报告年份']
            total_assets = row['total_assets']
            print(f"   {year}年: {total_assets/100000000:.2f}亿元")

def example_comprehensive_report():
    """综合报告生成示例"""
    print("=== 综合报告生成示例 ===\n")
    
    fetcher = AKShareDataFetcher(save_dir="./comprehensive_report_workspace")
    
    # 生成贵州茅台的综合报告
    stock_code = "600519"
    print(f"生成 {stock_code} 的综合分析报告...")
    
    comprehensive_report = fetcher.generate_comprehensive_report(stock_code, years=3)
    
    if comprehensive_report:
        # 保存报告为JSON
        report_file = os.path.join(fetcher.save_dir, f"{stock_code}_comprehensive_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"综合报告已保存到: {report_file}")
        
        # 显示报告摘要
        print("\n报告摘要：")
        print(f"   股票代码: {comprehensive_report.get('stock_code', 'N/A')}")
        print(f"   生成时间: {comprehensive_report.get('timestamp', 'N/A')}")
        
        # 显示基本信息
        basic_info = comprehensive_report.get('basic_info')
        if basic_info is not None and not basic_info.empty:
            print(f"   股票名称: {basic_info.get('名称', 'N/A')}")
            print(f"   最新价格: {basic_info.get('最新价', 'N/A')}元")
        
        # 显示财务比率
        ratios = comprehensive_report.get('calculated_ratios', {})
        if ratios:
            print(f"   ROE: {ratios.get('ROE', 0):.2f}%")
            print(f"   ROA: {ratios.get('ROA', 0):.2f}%")
            print(f"   净利率: {ratios.get('net_profit_margin', 0):.2f}%")
        
        # 显示同行业股票数量
        peers = comprehensive_report.get('peers', [])
        print(f"   同行业股票数: {len(peers)}")

def main():
    """主函数"""
    print("AKShare增强版数据获取工具示例")
    print("="*60)
    print("本示例展示了增强版AKShare数据获取工具的完整功能")
    print("包括：")
    print("1. 综合财务分析")
    print("2. 市场总览分析")
    print("3. 行业对比分析")
    print("4. 财务趋势分析")
    print("5. 综合报告生成")
    print("="*60 + "\n")
    
    try:
        # 运行各个示例
        example_comprehensive_analysis()
        print("\n" + "="*60 + "\n")
        
        example_market_analysis()
        print("\n" + "="*60 + "\n")
        
        example_industry_analysis()
        print("\n" + "="*60 + "\n")
        
        example_financial_trend_analysis()
        print("\n" + "="*60 + "\n")
        
        example_comprehensive_report()
        
        print("\n" + "="*60)
        print("所有示例运行完成！")
        print("请查看生成的workspace目录中的文件。")
        
    except Exception as e:
        print(f"运行示例时发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()