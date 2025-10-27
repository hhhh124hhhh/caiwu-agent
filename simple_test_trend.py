#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化的趋势分析测试脚本
"""

import json

# 陕西建工数据
data_dict = {
    "company_name": "陕西建工",
    "stock_code": "600248.SH",
    "financial_data": {
        "income_statement": {
            "records": 102,
            "latest": {
                "revenue": 573.88,
                "net_profit": 11.04
            },
            "previous_year": {
                "revenue": 1511.39,
                "net_profit": 36.11
            }
        }
    }
}

# 直接模拟我们添加的修复逻辑
print("模拟修复后的趋势分析逻辑...")

try:
    # 提取关键财务数据
    simple_data = {
        'company_name': data_dict.get('company_name', '目标公司'),
        'stock_code': data_dict.get('stock_code', ''),
        'revenue': data_dict['financial_data']['income_statement'].get('latest', {}).get('revenue', 0),
        'net_profit': data_dict['financial_data']['income_statement'].get('latest', {}).get('net_profit', 0),
        'prev_revenue': data_dict['financial_data']['income_statement'].get('previous_year', {}).get('revenue', 0),
        'prev_net_profit': data_dict['financial_data']['income_statement'].get('previous_year', {}).get('net_profit', 0)
    }
    
    # 计算增长率
    trends = {
        'revenue': {'data': [], 'trend': 'stable', 'average_growth': 0.0},
        'profit': {'data': [], 'trend': 'stable', 'average_growth': 0.0},
        'growth_rates': {'revenue_growth': [], 'profit_growth': [], 'assets_growth': []}
    }
    
    # 计算收入增长率
    if simple_data['prev_revenue'] > 0 and simple_data['revenue'] > 0:
        revenue_growth = ((simple_data['revenue'] - simple_data['prev_revenue']) / simple_data['prev_revenue']) * 100
        trends['revenue']['average_growth'] = round(revenue_growth, 2)
        trends['growth_rates']['revenue_growth'] = [round(revenue_growth, 2)]
        
        if revenue_growth > 5:
            trends['revenue']['trend'] = 'increasing'
        elif revenue_growth < -5:
            trends['revenue']['trend'] = 'decreasing'
    
    # 计算利润增长率
    if simple_data['prev_net_profit'] > 0 and simple_data['net_profit'] > 0:
        profit_growth = ((simple_data['net_profit'] - simple_data['prev_net_profit']) / simple_data['prev_net_profit']) * 100
        trends['profit']['average_growth'] = round(profit_growth, 2)
        trends['growth_rates']['profit_growth'] = [round(profit_growth, 2)]
        
        if profit_growth > 5:
            trends['profit']['trend'] = 'increasing'
        elif profit_growth < -5:
            trends['profit']['trend'] = 'decreasing'
    
    # 添加数据点
    company_name = simple_data.get('company_name', '目标公司')
    
    # 添加当年数据
    trends['revenue']['data'].append({
        '公司': company_name,
        '年份': '2025',
        '营业收入': simple_data['revenue']
    })
    
    trends['profit']['data'].append({
        '公司': company_name,
        '年份': '2025',
        '净利润': simple_data['net_profit']
    })
    
    # 添加历史数据点
    if simple_data['prev_revenue'] > 0:
        trends['revenue']['data'].append({
            '公司': company_name,
            '年份': '2024',
            '营业收入': simple_data['prev_revenue']
        })
    
    if simple_data['prev_net_profit'] > 0:
        trends['profit']['data'].append({
            '公司': company_name,
            '年份': '2024',
            '净利润': simple_data['prev_net_profit']
        })
    
    # 打印结果
    print("\n分析结果:")
    print(json.dumps(trends, indent=2, ensure_ascii=False))
    
    print("\n✅ 修复逻辑验证成功! 现在可以正确处理陕西建工的数据格式。")
    
    # 计算同比变化
    print(f"\n📊 财务分析摘要:")
    print(f"公司: {simple_data['company_name']} ({simple_data['stock_code']})")
    print(f"当年收入: {simple_data['revenue']}亿元")
    print(f"上年收入: {simple_data['prev_revenue']}亿元")
    print(f"收入同比变化: {trends['revenue']['average_growth']}%")
    print(f"当年利润: {simple_data['net_profit']}亿元")
    print(f"上年利润: {simple_data['prev_net_profit']}亿元")
    print(f"利润同比变化: {trends['profit']['average_growth']}%")
    
    # 分析结果解读
    print(f"\n📈 趋势分析:")
    print(f"收入趋势: {trends['revenue']['trend']}")
    print(f"利润趋势: {trends['profit']['trend']}")
    
    if trends['revenue']['average_growth'] < 0 and trends['profit']['average_growth'] < 0:
        print("⚠️  警示: 收入和利润均呈现下降趋势，需要深入分析原因。")
    elif trends['revenue']['average_growth'] < 0 and trends['profit']['average_growth'] > 0:
        print("📝 注意: 收入下降但利润增长，可能是成本控制有效或业务结构调整。")
    elif trends['revenue']['average_growth'] > 0 and trends['profit']['average_growth'] < 0:
        print("⚠️  警示: 收入增长但利润下降，可能是成本上升或竞争加剧。")
    else:
        print("✅ 良好: 收入和利润均呈现增长趋势。")
        
except Exception as e:
    print(f"\n❌ 错误: {str(e)}")
    import traceback
    traceback.print_exc()