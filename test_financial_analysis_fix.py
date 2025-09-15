#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的财务分析工具
"""

import json
from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer

def test_financial_analysis():
    """测试财务分析工具"""
    print("=== 测试修复后的财务分析工具 ===")
    
    # 初始化工具包
    analyzer = StandardFinancialAnalyzer()
    print("✓ 工具包初始化成功")
    
    # 测试简化指标数据（添加流动资产和流动负债数据）
    simple_metrics = {
        "company_name": "陕西建工",
        "stock_code": "600248", 
        "latest_year": 2025,
        "revenue": 573.88,
        "net_profit": 11.04,
        "total_assets": 3472.98,
        "total_liabilities": 3081.05,
        "total_equity": 391.93,
        "parent_net_profit": 10.52,
        "current_assets": 1520.32,  # 添加流动资产
        "current_liabilities": 1267.21  # 添加流动负债
    }
    
    # 将数据转换为JSON字符串
    financial_data_json = json.dumps(simple_metrics, ensure_ascii=False)
    
    try:
        # 测试 calculate_ratios 方法
        print("\n--- 测试 calculate_ratios 方法 ---")
        ratios = analyzer.calculate_ratios(financial_data_json)
        print("✓ calculate_ratios 方法调用成功")
        print(f"  盈利能力指标: {list(ratios.get('profitability', {}).keys())}")
        print(f"  偿债能力指标: {list(ratios.get('solvency', {}).keys())}")
        print(f"  运营效率指标: {list(ratios.get('efficiency', {}).keys())}")
        print(f"  成长能力指标: {list(ratios.get('growth', {}).keys())}")
        
        # 显示具体比率值
        profitability = ratios.get('profitability', {})
        solvency = ratios.get('solvency', {})
        growth = ratios.get('growth', {})
        print(f"  净利率: {profitability.get('net_profit_margin', 'N/A')}%")
        print(f"  ROE: {profitability.get('roe', 'N/A')}%")
        print(f"  资产负债率: {solvency.get('debt_to_asset_ratio', 'N/A')}%")
        print(f"  流动比率: {solvency.get('current_ratio', 'N/A')}")
        print(f"  收入增长率: {growth.get('revenue_growth', 'N/A')}%")
        print(f"  利润增长率: {growth.get('profit_growth', 'N/A')}%")
        
        # 测试 generate_report 方法
        print("\n--- 测试 generate_report 方法 ---")
        report = analyzer.generate_report(financial_data_json, "陕西建工")
        print("✓ generate_report 方法调用成功")
        print(f"  报告生成时间: {report.get('analysis_date', 'N/A')}")
        print(f"  公司名称: {report.get('company_name', 'N/A')}")
        print(f"  健康评分: {report.get('health_assessment', {}).get('overall_score', 'N/A')}")
        
    except Exception as e:
        print(f"✗ 方法调用失败: {e}")
        import traceback
        traceback.print_exc()

def test_chart_generation():
    """测试图表生成工具"""
    print("\n=== 测试图表生成工具 ===")
    
    try:
        from utu.tools.tabular_data_toolkit import TabularDataToolkit
        from utu.config import ToolkitConfig
        
        # 初始化工具包
        config = ToolkitConfig()
        toolkit = TabularDataToolkit(config=config)
        print("✓ 表格数据工具包初始化成功")
        
        # 测试数据
        chart_data = {
            "营业收入": 573.88,
            "净利润": 11.04,
            "总资产": 3472.98,
            "净资产": 391.93
        }
        
        # 将数据转换为JSON字符串
        data_json = json.dumps(chart_data, ensure_ascii=False)
        
        # 测试生成柱状图
        print("\n--- 测试生成柱状图 ---")
        result = toolkit.generate_charts(data_json, chart_type="bar", output_dir="./test_charts")
        print(f"✓ 图表生成结果: {result}")
        
        # 测试生成折线图
        print("\n--- 测试生成折线图 ---")
        result = toolkit.generate_charts(data_json, chart_type="line", output_dir="./test_charts")
        print(f"✓ 图表生成结果: {result}")
        
        # 测试生成饼图
        print("\n--- 测试生成饼图 ---")
        result = toolkit.generate_charts(data_json, chart_type="pie", output_dir="./test_charts")
        print(f"✓ 图表生成结果: {result}")
        
    except Exception as e:
        print(f"✗ 图表生成测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_financial_analysis()
    test_chart_generation()
    print("\n=== 测试完成 ===")