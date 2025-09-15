import pathlib
import asyncio

from utu.agents import OrchestraAgent
from utu.config import ConfigLoader
from utu.ui import ExampleConfig
from utu.ui.webui_chatbot import WebUIChatbot


async def build_agent(config):
    """构建并初始化OrchestraAgent"""
    runner = OrchestraAgent(config)
    await runner.build()
    return runner


def main():
    env_and_args = ExampleConfig()
    config = ConfigLoader.load_agent_config("examples/stock_analysis_final")
    config.planner_config["examples_path"] = pathlib.Path(__file__).parent / "stock_analysis_examples.json"
    
    # Setup workspace for stock analysis
    workspace_path = pathlib.Path(__file__).parent / "stock_analysis_workspace"
    workspace_path.mkdir(exist_ok=True)
    
    # Configure all toolkits workspace
    # 修复：为所有工具配置正确的工作目录
    toolkits_to_configure = ["akshare_data", "financial_analyzer", "analysis_executor", "tabular"]
    
    for toolkit_name in toolkits_to_configure:
        toolkit = config.toolkits.get(toolkit_name)
        if toolkit is not None and toolkit.config is not None:
            toolkit.config["workspace_root"] = str(workspace_path)
        elif toolkit is not None:
            # 如果 config 是 None，创建一个新的字典
            toolkit.config = {"workspace_root": str(workspace_path)}
    
    # 正确构建和初始化智能体
    runner = asyncio.run(build_agent(config))

    # 设置示例查询
    example_query = "分析陕西建工(600248.SH)最新财报数据，比较主要财务指标差异，绘制可视化图表出具报告"

    ui = WebUIChatbot(runner, example_query=example_query)
    # 使用默认值或环境变量，确保类型正确
    # 从配置中获取Web界面配置
    port = getattr(config, 'web_interface', {}).get('port', 8848) if hasattr(config, 'web_interface') else 8848
    port = int(env_and_args.port) if env_and_args.port is not None else port
    ip = env_and_args.ip if env_and_args.ip is not None else getattr(config, 'web_interface', {}).get('host', "127.0.0.1") if hasattr(config, 'web_interface') else "127.0.0.1"
    autoload = env_and_args.autoload if env_and_args.autoload is not None else False
    ui.launch(port=port, ip=ip, autoload=autoload)


if __name__ == "__main__":
    main()