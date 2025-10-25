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

    # 调用ReportAgent生成完整报告
    try:
        # 获取ReportAgent
        report_agent_config = config.workers.get('ReportAgent')
        if report_agent_config:
            from utu.agents.simple_agent import SimpleAgent
            from utu.tools.report_saver_toolkit import ReportSaverToolkit
            import json
            from datetime import datetime
            
            # 创建ReportAgent实例
            report_agent = SimpleAgent(config=report_agent_config)
            await report_agent.build()
            
            # 直接创建ReportSaverToolkit实例
            from utu.config import ToolkitConfig
            toolkit_config = ToolkitConfig(config={"workspace_root": str(workspace_path)}, name="report_saver")
            report_saver_toolkit = ReportSaverToolkit(config=toolkit_config)
            
            # 从任务记录中收集并整合前面智能体的所有分析结果
            def collect_agent_results(task_records):
                """从任务记录中收集并整合各个智能体的分析结果"""
                results = {
                    "basic_info": {"company_profile": "", "business_description": ""},
                    "financial_data": {"revenue": "N/A", "net_profit": "N/A", "total_assets": "N/A", "total_liabilities": "N/A"},
                    "ratio_analysis": {"summary": ""},
                    "trend_analysis": {"summary": ""},
                    "cash_flow_analysis": {},
                    "valuation_analysis": {},
                    "risk_assessment": {"summary": "", "risk_factors": []},
                    "investment_advice": {"summary": "", "recommendation": "", "target_price": "N/A", "rating": "N/A"}
                }
                
                # 从任务记录中提取信息
                for task in task_records:
                    if hasattr(task, 'output') and task.output:
                        output_str = str(task.output)
                        
                        # 提取公司名称和股票代码
                        import re
                        stock_match = re.search(r'([^()]+)\((\d{6}\.(?:SH|SZ))\)', output_str)
                        if stock_match:
                            results["company_name"] = stock_match.group(1)
                            results["stock_code"] = stock_match.group(2)
                        
                        # 提取财务数据
                        if any(keyword in output_str for keyword in ["营业收入", "净利润", "总资产", "总负债"]):
                            for key, pattern in {
                                "revenue": r'营业收入[^\d]+([\d.]+)',
                                "net_profit": r'净利润[^\d]+([\d.]+)',
                                "total_assets": r'总资产[^\d]+([\d.]+)',
                                "total_liabilities": r'总负债[^\d]+([\d.]+)'
                            }.items():
                                match = re.search(pattern, output_str)
                                if match:
                                    results["financial_data"][key] = match.group(1)
                        
                        # 提取投资建议
                        if "投资建议" in output_str or "评级" in output_str:
                            results["investment_advice"]["summary"] = output_str[:200] + "..." if len(output_str) > 200 else output_str
                            if "买入" in output_str or "推荐" in output_str:
                                results["investment_advice"]["recommendation"] = "推荐买入"
                                results["investment_advice"]["rating"] = "买入"
                            elif "持有" in output_str:
                                results["investment_advice"]["recommendation"] = "建议持有"
                                results["investment_advice"]["rating"] = "持有"
                        
                        # 提取风险因素
                        if "风险" in output_str:
                            results["risk_assessment"]["summary"] = output_str[:200] + "..." if len(output_str) > 200 else output_str
                            # 尝试提取具体风险点
                            risk_patterns = [r'[。，]([^。，]+风险[^。，]+)[。，]', r'风险：([^。]+)']
                            for pattern in risk_patterns:
                                for match in re.finditer(pattern, output_str):
                                    risk_item = match.group(1)
                                    if risk_item not in results["risk_assessment"]["risk_factors"]:
                                        results["risk_assessment"]["risk_factors"].append(risk_item)
                
                # 如果没有找到公司名称，使用默认值
                if "company_name" not in results:
                    results["company_name"] = "目标公司"
                    results["stock_code"] = "N/A"
                
                return results
            
            # 收集并整合智能体结果
            agent_results = collect_agent_results(result.task_records)
            
            # 整合前面智能体的所有分析结果
            integrated_data = {
                "company_name": agent_results.get("company_name", "目标公司"),
                "stock_code": agent_results.get("stock_code", "N/A"),
                "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # 使用当前时间
                "basic_info": agent_results["basic_info"],
                "financial_data": agent_results["financial_data"],
                "ratio_analysis": agent_results["ratio_analysis"],
                "trend_analysis": agent_results["trend_analysis"],
                "chart_files": [str(f) for f in workspace_path.glob("*.png")],  # 包含所有生成的图表
                "cash_flow_analysis": agent_results["cash_flow_analysis"],
                "valuation_analysis": agent_results["valuation_analysis"],
                "risk_assessment": agent_results["risk_assessment"],
                "investment_advice": agent_results["investment_advice"]
            }
            
            # 生成完整的HTML报告
            print("\n📊 正在生成HTML报告...")
            # 创建结构化的HTML报告内容
            html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{integrated_data['company_name']} 综合财务分析报告</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        h1, h2, h3 {{ color: #2c3e50; }}
        h1 {{ text-align: center; margin-bottom: 30px; padding-bottom: 15px; border-bottom: 2px solid #3498db; }}
        h2 {{ margin-top: 40px; padding-bottom: 10px; border-bottom: 1px solid #eee; }}
        .report-info {{ text-align: center; margin-bottom: 30px; color: #666; }}
        .section {{ background: white; padding: 20px; margin-bottom: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .chart-container {{ margin: 20px 0; text-align: center; }}
        .chart-container img {{ max-width: 100%; height: auto; border: 1px solid #eee; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .highlight {{ background-color: #ffffcc; padding: 10px; margin: 10px 0; border-left: 4px solid #f39c12; }}
        .risk {{ color: #e74c3c; font-weight: bold; }}
        .opportunity {{ color: #27ae60; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>{integrated_data['company_name']} 综合财务分析报告</h1>
    <div class="report-info">
        <p>股票代码: {integrated_data['stock_code']}</p>
        <p>分析日期: {integrated_data['analysis_date']}</p>
    </div>
    
    <div class="section">
        <h2>1. 执行摘要</h2>
        <p>{investment_advice.get('summary', '公司财务状况总体分析...')}</p>
    </div>
    
    <div class="section">
        <h2>2. 公司基本信息</h2>
        <p>{basic_info.get('company_profile', '公司基本情况介绍...')}</p>
        <p>{basic_info.get('business_description', '主营业务描述...')}</p>
    </div>
    
    <div class="section">
        <h2>3. 财务数据分析</h2>
        <p>主要财务指标:</p>
        <table>
            <tr><th>指标</th><th>数值</th><th>单位</th></tr>
            <tr><td>营业收入</td><td>{financial_data.get('revenue', 'N/A')}</td><td>亿元</td></tr>
            <tr><td>净利润</td><td>{financial_data.get('net_profit', 'N/A')}</td><td>亿元</td></tr>
            <tr><td>总资产</td><td>{financial_data.get('total_assets', 'N/A')}</td><td>亿元</td></tr>
            <tr><td>总负债</td><td>{financial_data.get('total_liabilities', 'N/A')}</td><td>亿元</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h2>4. 财务比率分析</h2>
        <p>{ratio_analysis.get('summary', '财务比率分析结果...')}</p>
    </div>
    
    <div class="section">
        <h2>5. 趋势分析</h2>
        <p>{trend_analysis.get('summary', '财务趋势分析...')}</p>
    </div>
    
    <div class="section">
        <h2>6. 风险评估</h2>
        <p>{risk_assessment.get('summary', '风险因素分析...')}</p>
        <ul>
            {''.join([f'<li class="risk">{risk}</li>' for risk in risk_assessment.get('risk_factors', [])])}
        </ul>
    </div>
    
    <div class="section">
        <h2>7. 投资建议</h2>
        <p class="highlight">{investment_advice.get('recommendation', '投资建议内容...')}</p>
        <p>目标价位: {investment_advice.get('target_price', 'N/A')}</p>
        <p>投资评级: {investment_advice.get('rating', 'N/A')}</p>
    </div>
    
    <div class="section">
        <h2>8. 附录 - 图表</h2>
        <p>以下是本次分析生成的主要图表:</p>
        <!-- 这里将在保存时动态添加图表 -->
    </div>
</body>
</html>
            """
            
            # 保存HTML报告
            current_date = datetime.now().strftime("%Y%m%d%H%M%S")
            html_file_name = f"{integrated_data['company_name']}_综合财务分析报告_{current_date}.html"
            html_file_path = workspace_path / html_file_name
            
            # 添加图表到HTML报告
            for chart_file in integrated_data['chart_files']:
                chart_name = chart_file.split('\\')[-1]
                html_content = html_content.replace('<!-- 这里将在保存时动态添加图表 -->', 
                    f'<div class="chart-container"><h3>{chart_name}</h3><img src="{chart_name}" alt="{chart_name}"></div>\n<!-- 这里将在保存时动态添加图表 -->')
            
            # 移除剩余的注释标记
            html_content = html_content.replace('<!-- 这里将在保存时动态添加图表 -->', '')
            
            with open(html_file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✅ HTML报告已生成: {html_file_path}")
            
            # 调用save_pdf_report方法生成PDF报告
            print("\n📄 正在生成PDF报告...")
            financial_data_json = json.dumps(integrated_data, ensure_ascii=False)
            pdf_result = await report_saver_toolkit.save_pdf_report(
                financial_data_json=financial_data_json,
                stock_name=integrated_data['company_name'],
                file_prefix=str(workspace_path),
                chart_files=integrated_data['chart_files']
            )
            
            if pdf_result.get("success"):
                print(f"✅ PDF报告已生成: {pdf_result.get('file_path')}")
            else:
                print(f"⚠️ PDF报告生成失败: {pdf_result.get('message')}")
                
            # 也生成Markdown版本报告作为备份
            md_content = f"# {integrated_data['company_name']} 综合财务分析报告\n\n"
            md_content += f"**股票代码**: {integrated_data['stock_code']}\n"
            md_content += f"**分析日期**: {integrated_data['analysis_date']}\n\n"
            md_content += "## 1. 执行摘要\n"
            md_content += f"{investment_advice.get('summary', '公司财务状况总体分析...')}\n\n"
            md_content += "## 2. 公司基本信息\n"
            md_content += f"{basic_info.get('company_profile', '公司基本情况介绍...')}\n\n"
            
            md_file_name = f"{integrated_data['company_name']}_财务分析报告_{current_date}.md"
            md_file_path = workspace_path / md_file_name
            with open(md_file_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"✅ Markdown报告已生成: {md_file_path}")
        else:
            print("⚠️ 未找到ReportAgent配置")
    except Exception as e:
        print(f"⚠️ 生成报告时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        traceback.print_exc()

    # Print summary with more details
    task_count = len(result.task_records)
    successful_tasks = sum(1 for task in result.task_records if hasattr(task, 'output') and task.output)

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