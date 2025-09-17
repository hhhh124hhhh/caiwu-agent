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

# 直接从工具文件导入，避免utu模块初始化问题
from utu.tools.report_saver_toolkit import ReportSaverToolkit

async def test_fixed_pdf_report():
    """测试修复后的PDF报告生成功能"""
    
    # 创建工具包实例，使用字典配置
    config = {"workspace_root": "./run_workdir"}
    report_toolkit = ReportSaverToolkit(config)
    
    # 创建更复杂的测试数据
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
            "营收持续增长，三年复合增长率达12.5%",
            "盈利能力稳定提升，净利润率保持在15%以上",
            "资产负债结构合理，财务风险可控"
        ],
        "investment_advice": "建议长期持有，关注公司在新兴市场的拓展情况",
        "risks": [
            "行业竞争加剧风险，需关注市场份额变化",
            "原材料价格波动风险，建议关注成本控制",
            "宏观经济政策变化风险，需关注政策导向"
        ],
        "executive_summary": [
            "公司财务状况良好，盈利能力持续增强",
            "资产结构优化，负债水平合理",
            "现金流充裕，具备良好的发展潜力"
        ]
    }
    
    # 将数据转换为JSON字符串
    financial_data_json = json.dumps(test_data, ensure_ascii=False)
    
    # 使用时间戳创建唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 调用save_pdf_report方法生成PDF报告
    print("正在生成修复版PDF报告...")
    result: Dict[str, Any] = await report_toolkit.save_pdf_report(
        financial_data_json=financial_data_json,
        stock_name=f"测试公司_{timestamp}",
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
    asyncio.run(test_fixed_pdf_report())