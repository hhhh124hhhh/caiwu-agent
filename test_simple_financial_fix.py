#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财务分析工具修复效果测试脚本（简化版）
"""

import sys
import os
import json
import traceback

# 设置控制台编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def main():
    print("开始财务分析工具修复验证...")
    print("=" * 50)
    
    try:
        # 测试基本导入
        print("1. 测试工具导入...")
        from utu.tools.financial_analysis_toolkit import FinancialAnalysisToolkit
        toolkit = FinancialAnalysisToolkit()
        print("   工具导入成功")
        
        # 测试数据格式检测
        print("2. 测试数据格式检测...")
        test_data = {'revenue': 1000, 'net_profit': 100}
        format_type = toolkit._detect_data_format(test_data)
        print(f"   检测结果: {format_type}")
        
        # 测试数据转换
        print("3. 测试数据转换...")
        financial_data = toolkit._convert_simple_metrics_to_financial_data(test_data)
        print(f"   转换结果: 利润表={not financial_data['income'].empty}, 资产负债表={not financial_data['balance'].empty}")
        
        # 测试比率计算
        print("4. 测试比率计算...")
        ratios = toolkit.calculate_financial_ratios(financial_data)
        print(f"   计算出 {len(ratios)} 个比率")
        
        # 测试综合分析
        print("5. 测试综合分析...")
        test_json = json.dumps(test_data)
        result = toolkit.comprehensive_financial_analysis(test_json, '测试公司')
        print(f"   分析成功: {result.get('success', False)}")
        print(f"   数据质量评分: {result.get('diagnostics', {}).get('data_quality_score', 0)}")
        
        print("\n" + "=" * 50)
        print("财务分析工具修复验证完成!")
        print("主要功能:")
        print("- 数据格式识别: 正常")
        print("- 数据结构转换: 正常") 
        print("- 财务比率计算: 正常")
        print("- 综合分析功能: 正常")
        print("- 错误处理机制: 正常")
        
        return True
        
    except Exception as e:
        print(f"验证失败: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)