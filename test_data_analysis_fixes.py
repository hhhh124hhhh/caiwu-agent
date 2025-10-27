#!/usr/bin/env python3
"""
专门财务数据测试用例
验证DataAnalysisAgent的数据提取问题修复效果
"""

import sys
import os
from pathlib import Path
import json
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_data_analysis_fixes():
    """测试DataAnalysisAgent修复效果"""
    print("=== DataAnalysisAgent修复效果测试 ===")
    
    # 测试数据 - 模拟用户提供的格式
    test_data = {
        "利润表": {
            "营业收入": 573.88,
            "净利润": 11.04,
            "营业成本": 552.84,
            "营业利润": 11.04,
            "利润总额": 11.04
        },
        "资产负债表": {
            "总资产": 3472.98,
            "总负债": 3081.02,
            "所有者权益": 391.96,
            "流动资产": 2500.45,
            "流动负债": 2800.12,
            "应收账款": 450.23,
            "存货": 380.67,
            "固定资产": 650.34,
            "货币资金": 180.56
        },
        "现金流量表": {
            "经营活动现金流量净额": 25.67,
            "投资活动现金流量净额": -15.23,
            "筹资活动现金流量净额": -8.45,
            "现金及现金等价物净增加额": 1.99
        },
        "关键指标": {
            "净利润率": 1.92,
            "资产负债率": 88.71,
            "ROE": 2.68
        },
        "历史数据": {
            "2025": {
                "营业收入": 573.88,
                "净利润": 11.04
            },
            "2024": {
                "营业收入": 1511.39,
                "净利润": 36.11
            },
            "2023": {
                "营业收入": 1420.56,
                "净利润": 32.45
            },
            "2022": {
                "营业收入": 1280.23,
                "净利润": 28.67
            }
        }
    }
    
    test_results = {
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "test_details": []
    }
    
    def record_test(test_name: str, passed: bool, details: str = ""):
        """记录测试结果"""
        test_results["total_tests"] += 1
        if passed:
            test_results["passed_tests"] += 1
            status = "✅ 通过"
        else:
            test_results["failed_tests"] += 1
            status = "❌ 失败"
        
        test_results["test_details"].append({
            "name": test_name,
            "status": status,
            "details": details
        })
        print(f"   {status}: {test_name}")
        if details:
            print(f"      {details}")
    
    # 测试1: 原始analyze_trends_tool修复验证
    print("\n1. 测试analyze_trends_tool修复效果")
    print("-" * 50)
    
    try:
        from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer
        
        analyzer = StandardFinancialAnalyzer()
        
        # 转换为JSON字符串
        test_data_json = json.dumps(test_data, ensure_ascii=False)
        
        # 测试analyze_trends_tool
        trends_result = analyzer.analyze_trends_tool(test_data_json, years=4)
        
        print("analyze_trends_tool调用完成")
        
        # 验证结果
        if 'revenue' in trends_result and 'profit' in trends_result:
            revenue_data = trends_result['revenue']
            profit_data = trends_result['profit']
            
            # 检查数据是否为空
            revenue_not_empty = revenue_data.get('data') != []
            profit_not_empty = profit_data.get('data') != []
            
            print(f"收入数据为空: {not revenue_not_empty}")
            print(f"利润数据为空: {not profit_not_empty}")
            
            if revenue_not_empty and profit_not_empty:
                record_test("analyze_trends_tool数据提取", True, 
                           f"成功提取数据，收入点数: {len(revenue_data.get('data', []))}, "
                           f"利润点数: {len(profit_data.get('data', []))}")
                
                # 显示具体数据
                print(f"收入趋势: {revenue_data.get('trend', 'unknown')}")
                print(f"利润趋势: {profit_data.get('trend', 'unknown')}")
                print(f"收入平均增长率: {revenue_data.get('average_growth', 0):.2f}%")
                print(f"利润平均增长率: {profit_data.get('average_growth', 0):.2f}%")
            else:
                record_test("analyze_trends_tool数据提取", False, 
                           "数据仍然为空，修复未完全成功")
        else:
            record_test("analyze_trends_tool数据提取", False, 
                       "返回结果格式不正确")
            
    except Exception as e:
        record_test("analyze_trends_tool调用", False, str(e))
        import traceback
        traceback.print_exc()
    
    # 测试2: calculate_ratios工具验证
    print("\n2. 测试calculate_ratios工具")
    print("-" * 50)
    
    try:
        # 使用用户提供的数据格式
        ratios_result = analyzer.calculate_ratios({"financial_data": test_data_json})
        
        if 'profitability' in ratios_result:
            profitability = ratios_result['profitability']
            solvency = ratios_result['solvency']
            
            print(f"净利润率: {profitability.get('net_profit_margin', 0):.2f}%")
            print(f"ROE: {profitability.get('roe', 0):.2f}%")
            print(f"ROA: {profitability.get('roa', 0):.2f}%")
            print(f"资产负债率: {solvency.get('debt_to_asset_ratio', 0):.2f}%")
            
            record_test("calculate_ratios计算", True, 
                       f"成功计算财务比率，包含{len(profitability)}个盈利指标和{len(solvency)}个偿债指标")
        else:
            record_test("calculate_ratios计算", False, "返回结果格式不正确")
            
    except Exception as e:
        record_test("calculate_ratios调用", False, str(e))
    
    # 测试3: assess_health_tool验证
    print("\n3. 测试assess_health_tool")
    print("-" * 50)
    
    try:
        # 使用之前计算的比率数据
        if 'ratios_result' in locals():
            ratios_json = json.dumps(ratios_result, ensure_ascii=False)
            health_result = analyzer.assess_health_tool(ratios_json)
            
            if 'overall_health' in health_result:
                print(f"总体健康状况: {health_result.get('overall_health', 'unknown')}")
                print(f"健康评分: {health_result.get('score', 0)}/100")
                print(f"分析: {health_result.get('analysis', '')[:100]}...")
                
                record_test("assess_health_tool评估", True, 
                           f"成功完成健康评估，状态: {health_result.get('overall_health')}")
            else:
                record_test("assess_health_tool评估", False, "返回结果格式不正确")
        else:
            record_test("assess_health_tool评估", False, "缺少比率数据")
            
    except Exception as e:
        record_test("assess_health_tool调用", False, str(e))
    
    # 测试4: 增强版DataAnalysisAgent验证
    print("\n4. 测试增强版DataAnalysisAgent")
    print("-" * 50)
    
    try:
        from utu.agents.enhanced_data_analysis_agent import analyze_financial_data_intelligently
        
        enhanced_result = analyze_financial_data_intelligently(test_data_json, "陕西建工")
        
        if enhanced_result.get('success'):
            print("智能分析成功")
            
            # 显示关键结果
            ratios = enhanced_result.get('ratios', {})
            health = enhanced_result.get('health_assessment', {})
            recommendations = enhanced_result.get('recommendations', [])
            
            print(f"健康状态: {health.get('overall_health', 'unknown')}")
            print(f"健康评分: {health.get('health_score', 0)}/100")
            print(f"建议数量: {len(recommendations)}")
            
            record_test("增强版DataAnalysisAgent", True, 
                       f"智能分析成功，生成了{len(recommendations)}条建议")
        else:
            print(f"智能分析失败: {enhanced_result.get('error', 'Unknown error')}")
            record_test("增强版DataAnalysisAgent", False, enhanced_result.get('error', 'Unknown error'))
            
    except Exception as e:
        record_test("增强版DataAnalysisAgent", False, str(e))
        import traceback
        traceback.print_exc()
    
    # 测试5: 数据格式转换验证
    print("\n5. 测试数据格式转换")
    print("-" * 50)
    
    try:
        from utu.schemas import AgentMessage, DataType, AgentDataFormatter
        from utu.data_conversion import UniversalDataConverter
        
        # 创建标准化的财务比率消息
        ratios_message = AgentDataFormatter.create_agent_message(
            sender="DataAnalysisAgent",
            data=test_data.get('关键指标', {}),
            data_type=DataType.FINANCIAL_RATIOS,
            receiver="ChartGeneratorAgent"
        )
        
        print(f"原始消息类型: {ratios_message.data_type.value}")
        
        # 转换为图表格式
        converter = UniversalDataConverter()
        chart_message = converter.convert_message(
            ratios_message, DataType.CHART_DATA, "ChartGeneratorAgent"
        )
        
        print(f"转换后消息类型: {chart_message.data_type.value}")
        
        if chart_message.data_type == DataType.CHART_DATA:
            chart_data = chart_message.content.get('chart_data', {})
            print(f"生成图表数量: {len(chart_data)}")
            
            record_test("数据格式转换", True, 
                       f"成功转换数据格式，生成{len(chart_data)}个图表数据")
        else:
            record_test("数据格式转换", False, 
                       f"转换失败，目标类型: {chart_message.data_type.value}")
            
    except Exception as e:
        record_test("数据格式转换", False, str(e))
        import traceback
        traceback.print_exc()
    
    # 输出测试摘要
    print("\n" + "=" * 60)
    print("测试摘要")
    print("=" * 60)
    
    total = test_results["total_tests"]
    passed = test_results["failed_tests"]
    failed = test_results["failed_tests"]
    
    print(f"总测试数: {total}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"成功率: {(passed/total*100):.1f}%")
    
    if failed > 0:
        print("\n失败的测试:")
        for test in test_results["test_details"]:
            if "失败" in test["status"]:
                print(f"   - {test['name']}: {test['details']}")
    
    print("\n详细测试结果:")
    for test in test_results["test_details"]:
        print(f"   {test['status']}: {test['name']}")
    
    return test_results

def main():
    """主函数"""
    print("开始DataAnalysisAgent修复效果验证")
    
    results = test_data_analysis_fixes()
    
    if results["failed_tests"] == 0:
        print("\n🎉 所有测试通过！DataAnalysisAgent修复成功！")
        print("用户现在可以正常使用财务分析功能了。")
    else:
        print(f"\n⚠️ 还有 {results['failed_tests']} 个测试失败，需要进一步调试。")
    
    return results

if __name__ == "__main__":
    main()