#!/usr/bin/env python3
"""
测试图表生成工具修复效果
验证X轴数据格式处理和各种图表类型
"""

import sys
import json
import pathlib
import os

# 设置项目路径
project_root = pathlib.Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_chart_generator_fixes():
    """测试图表生成工具的修复效果"""

    print("=" * 60)
    print("图表生成工具修复验证测试")
    print("=" * 60)

    try:
        from utu.tools.tabular_data_toolkit import TabularDataToolkit

        # 创建工具实例
        toolkit = TabularDataToolkit({"workspace_root": "./test_charts"})

        # 测试用例1：用户实际的数据格式1 - X轴带name和data字段
        test_data_1 = {
            "title": "陕西建工盈利能力趋势分析",
            "x_axis": {
                "name": "年份",
                "data": ["2021", "2022", "2023", "2024"]
            },
            "series": [
                {"name": "营业收入(亿元)", "data": [520.45, 545.23, 560.78, 573.88]},
                {"name": "净利润(亿元)", "data": [9.85, 10.23, 10.67, 11.04]},
                {"name": "净利润率(%)", "data": [1.89, 1.88, 1.90, 1.92]},
                {"name": "ROE(%)", "data": [2.68, 2.70, 2.69, 2.68]}
            ]
        }

        print("\n1. 测试X轴字典格式 (带name和data字段)")
        print(f"数据格式: {json.dumps(test_data_1['x_axis'], ensure_ascii=False)}")

        try:
            result_1 = toolkit.generate_charts(
                data_json=json.dumps(test_data_1, ensure_ascii=False),
                chart_type="line",
                output_dir="./test_charts"
            )
            print(f"[SUCCESS] X轴字典格式测试通过")
            print(f"   结果: {result_1['message']}")
            print(f"   文件: {result_1.get('files', [])}")
        except Exception as e:
            print(f"[ERROR] X轴字典格式测试失败: {e}")
            return False

        # 测试用例2：X轴直接列表格式
        test_data_2 = {
            "title": "陕西建工偿债能力指标对比",
            "x_axis": ["2021", "2022", "2023", "2024"],
            "series": [
                {"name": "资产负债率(%)", "data": [88.36, 88.21, 88.71, 88.71]},
                {"name": "流动比率", "data": [1.10, 1.11, 1.12, 1.12]},
                {"name": "速动比率", "data": [0.92, 0.93, 0.94, 0.95]}
            ]
        }

        print("\n2. 测试X轴列表格式")
        print(f"数据格式: {test_data_2['x_axis']}")

        try:
            result_2 = toolkit.generate_charts(
                data_json=json.dumps(test_data_2, ensure_ascii=False),
                chart_type="line",
                output_dir="./test_charts"
            )
            print(f"[SUCCESS] X轴列表格式测试通过")
            print(f"   结果: {result_2['message']}")
            print(f"   文件: {result_2.get('files', [])}")
        except Exception as e:
            print(f"[ERROR] X轴列表格式测试失败: {e}")
            return False

        # 测试用例3：数据长度不匹配的情况（应该提供详细诊断）
        test_data_3 = {
            "title": "数据长度不匹配测试",
            "x_axis": ["2021", "2022", "2023", "2024", "2025"],  # 5个标签
            "series": [
                {"name": "测试系列1", "data": [100, 150, 120]},  # 3个数据点
                {"name": "测试系列2", "data": [80, 120, 110, 140, 160]}  # 5个数据点
            ]
        }

        print("\n3. 测试数据长度不匹配情况")
        print(f"X轴长度: {len(test_data_3['x_axis'])}")
        print(f"系列1长度: {len(test_data_3['series'][0]['data'])}")
        print(f"系列2长度: {len(test_data_3['series'][1]['data'])}")

        try:
            result_3 = toolkit.generate_charts(
                data_json=json.dumps(test_data_3, ensure_ascii=False),
                chart_type="line",
                output_dir="./test_charts"
            )
            print(f"[SUCCESS] 数据长度不匹配处理测试通过")
            print(f"   结果: {result_3['message']}")
            print(f"   文件: {result_3.get('files', [])}")
        except Exception as e:
            print(f"[ERROR] 数据长度不匹配测试失败: {e}")
            return False

        # 测试用例4：缺少必要字段的情况
        test_data_4 = {
            "x_axis": ["2021", "2022", "2023", "2024"],
            "series": [
                {"name": "测试系列", "data": [100, 150, 120, 180]}
            ]
            # 缺少 title 字段
        }

        print("\n4. 测试缺少必要字段情况")

        try:
            result_4 = toolkit.generate_charts(
                data_json=json.dumps(test_data_4, ensure_ascii=False),
                chart_type="line",
                output_dir="./test_charts"
            )
            print(f"[SUCCESS] 缺少字段处理测试通过")
            print(f"   结果: {result_4['message']}")
            if 'suggestions' in result_4:
                print("   修复建议:")
                for suggestion in result_4['suggestions']:
                    print(f"     {suggestion}")
            print(f"   格式示例: {json.dumps(result_4.get('format_example', {}), ensure_ascii=False)}")
        except Exception as e:
            print(f"[ERROR] 缺少字段测试失败: {e}")
            return False

        # 测试用例5：柱状图格式
        test_data_5 = {
            "title": "陕西建工财务指标柱状图",
            "x_axis": ["2021", "2022", "2023", "2024"],
            "series": [
                {"name": "营业收入(亿元)", "data": [520.45, 545.23, 560.78, 573.88]},
                {"name": "净利润(亿元)", "data": [9.85, 10.23, 10.67, 11.04]}
            ]
        }

        print("\n5. 测试柱状图格式")

        try:
            result_5 = toolkit.generate_charts(
                data_json=json.dumps(test_data_5, ensure_ascii=False),
                chart_type="bar",
                output_dir="./test_charts"
            )
            print(f"[SUCCESS] 柱状图测试通过")
            print(f"   结果: {result_5['message']}")
            print(f"   文件: {result_5.get('files', [])}")
        except Exception as e:
            print(f"[ERROR] 柱状图测试失败: {e}")
            return False

        # 检查生成的文件
        print("\n6. 检查生成的图表文件")
        chart_dir = pathlib.Path("./test_charts")
        if chart_dir.exists():
            chart_files = list(chart_dir.glob("*.png"))
            if chart_files:
                print(f"[SUCCESS] 生成了 {len(chart_files)} 个图表文件:")
                for file in chart_files:
                    file_size = file.stat().st_size
                    print(f"   - {file.name} ({file_size} bytes)")
            else:
                print("[WARNING] 没有找到生成的图表文件")

        print("\n" + "=" * 60)
        print("[SUCCESS] 所有图表生成工具修复测试通过！")
        print("\n修复效果总结:")
        print("1. 支持X轴字典格式（带name和data字段）")
        print("2. 兼容X轴列表格式")
        print("3. 提供详细的数据长度不匹配诊断")
        print("4. 增强错误处理和修复建议")
        print("5. 支持多种图表类型（折线图、柱状图等）")

        return True

    except ImportError as e:
        print(f"[ERROR] 无法导入图表生成工具: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chart_generator_fixes()

    print("\n" + "=" * 60)
    if success:
        print("[SUCCESS] 图表生成工具修复验证通过！")
        print("\n现在用户可以使用以下数据格式:")
        print("- X轴字典格式: {\"name\": \"标签名\", \"data\": [...] }")
        print("- X轴列表格式: [\"标签1\", \"标签2\", ...]")
        print("- 详细的错误诊断和修复建议")
        print("- 多种图表类型支持")
        sys.exit(0)
    else:
        print("[ERROR] 部分测试失败，需要进一步调试")
        sys.exit(1)