import sys
import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any

# 添加项目根目录到Python路径
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, project_root)

# 设置工作目录
os.chdir(project_root)

from utu.tools.report_saver_toolkit import ReportSaverToolkit
from utu.config import ToolkitConfig

async def test_pdf_report():
    """测试PDF报告生成功能"""
    
    # 创建工具包实例
    config = ToolkitConfig(config={"workspace_root": "./run_workdir"})
    toolkit = ReportSaverToolkit(config)
    
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
    result: Dict[str, Any] = await toolkit.save_pdf_report(
        financial_data_json=financial_data_json,
        stock_name="测试公司",
        file_prefix="./run_workdir"
    )
    
    # 打印结果
    print("PDF报告生成结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 检查文件是否生成成功
    if result.get("success"):
        file_path = result.get("file_path")
        if file_path and isinstance(file_path, str) and os.path.exists(file_path):
            print(f"\n✓ PDF报告已成功生成: {file_path}")
            file_size = result.get('file_size', 0)
            print(f"文件大小: {file_size} 字节")
        else:
            print(f"\n✗ PDF报告生成失败: 文件不存在")
    else:
        message = result.get('message', '未知错误')
        print(f"\n✗ PDF报告生成失败: {message}")

if __name__ == "__main__":
    asyncio.run(test_pdf_report())