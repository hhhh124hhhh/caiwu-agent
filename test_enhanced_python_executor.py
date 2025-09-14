#!/usr/bin/env python3
"""
Test script for the Enhanced Python Executor Toolkit
"""

import asyncio
import os
import sys
import shutil
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


async def test_enhanced_python_executor():
    """Test the enhanced Python executor toolkit"""
    print("Testing Enhanced Python Executor Toolkit...")
    
    # Create the toolkit instance
    toolkit = EnhancedPythonExecutorToolkit()
    
    # Get the tools map
    tools_map = await toolkit.get_tools_map()
    print(f"Available tools: {list(tools_map.keys())}")
    
    # Get the enhanced execution function
    execute_func = tools_map["execute_python_code_enhanced"]
    
    # Clean up any existing test directories
    test_dirs = ["./test_workdir1", "./test_workdir2", "./test_workdir3", "./test_workdir4"]
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
    
    # Test 1: Basic execution without code saving
    print("\n=== Test 1: Basic execution without code saving ===")
    code1 = """
print("Hello, World!")
x = 10
y = 20
result = x + y
print(f"Result: {result}")
"""
    
    result1 = await execute_func(code1, workdir="./test_workdir1", save_code=False)
    print(f"Success: {result1['success']}")
    print(f"Message: {result1['message']}")
    print(f"Code file saved: {'code_file' in result1}")
    
    # Test 2: Execution with code saving
    print("\n=== Test 2: Execution with code saving ===")
    code2 = """
import matplotlib.pyplot as plt

# Generate some data
x = list(range(10))
y = [i**2 for i in x]

# Plot
plt.figure(figsize=(10, 6))
plt.plot(x, y, label='y = x^2')
plt.title('Quadratic Function')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.grid(True)
plt.savefig('quadratic_plot.png')

print("Generated quadratic plot and saved as quadratic_plot.png")
"""
    
    result2 = await execute_func(code2, workdir="./test_workdir2", save_code=True)
    print(f"Success: {result2['success']}")
    print(f"Message: {result2['message']}")
    if 'code_file' in result2:
        print(f"Code file saved: {result2['code_file']}")
        # Check if file exists
        if os.path.exists(result2['code_file']):
            print(f"Code file exists: {os.path.exists(result2['code_file'])}")
            # Show the content of the saved file
            try:
                with open(result2['code_file'], 'r', encoding='utf-8') as f:
                    content = f.read()
                    print("Saved code file content (first 200 chars):")
                    print(content[:200] + ("..." if len(content) > 200 else ""))
            except Exception as e:
                print(f"Error reading saved code file: {e}")
    
    # Test 3: Error handling
    print("\n=== Test 3: Error handling ===")
    code3 = """
print("This code has an error")
undefined_variable + 10  # This will cause an error
"""
    
    result3 = await execute_func(code3, workdir="./test_workdir3", save_code=True)
    print(f"Success: {result3['success']}")
    print(f"Error: {result3.get('error', 'No error message')}")
    if 'code_file' in result3:
        print(f"Code file saved even with error: {result3['code_file']}")
        if os.path.exists(result3['code_file']):
            print("Code file was saved despite the error")
    
    # Test 4: Chinese characters handling
    print("\n=== Test 4: Chinese characters handling ===")
    code4 = '''
print("你好，世界！")
中文变量 = "这是一个测试"
print(f"中文测试: {中文变量}")

# Create a file with Chinese content
with open("中文测试文件.txt", "w", encoding="utf-8") as f:
    f.write("这是用Python创建的中文文件内容。")
print("已创建中文测试文件")
'''
    
    result4 = await execute_func(code4, workdir="./test_workdir4", save_code=True)
    print(f"Success: {result4['success']}")
    print(f"Message: {result4['message']}")
    if 'code_file' in result4:
        print(f"Code file with Chinese characters: {result4['code_file']}")
        # Read and display the saved code
        try:
            with open(result4['code_file'], 'r', encoding='utf-8') as f:
                saved_code = f.read()
                print("Saved code content (first 200 chars):")
                print(saved_code[:200] + ("..." if len(saved_code) > 200 else ""))
        except Exception as e:
            print(f"Error reading saved code: {e}")
    
    print("\n=== All tests completed ===")


if __name__ == "__main__":
    asyncio.run(test_enhanced_python_executor())