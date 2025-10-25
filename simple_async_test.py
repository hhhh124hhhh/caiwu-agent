import asyncio
import json
from utu.tools.report_saver_toolkit import ReportSaverToolkit

async def test():
    # 创建工具包实例
    toolkit = ReportSaverToolkit(config={"workspace_root": "./simple_async_test_output"})
    
    # 创建测试数据
    test_data = {
        "company_name": "测试公司",
        "stock_code": "000001"
    }
    
    # 将数据转换为JSON字符串
    financial_data_json = json.dumps(test_data, ensure_ascii=False)
    print(f"测试数据: {financial_data_json}")
    
    # 调用save_pdf_report方法生成PDF报告
    print("正在生成PDF报告...")
    result = await toolkit.save_pdf_report(
        financial_data_json=financial_data_json,
        stock_name="测试公司",
        file_prefix="./simple_async_test_output"
    )
    print(f"结果: {result}")
    
    return result

# 运行异步函数
result = asyncio.run(test())
print("测试完成")