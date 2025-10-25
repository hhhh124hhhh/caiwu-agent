import json
import asyncio
import os
from utu.tools.report_saver_toolkit import ReportSaverToolkit

# 检查PDF支持
try:
    from fpdf import FPDF
    from fpdf.html import HTMLMixin
    PDF_SUPPORT = True
    print("PDF支持可用")
except ImportError as e:
    PDF_SUPPORT = False
    print(f"PDF支持不可用: {e}")

async def debug_pdf():
    print("开始调试PDF生成功能...")
    
    # 创建工具包实例
    toolkit = ReportSaverToolkit(config={"workspace_root": "./debug_output"})
    
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
        "net_profit_margin": 15.12
    }
    
    # 将数据转换为JSON字符串
    financial_data_json = json.dumps(test_data, ensure_ascii=False)
    print(f"测试数据: {financial_data_json}")
    
    # 调用save_pdf_report方法生成PDF报告
    print("正在生成PDF报告...")
    try:
        result = await toolkit.save_pdf_report(
            financial_data_json=financial_data_json,
            stock_name="测试公司",
            file_prefix="./debug_output"
        )
        print(f"结果: {result}")
    except Exception as e:
        print(f"生成PDF时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_pdf())