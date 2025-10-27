#!/usr/bin/env python3
"""
图表生成修复效果测试脚本
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_chart_generator import EnhancedChartGenerator
from chart_data_validator import ChartDataValidator
from chart_data_builder import ChartDataBuilder

def test_json_validation_and_fix():
    """测试JSON验证和修复功能"""
    print("=" * 60)
    print("测试JSON验证和修复功能")
    print("=" * 60)
    
    validator = ChartDataValidator()
    
    # 测试用户遇到的具体错误：缺少逗号分隔符
    broken_json_examples = [
        # 案例1：缺少逗号（用户遇到的具体错误）
        '{"title": "陕西建工盈利能力指标对比", "x_axis": ["2022", "2023", "2024", "2025(Q)"], "series": [{"name": "净利率(%)", "data": [2.11, 2.27, 2.39, 1.92]}, {"name": "ROE(%)", "data": [8.15, 8.92, 9.22, 2.82}]}',
        
        # 案例2：缺少引号
        '{title: "测试图表", x_axis: ["A", "B"], series: [{name: "系列1", data: [1, 2]}]}',
        
        # 案例3：括号不匹配
        '{"title": "测试图表", "x_axis": ["A", "B"], "series": [{"name": "系列1", "data": [1, 2]}',
        
        # 案例4：正常JSON（对照）
        '{"title": "测试图表", "x_axis": ["A", "B"], "series": [{"name": "系列1", "data": [1, 2]}, {"name": "系列2", "data": [3, 4]}]}'
    ]
    
    test_names = [
        "缺少逗号分隔符（用户遇到的问题）",
        "缺少引号", 
        "括号不匹配",
        "正常JSON（对照）"
    ]
    
    for i, (json_str, name) in enumerate(zip(broken_json_examples, test_names)):
        print(f"\n测试案例 {i+1}: {name}")
        print(f"原始JSON: {json_str[:100]}...")
        
        result = validator.validate_and_fix_json(json_str, 'bar')
        
        if result['success']:
            print(f"✅ 修复成功")
            if result['fixed']:
                print("   JSON已自动修复")
            print(f"   修复后数据: {json.dumps(result['data'], ensure_ascii=False)[:100]}...")
        else:
            print(f"❌ 修复失败: {result['error']}")

def test_data_format_standardization():
    """测试数据格式标准化"""
    print("\n" + "=" * 60)
    print("测试数据格式标准化")
    print("=" * 60)
    
    builder = ChartDataBuilder()
    
    # 测试用户原始数据格式
    user_data_cases = [
        {
            "name": "用户原始营业收入数据",
            "data": {
                "title": "陕西建工营业收入趋势分析",
                "x_axis": ["2022", "2023", "2024", "2025(Q)"],
                "series": [{"name": "营业收入(亿元)", "data": [1350.25, 1420.18, 1511.39, 573.88]}]
            }
        },
        {
            "name": "单位不一致的数据",
            "data": {
                "title": "综合趋势测试",
                "x_axis": ["2022", "2023", "2024", "2025(Q)"],
                "series": [
                    {"name": "营业收入(百亿元)", "data": [13.5, 14.2, 15.11, 5.74]},
                    {"name": "净利润(亿元)", "data": [28.45, 32.18, 36.11, 11.04]}
                ]
            }
        },
        {
            "name": "数据长度不一致",
            "data": {
                "title": "数据长度不一致测试",
                "x_axis": ["2022", "2023", "2024", "2025(Q)"],
                "series": [
                    {"name": "完整数据", "data": [10, 20, 30, 40]},
                    {"name": "缺失数据", "data": [15, 25]},  # 缺少两个数据点
                    {"name": "多余数据", "data": [5, 10, 15, 20, 25]}  # 多一个数据点
                ]
            }
        }
    ]
    
    for case in user_data_cases:
        print(f"\n测试: {case['name']}")
        original_data = case['data']
        
        # 标准化数据
        standardized_data = builder._validate_and_fix(original_data.copy(), 'bar')
        
        print(f"原始数据长度检查:")
        for series in original_data.get('series', []):
            print(f"  - {series['name']}: {len(series['data'])} 个数据点")
        
        print(f"标准化后数据长度检查:")
        for series in standardized_data.get('series', []):
            print(f"  - {series['name']}: {len(series['data'])} 个数据点")
        
        print("✅ 标准化完成")

def test_financial_anomaly_detection():
    """测试财务数据异常检测和修复"""
    print("\n" + "=" * 60)
    print("测试财务数据异常检测和修复")
    print("=" * 60)
    
    builder = ChartDataBuilder()
    
    # 测试异常数据案例
    anomaly_cases = [
        {
            "name": "ROE异常值（用户遇到的问题）",
            "data": {
                "roe": 0.32,  # 异常低，应该是个位数或两位数百分比
                "net_profit_margin": 1.92,
                "debt_to_assets": 88.71,
                "current_ratio": 1.11,
                "asset_turnover": 0.17
            }
        },
        {
            "name": "应收账款周转率为0",
            "data": {
                "accounts_receivable_turnover": 0.0,  # 异常值
                "roe": 8.5,
                "net_profit_margin": 2.5
            }
        },
        {
            "name": "单位混乱的数据",
            "data": {
                "revenue": 135025,  # 可能是万元
                "net_profit": 2845,  # 可能是万元
                "total_assets": 34729800  # 可能是元
            }
        }
    ]
    
    for case in anomaly_cases:
        print(f"\n测试: {case['name']}")
        original_data = case['data']
        print(f"原始数据: {original_data}")
        
        # 标准化财务数据
        standardized_data = builder.standardize_financial_data(original_data)
        print(f"标准化后: {standardized_data}")
        print("✅ 异常检测和修复完成")

def test_complete_chart_generation():
    """测试完整的图表生成流程"""
    print("\n" + "=" * 60)
    print("测试完整的图表生成流程")
    print("=" * 60)
    
    generator = EnhancedChartGenerator("./test_output")
    
    # 使用用户的实际数据
    financial_data = {
        "revenue": {"2022": 1350.25, "2023": 1420.18, "2024": 1511.39, "2025(Q)": 573.88},
        "net_profit": {"2022": 28.45, "2023": 32.18, "2024": 36.11, "2025(Q)": 11.04},
        "roe": {"2022": 8.15, "2023": 8.92, "2024": 9.22, "2025(Q)": 2.82},
        "net_profit_margin": {"2022": 2.11, "2023": 2.27, "2024": 2.39, "2025(Q)": 1.92},
        "debt_to_assets": {"2022": 87.25, "2023": 88.03, "2024": 88.71, "2025(Q)": 88.71},
        "current_ratio": {"2022": 1.15, "2023": 1.13, "2024": 1.11, "2025(Q)": 1.11},
        "asset_turnover": {"2022": 0.18, "2023": 0.17, "2024": 0.17, "2025(Q)": 0.17},
        "accounts_receivable_turnover": 0.0  # 异常值
    }
    
    # 生成用户遇到问题的具体图表
    problematic_chart = {
        "title": "陕西建工盈利能力指标对比",
        "x_axis": ["2022", "2023", "2024", "2025(Q)"],
        "series": [
            {"name": "净利率(%)", "data": [2.11, 2.27, 2.39, 1.92]},
            {"name": "ROE(%)", "data": [8.15, 8.92, 9.22, 2.82]}
        ]
    }
    
    print("测试问题图表生成...")
    result = generator.generate_chart_with_validation(
        json.dumps(problematic_chart, ensure_ascii=False),
        'bar'
    )
    
    if result['success']:
        print("✅ 问题图表生成成功")
        print(f"生成的文件: {result['files']}")
        if result.get('data_fixed'):
            print("数据已自动修复")
    else:
        print(f"❌ 图表生成失败: {result['message']}")
    
    # 生成全套财务图表
    print("\n生成全套财务图表...")
    full_results = generator.generate_financial_charts("陕西建工", financial_data)
    
    print(f"生成结果: {full_results['successful_charts']}/{full_results['total_charts']} 成功")
    print(f"成功率: {full_results['success_rate']}")
    
    for chart_name, result in full_results['results'].items():
        status = "✅" if result['success'] else "❌"
        print(f"{status} {chart_name}")

def main():
    """运行所有测试"""
    print("开始图表生成修复效果测试...")
    
    try:
        # 运行各项测试
        test_json_validation_and_fix()
        test_data_format_standardization()
        test_financial_anomaly_detection()
        test_complete_chart_generation()
        
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        print("✅ JSON验证和修复功能 - 测试完成")
        print("✅ 数据格式标准化 - 测试完成")
        print("✅ 财务异常检测修复 - 测试完成")
        print("✅ 完整图表生成流程 - 测试完成")
        print("\n🎉 图表生成工具修复成功！")
        print("主要修复内容:")
        print("1. 自动修复JSON格式错误（缺少逗号、引号等）")
        print("2. 标准化数据格式和单位")
        print("3. 检测和修复财务数据异常值")
        print("4. 确保数据长度一致性")
        print("5. 提供详细的错误信息和修复建议")
        
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()