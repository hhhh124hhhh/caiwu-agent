#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合测试财务分析智能体集成效果
"""

import asyncio
import pandas as pd
import json
import os

async def test_financial_analysis_pipeline():
    """测试完整的财务分析流程"""
    
    print("=== 综合测试财务分析智能体 ===")
    
    financial_data = None  # 初始化变量
    
    # 1. 测试AKShare数据获取工具
    print("\n1. 测试AKShare财务数据工具...")
    try:
        from utu.tools.akshare_financial_tool import AKShareFinancialDataTool
        from utu.config import ToolkitConfig
        
        config = ToolkitConfig()
        akshare_tool = AKShareFinancialDataTool(config=config)
        
        # 获取陕西建工的财务数据（示例）
        print("获取陕西建工(600248)财务数据...")
        financial_data = akshare_tool.get_financial_reports("600248", "陕西建工")
        
        if financial_data:
            print("✓ 财务数据获取成功")
            print(f"  利润表行数: {len(financial_data.get('income', pd.DataFrame()))}")
            print(f"  资产负债表行数: {len(financial_data.get('balance', pd.DataFrame()))}")
            
            # 测试关键指标提取
            print("\n2. 测试关键指标提取...")
            key_metrics = akshare_tool.get_key_metrics(financial_data)
            if key_metrics:
                print("✓ 关键指标提取成功")
                for key, value in list(key_metrics.items())[:5]:  # 显示前5个指标
                    print(f"  {key}: {value}")
            else:
                print("✗ 关键指标提取失败")
        else:
            print("✗ 财务数据获取失败")
            
    except Exception as e:
        print(f"AKShare工具测试失败: {e}")
    
    # 3. 测试标准化财务分析工具
    print("\n3. 测试标准化财务分析工具...")
    try:
        from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer
        
        analyzer = StandardFinancialAnalyzer()
        
        # 使用前面获取的数据进行分析
        if financial_data:
            # 计算财务比率
            print("计算财务比率...")
            ratios = analyzer.calculate_financial_ratios(financial_data)
            if ratios:
                print("✓ 财务比率计算成功")
                print(f"  盈利能力指标: {list(ratios.get('profitability', {}).keys())}")
                print(f"  偿债能力指标: {list(ratios.get('solvency', {}).keys())}")
            
            # 分析趋势
            print("\n分析财务趋势...")
            trends = analyzer.analyze_trends(financial_data)
            if trends:
                print("✓ 财务趋势分析成功")
                print(f"  收入趋势: {trends.get('revenue', {}).get('trend', 'N/A')}")
            
            # 生成报告
            print("\n生成分析报告...")
            report = analyzer.generate_analysis_report(financial_data, "陕西建工")
            if report:
                print("✓ 分析报告生成成功")
                print(f"  公司名称: {report.get('company_name', 'N/A')}")
                print(f"  健康评分: {report.get('health_assessment', {}).get('overall_score', 'N/A')}")
        else:
            print("✗ 无财务数据用于分析")
            
    except Exception as e:
        print(f"标准化财务分析工具测试失败: {e}")
    
    # 4. 测试表格数据工具
    print("\n4. 测试表格数据工具...")
    try:
        from utu.tools.tabular_data_toolkit import TabularDataToolkit
        from utu.config import ToolkitConfig
        
        # 创建测试数据
        test_data = {
            '年份': [2020, 2021, 2022, 2023],
            '营业收入(亿元)': [100, 120, 135, 150],
            '净利润(亿元)': [8, 10, 12, 13.5],
            '总资产(亿元)': [80, 90, 100, 110],
            '总负债(亿元)': [50, 55, 60, 65]
        }
        
        df = pd.DataFrame(test_data)
        os.makedirs("run_workdir", exist_ok=True)
        csv_file_path = "run_workdir/test_financial_data.csv"
        df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')
        
        # 初始化工具包
        config = ToolkitConfig()
        tabular_tool = TabularDataToolkit(config=config)
        
        # 获取列信息
        columns_info = tabular_tool.get_tabular_columns(csv_file_path)
        print("✓ 表格列信息获取成功")
        print(f"  列信息长度: {len(columns_info)} 字符")
        
    except Exception as e:
        print(f"表格数据工具测试失败: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    asyncio.run(test_financial_analysis_pipeline())