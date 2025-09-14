"""
AKShare数据获取示例
演示如何使用AKShare获取A股财务数据
"""

import akshare as ak
import pandas as pd
import os
from datetime import datetime

def example_akshare_usage():
    """AKShare使用示例"""
    
    print("=== AKShare A股财务数据获取示例 ===\n")
    
    # 创建输出目录
    output_dir = "./akshare_examples"
    os.makedirs(output_dir, exist_ok=True)
    
    # 示例1：获取股票基本信息
    print("1. 获取A股实时行情数据...")
    try:
        # 获取A股实时行情
        spot_data = ak.stock_zh_a_spot_em()
        print(f"   获取到 {len(spot_data)} 只股票的实时行情数据")
        print(f"   列名: {list(spot_data.columns)}")
        
        # 筛选几只知名股票
        famous_stocks = ['600519', '000858', '002304', '000002', '600036']
        sample_data = spot_data[spot_data['代码'].isin(famous_stocks)]
        
        # 保存数据
        sample_data.to_csv(f"{output_dir}/famous_stocks_spot.csv", index=False, encoding='utf-8-sig')
        print(f"   知名股票数据已保存到: {output_dir}/famous_stocks_spot.csv")
        print(f"   示例数据:\n{sample_data[['代码', '名称', '最新价', '涨跌幅', '成交量']]}")
        
    except Exception as e:
        print(f"   获取实时行情失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 示例2：获取财务报表数据
    print("2. 获取财务报表数据...")
    
    # 使用最近一个季度的数据
    current_date = datetime.now()
    if current_date.month >= 9:
        report_date = f"{current_date.year}0930"  # 三季报
    elif current_date.month >= 6:
        report_date = f"{current_date.year}0630"  # 半年报
    elif current_date.month >= 3:
        report_date = f"{current_date.year}0331"  # 一季报
    else:
        report_date = f"{current_date.year-1}1231"  # 年报
    
    print(f"   使用报告日期: {report_date}")
    
    # 获取利润表
    try:
        income_data = ak.stock_lrb_em(date=report_date)
        print(f"   利润表数据: {len(income_data)} 条记录")
        
        # 筛选贵州茅台
        maotai_income = income_data[income_data['股票代码'] == '600519']
        if not maotai_income.empty:
            maotai_income.to_csv(f"{output_dir}/maotai_income_{report_date}.csv", index=False, encoding='utf-8-sig')
            print(f"   贵州茅台利润表已保存")
            print(f"   关键指标: 营业收入={maotai_income['营业收入'].iloc[0]:,.0f}元")
        
    except Exception as e:
        print(f"   获取利润表失败: {e}")
    
    # 获取资产负债表
    try:
        balance_data = ak.stock_zcfz_em(date=report_date)
        print(f"   资产负债表数据: {len(balance_data)} 条记录")
        
        # 筛选贵州茅台
        maotai_balance = balance_data[balance_data['股票代码'] == '600519']
        if not maotai_balance.empty:
            maotai_balance.to_csv(f"{output_dir}/maotai_balance_{report_date}.csv", index=False, encoding='utf-8-sig')
            print(f"   贵州茅台资产负债表已保存")
            print(f"   关键指标: 总资产={maotai_balance['资产-总资产'].iloc[0]:,.0f}元")
        
    except Exception as e:
        print(f"   获取资产负债表失败: {e}")
    
    # 获取现金流量表
    try:
        cashflow_data = ak.stock_xjll_em(date=report_date)
        print(f"   现金流量表数据: {len(cashflow_data)} 条记录")
        
        # 筛选贵州茅台
        maotai_cashflow = cashflow_data[cashflow_data['股票代码'] == '600519']
        if not maotai_cashflow.empty:
            maotai_cashflow.to_csv(f"{output_dir}/maotai_cashflow_{report_date}.csv", index=False, encoding='utf-8-sig')
            print(f"   贵州茅台现金流量表已保存")
        
    except Exception as e:
        print(f"   获取现金流量表失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 示例3：获取历史股价数据
    print("3. 获取历史股价数据...")
    try:
        # 获取贵州茅台历史数据
        stock_code = "600519"
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - pd.DateOffset(years=1)).strftime('%Y%m%d')
        
        hist_data = ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date, end_date=end_date, adjust="hfq")
        print(f"   获取到 {len(hist_data)} 天的历史数据")
        
        if not hist_data.empty:
            hist_data.to_csv(f"{output_dir}/{stock_code}_historical.csv", index=False, encoding='utf-8-sig')
            print(f"   历史数据已保存到: {output_dir}/{stock_code}_historical.csv")
            
            # 计算基本统计
            latest_price = hist_data['收盘'].iloc[-1]
            year_high = hist_data['收盘'].max()
            year_low = hist_data['收盘'].min()
            print(f"   最新价格: {latest_price:.2f}元")
            print(f"   年内最高: {year_high:.2f}元")
            print(f"   年内最低: {year_low:.2f}元")
        
    except Exception as e:
        print(f"   获取历史数据失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 示例4：行业数据对比
    print("4. 获取行业对比数据...")
    try:
        # 白酒行业主要股票
        liquor_stocks = ['600519', '000858', '002304', '000596', '000799']
        
        # 获取这些股票的财务指标
        industry_data = []
        for stock in liquor_stocks:
            try:
                stock_income = income_data[income_data['股票代码'] == stock]
                if not stock_income.empty:
                    stock_name = stock_income['股票简称'].iloc[0]
                    revenue = stock_income['营业收入'].iloc[0]
                    net_profit = stock_income['净利润'].iloc[0]
                    
                    industry_data.append({
                        '股票代码': stock,
                        '股票简称': stock_name,
                        '营业收入': revenue,
                        '净利润': net_profit
                    })
            except Exception as e:
                print(f"   处理股票 {stock} 失败: {e}")
        
        if industry_data:
            industry_df = pd.DataFrame(industry_data)
            industry_df.to_csv(f"{output_dir}/liquor_industry_comparison.csv", index=False, encoding='utf-8-sig')
            print(f"   白酒行业对比数据已保存")
            print(f"   行业数据:\n{industry_df}")
        
    except Exception as e:
        print(f"   获取行业对比数据失败: {e}")
    
    print("\n" + "="*50 + "\n")
    print("AKShare数据获取示例完成！")
    print(f"所有数据已保存到: {output_dir}/")

def example_multi_year_analysis():
    """多年财务分析示例"""
    print("\n=== 多年财务分析示例 ===")
    
    # 获取贵州茅台多年数据
    stock_code = "600519"
    current_year = datetime.now().year
    
    for year in [current_year-2, current_year-1, current_year]:
        report_date = f"{year}1231"
        
        try:
            # 获取利润表
            income_data = ak.stock_lrb_em(date=report_date)
            maotai_income = income_data[income_data['股票代码'] == stock_code]
            
            if not maotai_income.empty:
                revenue = maotai_income['营业收入'].iloc[0]
                net_profit = maotai_income['净利润'].iloc[0]
                
                print(f"{year}年: 营业收入={revenue:,.0f}元, 净利润={net_profit:,.0f}元")
            
        except Exception as e:
            print(f"获取{year}年数据失败: {e}")

if __name__ == "__main__":
    example_akshare_usage()
    example_multi_year_analysis()