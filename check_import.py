import sys
import traceback

print("开始检查导入...")

try:
    print("尝试导入fpdf...")
    from fpdf import FPDF
    print("fpdf导入成功")
except Exception as e:
    print(f"fpdf导入失败: {e}")
    traceback.print_exc()

try:
    print("尝试导入ReportSaverToolkit...")
    from utu.tools.report_saver_toolkit import ReportSaverToolkit
    print("ReportSaverToolkit导入成功")
except Exception as e:
    print(f"ReportSaverToolkit导入失败: {e}")
    traceback.print_exc()

print("检查完成")