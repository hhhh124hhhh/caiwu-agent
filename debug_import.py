import sys
import traceback

print("开始导入调试...")

# 重定向stderr以捕获所有错误
original_stderr = sys.stderr
try:
    with open('import_debug.log', 'w', encoding='utf-8') as f:
        sys.stderr = f
        
        print("1. 开始导入utu.config...")
        try:
            from utu.config import ToolkitConfig
            print("   ✓ utu.config导入成功")
        except Exception as e:
            print(f"   ✗ utu.config导入失败: {e}")
            traceback.print_exc()
        
        print("2. 开始导入utu.tools.base...")
        try:
            from utu.tools.base import AsyncBaseToolkit, register_tool
            print("   ✓ utu.tools.base导入成功")
        except Exception as e:
            print(f"   ✗ utu.tools.base导入失败: {e}")
            traceback.print_exc()
        
        print("3. 开始导入fpdf...")
        try:
            from fpdf import FPDF
            from fpdf.html import HTMLMixin
            print("   ✓ fpdf导入成功")
        except Exception as e:
            print(f"   ✗ fpdf导入失败: {e}")
            traceback.print_exc()
        
        print("4. 开始导入report_saver_toolkit...")
        try:
            from utu.tools.report_saver_toolkit import ReportSaverToolkit
            print("   ✓ report_saver_toolkit导入成功")
        except Exception as e:
            print(f"   ✗ report_saver_toolkit导入失败: {e}")
            traceback.print_exc()

finally:
    sys.stderr = original_stderr

print("导入调试完成，查看import_debug.log获取详细信息")