#!/usr/bin/env python3
"""
直接AKShare数据获取脚本 - 零token消耗
直接获取陕西建工财务数据并生成简单报告
"""

import asyncio
import pathlib
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

def setup_environment():
    """设置环境"""
    # 添加项目根目录到Python路径
    project_root = pathlib.Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # 创建工作目录
    workspace_path = pathlib.Path(__file__).parent / "stock_analysis_workspace"
    workspace_path.mkdir(exist_ok=True)
    
    return workspace_path

def test_akshare_availability():
    """测试AKShare是否可用"""
    try:
        import akshare as ak
        print("✓ AKShare导入成功")
        return ak
    except ImportError:
        print("✗ AKShare未安装，正在安装...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "akshare>=1.12.0"])
        import akshare as ak
        print("✓ AKShare安装成功")
        return ak

def get_financial_data(ak, stock_code="600248", stock_name="陕西建工"):
    """获取财务数据"""
    print(f"正在获取{stock_name}({stock_code})的财务数据...")
    
    # 转换股票代码格式（添加市场标识）
    if stock_code.startswith('6'):
        symbol = f"SH{stock_code}"
    elif stock_code.startswith('0') or stock_code.startswith('3'):
        symbol = f"SZ{stock_code}"
    else:
        symbol = stock_code
    
    print(f"股票代码转换: {stock_code} -> {symbol}")
    
    data = {}
    
    try:
        # 获取利润表
        print("  获取利润表...")
        income_df = ak.stock_profit_sheet_by_report_em(symbol=symbol)
        data['income'] = income_df
        print(f"    ✓ 利润表: {len(income_df)}行数据")
        
        # 获取资产负债表
        print("  获取资产负债表...")
        balance_df = ak.stock_balance_sheet_by_report_em(symbol=symbol)
        data['balance'] = balance_df
        print(f"    ✓ 资产负债表: {len(balance_df)}行数据")
        
        # 获取现金流量表
        print("  获取现金流量表...")
        cashflow_df = ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)
        data['cashflow'] = cashflow_df
        print(f"    ✓ 现金流量表: {len(cashflow_df)}行数据")
        
        return data
        
    except Exception as e:
        print(f"✗ 数据获取失败: {e}")
        return None

def clean_financial_data(data):
    """清洗财务数据"""
    print("清洗财务数据...")
    
    cleaned_data = {}
    
    for name, df in data.items():
        try:
            # 不直接删除所有空值，而是保留REPORT_DATE非空的行
            df_clean = df[df['REPORT_DATE'].notna()].copy()
            
            # 转换数值列
            for col in df_clean.columns:
                if col not in ['REPORT_DATE', '报表类型', 'REPORT_TYPE', 'SECUCODE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR']:
                    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            
            # 转换报告期并排序
            df_clean['REPORT_DATE'] = pd.to_datetime(df_clean['REPORT_DATE'])
            df_clean = df_clean.sort_values('REPORT_DATE', ascending=False)
            
            cleaned_data[name] = df_clean
            print(f"  ✓ {name}清洗完成，共{len(df_clean)}行数据")
            
        except Exception as e:
            print(f"  ✗ {name}清洗失败: {e}")
            cleaned_data[name] = df
    
    return cleaned_data

def extract_key_metrics(data):
    """提取关键财务指标"""
    print("提取关键财务指标...")
    
    metrics = {}
    
    try:
        # 获取最新一期数据
        latest_income = data['income'].iloc[0]
        latest_balance = data['balance'].iloc[0]
        latest_cashflow = data['cashflow'].iloc[0]
        
        # 盈利能力指标 (使用新的列名)
        revenue = latest_income.get('TOTAL_OPERATE_INCOME', 0) / 1e8  # 亿元
        net_profit = latest_income.get('NETPROFIT', 0) / 1e8
        parent_profit = latest_income.get('PARENT_NETPROFIT', 0) / 1e8
        
        metrics['盈利能力'] = {
            '营业收入(亿元)': revenue,
            '净利润(亿元)': net_profit,
            '归母净利润(亿元)': parent_profit,
            '净利率(%)': (net_profit / revenue * 100) if revenue > 0 else 0
        }
        
        # 财务状况指标 (使用新的列名)
        total_assets = latest_balance.get('TOTAL_ASSETS', 0) / 1e8
        total_liabilities = latest_balance.get('TOTAL_LIABILITIES', 0) / 1e8
        total_equity = latest_balance.get('TOTAL_EQUITY', 0) / 1e8
        
        metrics['财务状况'] = {
            '总资产(亿元)': total_assets,
            '总负债(亿元)': total_liabilities,
            '净资产(亿元)': total_equity,
            '资产负债率(%)': (total_liabilities / total_assets * 100) if total_assets > 0 else 0
        }
        
        # 计算ROE
        if total_equity > 0:
            roe = parent_profit / total_equity * 100
            metrics['盈利能力']['ROE(%)'] = roe
        
        print("  ✓ 关键指标提取完成")
        return metrics
        
    except Exception as e:
        print(f"  ✗ 指标提取失败: {e}")
        return None

def generate_trend_chart(data, workspace_path):
    """生成趋势图"""
    print("生成趋势分析图...")
    
    try:
        # 准备数据 - 获取最近4年数据
        income_data = data['income'].head(4).copy()
        
        # 转换报告期为年份
        income_data['年份'] = income_data['REPORT_DATE'].dt.year
        
        # 提取关键指标 (使用新的列名)
        trend_data = pd.DataFrame()
        trend_data['年份'] = income_data['年份']
        trend_data['营业收入'] = income_data.get('TOTAL_OPERATE_INCOME', 0) / 1e8
        trend_data['净利润'] = income_data.get('NETPROFIT', 0) / 1e8
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 营业收入趋势
        ax1.plot(trend_data['年份'], trend_data['营业收入'], 'bo-', linewidth=2, markersize=8)
        ax1.set_title('营业收入趋势', fontsize=14, fontweight='bold')
        ax1.set_xlabel('年份')
        ax1.set_ylabel('营业收入（亿元）')
        ax1.grid(True, alpha=0.3)
        
        # 添加数据标签
        for i, v in enumerate(trend_data['营业收入']):
            ax1.annotate(f'{v:.0f}', (trend_data['年份'].iloc[i], v), 
                        textcoords="offset points", xytext=(0,10), ha='center')
        
        # 净利润趋势
        ax2.plot(trend_data['年份'], trend_data['净利润'], 'ro-', linewidth=2, markersize=8)
        ax2.set_title('净利润趋势', fontsize=14, fontweight='bold')
        ax2.set_xlabel('年份')
        ax2.set_ylabel('净利润（亿元）')
        ax2.grid(True, alpha=0.3)
        
        # 添加数据标签
        for i, v in enumerate(trend_data['净利润']):
            ax2.annotate(f'{v:.0f}', (trend_data['年份'].iloc[i], v), 
                        textcoords="offset points", xytext=(0,10), ha='center')
        
        plt.tight_layout()
        
        # 保存图表
        chart_path = workspace_path / "financial_trend.png"
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ 趋势图已保存到: {chart_path}")
        return chart_path
        
    except Exception as e:
        print(f"  ✗ 图表生成失败: {e}")
        return None

def generate_html_report(metrics, chart_path, workspace_path, report_date=None):
    """生成HTML报告
    
    Args:
        metrics: 财务指标数据
        chart_path: 图表路径
        workspace_path: 工作目录路径
        report_date: 报告日期，如果不提供则使用当前时间
    """
    print("生成HTML分析报告...")
    
    try:
        # 使用传入的报告日期或当前时间
        report_date_display = report_date if report_date else datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        
        # 创建HTML内容
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>陕西建工财务分析报告</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #2980b9;
        }}
        .metric-label {{
            font-size: 14px;
            color: #7f8c8d;
            margin-top: 5px;
        }}
        .chart-container {{
            text-align: center;
            margin: 30px 0;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #7f8c8d;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>陕西建工(600248.SH)财务分析报告</h1>
        <p style="text-align: center; color: #7f8c8d;">
            生成时间: {report_date_display}
        </p>
        
        <h2>盈利能力指标</h2>
        <div class="metrics-grid">
        """
        
        # 添加盈利能力指标
        for key, value in metrics['盈利能力'].items():
            if isinstance(value, float):
                display_value = f"{value:.2f}"
            else:
                display_value = f"{value:,.0f}"
            html_content += f"""
            <div class="metric-card">
                <div class="metric-value">{display_value}</div>
                <div class="metric-label">{key}</div>
            </div>
            """
        
        html_content += """
        </div>
        
        <h2>财务状况指标</h2>
        <div class="metrics-grid">
        """
        
        # 添加财务状况指标
        for key, value in metrics['财务状况'].items():
            if isinstance(value, float):
                display_value = f"{value:.2f}"
            else:
                display_value = f"{value:,.0f}"
            html_content += f"""
            <div class="metric-card">
                <div class="metric-value">{display_value}</div>
                <div class="metric-label">{key}</div>
            </div>
            """
        
        html_content += f"""
        </div>
        
        <div class="chart-container">
            <h2>财务趋势图</h2>
            <img src="financial_trend.png" alt="财务趋势图">
        </div>
        
        <div class="footer">
            <p>本报告由AKShare数据自动生成 | 仅供参考，不构成投资建议</p>
        </div>
    </div>
</body>
</html>
        """
        
        # 保存HTML报告
        report_path = workspace_path / "financial_analysis_report.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"  ✓ HTML报告已保存到: {report_path}")
        return report_path
        
    except Exception as e:
        print(f"  ✗ 报告生成失败: {e}")
        return None

def main():
    """主函数"""
    print("=== 直接AKShare财务分析工具 ===")
    print("特点：零token消耗，直接获取和分析数据\n")
    
    # 设置环境
    workspace_path = setup_environment()
    
    # 测试AKShare
    ak = test_akshare_availability()
    
    # 获取财务数据
    data = get_financial_data(ak)
    if not data:
        print("数据获取失败，程序退出")
        return
    
    # 清洗数据
    cleaned_data = clean_financial_data(data)
    
    # 提取关键指标
    metrics = extract_key_metrics(cleaned_data)
    if not metrics:
        print("指标提取失败，程序退出")
        return
    
    # 显示关键指标
    print(f"\n=== 陕西建工关键财务指标 ===")
    for category, indicators in metrics.items():
        print(f"\n【{category}】")
        for key, value in indicators.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value:,.0f}")
    
    # 生成趋势图
    chart_path = generate_trend_chart(cleaned_data, workspace_path)
    
    # 设置报告日期（使用当前时间）
    from datetime import datetime
    report_date = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
    
    # 生成HTML报告
    report_path = generate_html_report(metrics, chart_path, workspace_path, report_date)
    
    # 总结
    print(f"\n=== 分析完成 ===")
    print(f"工作目录: {workspace_path}")
    
    # 列出生成的文件
    generated_files = list(workspace_path.glob("*"))
    print(f"\n生成的文件:")
    for file in sorted(generated_files):
        size_kb = file.stat().st_size / 1024
        print(f"  - {file.name} ({size_kb:.1f} KB)")
    
    print(f"\n🎉 分析完成！查看HTML报告了解详细分析结果。")
    print("提示：此方法完全不消耗LLM token，成本最低。")

if __name__ == "__main__":
    main()