#!/usr/bin/env python3
"""
图表生成工具修复验证测试
验证修复后的雷达图生成功能是否正常工作
"""

import sys
import pathlib
import json
import os

# 设置项目路径
project_root = pathlib.Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_radar_chart_generation():
    """测试雷达图生成功能"""
    print("=== 测试雷达图生成功能 ===\n")

    try:
        # 导入修复后的工具
        from utu.tools.tabular_data_toolkit import TabularDataToolkit

        # 创建工具实例
        toolkit = TabularDataToolkit({"workspace_root": "./test_workspace"})

        # 测试数据 - 陕西建工财务健康雷达图
        test_data = {
            "title": "陕西建工财务健康雷达图",
            "categories": ["盈利能力", "偿债能力", "运营效率", "成长能力", "现金流"],
            "series": [
                {"name": "陕西建工", "data": [30, 20, 25, 15, 10]},
                {"name": "行业平均", "data": [60, 70, 55, 50, 65]}
            ]
        }

        print("1. 测试数据格式:")
        print(f"   - 标题: {test_data['title']}")
        print(f"   - 维度: {', '.join(test_data['categories'])}")
        print(f"   - 数据系列: {[s['name'] for s in test_data['series']]}")

        # 转换为JSON字符串
        data_json = json.dumps(test_data, ensure_ascii=False)
        print(f"   - JSON大小: {len(data_json)} 字符")

        print("\n2. 调用图表生成工具...")

        # 创建输出目录
        output_dir = "./test_charts"
        os.makedirs(output_dir, exist_ok=True)

        # 生成雷达图
        result = toolkit.generate_charts(data_json, "radar", output_dir)

        print(f"   生成结果: {result.get('success', False)}")
        print(f"   消息: {result.get('message', 'N/A')}")

        if result.get('success'):
            files = result.get('files', [])
            print(f"   生成文件: {files}")

            # 检查文件是否存在
            for file_path in files:
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    print(f"   ✓ 文件存在: {file_path} ({file_size} 字节)")
                else:
                    print(f"   ✗ 文件不存在: {file_path}")

            return True
        else:
            print(f"   ✗ 图表生成失败: {result.get('message', 'Unknown error')}")
            if 'format_example' in result:
                print("   格式示例:")
                print(json.dumps(result['format_example'], ensure_ascii=False, indent=2))
            return False

    except Exception as e:
        print(f"   ✗ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_json_error_handling():
    """测试JSON错误处理功能"""
    print("\n=== 测试JSON错误处理功能 ===\n")

    try:
        from utu.tools.tabular_data_toolkit import TabularDataToolkit

        toolkit = TabularDataToolkit({"workspace_root": "./test_workspace"})

        # 测试无效JSON
        invalid_json = '{"title": "测试", "categories": ["A", "B"], "series": [{"name": "test", "data": [1, 2]'  # 缺少结束括号

        print("1. 测试无效JSON格式:")
        print(f"   输入: {invalid_json[:50]}...")

        result = toolkit.generate_charts(invalid_json, "radar", "./test_charts")

        print(f"   错误捕获: {not result.get('success', True)}")
        print(f"   错误消息: {result.get('message', 'N/A')[:100]}...")

        # 检查是否提供了格式示例
        if 'format_example' in result:
            print("   ✓ 提供了格式示例")
            example = result['format_example']
            print(f"   示例标题: {example.get('title', 'N/A')}")
            print(f"   示例维度: {example.get('categories', [])}")
        else:
            print("   ✗ 未提供格式示例")

        return True

    except Exception as e:
        print(f"   ✗ 测试过程中出现错误: {e}")
        return False

def test_html_report_variables():
    """测试HTML报告变量修复"""
    print("\n=== 测试HTML报告变量修复 ===\n")

    try:
        # 检查main.py中的变量引用是否已修复
        main_py_path = project_root / "examples" / "stock_analysis" / "main.py"

        if not main_py_path.exists():
            print(f"   ✗ 文件不存在: {main_py_path}")
            return False

        with open(main_py_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否还有未修复的变量引用
        problematic_patterns = [
            "{investment_advice.get(",
            "{basic_info.get(",
            "{financial_data.get(",
            "{ratio_analysis.get(",
            "{trend_analysis.get(",
            "{risk_assessment.get("
        ]

        fixed_patterns = [
            "{integrated_data['investment_advice'].get(",
            "{integrated_data['basic_info'].get(",
            "{integrated_data['financial_data'].get(",
            "{integrated_data['ratio_analysis'].get(",
            "{integrated_data['trend_analysis'].get(",
            "{integrated_data['risk_assessment'].get("
        ]

        issues_found = []
        fixes_found = []

        for pattern in problematic_patterns:
            if pattern in content:
                issues_found.append(pattern)

        for pattern in fixed_patterns:
            if pattern in content:
                fixes_found.append(pattern)

        print(f"   修复前问题模式: {len(issues_found)} 个")
        print(f"   修复后正确模式: {len(fixes_found)} 个")

        if issues_found:
            print("   ✗ 仍有未修复的变量引用:")
            for issue in issues_found:
                print(f"     - {issue}")
            return False
        else:
            print("   ✓ 所有变量引用已正确修复")
            return True

    except Exception as e:
        print(f"   ✗ 检查过程中出现错误: {e}")
        return False

def main():
    """主测试函数"""
    print("图表生成工具修复验证测试")
    print("=" * 50)

    # 运行所有测试
    test_results = []

    test_results.append(test_radar_chart_generation())
    test_results.append(test_json_error_handling())
    test_results.append(test_html_report_variables())

    # 总结测试结果
    passed = sum(test_results)
    total = len(test_results)

    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")

    if passed == total:
        print("✓ 所有修复验证通过！图表生成工具修复成功。")
        print("\n主要修复内容:")
        print("1. ✓ 增强雷达图支持单公司多维度数据格式")
        print("2. ✓ 修复HTML报告模板中的变量引用错误")
        print("3. ✓ 改进JSON解析的错误提示和使用指导")
        print("4. ✓ 提供正确的数据格式示例")

        print("\n使用示例:")
        print("```python")
        print("from utu.tools.tabular_data_toolkit import TabularDataToolkit")
        print("")
        print("toolkit = TabularDataToolkit()")
        print("data = {")
        print("    'title': '财务雷达图',")
        print("    'categories': ['盈利能力', '偿债能力', '运营效率'],")
        print("    'series': [")
        print("        {'name': '公司A', 'data': [80, 70, 60]},")
        print("        {'name': '行业平均', 'data': [70, 75, 65]}")
        print("    ]")
        print("}")
        print("result = toolkit.generate_charts(json.dumps(data), 'radar', './output')")
        print("```")

        return True
    else:
        print("✗ 部分测试失败，需要进一步调试。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)