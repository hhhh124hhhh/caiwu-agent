import asyncio
import json
import os
from utu.tools.report_saver_toolkit import ReportSaverToolkit

async def debug_toolkit():
    print("开始调试ReportSaverToolkit...")
    
    # 创建工具包实例
    toolkit = ReportSaverToolkit(config={"workspace_root": "./debug_toolkit_output"})
    print(f"工具包创建成功，工作目录: {toolkit.workspace_root}")
    
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
    print(f"测试数据创建成功，长度: {len(financial_data_json)}")
    
    # 确保输出目录存在
    os.makedirs("./debug_toolkit_output", exist_ok=True)
    print("输出目录已创建")
    
    # 调用save_pdf_report方法生成PDF报告
    print("正在调用save_pdf_report方法...")
    try:
        result = await toolkit.save_pdf_report(
            financial_data_json=financial_data_json,
            stock_name="测试公司",
            file_prefix="./debug_toolkit_output"
        )
        print(f"调用完成，结果: {result}")
    except Exception as e:
        print(f"调用时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("启动调试...")
    asyncio.run(debug_toolkit())
    print("调试完成")