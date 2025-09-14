from utu.config import ConfigLoader
from utu.tools.enhanced_python_executor_toolkit import EnhancedPythonExecutorToolkit
import os
import shutil

toolkit = EnhancedPythonExecutorToolkit(ConfigLoader.load_toolkit_config("enhanced_python_executor"))


async def test_enhanced_python_executor_toolkit():
    # Clean up any existing test directories
    test_dirs = ["./test_enhanced_workdir1", "./test_enhanced_workdir2"]
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
    
    test_code = """
print("Hello, Enhanced Python Executor!")
x = 5
y = 10
result = x * y
print(f"Result: {result}")
"""
    result = await toolkit.execute_python_code_enhanced(code=test_code, workdir="./test_enhanced_workdir1", save_code=True)
    print(result)
    assert result["success"]
    assert "Hello, Enhanced Python Executor!" in result["message"]
    assert "Result: 50" in result["message"]
    # Check that code file was saved
    assert "code_file" in result
    assert os.path.exists(result["code_file"])
    
    test_code_with_plot = """
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.cos(x)

plt.figure(figsize=(8, 6))
plt.plot(x, y, 'r-', label='cos(x)')
plt.title('Cosine Function')
plt.grid(True)

print("Cosine plot generated")
"""
    result_plot = await toolkit.execute_python_code_enhanced(code=test_code_with_plot, workdir="./test_enhanced_workdir2", save_code=True)
    print(result_plot)
    assert result_plot["success"]
    assert "Cosine plot generated" in result_plot["message"]
    assert len(result_plot["files"]) >= 1
    assert "code_file" in result_plot
    assert os.path.exists(result_plot["code_file"])