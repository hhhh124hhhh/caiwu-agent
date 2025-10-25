import sys
import traceback

print("开始逐步导入测试...")

# 1. 测试基本导入
try:
    print("1. 导入基本模块...")
    import os
    import json
    from datetime import datetime
    print("   ✓ 基本模块导入成功")
except Exception as e:
    print(f"   ✗ 基本模块导入失败: {e}")
    traceback.print_exc()

# 2. 测试配置模块
try:
    print("2. 导入配置模块...")
    from utu.config import ToolkitConfig
    print("   ✓ 配置模块导入成功")
except Exception as e:
    print(f"   ✗ 配置模块导入失败: {e}")
    traceback.print_exc()

# 3. 测试基类模块
try:
    print("3. 导入基类模块...")
    from utu.tools.base import AsyncBaseToolkit, register_tool
    print("   ✓ 基类模块导入成功")
except Exception as e:
    print(f"   ✗ 基类模块导入失败: {e}")
    traceback.print_exc()

# 4. 测试PDF模块
try:
    print("4. 导入PDF模块...")
    from fpdf import FPDF
    from fpdf.html import HTMLMixin
    print("   ✓ PDF模块导入成功")
except Exception as e:
    print(f"   ✗ PDF模块导入失败: {e}")
    traceback.print_exc()

# 5. 测试完整导入
try:
    print("5. 导入完整ReportSaverToolkit...")
    from utu.tools.report_saver_toolkit import ReportSaverToolkit
    print("   ✓ 完整导入成功")
    
    # 6. 测试实例化
    print("6. 测试实例化...")
    toolkit = ReportSaverToolkit(config={"workspace_root": "./test_output"})
    print("   ✓ 实例化成功")
    
except Exception as e:
    print(f"   ✗ 完整导入或实例化失败: {e}")
    traceback.print_exc()

print("逐步导入测试完成")