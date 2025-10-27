#!/usr/bin/env python3
"""
测试趋势分析工具修复效果
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer

def test_trend_analysis():
    """测试趋势分析功能"""
    
    # 创建工具实例
    toolkit = StandardFinancialAnalyzer()
    
    # 测试数据 - 包含financial_metrics格式的历史数据
    test_data = {
        "company_name": "测试公司",
        "financial_metrics": {
            "revenue": {
                "2024": 1511.39,
                "2025": 573.88
            },
            "net_profit": {
                "2024": 200.50,
                "2025": 150.30
            },
            "assets": {
                "2024": 2000.00,
                "2025": 2200.00
            },
            "liabilities": {
                "2024": 1500.00,
                "2025": 1600.00
            }
        },
        "current_year": "2025",
        "analysis_type": "trend"
    }
    
    print("=" * 60)
    print("趋势分析工具测试")
    print("=" * 60)
    print(f"测试数据: {test_data}")
    print()
    
    try:
        # 调用趋势分析工具
        result = toolkit.analyze_trends_tool(
            financial_data_json=json.dumps(test_data),
            years=2
        )
        
        print("分析结果:")
        print(f"- 趋势类型: {result.get('trend_type', 'N/A')}")
        print(f"- 整体增长率: {result.get('overall_growth_rate', 0):.2f}%")
        print(f"- 数据完整性: {result.get('data_completeness', 0):.1f}%")
        
        # 检查各项指标的趋势
        trend_indicators = result.get('trend_indicators', {})
        print(f"\n各项指标趋势:")
        for indicator, data in trend_indicators.items():
            if data:  # 只显示有数据的指标
                values = data.get('values', [])
                if values:
                    print(f"- {indicator}: {values}")
                    growth_rates = data.get('growth_rates', [])
                    if growth_rates:
                        print(f"  增长率: {growth_rates}")
                    trend = data.get('trend', 'unknown')
                    print(f"  趋势: {trend}")
        
        # 检查关键发现
        key_findings = result.get('key_findings', [])
        print(f"\n关键发现:")
        for i, finding in enumerate(key_findings, 1):
            print(f"{i}. {finding}")
        
        print(f"\n状态: {'[成功]' if result else '[失败]'}")
        
        # 验证是否解决了空结果问题
        has_data = (
            result.get('trend_indicators') and 
            any(result.get('trend_indicators', {}).values()) and
            result.get('data_completeness', 0) > 0
        )
        
        if has_data:
            print("[成功] 趋势分析工具修复成功 - 不再返回空结果")
        else:
            print("[失败] 趋势分析工具仍有问题 - 返回空结果")
            
        return result
        
    except Exception as e:
        print(f"[失败] 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_different_data_formats():
    """测试不同数据格式的兼容性"""
    
    toolkit = StandardFinancialAnalyzer()
    
    print("\n" + "=" * 60)
    print("测试不同数据格式兼容性")
    print("=" * 60)
    
    # 测试格式1: financial_metrics格式 (主要测试格式)
    financial_metrics_data = {
        "company_name": "Financial Metrics格式测试",
        "financial_metrics": {
            "revenue": {"2024": 1000, "2025": 1200},
            "net_profit": {"2024": 100, "2025": 150}
        },
        "analysis_type": "trend"
    }
    
    # 测试格式2: historical_trends格式
    historical_trends_data = {
        "company_name": "Historical Trends格式测试",
        "historical_trends": {
            "revenue": {"2024": 1000, "2025": 1200},
            "net_profit": {"2024": 100, "2025": 150}
        },
        "analysis_type": "trend"
    }
    
    # 测试格式3: 逐年数据格式
    yearly_data = {
        "company_name": "逐年格式测试",
        "2024_data": {
            "revenue": 1000,
            "net_profit": 100,
            "assets": 2000
        },
        "2025_data": {
            "revenue": 1200,
            "net_profit": 150,
            "assets": 2100
        },
        "analysis_type": "trend"
    }
    
    test_cases = [
        ("financial_metrics格式", financial_metrics_data),
        ("historical_trends格式", historical_trends_data),
        ("逐年数据格式", yearly_data)
    ]
    
    results = {}
    
    for case_name, data in test_cases:
        print(f"\n测试 {case_name}:")
        try:
            result = toolkit.analyze_trends_tool(
                financial_data_json=json.dumps(data),
                years=2
            )
            
            if result and result.get('data_completeness', 0) > 0:
                print(f"[成功] {case_name} - 成功")
                print(f"   趋势类型: {result.get('trend_type', 'N/A')}")
                print(f"   数据完整性: {result.get('data_completeness', 0):.1f}%")
                print(f"   指标数量: {len([k for k,v in result.get('trend_indicators', {}).items() if v])}")
                results[case_name] = "成功"
            else:
                print(f"[失败] {case_name} - 失败或返回空结果")
                results[case_name] = "失败"
                
        except Exception as e:
            print(f"[异常] {case_name} - 异常: {str(e)}")
            results[case_name] = f"异常: {str(e)}"
    
    return results

def test_edge_cases():
    """测试边缘情况"""
    
    toolkit = StandardFinancialAnalyzer()
    
    print("\n" + "=" * 60)
    print("测试边缘情况")
    print("=" * 60)
    
    # 测试单年数据
    single_year_data = {
        "company_name": "单年数据测试",
        "financial_metrics": {
            "revenue": {"2025": 1000}
        },
        "analysis_type": "trend"
    }
    
    # 测试空数据
    empty_data = {
        "company_name": "空数据测试",
        "financial_metrics": {},
        "analysis_type": "trend"
    }
    
    # 测试缺失年份
    missing_year_data = {
        "company_name": "缺失年份测试",
        "financial_metrics": {
            "revenue": {"2023": 1000, "2025": 1200}  # 缺少2024
        },
        "analysis_type": "trend"
    }
    
    edge_cases = [
        ("单年数据", single_year_data),
        ("空数据", empty_data),
        ("缺失年份", missing_year_data)
    ]
    
    for case_name, data in edge_cases:
        print(f"\n测试 {case_name}:")
        try:
            result = toolkit.analyze_trends_tool(
                financial_data_json=json.dumps(data),
                years=2
            )
            
            if result:
                print(f"[成功] {case_name} - 处理正常")
                print(f"   数据完整性: {result.get('data_completeness', 0):.1f}%")
                print(f"   趋势类型: {result.get('trend_type', 'N/A')}")
            else:
                print(f"[警告] {case_name} - 返回空结果（可能是预期的）")
                
        except Exception as e:
            print(f"[异常] {case_name} - 异常: {str(e)}")

def main():
    print("开始趋势分析工具测试...")
    
    # 1. 测试主要功能
    main_result = test_trend_analysis()
    
    # 2. 测试不同格式兼容性
    format_results = test_different_data_formats()
    
    # 3. 测试边缘情况
    test_edge_cases()
    
    # 4. 生成测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    if main_result and main_result.get('data_completeness', 0) > 0:
        print("[成功] 主要功能测试通过")
    else:
        print("[失败] 主要功能测试失败")
    
    print("\n格式兼容性测试结果:")
    for format_name, result in format_results.items():
        print(f"- {format_name}: {result}")
    
    # 总体评估
    success_count = sum(1 for r in format_results.values() if r == "成功")
    total_count = len(format_results)
    
    if success_count == total_count and main_result:
        print(f"\n[成功] 所有测试通过！趋势分析工具修复成功！")
        print(f"[成功] 主要功能正常")
        print(f"[成功] 格式兼容性 ({success_count}/{total_count})")
    else:
        print(f"\n[警告] 部分测试未通过，需要进一步检查")
        print(f"主要功能: {'[成功]' if main_result else '[失败]'}")
        print(f"格式兼容性: {success_count}/{total_count}")
    
    print("\n测试完成")

if __name__ == "__main__":
    main()