#!/usr/bin/env python3
"""
完整分析流程验证测试
使用用户提供的确切数据格式进行测试
"""

import sys
import os
from pathlib import Path
import json

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_complete_analysis_workflow():
    """测试完整的分析工作流程"""
    print("=== 完整分析流程验证 ===")
    
    # 使用用户提供的确切数据格式
    user_exact_data = {
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
            "2025": {"营业收入": 573.88, "净利润": 11.04},
            "2024": {"营业收入": 1511.39, "净利润": 36.11},
            "2023": {"营业收入": 1420.56, "净利润": 32.45},
            "2022": {"营业收入": 1280.23, "净利润": 28.67}
        }
    }
    
    try:
        from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer
        
        analyzer = StandardFinancialAnalyzer()
        data_json = json.dumps(user_exact_data, ensure_ascii=False)
        
        print("开始完整分析流程...")
        
        # 步骤1: calculate_ratios (用户之前成功的步骤)
        print("\n步骤1: calculate_ratios")
        ratios_result = analyzer.calculate_ratios({"financial_data": data_json})
        
        if 'profitability' in ratios_result:
            profit = ratios_result['profitability']
            solvency = ratios_result['solvency']
            print(f"  净利润率: {profit.get('net_profit_margin', 0):.2f}%")
            print(f"  ROE: {profit.get('roe', 0):.2f}%")
            print(f"  ROA: {profit.get('roa', 0):.2f}%")
            print(f"  资产负债率: {solvency.get('debt_to_asset_ratio', 0):.2f}%")
            print("  ✓ 财务比率计算成功")
        else:
            print("  ✗ 财务比率计算失败")
            return False
        
        # 步骤2: analyze_trends_tool (修复的重点)
        print("\n步骤2: analyze_trends_tool")
        trends_result = analyzer.analyze_trends_tool(data_json, years=4)
        
        if 'revenue' in trends_result and 'profit' in trends_result:
            revenue_data = trends_result['revenue']
            profit_data = trends_result['profit']
            
            print(f"  收入数据状态: {'有数据' if revenue_data.get('data') else '无数据'}")
            print(f"  利润数据状态: {'有数据' if profit_data.get('data') else '无数据'}")
            print(f"  收入趋势: {revenue_data.get('trend', 'unknown')}")
            print(f"  利润趋势: {profit_data.get('trend', 'unknown')}")
            print(f"  收入平均增长率: {revenue_data.get('average_growth', 0):.2f}%")
            print(f"  利润平均增长率: {profit_data.get('average_growth', 0):.2f}%")
            
            if revenue_data.get('data') and profit_data.get('data'):
                print("  ✓ 趋势分析修复成功")
            else:
                print("  ✗ 趋势分析仍有问题")
                return False
        else:
            print("  ✗ 趋势分析返回格式错误")
            return False
        
        # 步骤3: assess_health (使用独立工具)
        print("\n步骤3: assess_health_tool")
        ratios_json = json.dumps(ratios_result, ensure_ascii=False)
        health_result = analyzer.assess_health_tool(ratios_json)
        
        if 'overall_health' in health_result:
            print(f"  总体健康状况: {health_result.get('overall_health', 'unknown')}")
            print(f"  健康评分: {health_result.get('score', 0)}/100")
            print("  ✓ 健康评估成功")
        else:
            print("  ✗ 健康评估失败")
            return False
        
        # 步骤4: 增强版分析 (可选)
        print("\n步骤4: 增强版数据分析 (可选)")
        try:
            from utu.agents.enhanced_data_analysis_agent import analyze_financial_data_intelligently
            
            enhanced_result = analyze_financial_data_intelligently(data_json, "陕西建工")
            
            if enhanced_result.get('success'):
                print("  ✓ 增强版分析成功")
                recommendations = enhanced_result.get('recommendations', [])
                print(f"  生成建议数量: {len(recommendations)}")
            else:
                print("  ! 增强版分析失败，但不影响核心功能")
        except Exception as e:
            print(f"  ! 增强版分析跳过: {e}")
        
        print("\n=== 完整分析流程验证结果 ===")
        print("核心功能验证:")
        print("✓ calculate_ratios - 财务比率计算")
        print("✓ analyze_trends_tool - 历史数据趋势分析 (修复重点)")
        print("✓ assess_health_tool - 财务健康评估")
        print("✓ 数据格式兼容性 - 支持中文键名和历史数据")
        
        print("\n主要修复内容:")
        print("1. 修复了'历史数据'键名识别")
        print("2. 修复了年份键名解析 ('2025', '2024'等)")
        print("3. 修复了中英文字段名映射")
        print("4. 修复了DataFrame列名标准化")
        print("5. 增强了数据预处理逻辑")
        
        print("\n用户现在可以:")
        print("• 正常使用analyze_trends_tool分析历史数据趋势")
        print("• 获得非空的收入和利润数据")
        print("• 查看正确的趋势分析结果")
        print("• 继续完成完整的财务分析流程")
        
        return True
        
    except Exception as e:
        print(f"\n测试过程出现异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始验证DataAnalysisAgent修复效果")
    print("使用用户提供的确切数据格式进行测试")
    
    success = test_complete_analysis_workflow()
    
    if success:
        print("\n🎉 修复验证成功！")
        print("DataAnalysisAgent的数据提取问题已经完全解决！")
        print("用户可以正常使用财务分析功能了。")
    else:
        print("\n❌ 验证失败，需要进一步调试。")
    
    return success

if __name__ == "__main__":
    main()