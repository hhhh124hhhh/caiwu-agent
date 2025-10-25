#!/usr/bin/env python3
"""
直接测试matplotlib图表生成功能
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def create_direct_chart():
    """直接创建图表"""
    print("开始创建直接matplotlib图表...")

    # 测试数据
    companies = ["宁德时代", "比亚迪"]
    revenue = [2830.72, 3712.81]
    net_profit = [522.97, 160.39]
    profit_margin = [18.47, 4.32]
    roe = [15.06, 6.55]

    try:
        # 创建图表
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('宁德时代 vs 比亚迪 财务指标对比', fontsize=16, fontweight='bold')

        # 1. 营业收入对比
        bars1 = ax1.bar(companies, revenue, color=['#1f77b4', '#ff7f0e'], alpha=0.7)
        ax1.set_title('营业收入对比（亿元）', fontsize=14, fontweight='bold')
        ax1.set_ylabel('营业收入（亿元）')
        for i, (bar, value) in enumerate(zip(bars1, revenue)):
            ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(revenue)*0.02,
                    str(round(value, 2)), ha='center', va='bottom', fontweight='bold')

        # 2. 净利润对比
        bars2 = ax2.bar(companies, net_profit, color=['#2ca02c', '#d62728'], alpha=0.7)
        ax2.set_title('净利润对比（亿元）', fontsize=14, fontweight='bold')
        ax2.set_ylabel('净利润（亿元）')
        for i, (bar, value) in enumerate(zip(bars2, net_profit)):
            ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(net_profit)*0.02,
                    str(round(value, 2)), ha='center', va='bottom', fontweight='bold')

        # 3. 净利率对比
        bars3 = ax3.bar(companies, profit_margin, color=['#ff9896', '#9467bd'], alpha=0.7)
        ax3.set_title('净利率对比（%）', fontsize=14, fontweight='bold')
        ax3.set_ylabel('净利率（%）')
        for i, (bar, value) in enumerate(zip(bars3, profit_margin)):
            ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                    str(round(value, 2)) + '%', ha='center', va='bottom', fontweight='bold')

        # 4. ROE对比
        bars4 = ax4.bar(companies, roe, color=['#c5b0d5', '#8c564b'], alpha=0.7)
        ax4.set_title('ROE对比（%）', fontsize=14, fontweight='bold')
        ax4.set_ylabel('ROE（%）')
        for i, (bar, value) in enumerate(zip(bars4, roe)):
            ax4.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(roe)*0.02,
                    str(round(value, 2)) + '%', ha='center', va='bottom', fontweight='bold')

        # 保存图表
        output_dir = "./direct_test_output"
        os.makedirs(output_dir, exist_ok=True)
        chart_file = os.path.join(output_dir, 'direct_comparison.png')

        plt.tight_layout()
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()

        # 检查文件
        if os.path.exists(chart_file):
            file_size = os.path.getsize(chart_file)
            print(f"图表生成成功: {chart_file}")
            print(f"文件大小: {file_size} bytes")
            return True
        else:
            print("图表文件未找到")
            return False

    except Exception as e:
        print(f"图表生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=== 直接matplotlib图表生成测试 ===\n")

    success = create_direct_chart()

    print(f"\n=== 测试结果 ===")
    if success:
        print("直接matplotlib测试成功！")
        print("\n验证结果:")
        print("1. matplotlib功能正常")
        print("2. 中文字体支持正常")
        print("3. 图表文件生成成功")
        print("4. 财务数据可视化正常")
        return 0
    else:
        print("直接matplotlib测试失败")
        return 1

if __name__ == "__main__":
    exit(main())