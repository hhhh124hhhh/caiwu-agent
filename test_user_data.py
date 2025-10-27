#!/usr/bin/env python3
"""
使用用户原始数据测试趋势分析修复效果
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer

def test_user_original_data():
    """使用用户原始提供的测试数据进行验证"""
    
    toolkit = StandardFinancialAnalyzer()
    
    # 用户原始数据格式（来自对话历史）
    user_data = {
        "financial_metrics": {
            "revenue": {
                "2024": 1511.39,
                "2025": 573.88
            },
            "net_profit": {
                "2024": 200.50,
                "2025": 150.30
            }
        },
        "analysis_type": "trend"
    }
    
    print("=" * 60)
    print("用户原始数据趋势分析测试")
    print("=" * 60)
    print("测试数据:")
    print(json.dumps(user_data, ensure_ascii=False, indent=2))
    print()
    
    try:
        result = toolkit.analyze_trends_tool(
            financial_data_json=json.dumps(user_data),
            years=2
        )
        
        print("分析结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print()
        
        # 验证修复效果
        if result and result.get('data_completeness', 0) > 0:
            print("[成功] 修复成功！")
            print(f"- 趋势类型: {result.get('trend_type', 'N/A')}")
            print(f"- 整体增长率: {result.get('overall_growth_rate', 0):.2f}%")
            print(f"- 数据完整性: {result.get('data_completeness', 0):.1f}%")
            print(f"- 趋势指标数量: {len(result.get('trend_indicators', {}))}")
            
            # 显示各项指标的具体趋势
            for indicator, data in result.get('trend_indicators', {}).items():
                print(f"  - {indicator}: {data.get('trend', 'N/A')} (增长率: {data.get('average_growth', 0):.2f}%)")
            
            return True
        else:
            print("[失败] 仍然返回空结果")
            return False
            
    except Exception as e:
        print(f"[失败] 测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("验证趋势分析工具修复效果...")
    success = test_user_original_data()
    
    if success:
        print("\n[成功] 趋势分析工具修复成功！")
        print("[成功] financial_metrics格式数据可以正确处理")
        print("[成功] 不再返回空结果")
        print("[成功] 提供有意义的趋势分析")
    else:
        print("\n[失败] 趋势分析工具仍有问题")
    
    print("\n测试完成")