#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import pathlib
import re
import os
from typing import Optional
import argparse

from utu.agents import OrchestraAgent
from utu.config import ConfigLoader
from utu.utils.agents_utils import AgentsUtils


async def main():
    # 添加命令行参数解析
    parser = argparse.ArgumentParser(description="数据清洗财报分析智能体 - 支持中文数据处理")
    parser.add_argument("--stream", action="store_true", help="启用流式输出")
    args = parser.parse_args()
    
    # 检查是否设置了必要的环境变量
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

    # 设置数据清洗配置
    print("[CLEANSER] 加载数据清洗智能体配置...")
    try:
        config = ConfigLoader.load_agent_config("examples/stock_analysis_final_with_cleansing")
        print("[OK] 数据清洗配置加载成功")
    except Exception as e:
        print(f"[FAIL] 配置加载失败: {str(e)}")
        return
    
    config.planner_config["examples_path"] = pathlib.Path(__file__).parent / "stock_analysis_examples.json"
    
    # Setup workspace for stock analysis
    workspace_path = pathlib.Path(__file__).parent / "stock_analysis_workspace"
    workspace_path.mkdir(exist_ok=True)
    
    print(f"[WORKSPACE] 使用工作目录: {workspace_path}")
    
    # Initialize the agent
    try:
        runner = OrchestraAgent(config)
        await runner.build()
        print("[OK] 智能体初始化成功")
    except Exception as e:
        print(f"[FAIL] 智能体初始化失败: {str(e)}")
        return

    # 数据清洗专用测试查询
    cleansing_example_queries = [
        {
            "description": "中文财务数据清洗分析",
            "query": "分析测试公司的财务数据，利润表显示营业收入573.88亿元，净利润11.04亿元，历史数据包含2025年和2024年的完整财务表现，需要识别和清洗中文键名数据",
            "features": ["中文键名识别", "历史数据解析", "数据质量评估", "标准化输出"]
        },
        {
            "description": "复杂中文数据结构处理",
            "query": "分析某公司的完整财务报表，包含利润表（营业收入、营业成本、净利润）、资产负债表（总资产、总负债、所有者权益）、现金流量表，历史数据从2022年到2025年的详细财务指标，需要智能清洗和标准化",
            "features": ["完整报表解析", "多年历史数据", "智能字段映射", "数据格式转换"]
        },
        {
            "description": "问题数据修复测试",
            "query": "分析存在问题的财务数据，包含缺失字段、异常值、格式不一致等问题，测试数据清洗智能体的错误检测和自动修复功能",
            "features": ["错误检测", "自动修复", "数据验证", "质量提升"]
        },
        {
            "description": "实际股票分析",
            "query": "分析陕西建工(600248.SH)的最新财报数据，验证数据清洗功能是否正确处理中文键名和历史数据，生成标准化财务分析报告",
            "features": ["真实数据测试", "中文处理验证", "标准化分析", "对比评估"]
        },
        {
            "description": "多格式数据融合",
            "query": "分析包含中英文混合、格式不统一的复杂财务数据，测试数据清洗智能体的多格式处理能力和智能转换功能",
            "features": ["多格式处理", "智能识别", "格式转换", "数据融合"]
        }
    ]

    print("=== 数据清洗财报分析智能体 ===")
    print("[INFO] 增强智能体协作: DataAgent -> DataCleanserAgent -> DataAnalysisAgent -> FinancialAnalysisAgent -> ChartGeneratorAgent -> ReportAgent")
    print("[CLEANSER] 核心功能: 中文数据识别 -> 智能字段映射 -> 数据质量评估 -> 错误修复 -> 标准化输出")
    print("\n数据清洗测试案例:")
    for i, item in enumerate(cleansing_example_queries, 1):
        print(f"{i}. [TEST] {item['description']}")
        print(f"   [QUERY] {item['query']}")
        print(f"   [FEATURES] 数据清洗功能: {', '.join(item['features'])}")
        print()

    try:
        user_input = input("请选择测试案例 (输入数字 1-5) 或输入自定义中文数据分析 (按q退出): ").strip()
        if user_input.lower() == 'q':
            print("\n程序已退出。")
            return
    except EOFError:
        print("\n程序已优雅退出。")
        return

    if user_input.isdigit() and 1 <= int(user_input) <= len(cleansing_example_queries):
        selected_item = cleansing_example_queries[int(user_input) - 1]
        question = selected_item['query']
        print(f"\n[SELECTED] 选择测试: {selected_item['description']}")
        print(f"[CLEANSER] 数据清洗重点: {', '.join(selected_item['features'])}")
    else:
        question = user_input
        print(f"\n[CUSTOM] 自定义数据清洗分析: {question}")

    print(f"\n[START] 启动数据清洗分析流程...")
    print(f"[AGENTS] 增强智能体组合: DataAgent -> DataCleanserAgent -> DataAnalysisAgent -> FinancialAnalysisAgent -> ChartGeneratorAgent -> ReportAgent")
    print(f"[CLEANSING] 数据清洗步骤: 中文识别 -> 字段映射 -> 质量评估 -> 错误修复 -> 标准化输出")
    
    # Run the analysis with or without streaming
    try:
        if args.stream:
            print("[STREAM] 使用流式输出...")
            result = runner.run_streamed(question)
            await AgentsUtils.print_stream_events(result.stream_events())
            final_output = result.final_output
        else:
            print("[NORMAL] 使用标准输出...")
            result = await runner.run(question)
            final_output = result.final_output

        # Extract and save the result
        final_output = result.final_output
        
        # 改进的HTML检测和处理逻辑
        def is_html_content(content):
            """更准确的HTML内容检测"""
            html_indicators = [
                "<html", "<div", "<span", "<p>", "<h1", "<h2", "<h3",
                "<table", "<ul>", "<ol>", "<strong>", "<em>", "<br>", "<hr",
                "<style>", "<script>", "<link>", "<meta>"
            ]
            content_lower = content.lower()
            return any(indicator in content_lower for indicator in html_indicators)

        def format_html_content(content):
            """格式化HTML内容为完整文档"""
            # 提取HTML内容
            if "```html" in content:
                match = re.search(r"```html(.*?)```", content, re.DOTALL)
                if match:
                    content = match.group(1).strip()

            # 检查是否需要添加完整HTML结构
            if not content.strip().startswith("<!DOCTYPE") and not content.strip().startswith("<html"):
                # 添加基本HTML结构和样式
                formatted_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>数据清洗财务分析报告</title>
    <style>
        body {{
            font-family: "Microsoft YaHei", "PingFang SC", "Hiragino Sans GB", Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
            color: #333;
            background-color: #fff;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
        }}
        h1 {{ font-size: 28px; text-align: center; color: #2980b9; }}
        h2 {{ font-size: 22px; }}
        h3 {{ font-size: 18px; }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .metric {{
            background-color: #ecf0f1;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }}
        .positive {{ color: #27ae60; font-weight: bold; }}
        .negative {{ color: #e74c3c; font-weight: bold; }}
        .neutral {{ color: #f39c12; font-weight: bold; }}
        .cleansing-highlight {{
            background-color: #e8f5e8;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #27ae60;
        }}
        blockquote {{
            background-color: #f9f9f9;
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding: 15px;
        }}
        ul, ol {{ margin: 15px 0; padding-left: 30px; }}
        li {{ margin: 5px 0; }}
        .highlight {{
            background-color: #fff3cd;
            padding: 10px;
            border-radius: 4px;
            border: 1px solid #ffeaa7;
        }}
    </style>
</head>
<body>
{content}
</body>
</html>"""
                return formatted_html

            return content

        # 分析报告类型和统计信息
        def analyze_report_type(content):
            """分析报告类型"""
            company_count = len(re.findall(r'\\d{6}\\.(SH|SZ)', content))
            if company_count == 0:
                return "单公司深度分析"
            elif company_count == 1:
                return "单公司财务分析"
            else:
                return f"多公司对比分析({company_count}家)"

        def detect_cleansing_features(content):
            """检测数据清洗特性"""
            features = []
            cleansing_indicators = [
                ("数据清洗", ["清洗", "标准化", "转换", "映射"]),
                ("中文识别", ["中文", "键名", "字段", "中文键"]),
                ("历史数据", ["历史数据", "年份", "2025", "2024", "2023"]),
                ("质量评估", ["质量", "评估", "评分", "验证"]),
                ("错误修复", ["修复", "错误", "异常", "缺失"]),
                ("格式转换", ["格式", "转换", "标准化", "英文"])
            ]
            
            for feature, keywords in cleansing_indicators:
                if any(keyword in content for keyword in keywords):
                    features.append(feature)
            
            return features if features else ["综合分析"]

        # 检测内容类型并保存
        report_type = analyze_report_type(final_output)
        cleansing_features = detect_cleansing_features(final_output)

        print(f"\n[REPORT] 报告类型: {report_type}")
        print(f"[CLEANSER] 数据清洗功能: {', '.join(cleansing_features)}")
        print(f"[SIZE] 内容长度: {len(final_output):,} 字符")

        if is_html_content(final_output):
            # 格式化HTML内容
            formatted_html = format_html_content(final_output)

            report_path = workspace_path / "data_cleansing_analysis_report.html"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(formatted_html)

            file_size = report_path.stat().st_size
            print(f"[OK] HTML报告已生成: {report_path.name} ({file_size:,} bytes)")
            print(f"[HTML] 包含数据清洗高亮样式，完美支持中文内容")
        else:
            # 同时保存TXT和HTML格式
            txt_report_path = workspace_path / "data_cleansing_analysis_report.txt"
            html_report_path = workspace_path / "data_cleansing_analysis_report.html"

            # 保存文本格式
            with open(txt_report_path, "w", encoding="utf-8") as f:
                f.write(f"数据清洗财务分析报告\\n")
                f.write(f"分析时间: {asyncio.get_event_loop().time()}\\n")
                f.write(f"数据清洗功能: {', '.join(cleansing_features)}\\n")
                f.write(f"\\n分析结果:\\n")
                f.write(final_output)
            txt_size = txt_report_path.stat().st_size
            print(f"[TXT] 文本报告: {txt_report_path.name} ({txt_size:,} bytes)")

            # 将文本内容转换为HTML格式
            cleansing_highlight = f"<div class='cleansing-highlight'>数据清洗功能: {', '.join(cleansing_features)}</div>\\n\\n"
            basic_html = format_html_content(cleansing_highlight +
                                       final_output.replace('\\n', '<br>\\n').replace('**', '<strong>').replace('**', '</strong>'))

            with open(html_report_path, "w", encoding="utf-8") as f:
                f.write(basic_html)
            html_size = html_report_path.stat().st_size
            print(f"[HTML] HTML版本: {html_report_path.name} ({html_size:,} bytes)")

        # 分析任务执行情况
        if hasattr(result, 'task_records'):
            task_count = len(result.task_records)
            successful_tasks = sum(1 for task in result.task_records if hasattr(task, 'output') and task.output)
            
            # 检查DataCleanserAgent执行情况
            cleanser_tasks = [task for task in result.task_records if 'DataCleanser' in str(task)]
            cleanser_count = len(cleanser_tasks)
            
            print(f"\n[TASKS] 任务执行统计:")
            print(f"  总任务数: {task_count}")
            print(f"  成功任务: {successful_tasks}")
            print(f"  数据清洗任务: {cleanser_count}")
            print(f"  成功率: {successful_tasks/task_count*100:.1f}%" if task_count > 0 else "  成功率: N/A")
            
            if cleanser_tasks:
                print(f"  [OK] DataCleanserAgent正常执行 ({cleanser_count}个任务)")
            else:
                print(f"  [WARN] 未检测到DataCleanserAgent执行")
            
            # 检查数据清洗效果
            output_str = str(final_output).lower()
            chinese_indicators = ["利润表", "资产负债表", "现金流量表", "营业收入", "净利润"]
            chinese_found = [ind for ind in chinese_indicators if ind in final_output]
            
            if chinese_found:
                print(f"  [CHINESE] 中文数据处理: {', '.join(chinese_found)}")
            
            # 检查标准化输出
            english_indicators = ["income_statement", "balance_sheet", "cash_flow", "revenue", "net_profit"]
            english_found = [ind for ind in english_indicators if ind in output_str]
            
            if english_found:
                print(f"  [STANDARD] 标准化输出: {', '.join(english_found)}")

        print(f"\n[COMPLETE] 数据清洗分析完成!")
        print(f"[WORKSPACE] 工作目录: {workspace_path.absolute()}")
        print(f"[FEATURES] 数据清洗特性: {len(cleansing_features)}项功能应用")

        # List generated files with details
        generated_files = list(workspace_path.glob("*"))
        if generated_files:
            print(f"\n[FILES] 生成的文件 ({len(generated_files)} 个):")
            for file in sorted(generated_files):
                size = file.stat().st_size
                if file.suffix.lower() in ['.html', '.htm']:
                    print(f"  [HTML] {file.name} ({size:,} bytes) - HTML报告")
                elif file.suffix.lower() == '.pdf':
                    print(f"  [PDF] {file.name} ({size:,} bytes) - PDF报告")
                elif file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                    print(f"  [CHART] {file.name} ({size:,} bytes) - 图表文件")
                else:
                    print(f"  [FILE] {file.name} ({size:,} bytes)")

        print(f"\n[VALIDATION] 数据清洗验证:")
        print(f"  1. 在浏览器中打开 HTML 查看格式化报告")
        print(f"  2. 检查是否正确处理了中文键名数据")
        print(f"  3. 验证历史数据年份解析功能")
        print(f"  4. 确认数据质量评估结果")
        print(f"  5. 查看标准化格式输出效果")

    except Exception as e:
        print(f"\n[FAIL] 执行失败: {str(e)}")
        import traceback
        traceback.print_exc()


def main_web():
    """启动Web界面"""
    import argparse
    from utu.ui import ExampleConfig
    from utu.ui.webui_chatbot import WebUIChatbot
    
    # 解析命令行参数
    env_and_args = ExampleConfig()
    
    # 设置数据清洗配置
    print("[CLEANSER] 加载数据清洗智能体配置...")
    try:
        config = ConfigLoader.load_agent_config("examples/stock_analysis_final_with_cleansing")
        print("[OK] 数据清洗配置加载成功")
    except Exception as e:
        print(f"[FAIL] 配置加载失败: {str(e)}")
        return
    
    config.planner_config["examples_path"] = pathlib.Path(__file__).parent / "stock_analysis_examples.json"
    
    workspace_path = pathlib.Path(__file__).parent / "stock_analysis_workspace"
    workspace_path.mkdir(exist_ok=True)
    
    print(f"[WORKSPACE] 使用工作目录: {workspace_path}")
    
    try:
        runner = OrchestraAgent(config)
        example_query = "分析包含中文键名的财务数据，测试数据清洗和标准化功能"
        
        ui = WebUIChatbot(runner, example_query=example_query)
        # 使用默认值或环境变量
        port = int(env_and_args.port) if env_and_args.port else 8848
        ip = env_and_args.ip if env_and_args.ip else "127.0.0.1"
        ui.launch(port=port, ip=ip, autoload=env_and_args.autoload)
        
    except Exception as e:
        print(f"[FAIL] Web界面启动失败: {str(e)}")
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