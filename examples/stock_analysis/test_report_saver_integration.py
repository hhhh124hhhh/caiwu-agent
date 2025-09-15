#!/usr/bin/env python3
"""
测试ReportAgent与report_saver工具的集成
"""

import sys
import pathlib
import asyncio

# 添加项目根目录到Python路径
project_root = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utu.config import ConfigLoader
from utu.agents.orchestra_agent import OrchestraAgent


async def test_report_saver_integration():
    """测试ReportAgent与report_saver工具的集成"""
    print("=== 测试ReportAgent与report_saver工具的集成 ===\n")
    
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
        
        # 3. 检查ReportAgent是否包含report_saver工具
        print("\n3. 检查ReportAgent工具配置...")
        # 从workers_info中查找ReportAgent的工具配置
        workers_info = config.workers_info
        report_agent_tools = None
        for worker_info in workers_info:
            if worker_info.get('name') == 'ReportAgent':
                report_agent_tools = worker_info.get('tools', [])
                break
        
        if report_agent_tools is not None:
            print(f"   ReportAgent工具列表: {report_agent_tools}")
            if 'report_saver' in report_agent_tools:
                print("   ✓ ReportAgent已正确配置report_saver工具")
            else:
                print("   ✗ ReportAgent未配置report_saver工具")
                return False
        else:
            print("   ✗ 未找到ReportAgent配置")
            return False
        
        # 4. 测试简单的分析任务
        print("\n4. 测试简单的分析任务...")
        test_query = "分析贵州茅台(600519.SH)的财务状况"
        
        # 运行智能体
        result = await agent.run(test_query)
        
        # 检查结果
        if result and result.final_output:
            print("   ✓ 智能体运行成功")
            print(f"   最终输出长度: {len(result.final_output)} 字符")
            # 显示部分输出内容
            preview = result.final_output[:200] + "..." if len(result.final_output) > 200 else result.final_output
            print(f"   输出预览: {preview}")
        else:
            print("   ✗ 智能体运行失败或无输出")
            return False
            
        print("\n=== 测试总结 ===")
        print("✓ ReportAgent已成功集成report_saver工具")
        print("✓ 智能体配置正确加载")
        print("✓ 智能体能够正常运行")
        
        return True
        
    except Exception as e:
        print(f"   ✗ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(test_report_saver_integration())
    
    if success:
        print("\n🎉 ReportAgent与report_saver工具集成测试通过！")
        sys.exit(0)
    else:
        print("\n❌ ReportAgent与report_saver工具集成测试失败！")
        sys.exit(1)