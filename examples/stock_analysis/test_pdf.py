import asyncio
import json
from utu.tools.report_saver_toolkit import ReportSaverToolkit
from utu.config import ToolkitConfig
import pathlib

async def test_pdf_generation():
    # 设置工作目录
    workspace_path = pathlib.Path(__file__).parent / "stock_analysis_workspace"
    workspace_path.mkdir(exist_ok=True)
    
    # 创建ReportSaverToolkit实例
    toolkit_config = ToolkitConfig(config={"workspace_root": str(workspace_path)}, name="report_saver")
    report_saver_toolkit = ReportSaverToolkit(config=toolkit_config)
    
    # 创建测试数据
    test_data = {
        "company_name": "陕西建工",
        "stock_code": "600248.SH",
        "revenue_billion": 1500.0,
        "net_profit_billion": 28.0,
        "total_assets_billion": 2200.0,
        "total_liabilities_billion": 1700.0,
        "debt_to_asset_ratio": 77.3,
        "roe": 2.82,
        "net_profit_margin": 1.92,
        "trend_data": [
            {"year": "2020", "revenue": 1350.0, "net_profit": 25.0},
            {"year": "2021", "revenue": 1420.0, "net_profit": 26.5},
            {"year": "2022", "revenue": 1480.0, "net_profit": 27.2},
            {"year": "2023", "revenue": 1500.0, "net_profit": 28.0}
        ],
        "key_insights": [
            "公司营收保持稳定增长态势",
            "净利润率略有提升，盈利能力有所改善",
            "资产负债率较高，财务风险需要关注"
        ],
        "investment_advice": "建议关注公司降杠杆进展和盈利能力改善情况",
        "risks": [
            "资产负债率偏高，财务风险较大",
            "建筑行业竞争激烈，毛利率承压",
            "应收账款占比较高，现金流管理需关注"
        ]
    }
    
    # 调用save_pdf_report方法生成PDF报告
    financial_data_json = json.dumps(test_data, ensure_ascii=False)
    pdf_result = await report_saver_toolkit.save_pdf_report(
        financial_data_json=financial_data_json,
        stock_name="陕西建工",
        file_prefix=str(workspace_path)
    )
    
    print(f"PDF生成结果: {pdf_result}")
    
    if pdf_result.get("success"):
        print(f"✅ PDF报告已生成: {pdf_result.get('file_path')}")
    else:
        print(f"⚠️ PDF报告生成失败: {pdf_result.get('message')}")

if __name__ == "__main__":
    asyncio.run(test_pdf_generation())