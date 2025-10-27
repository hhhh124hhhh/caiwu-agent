#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据清洗配置的主程序
使用stock_analysis_final_with_cleansing.yaml配置
"""

import asyncio
import pathlib
import os
from typing import Optional
import argparse

from utu.agents import OrchestraAgent
from utu.config import ConfigLoader
from utu.utils.agents_utils import AgentsUtils


async def main():
    """测试数据清洗配置的主函数"""
    # 添加命令行参数解析
    parser = argparse.ArgumentParser(description="数据清洗财报分析智能体测试")
    parser.add_argument("--stream", action="store_true", help="启用流式输出")
    args = parser.parse_args()
    
    # 检查环境变量
    llm_type = os.environ.get("UTU_LLM_TYPE")
    llm_model = os.environ.get("UTU_LLM_MODEL")
    llm_api_key = os.environ.get("UTU_LLM_API_KEY")
    llm_base_url = os.environ.get("UTU_LLM_BASE_URL")
    
    if not all([llm_type, llm_model, llm_api_key, llm_base_url]):
        print("警告: 未设置完整的LLM环境变量")
        print("请确保设置了以下环境变量:")
        print("  - UTU_LLM_TYPE")
        print("  - UTU_LLM_MODEL")
        print("  - UTU_LLM_API_KEY")
        print("  - UTU_LLM_BASE_URL")
        print()

    # 使用数据清洗配置
    print("加载配置: stock_analysis_final_with_cleansing.yaml")
    try:
        config = ConfigLoader.load_agent_config("examples/stock_analysis_final_with_cleansing")
        print("✓ 配置加载成功")
    except Exception as e:
        print(f"✗ 配置加载失败: {str(e)}")
        return
    
    # 设置示例文件路径
    config.planner_config["examples_path"] = pathlib.Path(__file__).parent / "stock_analysis_examples.json"
    
    # 设置工作空间
    workspace_path = pathlib.Path(__file__).parent / "stock_analysis_workspace"
    workspace_path.mkdir(exist_ok=True)
    
    print(f"使用工作目录: {workspace_path}")
    
    try:
        # 初始化智能体
        print("初始化智能体...")
        runner = OrchestraAgent(config)
        await runner.build()
        print("✓ 智能体初始化成功")
    except Exception as e:
        print(f"✗ 智能体初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return

    # 测试查询 - 专门测试中文数据
    test_queries = [
        {
            "description": "测试中文财务数据解析",
            "query": "分析测试公司的财务数据，利润表显示营业收入573.88亿元，净利润11.04亿元，历史数据包含2025年和2024年的财务表现",
            "expected_features": ["中文数据识别", "历史数据解析", "数据清洗", "标准化输出"]
        },
        {
            "description": "测试复杂中文数据",
            "query": "分析某公司的完整财务报表，包含利润表、资产负债表、现金流量表，历史数据从2022年到2025年的详细财务指标",
            "expected_features": ["完整报表解析", "多年历史数据", "财务比率计算", "趋势分析"]
        }
    ]

    print("\n=== 🚀 数据清洗财报分析智能体测试 ===")
    print("💡 工作流程: DataAgent → DataCleanserAgent → DataAnalysisAgent → FinancialAnalysisAgent → ChartGeneratorAgent → ReportAgent")
    print("🎯 重点测试: 中文数据识别、历史数据解析、数据质量保证")
    
    print("\n📊 可选测试案例:")
    for i, item in enumerate(test_queries, 1):
        print(f"{i}. 🎯 {item['description']}")
        print(f"   📈 {item['query']}")
        print(f"   ✨ 预期特性: {', '.join(item['expected_features'])}")
        print()

    try:
        user_input = input("请选择测试案例 (输入数字 1-2) 或自定义测试 (按q退出): ").strip()
        if user_input.lower() == 'q':
            print("\n程序已退出。")
            return
    except EOFError:
        print("\n程序已优雅退出。")
        return

    if user_input.isdigit() and 1 <= int(user_input) <= len(test_queries):
        selected_item = test_queries[int(user_input) - 1]
        question = selected_item['query']
        print(f"\n🎯 选择测试: {selected_item['description']}")
        print(f"🔍 测试重点: {', '.join(selected_item['expected_features'])}")
    else:
        question = user_input
        print(f"\n🔍 自定义测试: {question}")

    print(f"\n⚡ 启动数据清洗分析流程...")
    print(f"🤖 智能体组合: DataAgent → DataCleanserAgent → DataAnalysisAgent → FinancialAnalysisAgent → ChartGeneratorAgent → ReportAgent")
    print(f"🧹 数据清洗: 中文识别 → 字段映射 → 质量评估 → 标准化输出")
    
    try:
        # 运行分析
        if args.stream:
            print("使用流式输出...")
            result = runner.run_streamed(question)
            await AgentsUtils.print_stream_events(result.stream_events())
            final_output = result.final_output
        else:
            print("使用标准输出...")
            result = await runner.run(question)
            final_output = result.final_output

        # 输出结果摘要
        print(f"\n📋 分析完成!")
        print(f"📄 内容长度: {len(str(final_output)):,} 字符")
        
        # 检查是否包含数据清洗的迹象
        output_str = str(final_output).lower()
        cleansing_indicators = [
            "标准化", "质量", "清洗", "映射", "转换", "验证"
        ]
        found_indicators = [ind for ind in cleansing_indicators if ind in output_str]
        
        if found_indicators:
            print(f"🧹 数据清洗迹象: {', '.join(found_indicators)}")
        
        # 检查是否成功处理了中文数据
        chinese_indicators = [
            "利润表", "资产负债表", "现金流量表", "营业收入", "净利润"
        ]
        chinese_found = [ind for ind in chinese_indicators if ind in final_output]
        
        if chinese_found:
            print(f"🈯 中文数据处理: {', '.join(chinese_found)}")
        
        # 保存结果
        result_file = workspace_path / "data_cleansing_test_result.txt"
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write(f"数据清洗配置测试结果\n")
            f.write(f"测试时间: {asyncio.get_event_loop().time()}\n")
            f.write(f"测试查询: {question}\n")
            f.write(f"数据清洗迹象: {found_indicators}\n")
            f.write(f"中文数据处理: {chinese_found}\n")
            f.write(f"\n分析结果:\n")
            f.write(str(final_output))
        
        print(f"✅ 结果已保存: {result_file}")
        
        # 分析任务执行情况
        if hasattr(result, 'task_records'):
            task_count = len(result.task_records)
            successful_tasks = sum(1 for task in result.task_records if hasattr(task, 'output') and task.output)
            
            print(f"\n🤖 任务执行统计:")
            print(f"  总任务数: {task_count}")
            print(f"  成功任务: {successful_tasks}")
            print(f"  成功率: {successful_tasks/task_count*100:.1f}%" if task_count > 0 else "  成功率: N/A")
            
            # 检查DataCleanserAgent是否执行
            cleanser_tasks = [task for task in result.task_records if 'DataCleanser' in str(task)]
            if cleanser_tasks:
                print(f"  ✓ DataCleanserAgent执行了 {len(cleanser_tasks)} 个任务")
            else:
                print(f"  ⚠️ 未检测到DataCleanserAgent执行记录")
        
        print(f"\n🎉 数据清洗配置测试完成!")
        print(f"📁 工作目录: {workspace_path.absolute()}")
        
        # 列出生成的文件
        generated_files = list(workspace_path.glob("*"))
        if generated_files:
            print(f"\n📄 生成的文件 ({len(generated_files)} 个):")
            for file in sorted(generated_files):
                size = file.stat().st_size
                if file.suffix.lower() in ['.html', '.htm']:
                    print(f"  🌐 {file.name} ({size:,} bytes) - HTML报告")
                elif file.suffix.lower() == '.pdf':
                    print(f"  📋 {file.name} ({size:,} bytes) - PDF报告")
                elif file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                    print(f"  📈 {file.name} ({size:,} bytes) - 图表文件")
                else:
                    print(f"  📄 {file.name} ({size:,} bytes)")

    except Exception as e:
        print(f"\n❌ 执行失败: {str(e)}")
        import traceback
        traceback.print_exc()


def main_web():
    """启动Web界面测试"""
    import argparse
    from utu.ui import ExampleConfig
    from utu.ui.webui_chatbot import WebUIChatbot
    
    # 解析命令行参数
    env_and_args = ExampleConfig()
    
    # 使用数据清洗配置
    print("加载配置: stock_analysis_final_with_cleansing.yaml")
    try:
        config = ConfigLoader.load_agent_config("examples/stock_analysis_final_with_cleansing")
        print("✓ 配置加载成功")
    except Exception as e:
        print(f"✗ 配置加载失败: {str(e)}")
        return
    
    config.planner_config["examples_path"] = pathlib.Path(__file__).parent / "stock_analysis_examples.json"
    
    workspace_path = pathlib.Path(__file__).parent / "stock_analysis_workspace"
    workspace_path.mkdir(exist_ok=True)
    
    print(f"使用工作目录: {workspace_path}")
    
    try:
        runner = OrchestraAgent(config)
        example_query = "分析测试公司的中文财务数据，验证数据清洗功能"
        
        ui = WebUIChatbot(runner, example_query=example_query)
        port = int(env_and_args.port) if env_and_args.port else 8848
        ip = env_and_args.ip if env_and_args.ip else "127.0.0.1"
        
        print(f"🌐 启动Web界面: http://{ip}:{port}")
        ui.launch(port=port, ip=ip, autoload=env_and_args.autoload)
        
    except Exception as e:
        print(f"❌ Web界面启动失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        try:
            main_web()
        except KeyboardInterrupt:
            print("\n程序已优雅退出。")
            exit(0)
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\n程序已优雅退出。")
            exit(0)