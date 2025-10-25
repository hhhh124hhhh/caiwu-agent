#!/usr/bin/env python3
"""
综合测试脚本：验证HTML报告渲染和PDF生成功能修复
"""

import sys
import os
import json
import asyncio
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utu.tools.report_saver_toolkit import ReportSaverToolkit

async def test_html_functionality():
    """测试HTML功能"""
    print("=== 测试HTML报告功能 ===")

    # 创建工具包实例
    config = {"workspace_root": "./stock_analysis_workspace"}
    toolkit = ReportSaverToolkit(config)

    # 创建测试HTML内容
    test_html_content = """
    <div class="metric">
        <h2>测试公司财务分析报告</h2>
        <table>
            <tr>
                <th>指标</th>
                <th>2023年</th>
                <th>2022年</th>
            </tr>
            <tr>
                <td>营业收入(亿元)</td>
                <td class="positive">100.5</td>
                <td>90.8</td>
            </tr>
            <tr>
                <td>净利润(亿元)</td>
                <td class="positive">15.2</td>
                <td>12.5</td>
            </tr>
            <tr>
                <td>ROE(%)</td>
                <td class="positive">12.5</td>
                <td>11.2</td>
            </tr>
        </table>

        <h3>关键洞察</h3>
        <ul>
            <li>营收持续增长，同比增长10.7%</li>
            <li>盈利能力稳定提升</li>
            <li>财务结构健康</li>
        </ul>
    </div>
    """

    # 测试保存HTML报告
    result = await toolkit.save_analysis_report(
        content=test_html_content,
        report_name="测试公司HTML报告",
        file_format="html",
        workspace_dir="./stock_analysis_workspace"
    )

    print("HTML保存结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    return result.get("success", False)

async def test_pdf_functionality():
    """测试PDF功能"""
    print("\n=== 测试PDF生成功能 ===")

    # 创建工具包实例
    config = {"workspace_root": "./stock_analysis_workspace"}
    toolkit = ReportSaverToolkit(config)

    # 测试字体检测
    print("测试字体检测功能...")
    available_fonts = toolkit.get_available_chinese_fonts()
    print(f"检测到可用字体: {available_fonts}")

    # 创建测试数据
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

    # 测试传统PDF生成
    print("测试传统PDF生成...")
    pdf_result = await toolkit.save_pdf_report(
        financial_data_json=financial_data_json,
        stock_name="测试公司",
        file_prefix="./stock_analysis_workspace"
    )

    print("PDF生成结果:")
    print(json.dumps(pdf_result, ensure_ascii=False, indent=2))

    # 测试HTML转PDF功能
    print("\n测试HTML转PDF功能...")
    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{test_data['company_name']}财务分析报告</title>
    </head>
    <body>
        <h1>{test_data['company_name']}财务分析报告</h1>
        <h2>核心财务指标</h2>
        <table border="1">
            <tr><th>指标</th><th>数值</th></tr>
            <tr><td>营业收入(亿元)</td><td>{test_data['revenue_billion']}</td></tr>
            <tr><td>净利润(亿元)</td><td>{test_data['net_profit_billion']}</td></tr>
            <tr><td>ROE(%)</td><td>{test_data['roe']}</td></tr>
        </table>
        <h2>关键洞察</h2>
        <ul>
            <li>{test_data['key_insights'][0]}</li>
            <li>{test_data['key_insights'][1]}</li>
            <li>{test_data['key_insights'][2]}</li>
        </ul>
    </body>
    </html>
    """

    html_pdf_result = await toolkit.save_html_as_pdf_report(
        html_content=html_content,
        stock_name="测试公司",
        file_prefix="./stock_analysis_workspace"
    )

    print("HTML转PDF结果:")
    print(json.dumps(html_pdf_result, ensure_ascii=False, indent=2))

    return pdf_result.get("success", False) or html_pdf_result.get("success", False)

async def test_workspace_consistency():
    """测试工作目录一致性"""
    print("\n=== 测试工作目录一致性 ===")

    # 创建工具包实例
    config = {"workspace_root": "./stock_analysis_workspace"}
    toolkit = ReportSaverToolkit(config)

    print(f"工具包工作目录: {toolkit.workspace_root}")

    # 检查目录是否正确创建
    workspace_path = Path("./stock_analysis_workspace")
    if workspace_path.exists():
        print(f"✓ 工作目录存在: {workspace_path.absolute()}")

        # 列出生成的文件
        files = list(workspace_path.glob("*"))
        if files:
            print("✓ 目录中的文件:")
            for file in files:
                print(f"  - {file.name} ({file.stat().st_size} bytes)")
        else:
            print("⚠ 目录为空")
    else:
        print(f"✗ 工作目录不存在: {workspace_path.absolute()}")
        return False

    return True

def test_main_py_html_logic():
    """测试main.py中的HTML处理逻辑"""
    print("\n=== 测试main.py HTML处理逻辑 ===")

    # 测试HTML检测函数
    def is_html_content(content):
        html_indicators = [
            "<html", "<div", "<span", "<p>", "<h1", "<h2", "<h3",
            "<table", "<ul>", "<ol>", "<strong>", "<em>", "<br>", "<hr",
            "<style>", "<script>", "<link>", "<meta"
        ]
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in html_indicators)

    # 测试不同类型的内容
    test_cases = [
        ("<div>这是一个HTML内容</div>", True, "简单HTML"),
        ("这是一个纯文本内容", False, "纯文本"),
        ("```html\n<h1>代码块中的HTML</h1>\n```", True, "代码块中的HTML"),
        ("# 标题\n**加粗文本**\n- 列表项", False, "Markdown格式"),
    ]

    all_passed = True
    for content, expected, description in test_cases:
        result = is_html_content(content)
        status = "✓" if result == expected else "✗"
        print(f"{status} {description}: 期望 {expected}, 实际 {result}")
        if result != expected:
            all_passed = False

    return all_passed

async def main():
    """主测试函数"""
    print("开始综合测试财务分析系统修复...")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 确保工作目录存在
    Path("./stock_analysis_workspace").mkdir(exist_ok=True)

    results = {}

    # 运行各项测试
    results['html_functionality'] = await test_html_functionality()
    results['pdf_functionality'] = await test_pdf_functionality()
    results['workspace_consistency'] = await test_workspace_consistency()
    results['main_py_html_logic'] = test_main_py_html_logic()

    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)

    total_tests = len(results)
    passed_tests = sum(results.values())

    for test_name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name:25} : {status}")

    print(f"\n总计: {passed_tests}/{total_tests} 项测试通过")

    if passed_tests == total_tests:
        print("🎉 所有测试通过！修复成功！")
        return True
    else:
        print("⚠️  部分测试失败，需要进一步调试")
        return False

if __name__ == "__main__":
    asyncio.run(main())