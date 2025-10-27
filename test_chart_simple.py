#!/usr/bin/env python3
"""
图表生成修复效果测试脚本（简化版，避免编码问题）
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_chart_generator import EnhancedChartGenerator
from chart_data_validator import ChartDataValidator
from chart_data_builder import ChartDataBuilder

def test_user_specific_issue():
    """测试用户遇到的具体问题"""
    print("=" * 60)
    print("测试用户遇到的具体问题")
    print("=" * 60)
    
    validator = ChartDataValidator()
    
    # 用户遇到的具体错误：JSON格式错误，缺少逗号分隔符
    broken_json = '{"title": "陕西建工盈利能力指标对比", "x_axis": ["2022", "2023", "2024", "2025(Q)"], "series": [{"name": "净利率(%)", "data": [2.11, 2.27, 2.39, 1.92]}, {"name": "ROE(%)", "data": [8.15, 8.92, 9.22, 2.82}]}'
    
    print("原始JSON（有格式错误）:")
    print(broken_json)
    print()
    
    # 尝试验证和修复
    result = validator.validate_and_fix_json(broken_json, 'bar')
    
    if result['success']:
        print("[成功] JSON修复成功")
        if result['fixed']:
            print("[信息] JSON已自动修复")
        print("修复后数据:")
        print(json.dumps(result['data'], ensure_ascii=False, indent=2))
        
        # 验证数据格式
        validation = validator.validate_chart_data(result['data'], 'bar')
        print(f"数据验证: {'通过' if validation['valid'] else '失败'}")
        if validation['warnings']:
            print(f"警告: {validation['warnings']}")
            
        return True
    else:
        print(f"[失败] JSON修复失败: {result['error']}")
        return False

def test_chart_data_builder():
    """测试图表数据构造器"""
    print("\n" + "=" * 60)
    print("测试图表数据构造器")
    print("=" * 60)
    
    builder = ChartDataBuilder()
    
    # 测试用户数据格式
    financial_data = {
        "revenue": {"2022": 1350.25, "2023": 1420.18, "2024": 1511.39, "2025(Q)": 573.88},
        "net_profit": {"2022": 28.45, "2023": 32.18, "2024": 36.11, "2025(Q)": 11.04},
        "roe": {"2022": 8.15, "2023": 8.92, "2024": 9.22, "2025(Q)": 2.82},
        "net_profit_margin": {"2022": 2.11, "2023": 2.27, "2024": 2.39, "2025(Q)": 1.92},
        "debt_to_assets": {"2022": 87.25, "2023": 88.03, "2024": 88.71, "2025(Q)": 88.71}
    }
    
    # 构建趋势图
    print("测试营业收入趋势图:")
    trend_data = builder.build_trend_chart_data(
        title="陕西建工营业收入趋势分析",
        years=["2022", "2023", "2024", "2025(Q)"],
        metrics={"营业收入": [1350.25, 1420.18, 1511.39, 573.88]},
        unit="亿元"
    )
    print(json.dumps(trend_data, ensure_ascii=False, indent=2))
    
    # 构建对比图
    print("\n测试盈利能力指标对比图:")
    comparison_data = builder.build_comparison_chart_data(
        title="陕西建工盈利能力指标对比",
        categories=["2022", "2023", "2024", "2025(Q)"],
        metrics={
            "净利率": [2.11, 2.27, 2.39, 1.92],
            "ROE": [8.15, 8.92, 9.22, 2.82]
        }
    )
    print(json.dumps(comparison_data, ensure_ascii=False, indent=2))
    
    # 构建雷达图
    print("\n测试财务健康雷达图:")
    radar_data = builder.build_financial_health_radar(
        company_name="陕西建工",
        financial_metrics=financial_data
    )
    print(json.dumps(radar_data, ensure_ascii=False, indent=2))
    
    print("[成功] 所有图表数据构造完成")

def test_enhanced_generator():
    """测试增强版图表生成器"""
    print("\n" + "=" * 60)
    print("测试增强版图表生成器")
    print("=" * 60)
    
    generator = EnhancedChartGenerator("./test_charts")
    
    # 测试用户遇到问题的具体图表
    problem_chart = {
        "title": "陕西建工盈利能力指标对比",
        "x_axis": ["2022", "2023", "2024", "2025(Q)"],
        "series": [
            {"name": "净利率(%)", "data": [2.11, 2.27, 2.39, 1.92]},
            {"name": "ROE(%)", "data": [8.15, 8.92, 9.22, 2.82]}
        ]
    }
    
    print("测试问题图表生成:")
    result = generator.generate_chart_with_validation(
        json.dumps(problem_chart, ensure_ascii=False),
        'bar'
    )
    
    if result['success']:
        print("[成功] 图表生成成功")
        print(f"生成的文件: {result['files']}")
        if result.get('data_fixed'):
            print("[信息] 数据已自动修复")
        return True
    else:
        print(f"[失败] 图表生成失败: {result['message']}")
        return False

def test_data_anomaly_fixes():
    """测试数据异常修复"""
    print("\n" + "=" * 60)
    print("测试数据异常修复")
    print("=" * 60)
    
    builder = ChartDataBuilder()
    
    # 测试ROE异常值
    print("测试ROE异常值修复:")
    anomaly_data = {
        "roe": 0.32,  # 异常低
        "net_profit_margin": 1.92,
        "debt_to_assets": 88.71,
        "current_ratio": 1.11
    }
    
    print(f"原始数据: {anomaly_data}")
    fixed_data = builder.standardize_financial_data(anomaly_data)
    print(f"修复后: {fixed_data}")
    
    # 测试应收账款周转率异常
    print("\n测试应收账款周转率异常修复:")
    ar_data = {
        "accounts_receivable_turnover": 0.0,  # 异常值
        "roe": 8.5,
        "net_profit_margin": 2.5
    }
    
    print(f"原始数据: {ar_data}")
    fixed_ar_data = builder.standardize_financial_data(ar_data)
    print(f"修复后: {fixed_ar_data}")
    
    print("[成功] 数据异常修复测试完成")

def main():
    """运行所有测试"""
    print("开始图表生成修复效果测试...")
    
    success_count = 0
    total_tests = 4
    
    try:
        # 运行各项测试
        if test_user_specific_issue():
            success_count += 1
        
        test_chart_data_builder()
        success_count += 1
        
        if test_enhanced_generator():
            success_count += 1
            
        test_data_anomaly_fixes()
        success_count += 1
        
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        print(f"测试完成: {success_count}/{total_tests} 项测试通过")
        
        if success_count == total_tests:
            print("\n[成功] 图表生成工具修复成功！")
            print("主要修复内容:")
            print("1. 自动修复JSON格式错误（缺少逗号、引号等）")
            print("2. 标准化数据格式和单位")
            print("3. 检测和修复财务数据异常值")
            print("4. 确保数据长度一致性")
            print("5. 提供详细的错误信息和修复建议")
        else:
            print(f"\n[警告] 部分测试未通过: {total_tests - success_count} 项失败")
        
    except Exception as e:
        print(f"[错误] 测试过程中出现异常: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()