#!/usr/bin/env python3
"""
简化的股票分析测试脚本
用于验证配置修复后的功能
"""

import asyncio
import pathlib
import sys
import os

# 添加项目根目录到Python路径
project_root = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utu.agents import OrchestraAgent
from utu.config import ConfigLoader


async def test_simple_analysis():
    """简单的财务分析测试"""
    print("=== 简化版A股财报分析智能体测试 ===")
    
    # 检查环境变量
    llm_type = os.environ.get("UTU_LLM_TYPE")
    llm_model = os.environ.get("UTU_LLM_MODEL")
    llm_api_key = os.environ.get("UTU_LLM_API_KEY")
    llm_base_url = os.environ.get("UTU_LLM_BASE_URL")
    
    if not all([llm_type, llm_model, llm_api_key, llm_base_url]):
        print("错误: 未设置完整的LLM环境变量")
        return False

    print("1. 加载配置...")
    try:
        config = ConfigLoader.load_agent_config("examples/stock_analysis_final")
        print("   配置加载成功")
    except Exception as e:
        print(f"   配置加载失败: {e}")
        return False

    print("2. 设置工作目录...")
    try:
        workspace_path = pathlib.Path(__file__).parent / "stock_analysis_workspace"
        workspace_path.mkdir(exist_ok=True)
        print(f"   工作目录: {workspace_path}")
    except Exception as e:
        print(f"   工作目录设置失败: {e}")
        return False

    print("3. 初始化智能体...")
    try:
        runner = OrchestraAgent(config)
        await runner.build()
        print("   智能体初始化成功")
    except Exception as e:
        print(f"   智能体初始化失败: {e}")
        return False

    print("4. 执行简单分析任务...")
    try:
        # 简单的测试任务
        question = "分析陕西建工(600248.SH)最新财务数据并生成基础分析报告"
        print(f"   分析任务: {question}")
        
        # 使用流式输出
        result = runner.run_streamed(question)
        
        print("5. 处理分析结果...")
        final_output = result.final_output
        print(f"   分析完成，结果长度: {len(final_output)} 字符")
        
        # 检查是否包含HTML内容
        if "<html" in final_output.lower():
            print("   检测到HTML报告内容")
        
        # 检查工作目录中的文件
        workspace_files = list(workspace_path.glob("*"))
        print(f"   生成文件数量: {len(workspace_files)}")
        for file in workspace_files[:5]:  # 只显示前5个文件
            print(f"   - {file.name}")
        
        print("分析测试成功完成！")
        return True
        
    except Exception as e:
        print(f"   分析执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(test_simple_analysis())
        if result:
            print("\n=== 测试结果: 成功 ===")
            print("配置修复有效，系统可以正常运行！")
        else:
            print("\n=== 测试结果: 失败 ===")
            print("仍需进一步调试。")
    except KeyboardInterrupt:
        print("\n用户取消测试")
    except Exception as e:
        print(f"\n测试过程出现异常: {e}")