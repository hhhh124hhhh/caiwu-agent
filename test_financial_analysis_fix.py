#!/usr/bin/env python3
"""
财务分析工具修复效果测试脚本
测试所有修复的功能，包括数据映射、比率计算、趋势分析等
"""

import sys
import os
import json
import traceback
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入修复后的财务分析工具
try:
    from utu.tools.financial_analysis_toolkit import FinancialAnalysisToolkit
    print("成功导入财务分析工具")
except ImportError as e:
    print(f"导入财务分析工具失败: {e}")
    # 尝试直接导入工具类
    try:
        import os
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utu', 'tools'))
        from financial_analysis_toolkit import FinancialAnalysisToolkit
        print("直接导入财务分析工具成功")
    except ImportError as e2:
        print(f"直接导入也失败: {e2}")
        sys.exit(1)

def test_data_format_detection():
    """测试数据格式检测功能"""
    print("\n" + "="*60)
    print("测试1: 数据格式检测功能")
    print("="*60)
    
    toolkit = FinancialAnalysisToolkit()
    
    # 测试各种数据格式
    test_cases = [
        {
            'name': 'historical_trends格式',
            'data': {'historical_trends': {'2024': {'revenue': 1000, 'net_profit': 100}}},
            'expected': 'historical_trends格式'
        },
        {
            'name': '扁平化财务指标格式',
            'data': {'revenue': 1000, 'net_profit': 100, 'total_assets': 5000},
            'expected': '扁平化财务指标格式'
        },
        {
            'name': 'financial_data嵌套格式',
            'data': {'financial_data': {'income_statement': {'latest': {'revenue': 1000}}}},
            'expected': 'financial_data嵌套格式'
        },
        {
            'name': '多年份数据格式',
            'data': {'2024': {'revenue': 1000}, '2023': {'revenue': 800}},
            'expected': '多年份数据格式'
        }
    ]
    
    success_count = 0
    for test_case in test_cases:
        try:
            detected = toolkit._detect_data_format(test_case['data'])
            if detected == test_case['expected']:
                print(f"[成功] {test_case['name']}: {detected}")
                success_count += 1
            else:
                print(f"[失败] {test_case['name']}: 期望 {test_case['expected']}, 实际 {detected}")
        except Exception as e:
            print(f"[错误] {test_case['name']}: 检测失败 - {e}")
    
    print(f"\n数据格式检测测试结果: {success_count}/{len(test_cases)} 通过")
    return success_count == len(test_cases)

def test_ratio_calculation():
    """测试财务比率计算功能"""
    print("\n" + "="*60)
    print("测试2: 财务比率计算功能")
    print("="*60)
    
    toolkit = FinancialAnalysisToolkit()
    
    # 测试数据 - 模拟陕西建工的财务数据
    test_data = {
        'revenue': 189315365715.47,  # 营业收入
        'net_profit': 3632558433.47,  # 净利润
        'total_assets': 198048254560.47,  # 总资产
        'total_liabilities': 175683811758.47,  # 总负债
        'current_assets': 134578123456.47,  # 流动资产
        'current_liabilities': 121234567890.47,  # 流动负债
        'inventory': 45678901234.47,  # 存货
        'accounts_receivable': 23456789012.47,  # 应收账款
        'total_equity': 22364442802.47  # 净资产
    }
    
    try:
        # 转换为JSON字符串再解析（模拟实际使用场景）
        test_json = json.dumps(test_data)
        financial_data = toolkit._convert_simple_metrics_to_financial_data(test_data)
        
        # 计算财务比率
        ratios = toolkit.calculate_financial_ratios(financial_data)
        
        print("计算的财务比率:")
        for ratio_name, value in ratios.items():
            print(f"  {ratio_name}: {value}")
        
        # 验证关键比率是否计算成功
        key_ratios = ['gross_profit_margin', 'net_profit_margin', 'roe', 'roa', 
                     'debt_to_asset_ratio', 'current_ratio', 'receivables_turnover']
        
        missing_ratios = [ratio for ratio in key_ratios if ratio not in ratios]
        if missing_ratios:
            print(f"\n⚠️  未能计算的比率: {missing_ratios}")
        else:
            print("\n✅ 所有关键比率都计算成功")
        
        # 验证比率合理性
        unreasonable_ratios = []
        for ratio_name, value in ratios.items():
            if ratio_name.endswith('_margin') and not (-50 <= value <= 100):
                unreasonable_ratios.append((ratio_name, value))
            elif ratio_name in ['roe', 'roa'] and not (-100 <= value <= 100):
                unreasonable_ratios.append((ratio_name, value))
            elif ratio_name == 'debt_to_asset_ratio' and not (0 <= value <= 100):
                unreasonable_ratios.append((ratio_name, value))
            elif ratio_name in ['current_ratio'] and not (0.1 <= value <= 10):
                unreasonable_ratios.append((ratio_name, value))
        
        if unreasonable_ratios:
            print(f"\n⚠️  不合理的比率值: {unreasonable_ratios}")
        else:
            print("\n✅ 所有比率值都在合理范围内")
        
        return len(missing_ratios) == 0 and len(unreasonable_ratios) == 0
        
    except Exception as e:
        print(f"[错误] 财务比率计算失败: {e}")
        traceback.print_exc()
        return False

def test_trend_analysis():
    """测试趋势分析功能"""
    print("\n" + "="*60)
    print("测试3: 趋势分析功能")
    print("="*60)
    
    toolkit = FinancialAnalysisToolkit()
    
    # 测试多年数据
    test_data = {
        'historical_trends': {
            '2024': {'revenue': 1893.15, 'net_profit': 36.33, 'total_assets': 1980.48},
            '2023': {'revenue': 1734.28, 'net_profit': 31.25, 'total_assets': 1856.32},
            '2022': {'revenue': 1654.12, 'net_profit': 28.94, 'total_assets': 1723.45},
            '2021': {'revenue': 1543.67, 'net_profit': 25.31, 'total_assets': 1634.78}
        }
    }
    
    try:
        test_json = json.dumps(test_data)
        trends = toolkit.analyze_trends_tool(test_json)
        
        print("趋势分析结果:")
        print(f"  收入数据点: {len(trends.get('revenue', {}).get('data', []))}")
        print(f"  利润数据点: {len(trends.get('profit', {}).get('data', []))}")
        print(f"  收入平均增长率: {trends.get('revenue', {}).get('average_growth', 0)}%")
        print(f"  利润平均增长率: {trends.get('profit', {}).get('average_growth', 0)}%")
        
        # 验证数据完整性
        revenue_data = trends.get('revenue', {}).get('data', [])
        profit_data = trends.get('profit', {}).get('data', [])
        
        if len(revenue_data) >= 2 and len(profit_data) >= 2:
            print("✅ 趋势分析数据完整")
            return True
        else:
            print("❌ 趋势分析数据不完整")
            return False
            
    except Exception as e:
        print(f"❌ 趋势分析失败: {e}")
        traceback.print_exc()
        return False

def test_comprehensive_analysis():
    """测试综合分析功能"""
    print("\n" + "="*60)
    print("测试4: 综合分析功能")
    print("="*60)
    
    toolkit = FinancialAnalysisToolkit()
    
    # 完整的测试数据
    test_data = {
        'company_name': '测试公司',
        'revenue': 189315365715.47,
        'net_profit': 3632558433.47,
        'gross_profit': 14072345678.90,
        'total_assets': 198048254560.47,
        'total_liabilities': 175683811758.47,
        'current_assets': 134578123456.47,
        'current_liabilities': 121234567890.47,
        'inventory': 45678901234.47,
        'accounts_receivable': 23456789012.47,
        'total_equity': 22364442802.47,
        'historical_trends': {
            '2024': {'revenue': 1893.15, 'net_profit': 36.33, 'total_assets': 1980.48},
            '2023': {'revenue': 1734.28, 'net_profit': 31.25, 'total_assets': 1856.32},
            '2022': {'revenue': 1654.12, 'net_profit': 28.94, 'total_assets': 1723.45}
        }
    }
    
    try:
        test_json = json.dumps(test_data)
        result = toolkit.comprehensive_financial_analysis(test_json, '测试公司')
        
        print("综合分析结果:")
        print(f"  分析成功: {result.get('success', False)}")
        print(f"  公司名称: {result.get('company_name', 'N/A')}")
        print(f"  数据格式: {result.get('diagnostics', {}).get('data_format_detected', 'N/A')}")
        print(f"  分析耗时: {result.get('analysis_duration_seconds', 0)}秒")
        print(f"  数据质量评分: {result.get('diagnostics', {}).get('data_quality_score', 0)}")
        print(f"  比率数量: {len(result.get('ratios', {}))}")
        print(f"  健康评分: {result.get('health_assessment', {}).get('overall_score', 0)}")
        
        # 检查关键组件
        success = result.get('success', False)
        has_ratios = bool(result.get('ratios', {}))
        has_trends = bool(result.get('trends', {}))
        has_health = bool(result.get('health_assessment', {}))
        has_diagnostics = bool(result.get('diagnostics', {}))
        
        print(f"\n组件检查:")
        print(f"  分析成功: {'✅' if success else '❌'}")
        print(f"  比率分析: {'✅' if has_ratios else '❌'}")
        print(f"  趋势分析: {'✅' if has_trends else '❌'}")
        print(f"  健康评估: {'✅' if has_health else '❌'}")
        print(f"  诊断信息: {'✅' if has_diagnostics else '❌'}")
        
        return success and has_ratios and has_health and has_diagnostics
        
    except Exception as e:
        print(f"❌ 综合分析失败: {e}")
        traceback.print_exc()
        return False

def test_error_handling():
    """测试错误处理功能"""
    print("\n" + "="*60)
    print("测试5: 错误处理功能")
    print("="*60)
    
    toolkit = FinancialAnalysisToolkit()
    
    error_test_cases = [
        {
            'name': '无效JSON格式',
            'data': 'invalid json string',
            'should_have_error': True
        },
        {
            'name': '空数据',
            'data': '{}',
            'should_have_error': False
        },
        {
            'name': '部分缺失数据',
            'data': '{"revenue": 1000}',  # 只有收入，缺少其他数据
            'should_have_error': False
        }
    ]
    
    success_count = 0
    for test_case in error_test_cases:
        try:
            result = toolkit.comprehensive_financial_analysis(test_case['data'], '测试')
            
            if test_case['should_have_error']:
                # 应该有错误的情况
                if not result.get('success', True):
                    print(f"✅ {test_case['name']}: 正确处理错误")
                    success_count += 1
                else:
                    print(f"❌ {test_case['name']}: 应该有错误但没有")
            else:
                # 不应该有错误的情况
                if result.get('success', False) or result.get('diagnostics'):
                    print(f"✅ {test_case['name']}: 正确处理")
                    success_count += 1
                else:
                    print(f"❌ {test_case['name']}: 处理失败")
                    
        except Exception as e:
            print(f"❌ {test_case['name']}: 异常 - {e}")
    
    print(f"\n错误处理测试结果: {success_count}/{len(error_test_cases)} 通过")
    return success_count == len(error_test_cases)

def main():
    """运行所有测试"""
    print("开始财务分析工具修复效果测试...")
    print("="*60)
    
    test_results = {}
    
    try:
        # 运行各项测试
        test_results['data_format_detection'] = test_data_format_detection()
        test_results['ratio_calculation'] = test_ratio_calculation()
        test_results['trend_analysis'] = test_trend_analysis()
        test_results['comprehensive_analysis'] = test_comprehensive_analysis()
        test_results['error_handling'] = test_error_handling()
        
        # 生成测试总结
        print("\n" + "="*60)
        print("测试总结")
        print("="*60)
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        print(f"测试结果: {passed_tests}/{total_tests} 通过")
        print()
        
        for test_name, passed in test_results.items():
            status = "✅ 通过" if passed else "❌ 失败"
            print(f"  {test_name}: {status}")
        
        if passed_tests == total_tests:
            print("\n🎉 所有测试通过！财务分析工具修复成功！")
            print()
            print("主要修复成果:")
            print("✅ 数据格式识别和标准化 - 支持多种数据格式")
            print("✅ 列映射逻辑增强 - 支持中英文字段名")
            print("✅ 财务比率计算优化 - 增强容错机制")
            print("✅ 趋势分析功能完善 - 支持多年数据分析")
            print("✅ 错误处理和报告 - 详细的诊断信息")
            print("✅ 综合分析工具 - 一站式财务分析")
            print()
            print("现在财务分析工具可以:")
            print("- 自动识别多种财务数据格式")
            print("- 准确计算关键财务比率")
            print("- 进行全面的趋势分析")
            print("- 提供详细的财务健康评估")
            print("- 生成完整的诊断报告")
        else:
            print(f"\n⚠️  {total_tests - passed_tests}项测试失败，需要进一步检查")
            
    except Exception as e:
        print(f"❌ 测试过程中出现严重错误: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()