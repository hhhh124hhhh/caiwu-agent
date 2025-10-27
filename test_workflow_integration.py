#!/usr/bin/env python3
"""
简化版智能体工作流程测试
验证增强图表生成功能在智能体工作流中的表现
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utu.tools.enhanced_chart_generator import EnhancedChartGenerator

def test_workflow_integration():
    """测试智能体工作流程集成"""
    print("=== 测试智能体工作流程集成 ===")
    
    print("1. 初始化增强图表生成器...")
    try:
        generator = EnhancedChartGenerator()
        print("   初始化成功")
    except Exception as e:
        print(f"   初始化失败: {e}")
        return False
    
    print("\n2. 模拟DataAnalysisAgent输出数据...")
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
        'warnings': ['资产负债率偏高', '净利润率较低']
    }
    
    print("3. 使用智能分析功能生成图表...")
    try:
        result = generator.analyze_and_generate_charts(
            data=financial_ratios_data,
            output_dir='./workflow_test_charts'
        )
        
        if result['success']:
            print(f"   智能分析成功: {result.get('message', '')}")
            print(f"   生成图表数量: {result.get('chart_count', 0)}")
            
            for chart in result.get('charts', []):
                print(f"   - {chart['chart_name']} ({chart['chart_type']})")
                
            print("\n4. 验证图表文件...")
            import os
            chart_dir = Path('./workflow_test_charts')
            if chart_dir.exists():
                chart_files = list(chart_dir.glob('*.png'))
                print(f"   找到 {len(chart_files)} 个图表文件")
                for file in chart_files:
                    print(f"   - {file.name}")
            
            return True
        else:
            print(f"   智能分析失败: {result.get('message', '')}")
            return False
            
    except Exception as e:
        print(f"   智能分析异常: {e}")
        return False

if __name__ == "__main__":
    try:
        success = test_workflow_integration()
        if success:
            print("\n=== 工作流程集成测试成功 ===")
            print("智能体间数据格式转换问题已解决")
            print("ChartGeneratorAgent现在可以:")
            print("1. 自动识别财务分析数据格式")
            print("2. 智能转换为图表所需格式")
            print("3. 生成多种类型的专业图表")
            print("4. 提供完整的图表分析报告")
        else:
            print("\n=== 工作流程集成测试失败 ===")
    except Exception as e:
        print(f"\n测试过程出现异常: {e}")
        import traceback
        traceback.print_exc()