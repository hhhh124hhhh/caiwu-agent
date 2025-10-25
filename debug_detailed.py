import asyncio
import json
import os
import sys
import traceback

# 重定向stdout和stderr到文件，以便捕获所有输出
# with open('debug_output.txt', 'w', encoding='utf-8') as f:
#     sys.stdout = f
#     sys.stderr = f

print("开始详细调试...")
print(f"当前工作目录: {os.getcwd()}")
print(f"Python版本: {sys.version}")

try:
    from utu.tools.report_saver_toolkit import ReportSaverToolkit
    print("成功导入ReportSaverToolkit")
except Exception as e:
    print(f"导入ReportSaverToolkit失败: {e}")
    traceback.print_exc()
    sys.exit(1)

async def debug_detailed():
    print("进入异步调试函数...")
    
    try:
        # 创建工具包实例
        print("创建工具包实例...")
        toolkit = ReportSaverToolkit(config={"workspace_root": "./debug_detailed_output"})
        print(f"工具包创建成功，工作目录: {toolkit.workspace_root}")
        
        # 创建测试数据
        print("创建测试数据...")
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
        print("转换JSON数据...")
        financial_data_json = json.dumps(test_data, ensure_ascii=False)
        print(f"测试数据创建成功，长度: {len(financial_data_json)}")
        
        # 确保输出目录存在
        print("创建输出目录...")
        os.makedirs("./debug_detailed_output", exist_ok=True)
        print("输出目录已创建")
        
        # 调用save_pdf_report方法生成PDF报告
        print("调用save_pdf_report方法...")
        result = await toolkit.save_pdf_report(
            financial_data_json=financial_data_json,
            stock_name="测试公司",
            file_prefix="./debug_detailed_output"
        )
        print(f"调用完成，结果: {result}")
        
    except Exception as e:
        print(f"异步调试函数执行出错: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("启动详细调试...")
    try:
        asyncio.run(debug_detailed())
    except Exception as e:
        print(f"运行异步函数时出错: {e}")
        traceback.print_exc()
    print("详细调试完成")