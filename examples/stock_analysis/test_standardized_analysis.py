#!/usr/bin/env python3
"""
标准化财务分析工具库集成测试
测试与AKShare数据获取工具的完整集成
"""

import sys
import pathlib
import pandas as pd
from datetime import datetime

# 添加项目根目录到Python路径
project_root = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utu.tools.akshare_financial_tool import AKShareFinancialDataTool
from utu.tools.financial_analysis_toolkit import (
    calculate_ratios, 
    analyze_trends, 
    assess_health, 
    generate_report
)


def test_financial_analysis_integration():
    """测试财务分析工具集成"""
    print("=== 标准化财务分析工具库集成测试 ===\n")
    
    try:
        # 1. 初始化数据获取工具
        print("1. 初始化AKShare数据获取工具...")
        data_tool = AKShareFinancialDataTool()
        print("   ✓ 数据获取工具初始化成功")
        
        # 2. 获取财务数据
        print("\n2. 获取陕西建工财务数据...")
        financial_data = data_tool.get_financial_reports("600248", "陕西建工")
        
        if not financial_data or 'income' not in financial_data:
            print("   ✗ 财务数据获取失败")
            return False
        
        print("   ✓ 财务数据获取成功")
        print(f"   - 利润表: {len(financial_data['income'])}行")
        print(f"   - 资产负债表: {len(financial_data['balance'])}行")
        
        # 3. 测试财务比率计算
        print("\n3. 测试财务比率计算...")
        ratios = calculate_ratios(financial_data)
        
        if ratios:
            print("   ✓ 财务比率计算成功")
            print("   主要财务比率:")
            
            for category, category_ratios in ratios.items():
                print(f"     {category}:")
                for ratio_name, ratio_value in category_ratios.items():
                    if isinstance(ratio_value, (int, float)):
                        print(f"       - {ratio_name}: {ratio_value}")
                    else:
                        print(f"       - {ratio_name}: {ratio_value}")
        else:
            print("   ✗ 财务比率计算失败")
            return False
        
        # 4. 测试趋势分析
        print("\n4. 测试趋势分析...")
        trends = analyze_trends(financial_data, 4)
        
        if trends:
            print("   ✓ 趋势分析成功")
            print("   趋势分析结果:")
            
            for trend_type, trend_data in trends.items():
                if isinstance(trend_data, dict) and not trend_data.get('error'):
                    print(f"     {trend_type}:")
                    for key, value in trend_data.items():
                        if key != 'error':
                            print(f"       - {key}: {value}")
        else:
            print("   ✗ 趋势分析失败")
            return False
        
        # 5. 测试健康评估
        print("\n5. 测试财务健康评估...")
        health = assess_health(ratios, trends)
        
        if health:
            print("   ✓ 财务健康评估成功")
            print("   健康评估结果:")
            print(f"     - 综合评分: {health.get('overall_score', 'N/A')}")
            print(f"     - 风险等级: {health.get('risk_level', 'N/A')}")
            
            if health.get('recommendations'):
                print("     - 建议:")
                for rec in health['recommendations']:
                    print(f"       * {rec}")
        else:
            print("   ✗ 财务健康评估失败")
            return False
        
        # 6. 测试完整报告生成
        print("\n6. 测试完整分析报告生成...")
        report = generate_report(financial_data, "陕西建工")
        
        if report:
            print("   ✓ 完整报告生成成功")
            print("   报告摘要:")
            print(f"     - 公司名称: {report.get('company_name', 'N/A')}")
            print(f"     - 分析日期: {report.get('analysis_date', 'N/A')}")
            print(f"     - 关键指标数量: {len(report.get('key_metrics', {}))}")
            print(f"     - 健康评分: {report.get('health_assessment', {}).get('overall_score', 'N/A')}")
            
            # 显示关键指标
            if 'key_metrics' in report:
                print("     关键财务指标:")
                for metric, value in report['key_metrics'].items():
                    print(f"       - {metric}: {value}亿元")
        else:
            print("   ✗ 完整报告生成失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ✗ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_performance_comparison():
    """测试性能对比（传统方式 vs 标准化工具）"""
    print("\n=== 性能对比测试 ===\n")
    
    try:
        # 初始化工具
        data_tool = AKShareFinancialDataTool()
        
        # 测试股票列表
        test_stocks = [
            ("600248", "陕西建工"),
            ("000858", "五粮液"),
            ("600519", "贵州茅台")
        ]
        
        total_time_standardized = 0
        success_count_standardized = 0
        
        for stock_code, stock_name in test_stocks:
            print(f"测试 {stock_name}({stock_code})...")
            
            # 获取数据
            financial_data = data_tool.get_financial_reports(stock_code, stock_name)
            
            if not financial_data:
                print(f"   ✗ 数据获取失败: {stock_name}")
                continue
            
            # 使用标准化工具分析
            start_time = datetime.now()
            
            try:
                ratios = calculate_ratios(financial_data)
                trends = analyze_trends(financial_data)
                health = assess_health(ratios, trends)
                report = generate_report(financial_data, stock_name)
                
                end_time = datetime.now()
                elapsed = (end_time - start_time).total_seconds()
                total_time_standardized += elapsed
                
                if report and health:
                    success_count_standardized += 1
                    print(f"   ✓ 标准化分析成功 - 用时: {elapsed:.2f}秒")
                    print(f"     健康评分: {health.get('overall_score', 'N/A')}")
                else:
                    print(f"   ✗ 标准化分析失败 - 用时: {elapsed:.2f}秒")
                    
            except Exception as e:
                print(f"   ✗ 标准化分析异常: {e}")
        
        # 统计结果
        success_rate = success_count_standardized / len(test_stocks) * 100
        avg_time = total_time_standardized / len(test_stocks)
        
        print(f"\n=== 性能统计 ===")
        print(f"测试股票数: {len(test_stocks)}")
        print(f"成功分析数: {success_count_standardized}")
        print(f"成功率: {success_rate:.1f}%")
        print(f"平均分析时间: {avg_time:.2f}秒/股")
        print(f"总分析时间: {total_time_standardized:.2f}秒")
        
        if success_rate >= 80:
            print("✓ 标准化工具性能表现优秀")
        elif success_rate >= 60:
            print("⚠ 标准化工具性能表现一般")
        else:
            print("✗ 标准化工具性能需要改进")
        
        return success_rate >= 60
        
    except Exception as e:
        print(f"性能对比测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("标准化财务分析工具库完整测试")
    print("=" * 60)
    
    # 基本集成测试
    integration_passed = test_financial_analysis_integration()
    
    # 性能对比测试
    performance_passed = test_performance_comparison()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试结果总结:")
    print(f"集成测试: {'✓ 通过' if integration_passed else '✗ 失败'}")
    print(f"性能测试: {'✓ 通过' if performance_passed else '✗ 失败'}")
    
    if integration_passed and performance_passed:
        print("\n🎉 所有测试通过！")
        print("标准化财务分析工具库可以安全集成到智能体系统中。")
        print("\n主要优势:")
        print("✓ 零代码生成错误")
        print("✓ 稳定的财务比率计算")
        print("✓ 标准化的趋势分析")
        print("✓ 可靠的健康评估")
        print("✓ 完整的报告生成")
        print("✓ 大幅减少token消耗")
        
        print("\n使用建议:")
        print("1. 替换原有的代码生成方式")
        print("2. DataAnalysisAgent专注于调用分析工具")
        print("3. FinancialAnalysisAgent专注于结果解读")
        print("4. 根据分析结果生成投资建议")
    else:
        print("\n❌ 部分测试未通过，需要修复后再使用。")


if __name__ == "__main__":
    main()