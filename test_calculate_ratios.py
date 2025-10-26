"""
测试calculate_ratios函数的修复
验证财务比率计算功能是否正常工作
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_calculate_ratios():
    """测试calculate_ratios函数"""
    analyzer = StandardFinancialAnalyzer()
    
    print("\n=== 测试1: 使用扁平化财务指标格式 ===")
    financial_data = {
        "revenue": 573.88,
        "net_profit": 11.04,
        "operating_cost": 522.84,
        "operating_profit": 12.15,
        "total_assets": 3472.98,
        "total_liabilities": 3081.05,
        "current_assets": 2500.00,
        "current_liabilities": 2200.00,
        "accounts_receivable": 800.00,
        "inventory": 600.00,
        "equity": 391.93,
        "operating_cash_flow": 15.00,
        "investing_cash_flow": -20.00,
        "financing_cash_flow": 5.00,
        "previous_revenue": 1511.39,
        "previous_net_profit": 36.11
    }
    
    try:
        result = analyzer.calculate_ratios(financial_data)
        print(f"测试1结果: 成功!")
        print(f"盈利能力指标: {result.get('profitability', {})}")
        print(f"偿债能力指标: {result.get('solvency', {})}")
        print(f"运营效率指标: {result.get('efficiency', {})}")
        print(f"成长能力指标: {result.get('growth', {})}")
        return True
    except Exception as e:
        print(f"测试1失败: {e}")
        return False

def test_calculate_ratios_with_chinese_names():
    """测试使用中文键名的财务数据"""
    analyzer = StandardFinancialAnalyzer()
    
    print("\n=== 测试2: 使用中文键名格式 ===")
    financial_data = {
        "利润表": {
            "营业收入": 573.88,
            "净利润": 11.04,
            "营业成本": 522.84,
            "营业利润": 12.15,
            "利润总额": 12.15
        },
        "资产负债表": {
            "总资产": 3472.98,
            "总负债": 3081.05,
            "流动资产": 2500.00,
            "流动负债": 2200.00,
            "应收账款": 800.00,
            "存货": 600.00,
            "所有者权益": 391.93
        },
        "现金流量表": {
            "经营活动现金流量净额": 15.00,
            "投资活动现金流量净额": -20.00,
            "筹资活动现金流量净额": 5.00
        }
    }
    
    try:
        result = analyzer.calculate_ratios(financial_data)
        print(f"测试2结果: 成功!")
        print(f"盈利能力指标: {result.get('profitability', {})}")
        return True
    except Exception as e:
        print(f"测试2失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试calculate_ratios函数修复...")
    test1_result = test_calculate_ratios()
    test2_result = test_calculate_ratios_with_chinese_names()
    
    if test1_result and test2_result:
        print("\n🎉 所有测试通过! calculate_ratios函数修复成功!")
    else:
        print("\n❌ 部分测试失败，需要进一步调试。")