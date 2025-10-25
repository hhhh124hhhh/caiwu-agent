#!/usr/bin/env python3
"""
演示前快速测试脚本
"""

import asyncio
import pathlib
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def quick_demo_test():
    """快速演示测试"""
    print("🚀 演示前快速测试...")

    try:
        # 导入测试
        from utu.agents import OrchestraAgent
        from utu.config import ConfigLoader
        print("✅ 核心模块导入成功")

        # 检查环境变量
        llm_type = os.environ.get("UTU_LLM_TYPE")
        llm_model = os.environ.get("UTU_LLM_MODEL")
        if llm_type and llm_model:
            print(f"✅ LLM配置检查通过: {llm_model}")
        else:
            print("⚠️  LLM配置可能有问题")

        # 测试配置加载
        config = ConfigLoader.load_agent_config("examples/stock_analysis_final")
        print("✅ 配置文件加载成功")

        # 检查工作目录
        workspace_path = pathlib.Path(__file__).parent / "stock_analysis_workspace"
        workspace_path.mkdir(exist_ok=True)
        print(f"✅ 工作目录准备完成: {workspace_path}")

        # 检查示例文件
        examples_file = pathlib.Path(__file__).parent / "examples/stock_analysis/stock_analysis_examples.json"
        if examples_file.exists():
            print("✅ 演示案例文件存在")
        else:
            print("❌ 演示案例文件不存在")
            return False

        print("\n🎯 系统准备就绪，可以开始演示!")
        print("💡 建议演示流程:")
        print("   1. cd examples/stock_analysis")
        print("   2. python main.py --stream")
        print("   3. 选择案例 1: 单公司深度分析")
        print("   4. 观察智能体协作过程")
        print("   5. 查看生成的HTML和PDF报告")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_html_rendering():
    """测试HTML渲染功能"""
    print("\n🌐 测试HTML渲染功能...")

    try:
        from utu.tools.report_saver_toolkit import ReportSaverToolkit

        # 创建工具包
        config = {"workspace_root": "./stock_analysis_workspace"}
        toolkit = ReportSaverToolkit(config)

        # 测试HTML内容
        test_html = """
        <div class="metric">
            <h2>演示公司财务分析报告</h2>
            <table>
                <tr><th>指标</th><th>2023年</th><th>增长率</th></tr>
                <tr><td>营业收入</td><td>100.5亿元</td><td class="positive">+12.5%</td></tr>
                <tr><td>净利润</td><td>15.2亿元</td><td class="positive">+15.3%</td></tr>
                <tr><td>ROE</td><td>12.5%</td><td class="positive">+0.8pp</td></tr>
            </table>
            <h3>投资建议</h3>
            <p>基于当前财务表现，建议<strong>持有</strong>该股票。</p>
        </div>
        """

        # 异步测试HTML保存
        async def test_html():
            result = await toolkit.save_analysis_report(
                content=test_html,
                report_name="演示财务分析报告",
                file_format="html",
                workspace_dir="./stock_analysis_workspace"
            )
            return result

        # 运行异步测试
        result = asyncio.run(test_html())

        if result.get("success"):
            print(f"✅ HTML报告生成成功: {result.get('file_path')}")
            print(f"📊 文件大小: {result.get('file_size'):,} bytes")
            return True
        else:
            print(f"❌ HTML报告生成失败: {result.get('message')}")
            return False

    except Exception as e:
        print(f"❌ HTML测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🎭 演示前验证测试")
    print("=" * 40)

    # 基础系统测试
    system_ok = asyncio.run(quick_demo_test())

    # HTML功能测试
    html_ok = test_html_rendering()

    print("\n" + "=" * 40)
    print("📊 测试结果汇总:")
    print(f"   系统状态: {'✅ 正常' if system_ok else '❌ 异常'}")
    print(f"   HTML功能: {'✅ 正常' if html_ok else '❌ 异常'}")

    if system_ok and html_ok:
        print("\n🎉 演示系统准备就绪!")
        print("\n🚀 快速开始演示:")
        print("1. 打开终端")
        print("2. cd examples/stock_analysis")
        print("3. python main.py --stream")
        print("4. 选择演示案例并查看结果")

        # 显示现有演示文件
        workspace_path = Path("./stock_analysis_workspace")
        if workspace_path.exists():
            existing_files = list(workspace_path.glob("*.html")) + list(workspace_path.glob("*.pdf"))
            if existing_files:
                print(f"\n📁 现有演示文件:")
                for file in existing_files:
                    size = file.stat().st_size
                    print(f"   - {file.name} ({size:,} bytes)")

        return True
    else:
        print("\n⚠️  系统存在问题，请检查配置后再演示")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)