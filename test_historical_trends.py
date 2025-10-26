import json
from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer

# 用户提供的测试数据
financial_data_json = '''{"income_statement": {"revenue": 573.88, "net_profit": 11.04, "gross_profit": 0.0, "operating_profit": 0.0}, "balance_sheet": {"total_assets": 3472.98, "total_liabilities": 3081.05, "equity": 391.93, "current_assets": 0.0, "current_liabilities": 0.0}, "cash_flow": {"operating_cash_flow": 25.0, "investing_cash_flow": 0.0, "financing_cash_flow": 0.0}, "key_ratios": {"net_profit_margin": 1.92, "roe": 100.0, "roa": 0.32, "debt_to_asset_ratio": 88.71, "current_ratio": 0.72, "quick_ratio": 0.72, "asset_turnover": 0.17, "receivables_turnover": 50.0, "inventory_turnover": 383000000.0, "cash_flow_ratio": 0.01, "cash_reinvestment_ratio": 0.42}, "historical_trends": {"revenue_trend": [573.88, 500.0, 450.0, 400.0], "net_profit_trend": [11.04, 10.0, 8.0, 6.0], "years": [2025, 2024, 2023, 2022]}}'''

# 初始化分析器
analyzer = StandardFinancialAnalyzer()

# 调用修复后的函数
result = analyzer.analyze_trends_tool(financial_data_json, years=4)

# 打印结果
print("趋势分析结果:")
print(json.dumps(result, ensure_ascii=False, indent=2))

# 验证是否有数据返回
if result.get('revenue', {}).get('data') and result.get('profit', {}).get('data'):
    print("\n测试成功: 已正确处理historical_trends格式的数据")
    # 检查增长率计算
    if result.get('growth_rates', {}).get('revenue_growth') and result.get('growth_rates', {}).get('profit_growth'):
        print(f"\n收入平均增长率: {result['revenue']['average_growth']}%")
        print(f"利润平均增长率: {result['profit']['average_growth']}%")
        print("增长率计算正确!")
else:
    print("\n测试失败: 数据处理仍然存在问题")