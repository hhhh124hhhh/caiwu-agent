#!/usr/bin/env python3
"""
Simple script to start a Youtu-Agent
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

# Set UTF-8 encoding for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Set a dummy SERPER_API_KEY to avoid the error
os.environ['SERPER_API_KEY'] = 'dummy_key'

try:
    from utu.agents import SimpleAgent
    from utu.config import AgentConfig, ConfigLoader
    print("Successfully imported Youtu-Agent modules")
except ImportError as e:
    print(f"Failed to import Youtu-Agent modules: {e}")
    sys.exit(1)


async def main():
    """Main function to start the agent"""
    print("Starting Youtu-Agent...")
    
    try:
        # Load the base agent configuration (without search tool)
        config: AgentConfig = ConfigLoader.load_agent_config("base")
        print(f"Loaded agent config: {config.agent.name}")
        
        # Create and run the agent
        async with SimpleAgent(config=config) as agent:
            print("Agent started successfully!")
            print("You can now interact with the agent.")
            print("Type 'exit', 'quit', or 'q' to quit.")
            
            while True:
                try:
                    user_input = input("> ")
                    if user_input.lower() in ["exit", "quit", "q"]:
                        break
                    response = await agent.chat(user_input)
                    print(f"Agent: {response}")
                except KeyboardInterrupt:
                    print("\nExiting...")
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    
    except Exception as e:
        print(f"Failed to start agent: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())