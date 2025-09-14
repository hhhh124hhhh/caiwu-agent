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
from datetime import datetime
from typing import Callable, Dict, Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ..config import ToolkitConfig
from .base import AsyncBaseToolkit

# Used to clean ANSI escape sequences
ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")


def _execute_python_code_sync(code: str, workdir: str, save_code: bool = False):
    """
    Synchronous execution of Python code with optional code saving.
    This function is intended to be run in a separate thread.
    """
    original_dir = os.getcwd()
    try:
        # Clean up code format
        code_clean = code.strip()
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
            "success": False
            if "Error" in stderr_result or ("Error" in stdout_result and "Traceback" in stdout_result)
            else True,
            "message": f"Code execution completed\nOutput:\n{stdout_result.strip()}"
            if stdout_result.strip()
            else "Code execution completed, no output",
            "status": True,
            "files": new_files,
            "error": stderr_result.strip() if stderr_result.strip() else "",
        }
        
        # 如果成功保存了代码文件，将其添加到结果中
        if code_file_path and os.path.exists(code_file_path):
            result["code_file"] = code_file_path

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
        loop = asyncio.get_running_loop()
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(
                    None,  # Use the default thread pool executor
                    _execute_python_code_sync,
                    code,
                    workdir,
                    save_code,
                ),
                timeout=timeout,
            )
        except TimeoutError:
            return {
                "success": False,
                "message": f"Code execution timed out ({timeout} seconds)",
                "stdout": "",
                "stderr": "",
                "status": False,
                "output": "",
                "files": [],
                "error": f"Code execution timed out ({timeout} seconds)",
            }