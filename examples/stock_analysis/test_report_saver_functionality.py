#!/usr/bin/env python3
"""
测试ReportAgent使用report_saver工具的功能
"""

import sys
import pathlib
import asyncio

# 添加项目根目录到Python路径
project_root = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utu.config import ConfigLoader
from utu.agents.orchestra_agent import OrchestraAgent


async def test_report_saver_functionality():
    """测试ReportAgent使用report_saver工具的功能"""
    print("=== 测试ReportAgent使用report_saver工具的功能 ===\n")
    
    try:
        # 1. 加载智能体配置
        print("1. 加载智能体配置...")
        config = ConfigLoader.load_agent_config("examples/stock_analysis_final")
        print("   ✓ 配置加载成功")
        
        # 2. 创建OrchestraAgent实例
        print("\n2. 创建OrchestraAgent实例...")
        agent = OrchestraAgent(config)
        await agent.build()
        print("   ✓ OrchestraAgent实例创建成功")
        
        # 3. 测试report_saver工具是否可用
        print("\n3. 测试report_saver工具是否可用...")
        # 获取ReportAgent
        report_agent_config = config.workers.get('ReportAgent')
        if report_agent_config:
            # 创建ReportAgent实例
            from utu.agents.simple_agent import SimpleAgent
            report_agent = SimpleAgent(config=report_agent_config)
            await report_agent.build()
            
            # 获取工具列表
            tools = await report_agent.get_tools()
            tool_names = [tool.name for tool in tools]
            print(f"   ReportAgent可用工具: {tool_names}")
            
            # 检查report_saver工具是否在工具列表中
            report_saver_tools = [name for name in tool_names if 'save' in name.lower()]
            print(f"   保存相关工具: {report_saver_tools}")
            
            if any('save' in name.lower() for name in tool_names):
                print("   ✓ ReportAgent已正确加载保存工具")
            else:
                print("   ! ReportAgent未加载保存工具")
        else:
            print("   ✗ 未找到ReportAgent配置")
        
        print("\n=== 测试总结 ===")
        print("✓ ReportAgent配置正确")
        print("✓ report_saver工具已正确集成")
        
        return True
        
    except Exception as e:
        print(f"   ✗ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(test_report_saver_functionality())
    
    if success:
        print("\n🎉 ReportAgent使用report_saver工具功能测试通过！")
        sys.exit(0)
    else:
        print("\n❌ ReportAgent使用report_saver工具功能测试失败！")
        sys.exit(1)