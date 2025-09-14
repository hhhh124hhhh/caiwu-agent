#!/usr/bin/env python3
"""
Simple test script for the Enhanced Python Executor Toolkit
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

try:
    from utu.tools.enhanced_python_executor_toolkit import EnhancedPythonExecutorToolkit
    print("Successfully imported EnhancedPythonExecutorToolkit")
except ImportError as e:
    print(f"Failed to import EnhancedPythonExecutorToolkit: {e}")
    sys.exit(1)


async def main():
    """Main test function"""
    print("Testing Enhanced Python Executor Toolkit...")
    
    # Create the toolkit instance
    toolkit = EnhancedPythonExecutorToolkit()
    
    # Get the tools map
    tools_map = await toolkit.get_tools_map()
    print(f"Available tools: {list(tools_map.keys())}")
    
    # Get the enhanced execution function
    execute_func = tools_map["execute_python_code_enhanced"]
    
    # Test: Simple execution with code saving
    print("\n=== Simple Test ===")
    code = """
print("Hello, World!")
x = 10
y = 20
result = x + y
print(f"Result: {result}")
"""
    
    # Clean up any existing test directory
    if os.path.exists("./simple_test_workdir"):
        import shutil
        shutil.rmtree("./simple_test_workdir")
    
    result = await execute_func(code, workdir="./simple_test_workdir", save_code=True)
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if 'code_file' in result:
        print(f"Code file saved: {result['code_file']}")
        # Check if file exists
        if os.path.exists(result['code_file']):
            print(f"Code file exists: True")
            # Show the content of the saved file
            try:
                with open(result['code_file'], 'r', encoding='utf-8') as f:
                    content = f.read()
                    print("Saved code file content:")
                    print(content)
            except Exception as e:
                print(f"Error reading saved code file: {e}")
        else:
            print("Code file exists: False")
    
    print("\n=== Test completed ===")


if __name__ == "__main__":
    asyncio.run(main())