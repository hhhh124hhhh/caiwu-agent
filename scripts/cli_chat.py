import argparse
import asyncio
import sys

import art

from utu.agents import SimpleAgent
from utu.config import AgentConfig, ConfigLoader
from utu.utils import PrintUtils

USAGE_MSG = f"""{"-" * 100}
用法: python cli_chat.py --config_name <配置名称>
退出: exit, quit, q
{"-" * 100}""".strip()


async def main():
    # 修改标题文字为中文
    text = str(art.text2art("Caiwu-agent", font="small"))
    PrintUtils.print_info(text, color="blue")
    PrintUtils.print_info(USAGE_MSG, color="yellow")

    parser = argparse.ArgumentParser(description="财务分析智能体命令行界面")
    parser.add_argument("--config_name", type=str, default="default", help="配置文件名称")
    parser.add_argument("--agent_model", type=str, default=None, help="智能体模型")
    parser.add_argument("--tools", type=str, nargs="*", help="要加载的工具名称列表")
    parser.add_argument("--stream", action="store_true", help="流式输出")
    args = parser.parse_args()

    config: AgentConfig = ConfigLoader.load_agent_config(args.config_name)
    if args.agent_model:
        config.model.model_provider.model = args.agent_model
    if args.tools:
        # 从配置中加载工具包
        for tool_name in args.tools:
            config.toolkits[tool_name] = ConfigLoader.load_toolkit_config(tool_name)

    # 保持单一智能体模式，只使用 SimpleAgent
    async with SimpleAgent(config=config) as agent:
        PrintUtils.print_info("财务分析智能体已启动，输入 'exit', 'quit' 或 'q' 退出。", color="green")
        while True:
            user_input = await PrintUtils.async_print_input("请输入您的问题: ")
            if user_input.lower() in ["exit", "quit", "q"]:
                PrintUtils.print_info("再见！", color="blue")
                break
            if args.stream:
                await agent.chat_streamed(user_input)
            else:
                await agent.chat(user_input)


if __name__ == "__main__":
    asyncio.run(main())