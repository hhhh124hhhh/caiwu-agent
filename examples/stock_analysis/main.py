import asyncio
import pathlib
import re
import os
from typing import Optional

from utu.agents import OrchestraAgent
from utu.config import ConfigLoader


async def main():
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

    # Set up the stock analysis agent
    config = ConfigLoader.load_agent_config("examples/stock_analysis")
    config.planner_config["examples_path"] = pathlib.Path(__file__).parent / "stock_analysis_examples.json"
    
    # Setup workspace for stock analysis
    workspace_path = pathlib.Path(__file__).parent / "stock_analysis_workspace"
    workspace_path.mkdir(exist_ok=True)
    
    # Configure enhanced Python executor workspace
    enhanced_executor = config.toolkits.get("enhanced_python_executor")
    if enhanced_executor is not None and enhanced_executor.config is not None:
        enhanced_executor.config["workspace_root"] = str(workspace_path)
    elif enhanced_executor is not None:
        # 如果 config 是 None，创建一个新的字典
        enhanced_executor.config = {"workspace_root": str(workspace_path)}
    
    # Initialize the agent
    runner = OrchestraAgent(config)
    await runner.build()

    # Example queries for stock analysis
    example_queries = [
        "分析陕西建工(600248.SH)最新财报数据，比较主要财务指标差异，绘制可视化图表出具报告",
        "分析贵州茅台(600519.SH)最近3年的财务状况，生成包含营收、利润、ROE趋势的分析报告",
        "对比分析宁德时代(300750.SZ)和比亚迪(002594.SZ)最近2年的财务表现",
        "分析工商银行(601398.SH)的财务健康状况，重点关注资产质量和盈利能力",
        "评估腾讯控股(00700.HK)的投资价值和风险因素"
    ]
    
    print("=== A股财报分析智能体 ===")
    print("可选的分析任务：")
    for i, query in enumerate(example_queries, 1):
        print(f"{i}. {query}")
    
    # Get user input
    user_input = input("\n请选择分析任务 (输入数字) 或自定义分析任务: ").strip()
    
    if user_input.isdigit() and 1 <= int(user_input) <= len(example_queries):
        question = example_queries[int(user_input) - 1]
    else:
        question = user_input
    
    print(f"\n开始分析: {question}")
    
    # Run the analysis
    result = await runner.run(question)

    # Extract and save the result
    final_output = result.final_output
    
    # Save to HTML file if it contains HTML content
    if "<html" in final_output.lower() or "<div" in final_output.lower():
        html_content = final_output
        if "```html" in html_content:
            # Extract HTML from code block
            match = re.search(r"```html(.*?)```", html_content, re.DOTALL)
            if match:
                html_content = match.group(1).strip()
        
        report_path = workspace_path / "stock_analysis_report.html"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"HTML报告已保存到: {report_path}")
    else:
        # Save as text file
        report_path = workspace_path / "stock_analysis_report.txt"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(final_output)
        print(f"分析报告已保存到: {report_path}")

    # Print summary
    print(f"\n分析完成!")
    print(f"执行了 {len(result.task_records)} 个子任务")
    print(f"工作目录: {workspace_path}")
    
    # List generated files
    generated_files = list(workspace_path.glob("*"))
    if generated_files:
        print(f"\n生成的文件:")
        for file in generated_files:
            print(f"  - {file.name}")


if __name__ == "__main__":
    asyncio.run(main())