#!/usr/bin/env python3
"""
优化版股票分析智能体 - 减少token消耗
专注于直接使用AKShare获取数据，避免不必要的搜索和复杂处理
"""

import asyncio
import pathlib
import os
import sys

# 添加项目根目录到Python路径
project_root = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utu.agents import OrchestraAgent
from utu.config import ConfigLoader


async def main():
    """主函数"""
    # 检查环境变量
    llm_type = os.environ.get("UTU_LLM_TYPE")
    llm_model = os.environ.get("UTU_LLM_MODEL")
    llm_api_key = os.environ.get("UTU_LLM_API_KEY")
    llm_base_url = os.environ.get("UTU_LLM_BASE_URL")
    
    if not all([llm_type, llm_model, llm_api_key, llm_base_url]):
        print("错误: 未设置完整的LLM环境变量")
        print("请确保设置了以下环境变量:")
        print("  - UTU_LLM_TYPE")
        print("  - UTU_LLM_MODEL") 
        print("  - UTU_LLM_API_KEY")
        print("  - UTU_LLM_BASE_URL")
        return

    print("=== 优化版A股财报分析智能体 ===")
    print("特点：直接使用AKShare，减少token消耗\n")

    # 加载优化配置
    try:
        config = ConfigLoader.load_agent_config("examples/stock_analysis_optimized")
        print("✓ 优化配置加载成功")
    except Exception as e:
        print(f"✗ 配置加载失败: {e}")
        return

    # 设置工作目录
    workspace_path = pathlib.Path(__file__).parent / "stock_analysis_workspace"
    workspace_path.mkdir(exist_ok=True)
    
    # 配置enhanced_python_executor
    enhanced_executor = config.toolkits.get("enhanced_python_executor")
    if enhanced_executor:
        if enhanced_executor.config is None:
            enhanced_executor.config = {}
        enhanced_executor.config["workspace_root"] = str(workspace_path)
    
    # 初始化智能体
    try:
        runner = OrchestraAgent(config)
        await runner.build()
        print("✓ 智能体初始化成功")
    except Exception as e:
        print(f"✗ 智能体初始化失败: {e}")
        return

    # 简化的分析任务
    analysis_tasks = [
        "使用AKShare获取陕西建工(600248.SH)最新财务数据并生成基础分析报告",
        "分析陕西建工最近3年营收和利润趋势，计算同比变化",
        "计算陕西建工关键财务比率：ROE、负债率、流动比率",
        "生成简单的财务分析HTML报告"
    ]
    
    print("可选的分析任务（已优化以减少token消耗）：")
    for i, task in enumerate(analysis_tasks, 1):
        print(f"{i}. {task}")
    
    print(f"{len(analysis_tasks)+1}. 自定义任务")
    
    # 获取用户选择
    try:
        user_input = input("\n请选择分析任务 (输入数字): ").strip()
        
        if user_input.isdigit() and 1 <= int(user_input) <= len(analysis_tasks):
            question = analysis_tasks[int(user_input) - 1]
        elif user_input.isdigit() and int(user_input) == len(analysis_tasks) + 1:
            question = input("请输入自定义分析任务: ").strip()
        else:
            question = user_input if user_input else analysis_tasks[0]
            
    except KeyboardInterrupt:
        print("\n用户取消操作")
        return
    except Exception as e:
        print(f"输入错误，使用默认任务: {e}")
        question = analysis_tasks[0]
    
    print(f"\n开始分析: {question}")
    print("提示：此版本已优化，将直接使用AKShare获取数据，减少token消耗\n")
    
    # 执行分析
    try:
        result = await runner.run(question)
        
        # 保存结果
        final_output = result.final_output
        
        # 检查是否包含HTML内容
        if "<html" in final_output.lower() or "<div" in final_output.lower():
            html_content = final_output
            if "```html" in html_content:
                import re
                match = re.search(r"```html(.*?)```", html_content, re.DOTALL)
                if match:
                    html_content = match.group(1).strip()
            
            report_path = workspace_path / "analysis_report.html"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"✓ HTML报告已保存到: {report_path}")
        else:
            # 保存为文本文件
            report_path = workspace_path / "analysis_report.txt"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(final_output)
            print(f"✓ 分析报告已保存到: {report_path}")
        
        # 显示统计信息
        print(f"\n=== 分析完成 ===")
        print(f"执行子任务数: {len(result.task_records)}")
        print(f"工作目录: {workspace_path}")
        
        # 列出生成的文件
        generated_files = list(workspace_path.glob("*"))
        if generated_files:
            print(f"\n生成的文件:")
            for file in sorted(generated_files):
                size_kb = file.stat().st_size / 1024
                print(f"  - {file.name} ({size_kb:.1f} KB)")
                
    except Exception as e:
        print(f"✗ 分析执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())