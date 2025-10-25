import sys
import traceback

print("开始最小工具包测试...")

# 尝试导入并创建ReportSaverToolkit实例
try:
    print("1. 导入ReportSaverToolkit...")
    from utu.tools.report_saver_toolkit import ReportSaverToolkit
    print("   ✓ 导入成功")
    
    print("2. 创建工具包实例...")
    toolkit = ReportSaverToolkit(config={"workspace_root": "./test_output"})
    print(f"   ✓ 实例创建成功，工作目录: {toolkit.workspace_root}")
    
    print("3. 检查工具包方法...")
    methods = [method for method in dir(toolkit) if not method.startswith('_')]
    print(f"   ✓ 可用方法: {methods}")
    
    print("最小工具包测试完成！")
    
except Exception as e:
    print(f"✗ 测试失败: {e}")
    traceback.print_exc()
    sys.exit(1)