#!/usr/bin/env python3
"""
简化版真实财务数据图表生成演示
"""

import json
import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_tabular_data_toolkit():
    """测试TabularDataToolkit的修复效果"""
    print("测试TabularDataToolkit.generate_charts方法...")

    try:
        # 导入修复后的工具
        from utu.tools.tabular_data_toolkit import TabularDataToolkit

        toolkit = TabularDataToolkit()

        # 真实测试数据
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

        print(f"准备为 {len(test_data['companies'])} 家公司生成对比图表...")
        print(f"财务指标: {[k for k in test_data.keys() if k != 'companies']}")

        # 创建输出目录
        output_dir = "./demo_output"
        os.makedirs(output_dir, exist_ok=True)

        # 调用修复后的generate_charts方法
        result = toolkit.generate_charts(
            data_json=json.dumps(test_data, ensure_ascii=False),
            chart_type="comparison",
            output_dir=output_dir
        )

        print(f"图表生成结果: {result.get('success', False)}")
        print(f"消息: {result.get('message', 'No message')}")
        print(f"生成文件数: {len(result.get('files', []))}")

        if result.get('success'):
            files = result.get('files', [])
            for file_path in files:
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    print(f"  文件: {os.path.basename(file_path)} ({file_size} bytes)")
                else:
                    print(f"  文件不存在: {file_path}")

        return result.get('success', False)

    except ImportError as e:
        print(f"导入错误: {e}")
        return False
    except Exception as e:
        print(f"测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_python_executor_toolkit():
    """测试EnhancedPythonExecutorToolkit的修复效果"""
    print("\n测试EnhancedPythonExecutorToolkit.execute_python_code_enhanced方法...")

    try:
        # 导入修复后的工具
        from utu.tools.enhanced_python_executor_toolkit import EnhancedPythonExecutorToolkit

        executor = EnhancedPythonExecutorToolkit()

        # 测试matplotlib代码
        test_code = '''
import matplotlib.pyplot as plt
import numpy as np

# 使用注入的变量创建对比图表
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# 营业收入对比
bars1 = ax1.bar(companies, revenue, color=['blue', 'orange'], alpha=0.7)
ax1.set_title('营业收入对比（亿元）')
ax1.set_ylabel('营业收入（亿元）')

for i, (bar, value) in enumerate(zip(bars1, revenue)):
    ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(revenue)*0.02,
            f'{value:.2f}', ha='center', va='bottom')

# 净利率对比
bars2 = ax2.bar(companies, profit_margin, color=['green', 'red'], alpha=0.7)
ax2.set_title('净利率对比（%）')
ax2.set_ylabel('净利率（%）')

for i, (bar, value) in enumerate(zip(bars2, profit_margin)):
    ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(profit_margin)*0.02,
            f'{value:.2f}%', ha='center', va='bottom')

plt.tight_layout()
plt.savefig('demo_output/matplotlib_test.png', dpi=300, bbox_inches='tight')
plt.close()

print("matplotlib图表生成完成")
'''

        # 创建输出目录
        output_dir = "./demo_output"
        os.makedirs(output_dir, exist_ok=True)

        print("执行matplotlib代码测试...")
        result = await executor.execute_python_code_enhanced(
            code=test_code,
            workdir=output_dir,
            save_code=True
        )

        print(f"执行结果: {result.get('success', False)}")
        print(f"消息: {result.get('message', 'No message')}")
        print(f"输出文件数: {len(result.get('files', []))}")

        if result.get('success'):
            files = result.get('files', [])
            for file_path in files:
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    print(f"  文件: {os.path.basename(file_path)} ({file_size} bytes)")
                else:
                    print(f"  文件不存在: {file_path}")

        return result.get('success', False)

    except ImportError as e:
        print(f"导入错误: {e}")
        return False
    except Exception as e:
        print(f"测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("=== 真实图表生成工具修复演示 ===\n")

    # 创建输出目录
    os.makedirs("./demo_output", exist_ok=True)

    success_count = 0
    total_tests = 2

    # 测试1: TabularDataToolkit
    print("--- 测试1: TabularDataToolkit ---")
    if test_tabular_data_toolkit():
        success_count += 1
        print("✅ TabularDataToolkit测试通过\n")
    else:
        print("❌ TabularDataToolkit测试失败\n")

    # 测试2: EnhancedPythonExecutorToolkit
    print("--- 测试2: EnhancedPythonExecutorToolkit ---")
    if test_python_executor_toolkit():
        success_count += 1
        print("✅ EnhancedPythonExecutorToolkit测试通过\n")
    else:
        print("❌ EnhancedPythonExecutorToolkit测试失败\n")

    # 输出结果
    print("=== 演示结果汇总 ===")
    print(f"成功测试: {success_count}/{total_tests}")
    print(f"失败测试: {total_tests - success_count}/{total_tests}")

    if success_count == total_tests:
        print("\n🎉 所有测试通过！图表生成工具修复成功！")
        print("\n修复总结:")
        print("1. ✅ generate_charts方法支持公司对比数据格式")
        print("2. ✅ execute_python_code_enhanced方法支持变量注入")
        print("3. ✅ 增强错误处理和调试机制")
        print("4. ✅ 图表文件正确生成和保存")
        return 0
    else:
        print("\n⚠️  部分测试失败，工具修复需要进一步调整")
        return 1

if __name__ == "__main__":
    import asyncio
    exit(asyncio.run(main()))