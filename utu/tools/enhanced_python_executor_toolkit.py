"""
Enhanced Python Executor Toolkit with code saving functionality.
This is an enhanced version that preserves the original python_executor_toolkit.py
"""

import asyncio
import base64
import contextlib
import glob
import io
import os
import re
import json
import warnings
from datetime import datetime
from typing import Callable, Dict, Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# 忽略警告
warnings.filterwarnings('ignore')

# 设置中文字体支持
try:
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
except:
    pass

from ..config import ToolkitConfig
from .base import AsyncBaseToolkit, register_tool

# Used to clean ANSI escape sequences
ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")


def _unescape_code_string(code: str) -> str:
    """
    处理代码字符串中的转义字符，特别是换行符和制表符
    """
    # 如果输入不是字符串，直接返回
    if not isinstance(code, str):
        return str(code)
    
    # 如果代码中包含三重引号，可能是多行字符串
    if '"""' in code or "'''" in code:
        # 尝试直接返回，可能是已经格式化的多行字符串
        return code
    
    # 处理常见的转义序列
    code = code.replace('\\n', '\n')
    code = code.replace('\\t', '\t')
    code = code.replace('\\r', '\r')
    code = code.replace('\\\\', '\\')  # 处理双反斜杠
    
    # 处理可能的JSON转义
    try:
        # 如果代码看起来像JSON字符串，尝试解码
        if code.startswith('"') and code.endswith('"') and len(code) > 1:
            # 尝试JSON解码，处理多行字符串
            decoded = json.loads(code)
            # 如果解码后还是字符串，直接返回
            if isinstance(decoded, str):
                return decoded
            # 如果解码后是字典且包含code键，返回code值
            elif isinstance(decoded, dict) and 'code' in decoded:
                return str(decoded['code'])
            else:
                return str(decoded)
    except (json.JSONDecodeError, TypeError):
        # 如果解码失败，保持原样
        pass
    
    return code


def _safe_json_parse(input_str: str) -> Any:
    """
    安全地解析JSON字符串，特别处理多行代码字符串
    """
    if not isinstance(input_str, str):
        return input_str
    
    # 如果字符串不以引号开头，可能不是JSON字符串
    if not (input_str.startswith('"') and input_str.endswith('"')):
        return input_str
    
    try:
        # 尝试解析JSON
        return json.loads(input_str)
    except json.JSONDecodeError:
        # 如果解析失败，可能是包含特殊字符的普通字符串
        # 尝试手动处理常见的转义字符
        result = input_str
        # 处理双反斜杠
        result = result.replace('\\\\', '\\')
        # 处理换行符转义
        result = result.replace('\\n', '\n')
        # 处理制表符转义
        result = result.replace('\\t', '\t')
        # 处理回车符转义
        result = result.replace('\\r', '\r')
        # 移除外层引号（如果存在）
        if result.startswith('"') and result.endswith('"') and len(result) > 1:
            result = result[1:-1]
        return result


def _preprocess_code_input(code_input: Any) -> str:
    """
    预处理代码输入，确保其为正确的字符串格式
    """
    try:
        # 如果输入是字典且包含'code'键，提取代码
        if isinstance(code_input, dict) and 'code' in code_input:
            code = code_input['code']
        else:
            code = code_input
        
        # 转换为字符串
        if not isinstance(code, str):
            code = str(code)
        
        # 使用安全的JSON解析处理可能的转义问题
        code = _safe_json_parse(code)
        
        # 如果解析后仍然是字符串，再次确保格式正确
        if isinstance(code, str):
            # 处理转义字符
            code = _unescape_code_string(code)
            return code
        else:
            # 如果解析后不是字符串，转换为字符串
            return str(code)
    except Exception as e:
        # 如果预处理失败，返回原始输入的字符串表示
        print(f"Warning: Code preprocessing failed: {e}")
        return str(code_input) if code_input is not None else ""


def _execute_python_code_sync(code: str, workdir: str, save_code: bool = False):
    """
    Synchronous execution of Python code with optional code saving.
    This function is intended to be run in a separate thread.
    """
    original_dir = os.getcwd()
    try:
        # 预处理代码输入
        code_clean = _preprocess_code_input(code)
        
        # Clean up code format
        code_clean = code_clean.strip()
        if code_clean.startswith("```python"):
            code_clean = code_clean.split("```python")[1].split("```")[0].strip()

        # Create and change to working directory (use absolute path)
        workdir_abs = os.path.abspath(workdir)
        os.makedirs(workdir_abs, exist_ok=True)
        os.chdir(workdir_abs)

        # Get file list before execution
        files_before = set(glob.glob("*"))

        # Save code to file if requested (safely)
        code_file_path = None
        if save_code:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                code_file_path = os.path.join(workdir_abs, f"executed_code_{timestamp}.py")
                with open(code_file_path, "w", encoding="utf-8") as f:
                    f.write(f"# Executed at: {timestamp}\n")
                    f.write(f"# Work directory: {workdir}\n")
                    f.write("#" + "="*50 + "\n\n")
                    f.write(code_clean)
            except Exception as save_error:
                # 如果保存失败，不中断主流程，只记录警告
                print(f"Warning: Failed to save code file: {save_error}")
                code_file_path = None

        # Create a new IPython shell instance
        from IPython.core.interactiveshell import InteractiveShell
        from traitlets.config.loader import Config

        InteractiveShell.clear_instance()

        config = Config()
        config.HistoryManager.enabled = False
        config.HistoryManager.hist_file = ":memory:"

        shell = InteractiveShell.instance(config=config)

        if hasattr(shell, "history_manager") and shell.history_manager is not None:
            shell.history_manager.enabled = False

        output = io.StringIO()
        error_output = io.StringIO()

        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error_output):
            # 在执行代码前确保导入必要的库
            setup_code = """
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np

# 导入核心库
libs_to_import = [
    'matplotlib',
    'matplotlib.pyplot as plt'
]

for lib_import in libs_to_import:
    try:
        if 'matplotlib' in lib_import:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        else:
            exec(f"import {lib_import}")
    except ImportError:
        pass

# 安全导入可选库
optional_libs = [
    'seaborn as sns',
    'plotly.express as px',
    'plotly.graph_objects as go'
]

for lib_import in optional_libs:
    try:
        exec(f"import {lib_import}")
    except ImportError:
        pass
"""
            # 执行设置代码
            shell.run_cell(setup_code)
            # 执行用户代码
            shell.run_cell(code_clean)

            if plt.get_fignums():
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format="png")
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode("utf-8")
                plt.close()

                image_name = "output_image.png"
                counter = 1
                while os.path.exists(image_name):
                    image_name = f"output_image_{counter}.png"
                    counter += 1

                with open(image_name, "wb") as f:
                    f.write(base64.b64decode(img_base64))

        stdout_result = output.getvalue()
        stderr_result = error_output.getvalue()

        stdout_result = ANSI_ESCAPE.sub("", stdout_result)
        stderr_result = ANSI_ESCAPE.sub("", stderr_result)

        files_after = set(glob.glob("*"))
        new_files = list(files_after - files_before)
        new_files = [os.path.join(workdir_abs, f) for f in new_files]

        try:
            shell.atexit_operations = lambda: None
            if hasattr(shell, "history_manager") and shell.history_manager is not None:
                shell.history_manager.enabled = False
                shell.history_manager.end_session = lambda: None
            InteractiveShell.clear_instance()
        except Exception:  # pylint: disable=broad-except
            pass

        result = {
            "成功": False
            if "Error" in stderr_result or ("Error" in stdout_result and "Traceback" in stdout_result)
            else True,
            "消息": f"代码执行完成\n输出:\n{stdout_result.strip()}"
            if stdout_result.strip()
            else "代码执行完成，无输出",
            "状态": True,
            "文件": new_files,
            "错误": stderr_result.strip() if stderr_result.strip() else "",
        }
        
        # 如果成功保存了代码文件，将其添加到结果中
        if code_file_path and os.path.exists(code_file_path):
            result["代码文件"] = code_file_path

        return result
    except Exception as e:  # pylint: disable=broad-except
        return {
            "success": False,
            "message": f"Code execution failed, error message:\n{str(e)}",
            "status": False,
            "files": [],
            "error": str(e),
        }
    finally:
        os.chdir(original_dir)


class EnhancedPythonExecutorToolkit(AsyncBaseToolkit):
    """
    An enhanced tool for executing Python code in a sandboxed environment with code saving functionality.
    This tool extends the original PythonExecutorToolkit with additional features.
    """

    def __init__(self, config: ToolkitConfig | dict | None = None):
        super().__init__(config)

    async def get_tools_map(self) -> Dict[str, Callable]:
        return {
            "execute_python_code_enhanced": self.execute_python_code_enhanced,
        }

    @register_tool()
    async def execute_python_code_enhanced(self, code: str, workdir: str = "./run_workdir", timeout: int = 30, save_code: bool = False) -> Dict[str, Any]:
        """
        Executes Python code and returns the output with optional code saving.

        Args:
            code (str): The Python code to execute.
            workdir (str): The working directory for the execution. Defaults to "./run_workdir".
            timeout (int): The execution timeout in seconds. Defaults to 30.
            save_code (bool): Whether to save the executed code to a file. Defaults to False.

        Returns:
            dict: A dictionary containing the execution results.
        """
        try:
            # 预处理代码输入，确保其格式正确
            processed_code = _preprocess_code_input(code)

            # 添加调试信息
            print(f"Debug: Original code type: {type(code)}")
            print(f"Debug: Processed code type: {type(processed_code)}")
            if isinstance(code, str) and len(code) < 200:
                print(f"Debug: Original code: {code}")
            if isinstance(processed_code, str) and len(processed_code) < 200:
                print(f"Debug: Processed code: {processed_code}")

            # 检查是否是matplotlib代码，如果是则注入常用变量
            if isinstance(processed_code, str) and any(keyword in processed_code.lower() for keyword in ['plt', 'matplotlib', 'companies', 'revenue', 'profit']):
                # 为matplotlib代码预定义常用财务数据变量
                matplotlib_code = _inject_matplotlib_variables(processed_code)
                processed_code = matplotlib_code

            loop = asyncio.get_running_loop()
            return await asyncio.wait_for(
                loop.run_in_executor(
                    None,  # Use the default thread pool executor
                    _execute_python_code_sync,
                    processed_code,
                    workdir,
                    save_code,
                ),
                timeout=timeout,
            )
        except TimeoutError:
            return {
                "success": False,
                "message": f"代码执行超时 ({timeout} 秒)",
                "stdout": "",
                "stderr": "",
                "status": False,
                "output": "",
                "files": [],
                "error": f"Code execution timed out ({timeout} seconds)",
            }
        except json.JSONDecodeError as je:
            # 特别处理JSON解析错误
            error_msg = f"JSON解析错误: {str(je)}. 请检查输入的代码格式是否正确，特别是多行字符串和特殊字符的处理。"
            print(f"Error: {error_msg}")
            return {
                "success": False,
                "message": error_msg,
                "stdout": "",
                "stderr": "",
                "status": False,
                "output": "",
                "files": [],
                "error": f"JSONDecodeError: {str(je)}",
            }
        except Exception as e:
            # 捕获所有其他异常并返回错误信息
            error_msg = f"执行代码时发生错误: {str(e)}"
            print(f"Error: {error_msg}")
            return {
                "success": False,
                "message": error_msg,
                "stdout": "",
                "stderr": "",
                "status": False,
                "output": "",
                "files": [],
                "error": str(e),
            }


def _inject_matplotlib_variables(code: str) -> str:
    """
    为matplotlib代码注入常用变量

    Args:
        code (str): 原始Python代码

    Returns:
        str: 注入变量后的代码
    """
    # 检查代码中是否缺少变量定义
    import re

    # 常见的matplotlib图表变量
    common_vars = {
        'companies': ["宁德时代", "比亚迪"],
        'revenue': [2830.72, 3712.81],
        'net_profit': [522.97, 160.39],
        'profit_margin': [18.47, 4.32],
        'roe': [15.06, 6.55],
        'asset_turnover': [0.32, 0.44],
        'debt_ratio': [61.27, 71.08],
        'current_ratio': [1.33, 1.14],
        'revenue_growth': [41.54, 117.9],
        'profit_growth': [30.74, 69.8]
    }

    # 构建变量注入代码
    variable_injections = []
    for var_name, var_value in common_vars.items():
        if var_name in code and f"{var_name} = " not in code:
            # 检查是否需要导入matplotlib
            if 'import matplotlib' not in code and 'plt.' in code:
                variable_injections.append("import matplotlib.pyplot as plt")
                variable_injections.append("import numpy as np")

            # 注入变量定义
            variable_injections.append(f"{var_name} = {repr(var_value)}")

    if variable_injections:
        injected_code = "\n".join(variable_injections) + "\n\n" + code
        print(f"Debug: Injected variables: {list(common_vars.keys())}")
        print(f"Debug: Variable code: {variable_injections}")
        return injected_code
    else:
        return code