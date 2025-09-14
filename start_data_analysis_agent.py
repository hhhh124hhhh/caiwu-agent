#!/usr/bin/env python3
"""
Simple script to start the data analysis agent
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

# Set dummy API keys to avoid errors
os.environ['SERPER_API_KEY'] = 'dummy_key'
os.environ['JINA_API_KEY'] = 'dummy_key'

try:
    from utu.agents import SimpleAgent
    from utu.config import AgentConfig, ConfigLoader
    print("Successfully imported Youtu-Agent modules")
except ImportError as e:
    print(f"Failed to import Youtu-Agent modules: {e}")
    sys.exit(1)


async def main():
    """Main function to start the data analysis agent"""
    print("Starting Data Analysis Agent...")
    
    try:
        # Load the data analysis agent configuration
        config: AgentConfig = ConfigLoader.load_agent_config("examples/data_analysis")
        print(f"Loaded agent config: {config.type}")
        
        # Create and run the agent
        async with SimpleAgent(config=config) as agent:
            print("Data Analysis Agent started successfully!")
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