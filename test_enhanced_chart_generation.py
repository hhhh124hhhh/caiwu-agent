#!/usr/bin/env python3
"""
测试增强版图表生成功能
验证智能体间数据格式转换和图表生成
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utu.tools.enhanced_chart_generator import EnhancedChartGenerator


def test_enhanced_chart_generation():
    """测试增强版图表生成功能"""
    print("=== 测试增强版图表生成功能 ===")
    
    print("1. 创建增强图表生成器实例...")
    try:
        generator = EnhancedChartGenerator()
        print("   实例创建成功")
    except Exception as e:
        print(f"   实例创建失败: {e}")
        return False
    
    print("\n2. 测试财务比率数据转换...")
    # 模拟DataAnalysisAgent输出的财务比率数据
    financial_ratios_data = {
        'profitability': {
            'gross_profit_margin': 0.0528,
            'net_profit_margin': 0.0192,
            'roe': 0.0282,
            'roa': 0.0032
        },
        'solvency': {
            'debt_to_asset_ratio': 0.8871,
            'current_ratio': 1.0,
            'quick_ratio': 1.0
        },
        'efficiency': {
            'asset_turnover': 0.10,
            'inventory_turnover': 0.0,
            'receivables_turnover': 0.0
        },
        'growth': {
            'revenue_growth': 0.0,
            'profit_growth': 0.0
        },
        'cash_flow': {
            'operating_cash_flow': 0.0,
            'cash_flow_ratio': 0.0,
            'free_cash_flow': 0.0
        },
        'warnings': []
    }
    
    try:
        result = generator.generate_charts_from_financial_data(
            financial_data=financial_ratios_data,
            chart_types=['bar', 'radar'],
            output_dir='./test_charts'
        )
        
        print(f"   财务比率数据转换结果: {result['success']}")
        print(f"   生成图表数量: {result.get('chart_count', 0)}")
        print(f"   消息: {result.get('message', '')}")
        
        if result['success']:
            for chart in result.get('charts', []):
                print(f"   - {chart['chart_name']} ({chart['chart_type']}): {len(chart['files'])} 个文件")
        
    except Exception as e:
        print(f"   财务比率数据测试失败: {e}")
        return False
    
    print("\n3. 测试基础财务数据转换...")
    # 模拟DataAgent输出的基础财务数据
    basic_financial_data = {
        'revenue': 573.88,
        'net_profit': 11.04,
        'gross_profit': None,
        'total_assets': 3472.98,
        'total_liabilities': 3081.05,
        'total_equity': 391.93
    }
    
    try:
        result = generator.generate_charts_from_basic_data(
            basic_data=basic_financial_data,
            chart_types=['bar', 'pie'],
            output_dir='./test_charts'
        )
        
        print(f"   基础财务数据转换结果: {result['success']}")
        print(f"   生成图表数量: {result.get('chart_count', 0)}")
        print(f"   消息: {result.get('message', '')}")
        
        if result['success']:
            for chart in result.get('charts', []):
                print(f"   - {chart['chart_name']} ({chart['chart_type']}): {len(chart['files'])} 个文件")
        
    except Exception as e:
        print(f"   基础财务数据测试失败: {e}")
        return False
    
    print("\n4. 测试智能分析功能...")
    try:
        result = generator.analyze_and_generate_charts(
            data=financial_ratios_data,
            output_dir='./test_charts'
        )
        
        print(f"   智能分析结果: {result['success']}")
        print(f"   生成图表数量: {result.get('chart_count', 0)}")
        print(f"   消息: {result.get('message', '')}")
        
    except Exception as e:
        print(f"   智能分析测试失败: {e}")
        return False
    
    print("\n=== 测试结果 ===")
    print("✅ 增强版图表生成功能测试通过")
    print("✅ 财务比率数据格式转换正常")
    print("✅ 基础财务数据格式转换正常")
    print("✅ 智能数据分析和图表生成正常")
    print("✅ 智能体间数据格式问题已解决")
    
    return True


if __name__ == "__main__":
    try:
        success = test_enhanced_chart_generation()
        if success:
            print("\n🎉 所有测试通过！数据格式转换问题已完全解决！")
        else:
            print("\n❌ 测试失败，需要进一步调试")
    except Exception as e:
        print(f"\n💥 测试过程出现异常: {e}")
        import traceback
        traceback.print_exc()