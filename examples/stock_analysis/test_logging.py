#!/usr/bin/env python3
"""
测试股票分析多智能体系统的日志功能
"""

import asyncio
import pathlib
import os
import sys
from utu.agents import OrchestraAgent
from utu.config import ConfigLoader
from utu.utils.agents_utils import AgentsUtils


async def test_logging_functionality():
    """测试日志功能的股票分析"""

    print("=== 测试多智能体股票分析日志系统 ===")

    # 检查环境变量
    llm_type = os.environ.get("UTU_LLM_TYPE")
    llm_model = os.environ.get("UTU_LLM_MODEL")
    llm_api_key = os.environ.get("UTU_LLM_API_KEY")
    llm_base_url = os.environ.get("UTU_LLM_BASE_URL")

    if not all([llm_type, llm_model, llm_api_key, llm_base_url]):
        print("环境变量设置不完整")
        return False

    print("环境变量检查通过")

    try:
        # 设置配置
        config = ConfigLoader.load_agent_config("examples/stock_analysis_final")
        config.planner_config["examples_path"] = pathlib.Path(__file__).parent / "stock_analysis_examples.json"

        # 设置工作目录
        workspace_path = pathlib.Path(__file__).parent / "stock_analysis_workspace"
        workspace_path.mkdir(exist_ok=True)

        print(f"✅ 配置加载成功，工作目录: {workspace_path}")

        # 初始化智能体
        runner = OrchestraAgent(config)
        await runner.build()
        print("✅ OrchestraAgent初始化成功")

        # 检查日志系统是否集成
        if hasattr(runner, 'orchestra_logger'):
            print("✅ 日志系统集成成功")
        else:
            print("⚠️ 未找到orchestra_logger属性")

        # 简单的查询测试
        question = "分析贵州茅台(600519.SH)的基本财务指标"
        print(f"🚀 开始分析: {question}")

        # 运行分析
        result = await runner.run(question)
        final_output = result.final_output

        print("✅ 分析完成")
        print(f"📊 分析结果长度: {len(final_output)} 字符")

        # 检查日志文件是否生成
        logs_dir = pathlib.Path("../../logs")
        if logs_dir.exists():
            log_files = list(logs_dir.glob("orchestra_*.json"))
            if log_files:
                print(f"✅ 发现 {len(log_files)} 个日志文件")
                for log_file in log_files:
                    print(f"   📝 {log_file.name}")
                    # 检查日志文件内容
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            lines = content.strip().split('\n')
                            print(f"      日志条目数: {len(lines)}")

                            # 检查是否为有效的JSON格式
                            if lines:
                                import json
                                first_log = json.loads(lines[0])
                                if 'trace_id' in first_log and 'session_id' in first_log:
                                    print("      ✅ 日志格式正确 (包含trace_id和session_id)")
                                else:
                                    print("      ⚠️ 日志格式可能不完整")
                    except Exception as e:
                        print(f"      ❌ 读取日志文件出错: {e}")
            else:
                print("⚠️ 未找到日志文件")
        else:
            print("⚠️ 日志目录不存在")

        # 测试日志方法
        if hasattr(runner, 'get_session_summary'):
            try:
                summary = runner.get_session_summary()
                print(f"✅ 会话摘要获取成功: {summary}")
            except Exception as e:
                print(f"⚠️ 获取会话摘要失败: {e}")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_logging_functionality())
    if success:
        print("\n🎉 多智能体日志系统测试完成！")
    else:
        print("\n❌ 测试失败，请检查配置和依赖")
        sys.exit(1)