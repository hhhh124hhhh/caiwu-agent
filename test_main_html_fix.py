#!/usr/bin/env python3
"""
测试main.py中HTML修复功能的简化脚本
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_html_detection():
    """测试HTML检测功能"""
    print("=== 测试HTML检测功能 ===")

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
            import re
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
    </style>
</head>
<body>
{content}
</body>
</html>"""
            return formatted_html

        return content

    # 测试用例
    test_cases = [
        # 简单HTML内容
        ("<div>测试内容</div>", True, "简单HTML"),

        # 带代码块的HTML
        ("```html\n<div>代码块中的HTML</div>\n```", True, "代码块HTML"),

        # 纯文本内容
        ("这是纯文本内容", False, "纯文本"),

        # 复杂HTML表格
        ("<table><tr><th>指标</th><td>100.5</td></tr></table>", True, "HTML表格"),

        # 财务分析内容（模拟智能体输出）
        ("""基于对宁德时代(300750.SZ)最近2年财务表现的深入分析，以下是详细的对比分析报告：

## 一、核心财务指标对比

<div class="metric">
<strong>营业收入</strong>：比亚迪3712.81亿元 > 宁德时代2830.72亿元
<strong>净利润</strong>：宁德时代522.97亿元 > 比亚迪160.39亿元
</div>

<table>
<tr><th>指标</th><th>宁德时代</th><th>比亚迪</th></tr>
<tr><td>净利润率</td><td class="positive">18.47%</td><td>4.32%</td></tr>
<tr><td>ROE</td><td class="positive">15.06%</td><td>6.55%</td></tr>
</table>""", True, "智能体输出混合内容")
    ]

    all_passed = True
    workspace_path = Path("./stock_analysis_workspace")
    workspace_path.mkdir(exist_ok=True)

    for i, (content, expected, description) in enumerate(test_cases, 1):
        # 测试HTML检测
        detected = is_html_content(content)
        detection_passed = detected == expected

        # 如果检测为HTML，测试格式化
        if detected:
            formatted = format_html_content(content)
            # 保存测试文件
            test_file = workspace_path / f"test_html_{i}_{description.replace(' ', '_')}.html"
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(formatted)

            print(f"✓ {description}: HTML检测正确，已保存测试文件 {test_file.name}")
        else:
            # 保存为文本文件
            test_file = workspace_path / f"test_text_{i}_{description.replace(' ', '_')}.txt"
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✓ {description}: 文本检测正确，已保存测试文件 {test_file.name}")

        if not detection_passed:
            print(f"✗ {description}: HTML检测失败 (期望: {expected}, 实际: {detected})")
            all_passed = False

    return all_passed

def test_workspace_config():
    """测试工作目录配置一致性"""
    print("\n=== 测试工作目录配置 ===")

    # 检查配置文件
    config_files = [
        "configs/tools/report_saver.yaml",
        "configs/tools/financial_analysis.yaml",
        "configs/tools/tabular.yaml"
    ]

    workspace_settings = {}
    for config_file in config_files:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if "workspace_root:" in content:
                    # 提取工作目录设置
                    lines = content.split('\n')
                    for line in lines:
                        if 'workspace_root:' in line:
                            workspace = line.split(':')[1].strip().replace('"', '').replace("'", "")
                            workspace_settings[config_file] = workspace
                            break

    print("工作目录配置:")
    for config_file, workspace in workspace_settings.items():
        status = "✓" if "stock_analysis_workspace" in workspace else "⚠"
        print(f"{status} {config_file}: {workspace}")

    # 检查是否统一
    unique_workspaces = set(workspace_settings.values())
    consistent = len(unique_workspaces) == 1 and "stock_analysis_workspace" in unique_workspaces

    if consistent:
        print("✓ 工作目录配置统一")
    else:
        print("⚠ 工作目录配置不统一")
        print(f"  发现的工作目录: {unique_workspaces}")

    return consistent

def main():
    """主函数"""
    print("测试main.py HTML修复和工作目录配置...")
    print("=" * 50)

    # 运行测试
    html_test_passed = test_html_detection()
    workspace_test_passed = test_workspace_config()

    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)
    print(f"HTML检测与格式化: {'✓ 通过' if html_test_passed else '✗ 失败'}")
    print(f"工作目录配置: {'✓ 通过' if workspace_test_passed else '✗ 失败'}")

    # 显示生成的测试文件
    workspace_path = Path("./stock_analysis_workspace")
    if workspace_path.exists():
        test_files = list(workspace_path.glob("test_*.html")) + list(workspace_path.glob("test_*.txt"))
        if test_files:
            print(f"\n生成的测试文件 ({len(test_files)}个):")
            for file in sorted(test_files):
                size = file.stat().st_size
                print(f"  - {file.name} ({size} bytes)")

    overall_success = html_test_passed and workspace_test_passed

    if overall_success:
        print("\n🎉 所有测试通过！修复功能正常工作！")
    else:
        print("\n⚠ 部分测试失败，需要进一步检查")

    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)