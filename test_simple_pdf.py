import json
import asyncio
import os
from utu.tools.report_saver_toolkit import ReportSaverToolkit

async def test_simple_pdf():
    # 创建工具包实例
    toolkit = ReportSaverToolkit(config={"workspace_root": "./test_output"})
    
    # 创建测试数据
    test_data = {
        "company_name": "测试公司",
        "stock_code": "000001",
        "revenue_billion": 100.5,
        "net_profit_billion": 15.2,
        "total_assets_billion": 200.8,
        "total_liabilities_billion": 80.3,
        "debt_to_asset_ratio": 39.99,
        "roe": 12.5,
        "net_profit_margin": 15.12,
        "trend_data": [
            {"year": "2021", "revenue": 80.2, "net_profit": 10.1},
            {"year": "2022", "revenue": 90.8, "net_profit": 12.5},
            {"year": "2023", "revenue": 100.5, "net_profit": 15.2}
        ],
        "key_insights": [
            "营收持续增长",
            "盈利能力稳定提升",
            "资产负债结构合理"
        ],
        "investment_advice": "建议长期持有",
        "risks": [
            "行业竞争加剧风险",
            "原材料价格波动风险"
        ]
    }
    
    # 将数据转换为JSON字符串
    financial_data_json = json.dumps(test_data, ensure_ascii=False)
    
    # 调用save_pdf_report方法生成PDF报告
    print("正在生成PDF报告...")
    result = await toolkit.save_pdf_report(
        financial_data_json=financial_data_json,
        stock_name="测试公司",
        file_prefix="./test_output"
    )
    
    # 打印结果
    print("PDF报告生成结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    return result

if __name__ == "__main__":
    result = asyncio.run(test_simple_pdf())
    print("测试完成")