#!/usr/bin/env python3
"""
修复后的季度环比增长率图表生成代码
解决了变量名冲突和数据格式问题
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
import os
import re

def generate_quarterly_growth_chart():
    """生成陕西建工季度环比增长率图表"""

    # 设置中文字体
    rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
    rcParams['axes.unicode_minus'] = False

    # 季度数据（单位：亿元）
    quarters = ['2024Q1', '2024Q2', '2024Q3', '2024Q4', '2025Q1']
    revenue_values = [150.2, 320.5, 480.8, 650.1, 180.3]
    net_profit_values = [3.2, 7.8, 12.5, 15.6, 4.1]

    # 计算环比增长率 - 修复变量名冲突
    revenue_growth_rates = []
    profit_growth_rates = []

    # 修复：使用不同的变量名避免冲突
    for i in range(1, len(revenue_values)):
        rev_growth = (revenue_values[i] - revenue_values[i-1]) / revenue_values[i-1] * 100
        profit_growth = (net_profit_values[i] - net_profit_values[i-1]) / net_profit_values[i-1] * 100

        revenue_growth_rates.append(rev_growth)
        profit_growth_rates.append(profit_growth)

    growth_quarters = ['2024Q2', '2024Q3', '2024Q4', '2025Q1']

    # 创建环比增长率图表
    fig, ax = plt.subplots(figsize=(12, 8))

    x = np.arange(len(growth_quarters))
    width = 0.35

    bars1 = ax.bar(x - width/2, revenue_growth_rates, width,
                   label='营业收入环比增长(%)', color='#1f77b4', alpha=0.7)
    bars2 = ax.bar(x + width/2, profit_growth_rates, width,
                   label='净利润环比增长(%)', color='#ff7f0e', alpha=0.7)

    ax.set_xlabel('季度')
    ax.set_ylabel('环比增长率(%)')
    ax.set_title('陕西建工季度环比增长率分析', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(growth_quarters)
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 添加数值标签
    for bar, value in zip(bars1, revenue_growth_rates):
        label_height = bar.get_height()
        text_y = label_height + (5 if label_height > 0 else -15)
        text_va = 'bottom' if label_height > 0 else 'top'
        ax.text(bar.get_x() + bar.get_width()/2, text_y,
               f'{value:.1f}%', ha='center', va=text_va, fontsize=10)

    for bar, value in zip(bars2, profit_growth_rates):
        label_height = bar.get_height()
        text_y = label_height + (5 if label_height > 0 else -15)
        text_va = 'bottom' if label_height > 0 else 'top'
        ax.text(bar.get_x() + bar.get_width()/2, text_y,
               f'{value:.1f}%', ha='center', va=text_va, fontsize=10)

    plt.tight_layout()

    # 确保输出目录存在
    output_dir = './run_workdir'
    os.makedirs(output_dir, exist_ok=True)

    # 保存图表
    chart_filename = '陕西建工季度环比增长率分析.png'
    chart_path = os.path.join(output_dir, chart_filename)
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"季度环比增长率分析图表已生成并保存: {chart_path}")

    # 输出分析结果
    print("\n=== 环比增长率分析结果 ===")
    print("季度    营业收入环比增长率(%)    净利润环比增长率(%)")
    print("-" * 50)
    for i, quarter in enumerate(growth_quarters):
        print(f"{quarter}    {revenue_growth_rates[i]:8.1f}            {profit_growth_rates[i]:8.1f}")

    # 分析趋势
    avg_revenue_growth = sum(revenue_growth_rates) / len(revenue_growth_rates)
    avg_profit_growth = sum(profit_growth_rates) / len(profit_growth_rates)

    print(f"\n平均环比增长率:")
    print(f"  营业收入: {avg_revenue_growth:.1f}%")
    print(f"  净利润: {avg_profit_growth:.1f}%")

    # 检查2025Q1是否异常下降
    if revenue_growth_rates[-1] < -50:
        print(f"\n⚠️  注意: 2025Q1营业收入环比下降{abs(revenue_growth_rates[-1]):.1f}%，可能存在季节性因素")
    if profit_growth_rates[-1] < -50:
        print(f"⚠️  注意: 2025Q1净利润环比下降{abs(profit_growth_rates[-1]):.1f}%，可能存在季节性因素")

    return chart_path

def generate_standard_format_chart_data():
    """生成符合图表生成工具标准格式的数据"""

    # 准备标准格式的数据
    chart_data = {
        "title": "陕西建工季度财务指标趋势对比",
        "x_axis": ["2024Q1", "2024Q2", "2024Q3", "2024Q4", "2025Q1"],
        "series": [
            {
                "name": "营业收入(亿元)",
                "data": [150.2, 320.5, 480.8, 650.1, 180.3]
            },
            {
                "name": "净利润(亿元)",
                "data": [3.2, 7.8, 12.5, 15.6, 4.1]
            },
            {
                "name": "资产负债率(%)",
                "data": [87.2, 88.1, 88.9, 89.3, 88.7]
            },
            {
                "name": "ROE(%)",
                "data": [2.1, 2.4, 2.7, 3.0, 2.7]
            }
        ]
    }

    return chart_data

def main():
    """主函数"""
    print("=== 修复后的季度图表生成测试 ===")

    try:
        # 1. 生成环比增长率图表
        chart_path = generate_quarterly_growth_chart()

        # 2. 生成标准格式数据
        standard_data = generate_standard_format_chart_data()

        print(f"\n=== 标准格式数据 ===")
        print("图表标题:", standard_data['title'])
        print("X轴标签:", standard_data['x_axis'])
        print("数据系列:")
        for series in standard_data['series']:
            print(f"  - {series['name']}: {series['data']}")

        # 3. 验证数据格式
        required_fields = ['title', 'x_axis', 'series']
        missing_fields = [field for field in required_fields if field not in standard_data]

        if missing_fields:
            print(f"\n❌ 数据格式不完整，缺少字段: {missing_fields}")
        else:
            print(f"\n✅ 数据格式验证通过，可以用于图表生成工具")

        return True

    except Exception as e:
        print(f"❌ 生成过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)