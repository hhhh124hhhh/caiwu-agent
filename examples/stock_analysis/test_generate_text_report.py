#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试 generate_text_report 工具功能
验证是否能正确处理财务数据并生成报告
"""

import sys
import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer


def test_generate_text_report():
    """测试生成文本报告功能"""
    print("=== 测试 generate_text_report 工具 ===\n")
    
    # 创建分析器实例
    analyzer = StandardFinancialAnalyzer()
    
    # 创建符合工具期望格式的测试数据
    # 创建利润表数据
    income_data = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31', '2022-12-31', '2021-12-31'],
        'TOTAL_OPERATE_INCOME': [323.48 * 1e8, 280.12 * 1e8, 250.45 * 1e8],  # 营业收入(元)
        'NETPROFIT': [33.68 * 1e8, 28.45 * 1e8, 25.12 * 1e8],  # 净利润(元)
        'PARENT_NETPROFIT': [33.68 * 1e8, 28.45 * 1e8, 25.12 * 1e8],  # 归母净利润(元)
        'TOTAL_OPERATE_COST': [290.12 * 1e8, 252.34 * 1e8, 225.67 * 1e8]  # 营业成本(元)
    })
    
    # 创建资产负债表数据
    balance_data = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31', '2022-12-31', '2021-12-31'],
        'TOTAL_ASSETS': [3541.68 * 1e8, 3420.56 * 1e8, 3210.45 * 1e8],  # 总资产(元)
        'TOTAL_LIABILITIES': [3541.68 * 1e8 * 0.3378, 3420.56 * 1e8 * 0.3421, 3210.45 * 1e8 * 0.3567],  # 总负债(元)
        'TOTAL_EQUITY': [3541.68 * 1e8 * (1-0.3378), 3420.56 * 1e8 * (1-0.3421), 3210.45 * 1e8 * (1-0.3567)],  # 净资产(元)
        'TOTAL_CURRENT_ASSETS': [2100.34 * 1e8, 2010.56 * 1e8, 1920.78 * 1e8],  # 流动资产(元)
        'TOTAL_CURRENT_LIABILITIES': [1200.45 * 1e8, 1150.67 * 1e8, 1100.89 * 1e8]  # 流动负债(元)
    })
    
    # 创建现金流量表数据（空表）
    cashflow_data = pd.DataFrame()
    
    # 构建完整的财务数据字典
    financial_data_dict = {
        'income': income_data,
        'balance': balance_data,
        'cashflow': cashflow_data
    }
    
    # 转换为JSON字符串
    financial_data_json = json.dumps({
        'income': income_data.to_dict('records'),
        'balance': balance_data.to_dict('records'),
        'cashflow': cashflow_data.to_dict('records')
    }, ensure_ascii=False)
    
    # 测试生成文本报告
    print("1. 测试生成文本报告...")
    try:
        report_text = analyzer.generate_text_report(
            financial_data_json=financial_data_json,
            stock_name="芯片龙头企业"
        )
        print("   ✓ 文本报告生成成功")
        print(f"   ✓ 报告长度: {len(report_text)} 字符")
        
        # 检查报告内容
        if "芯片龙头企业" in report_text and "财务分析报告" in report_text:
            print("   ✓ 报告内容验证通过")
        else:
            print("   ✗ 报告内容验证失败")
            
        # 显示报告前几行
        print("\n   报告预览:")
        preview_lines = report_text.split('\n')[:15]
        for line in preview_lines:
            print(f"   {line}")
            
        # 测试保存报告
        print("\n2. 测试保存文本报告...")
        save_result = analyzer.save_text_report(
            financial_data_json=financial_data_json,
            stock_name="芯片龙头企业",
            file_prefix="./run_workdir"
        )
        print(f"   ✓ {save_result}")
            
    except Exception as e:
        print(f"   ✗ 生成文本报告时出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_generate_text_report()