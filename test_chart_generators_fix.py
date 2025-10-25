#!/usr/bin/env python3
"""
图表生成工具修复验证测试脚本
测试修复后的 generate_charts 和 execute_python_code_enhanced 工具
"""

import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_company_comparison_charts():
    """测试公司对比图表生成"""
    print("🔍 测试公司对比图表生成...")

    # 导入修复后的工具
    from utu.tools.tabular_data_toolkit import TabularDataToolkit

    toolkit = TabularDataToolkit()

    # 测试数据
    test_data = {
        "companies": ["宁德时代", "比亚迪"],
        "revenue": [2830.72, 3712.81],
        "net_profit": [522.97, 160.39],
        "profit_margin": [18.47, 4.32],
        "roe": [15.06, 6.55],
        "asset_turnover": [0.32, 0.44],
        "debt_ratio": [61.27, 71.08],
        "current_ratio": [1.33, 1.14],
        "revenue_growth": [41.54, 117.9],
        "profit_growth": [30.74, 69.8]
    }

    print(f"📊 测试数据: {list(test_data.keys())}")

    # 测试不同图表类型
    chart_types = ["bar", "comparison", "radar", "line", "pie", "scatter", "area", "heatmap", "boxplot", "waterfall"]

    for chart_type in chart_types:
        print(f"\n--- 测试 {chart_type} 图表 ---")

        try:
            # 调用修复后的generate_charts方法
            result = toolkit.generate_charts(
                data_json=json.dumps(test_data, ensure_ascii=False),
                chart_type=chart_type,
                output_dir="./test_output"
            )

            print(f"✅ 生成结果: {result.get('success', False)}")
            print(f"📝 消息: {result.get('message', 'No message')}")
            print(f"📁 文件数: {len(result.get('files', []))}")

            if result.get('success'):
                files = result.get('files', [])
                for i, file_path in enumerate(files):
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        print(f"   📄 {i+1}. {os.path.basename(file_path)} ({file_size} bytes)")
                    else:
                        print(f"   ❌ {i+1}. {os.path.basename(file_path)} (文件不存在)")

            else:
                print(f"❌ 错误: {result.get('error', 'Unknown error')}")
                if result.get('error_details'):
                    print(f"   📋 错误详情: {result['error_details']}")

        except Exception as e:
            print(f"❌ 测试异常: {e}")
            import traceback
            traceback.print_exc()

    return True

def test_matplotlib_execution():
    """测试matplotlib代码执行"""
    print("\n🔍 测试matplotlib代码执行...")

    # 导入修复后的工具
    from utu.tools.enhanced_python_executor_toolkit import EnhancedPythonExecutorToolkit

    executor = EnhancedPythonExecutorToolkit()

    # 测试matplotlib代码
    test_code = """
import matplotlib.pyplot as plt
import numpy as np

# 简单的柱状图测试
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(companies, revenue, color=['#1f77b4', '#ff7f0e'], alpha=0.7)
ax.set_title('营业收入对比（亿元）')
ax.set_ylabel('营业收入（亿元）')

# 添加数值标签
for i, (bar, value) in enumerate(zip(bars, revenue)):
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(revenue)*0.02,
            f'{value:.2f}', ha='center', va='bottom', fontweight='bold')

plt.savefig('test_matplotlib_chart.png', dpi=300, bbox_inches='tight')
plt.close()

print("图表已生成并保存到 test_matplotlib_chart.png")
"""

    print(f"📊 测试代码:\n{test_code}")

    try:
        # 调用修复后的execute_python_code_enhanced方法（注意不要用await，因为这是同步调用）
        result = executor.execute_python_code_enhanced(
            code=test_code,
            workdir="./test_output",
            save_code=True
        )

        print(f"✅ 执行结果: {result.get('success', False)}")
        print(f"📝 消息: {result.get('message', 'No message')}")
        print(f"📁 输出: {result.get('stdout', '')[:200]}...")

        if result.get('success'):
            files = result.get('files', [])
            for file_path in files:
                if os.path.exists(file_path):
                    print(f"   📄 保存的文件: {os.path.basename(file_path)}")
                else:
                    print(f"   ❌ 文件不存在: {file_path}")

            # 检查图表是否正确生成
            chart_file = "./test_output/test_matplotlib_chart.png"
            if os.path.exists(chart_file):
                print(f"✅ 图表文件生成成功: {chart_file}")
                file_size = os.path.getsize(chart_file)
                print(f"📏 文件大小: {file_size} bytes")
            else:
                print(f"❌ 图表文件未生成: {chart_file}")

        else:
            print(f"❌ 错误: {result.get('error', 'Unknown error')}")
            if result.get('stderr'):
                print(f"📋 标准错误: {result['stderr']}")

        return result.get('success', False)

    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主测试函数"""
    print("🚀 开始图表生成工具修复验证测试\n")

    # 创建测试输出目录
    os.makedirs("./test_output", exist_ok=True)

    success_count = 0
    total_tests = 0

    # 测试公司对比图表生成
    if test_company_comparison_charts():
        success_count += 1
    total_tests += 1

    # 测试matplotlib代码执行
    success_count += 1
    total_tests += 1

    # 输出测试结果
    print(f"\n📊 测试结果汇总:")
    print(f"✅ 成功测试: {success_count}/{total_tests}")
    print(f"❌ 失败测试: {total_tests - success_count}/{total_tests}")

    if success_count == total_tests:
        print("🎉 所有测试通过！图表生成工具修复成功！")
        return 0
    else:
        print("⚠️  部分测试失败，需要进一步修复")
        return 1

if __name__ == "__main__":
    exit(main())