import json
import sys
import os
import asyncio

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the ReportSaverToolkit
from utu.tools.report_saver_toolkit import ReportSaverToolkit

# 测试数据 - 医药行业分析数据
medical_data = {
    "医药行业分析": {
        "分析时间": "2025年",
        "分析公司数量": 5,
        "公司明细": [
            {
                "名称": "药明康德",
                "股票代码": "603259",
                "净利润率": 41.64,
                "营收(亿元)": 207.99,
                "净利润(亿元)": 86.60,
                "ROE": 14.17,
                "资产负债率": 27.93,
                "行业分类": "CXO"
            }
        ]
    },
    "关键发现": {
        "利润率超过10%的公司数量": 5,
        "平均净利润率": 29.0,
        "最高利润率": 41.64,
        "最低利润率": 17.15,
        "行业特点": "高利润率、高ROE、相对低负债"
    }
}

async def test_save_report():
    # 创建ReportSaverToolkit实例
    toolkit = ReportSaverToolkit()
    
    # 测试保存报告功能
    print("测试保存行业分析报告...")
    try:
        json_data = json.dumps(medical_data, ensure_ascii=False)
        print(f"输入JSON数据: {json_data}")
        
        result = await toolkit.save_text_report(
            financial_data_json=json_data,
            stock_name="医药行业",
            file_prefix="./run_workdir"
        )
        print(f"保存结果: {result}")
        
        # 检查生成的文件
        if result.get("success") and result.get("file_path"):
            file_path = result["file_path"]
            print(f"检查生成的文件: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print("文件内容预览:")
                print(content[:500] + "..." if len(content) > 500 else content)
    except Exception as e:
        print(f"保存失败: {e}")
        import traceback
        traceback.print_exc()

# 运行异步测试
if __name__ == "__main__":
    asyncio.run(test_save_report())