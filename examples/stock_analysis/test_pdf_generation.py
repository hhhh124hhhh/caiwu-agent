"""
测试PDF报告生成功能
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utu.config import ConfigLoader
from utu.agents.simple_agent import SimpleAgent
from utu.tools.report_saver_toolkit import ReportSaverToolkit

async def test_pdf_generation():
    """测试PDF报告生成功能"""
    print("=== 测试PDF报告生成功能 ===\n")
    
    try:
        # 1. 加载智能体配置
        print("1. 加载智能体配置...")
        config = ConfigLoader.load_agent_config("examples/stock_analysis_final")
        print("   ✓ 配置加载成功")
        
        # 2. 获取ReportAgent配置
        print("\n2. 获取ReportAgent配置...")
        report_agent_config = config.workers.get('ReportAgent')
        if not report_agent_config:
            print("   ✗ 未找到ReportAgent配置")
            return False
            
        print("   ✓ ReportAgent配置获取成功")
        
        # 3. 创建ReportAgent实例
        print("\n3. 创建ReportAgent实例...")
        report_agent = SimpleAgent(config=report_agent_config)
        await report_agent.build()
        print("   ✓ ReportAgent实例创建成功")
        
        # 4. 获取工具列表
        print("\n4. 获取工具列表...")
        tools = await report_agent.get_tools()
        report_saver_tool = None
        for tool in tools:
            if hasattr(tool, '__class__') and 'ReportSaverToolkit' in str(tool.__class__):
                report_saver_tool = tool
                break
                
        if not report_saver_tool:
            print("   ✗ 未找到report_saver工具")
            return False
            
        print("   ✓ report_saver工具获取成功")
        
        # 5. 创建测试数据
        print("\n5. 创建测试数据...")
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
        
        financial_data_json = json.dumps(test_data, ensure_ascii=False)
        print("   ✓ 测试数据创建成功")
        
        # 6. 调用save_pdf_report方法生成PDF报告
        print("\n6. 调用save_pdf_report方法生成PDF报告...")
        workspace_path = Path(__file__).parent / "stock_analysis_workspace"
        workspace_path.mkdir(exist_ok=True)
        
        pdf_result = await report_saver_tool.save_pdf_report(
            financial_data_json=financial_data_json,
            stock_name="测试公司",
            file_prefix=str(workspace_path)
        )
        
        print("   PDF报告生成结果:")
        print(f"   {json.dumps(pdf_result, ensure_ascii=False, indent=2)}")
        
        # 7. 检查文件是否生成成功
        if pdf_result.get("success"):
            file_path = pdf_result.get("file_path")
            if file_path and isinstance(file_path, str) and os.path.exists(file_path):
                print(f"\n   ✓ PDF报告已成功生成: {file_path}")
                file_size = pdf_result.get('file_size', 0)
                print(f"   文件大小: {file_size} 字节")
                return True
            else:
                print(f"\n   ✗ PDF报告生成失败: 文件不存在")
                return False
        else:
            message = pdf_result.get('message', '未知错误')
            print(f"\n   ✗ PDF报告生成失败: {message}")
            return False
            
    except Exception as e:
        print(f"   ✗ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(test_pdf_generation())
    
    if success:
        print("\n🎉 PDF报告生成功能测试通过！")
        sys.exit(0)
    else:
        print("\n❌ PDF报告生成功能测试失败！")
        sys.exit(1)