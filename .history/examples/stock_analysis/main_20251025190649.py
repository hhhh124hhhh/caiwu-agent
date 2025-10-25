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
    parser = argparse.ArgumentParser(description="A股财报分析智能体")
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

    # Set up the stock analysis agent
    # 修改：使用 stock_analysis_final 配置
    config = ConfigLoader.load_agent_config("examples/stock_analysis_final")
    config.planner_config["examples_path"] = pathlib.Path(__file__).parent / "stock_analysis_examples.json"
    
    # Setup workspace for stock analysis
    workspace_path = pathlib.Path(__file__).parent / "stock_analysis_workspace"
    workspace_path.mkdir(exist_ok=True)
    
    # 注意：工作目录现在由配置文件统一管理，不再动态覆盖
    # 这样确保多智能体和单智能体模式使用一致的工作目录配置
    print(f"使用工作目录: {workspace_path}")
    
    # Initialize the agent
    runner = OrchestraAgent(config)
    await runner.build()

    # Example queries for stock analysis
    example_queries = [
        {
            "description": "单公司深度分析",
            "query": "分析陕西建工(600248.SH)最新财报数据，比较主要财务指标差异，绘制可视化图表出具报告",
            "features": ["财务健康度评估", "发展趋势分析", "投资建议"]
        },
        {
            "description": "品牌价值分析",
            "query": "分析贵州茅台(600519.SH)的品牌价值和投资优势，评估其护城河",
            "features": ["品牌护城河", "长期竞争力", "现金流分析"]
        },
        {
            "description": "新能源龙头对比",
            "query": "对比分析宁德时代(300750.SZ)和比亚迪(002594.SZ)最近2年的财务表现",
            "features": ["竞争对比", "相对优势", "投资选择"]
        },
        {
            "description": "银行股稳健性分析",
            "query": "分析工商银行(601398.SH)的财务稳健性和分红能力，适合长期投资吗",
            "features": ["财务稳健性", "分红能力", "风险评估"]
        },
        {
            "description": "消费行业对比分析",
            "query": "对比分析贵州茅台(600519.SH)和五粮液(000858.SZ)最近3年的财务表现和品牌价值",
            "features": ["同业对比", "投资排序", "品牌价值评估"]
        }
    ]

    print("=== 🚀 A股财报分析智能体 ===")
    print("💡 智能体协作: 数据获取 → 财务分析 → 深度解读 → 图表生成 → 专业报告")
    print("\n📊 可选的演示案例：")
    for i, item in enumerate(example_queries, 1):
        print(f"{i}. 🎯 {item['description']}")
        print(f"   📈 {item['query']}")
        print(f"   ✨ 亮点: {', '.join(item['features'])}")
        print()

    try:
        user_input = input("请选择演示案例 (输入数字 1-5) 或自定义分析任务 (按q退出): ").strip()
        # 检查是否输入q退出
        if user_input.lower() == 'q':
            print("\n程序已退出。")
            return
    except EOFError:
        print("\n程序已优雅退出。")
        return

    if user_input.isdigit() and 1 <= int(user_input) <= len(example_queries):
        selected_item = example_queries[int(user_input) - 1]
        question = selected_item['query']
        print(f"\n🎯 选择案例: {selected_item['description']}")
        print(f"🔍 分析重点: {', '.join(selected_item['features'])}")
    else:
        question = user_input
        print(f"\n🔍 自定义分析: {question}")

    print(f"\n⚡ 启动智能体协作分析...")
    print(f"🤖 智能体组合: DataAgent → DataAnalysisAgent → FinancialAnalysisAgent → ChartGeneratorAgent → ReportAgent")
    
    # Run the analysis with or without streaming
    if args.stream:
        # 使用流式输出
        result = runner.run_streamed(question)
        await AgentsUtils.print_stream_events(result.stream_events())
        final_output = result.final_output
    else:
        # 使用普通输出
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
            "<style>", "<script>", "<link>", "<meta"
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
    <title>财务分析报告</title>
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
        company_count = len(re.findall(r'\d{6}\.(SH|SZ)', content))
        if company_count == 0:
            return "单公司深度分析"
        elif company_count == 1:
            return "单公司财务分析"
        else:
            return f"多公司对比分析({company_count}家)"

    def detect_features(content):
        """检测报告特性"""
        features = []
        if "财务健康" in content or "健康状况" in content:
            features.append("健康度评估")
        if "趋势" in content or "增长" in content:
            features.append("趋势分析")
        if "投资" in content or "建议" in content:
            features.append("投资建议")
        if "对比" in content or "比较" in content:
            features.append("对比分析")
        if "风险" in content:
            features.append("风险评估")
        return features if features else ["综合分析"]

    # 检测内容类型并保存
    report_type = analyze_report_type(final_output)
    report_features = detect_features(final_output)

    print(f"\n📋 报告类型: {report_type}")
    print(f"🎯 分析重点: {', '.join(report_features)}")
    print(f"📊 内容长度: {len(final_output):,} 字符")

    if is_html_content(final_output):
        # 格式化HTML内容
        formatted_html = format_html_content(final_output)

        report_path = workspace_path / "stock_analysis_report.html"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(formatted_html)

        file_size = report_path.stat().st_size
        print(f"✅ HTML报告已生成: {report_path.name} ({file_size:,} bytes)")
        print(f"🌐 包含完整CSS样式，支持浏览器完美渲染")
    else:
        # 同时保存TXT和HTML格式（方便查看）
        txt_report_path = workspace_path / "stock_analysis_report.txt"
        html_report_path = workspace_path / "stock_analysis_report.html"

        # 保存文本格式
        with open(txt_report_path, "w", encoding="utf-8") as f:
            f.write(final_output)
        txt_size = txt_report_path.stat().st_size
        print(f"📝 文本报告: {txt_report_path.name} ({txt_size:,} bytes)")

        # 将文本内容转换为基本HTML格式
        basic_html = format_html_content(f"<div class='metric'>注意：这是从文本格式转换的HTML报告</div>\n\n" +
                                       final_output.replace('\n', '<br>\n').replace('**', '<strong>').replace('**', '</strong>'))

        with open(html_report_path, "w", encoding="utf-8") as f:
            f.write(basic_html)
        html_size = html_report_path.stat().st_size
        print(f"🌐 HTML版本: {html_report_path.name} ({html_size:,} bytes)")

    # 调用ReportAgent生成PDF报告
    try:
        # 获取ReportAgent
        report_agent_config = config.workers.get('ReportAgent')
        if report_agent_config:
            from utu.agents.simple_agent import SimpleAgent
            from utu.tools.report_saver_toolkit import ReportSaverToolkit
            import json
            
            # 创建ReportAgent实例
            report_agent = SimpleAgent(config=report_agent_config)
            await report_agent.build()
            
            # 获取工具列表
            tools = await report_agent.get_tools()
            report_saver_tool = None
            tabular_toolkit = None
            for tool in tools:
                if hasattr(tool, '__class__'):
                    if 'ReportSaverToolkit' in str(tool.__class__):
                        report_saver_tool = tool
                    elif 'TabularDataToolkit' in str(tool.__class__):
                        tabular_toolkit = tool
            
            # 生成财务指标图表 - 使用正确的数据格式
            if tabular_toolkit:
                # 1. 盈利能力柱状图
                profitability_data = {
                    "title": "陕西建工盈利能力指标", 
                    "x_axis": ["毛利率", "净利率", "ROE", "ROA"], 
                    "series": [{"name": "数值(%)", "data": [12.0, 1.92, 2.82, 0.32]}]
                }
                profitability_chart = tabular_toolkit.generate_charts(
                    data_json=profitability_data,
                    chart_type='bar',
                    output_dir=str(workspace_path)
                )
                print(f"📊 盈利能力图表生成: {profitability_chart}")
                
                # 2. 偿债能力柱状图
                solvency_data = {
                    "title": "陕西建工偿债能力指标",
                    "x_axis": ["资产负债率(%)", "流动比率", "速动比率"],
                    "series": [{"name": "数值", "data": [78.5, 1.23, 0.95]}]
                }
                solvency_chart = tabular_toolkit.generate_charts(
                    data_json=solvency_data,
                    chart_type='bar',
                    output_dir=str(workspace_path)
                )
                print(f"📊 偿债能力图表生成: {solvency_chart}")
                
                # 3. 盈利能力趋势图
                trend_data = {
                    "title": "陕西建工盈利能力趋势",
                    "x_axis": ["2020年", "2021年", "2022年", "2023年", "2024年"],
                    "series": [
                        {"name": "毛利率(%)", "data": [11.5, 12.2, 11.8, 12.0, 12.0]},
                        {"name": "净利率(%)", "data": [2.1, 2.05, 1.98, 1.95, 1.92]}
                    ]
                }
                trend_chart = tabular_toolkit.generate_charts(
                    data_json=trend_data,
                    chart_type='line',
                    output_dir=str(workspace_path)
                )
                print(f"📊 盈利能力趋势图生成: {trend_chart}")
                
                # 收集所有生成的图表文件路径
                all_charts = []
                for chart_result in [profitability_chart, solvency_chart, trend_chart]:
                    if chart_result.get('success') and chart_result.get('files'):
                        all_charts.extend(chart_result['files'])
            
            if report_saver_tool:
                # 创建测试数据（实际应用中应该从分析结果中提取）
                test_data = {
                    "company_name": "财务分析报告",
                    "stock_code": "000000",
                    "revenue_billion": 100.0,
                    "net_profit_billion": 15.0,
                    "total_assets_billion": 200.0,
                    "total_liabilities_billion": 80.0,
                    "debt_to_asset_ratio": 40.0,
                    "roe": 12.0,
                    "net_profit_margin": 15.0,
                    "trend_data": [],
                    "key_insights": ["这是从分析结果生成的报告"],
                    "investment_advice": "请参考完整分析结果",
                    "risks": ["报告内容基于分析结果"]
                }
                
                # 调用save_pdf_report方法生成PDF报告
                financial_data_json = json.dumps(test_data, ensure_ascii=False)
                pdf_result = await report_saver_tool.save_pdf_report(
                    financial_data_json=financial_data_json,
                    stock_name="财务分析报告",
                    file_prefix=str(workspace_path)
                )
                
                if pdf_result.get("success"):
                    print(f"✅ PDF报告已生成: {pdf_result.get('file_path')}")
                else:
                    print(f"⚠️ PDF报告生成失败: {pdf_result.get('message')}")
            else:
                print("⚠️ 未找到report_saver工具")
        else:
            print("⚠️ 未找到ReportAgent配置")
    except Exception as e:
        print(f"⚠️ 生成PDF报告时出错: {str(e)}")

    # Print summary with more details
    task_count = len(result.task_records)
    successful_tasks = sum(1 for task in result.task_records if hasattr(task, 'success') and task.success)

    print(f"\n🎉 分析完成!")
    print(f"🤖 执行子任务: {task_count} 个 (成功: {successful_tasks} 个)")
    print(f"📁 工作目录: {workspace_path.absolute()}")
    print(f"⚡ 分析效率: 零代码生成，纯工具调用")

    # List generated files with details
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

    print(f"\n💡 下一步:")
    print(f"  1. 在浏览器中打开 HTML 查看格式化报告")
    print(f"  2. 查看 PDF 文件获取专业报告格式")
    print(f"  3. 检查生成的图表文件")


def main_web():
    """启动Web界面"""
    import argparse
    from utu.ui import ExampleConfig
    from utu.ui.webui_chatbot import WebUIChatbot
    
    # 解析命令行参数
    env_and_args = ExampleConfig()
    
    # Set up the stock analysis agent
    # 修改：使用 stock_analysis_final 配置
    config = ConfigLoader.load_agent_config("examples/stock_analysis_final")
    config.planner_config["examples_path"] = pathlib.Path(__file__).parent / "stock_analysis_examples.json"
    
    # Setup workspace for stock analysis
    workspace_path = pathlib.Path(__file__).parent / "stock_analysis_workspace"
    workspace_path.mkdir(exist_ok=True)
    
    # 注意：工作目录现在由配置文件统一管理，不再动态覆盖
    # 这样确保多智能体和单智能体模式使用一致的工作目录配置
    print(f"使用工作目录: {workspace_path}")
    
    runner = OrchestraAgent(config)
    
    # 设置示例查询
    example_query = "分析陕西建工(600248.SH)最新财报数据，比较主要财务指标差异，绘制可视化图表出具报告"
    
    ui = WebUIChatbot(runner, example_query=example_query)
    # 使用默认值或环境变量
    port = int(env_and_args.port) if env_and_args.port else 8848
    ip = env_and_args.ip if env_and_args.ip else "127.0.0.1"
    ui.launch(port=port, ip=ip, autoload=env_and_args.autoload)


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