#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试脚本，用于验证financial_analysis_toolkit.py的语法错误修复
"""

import sys
import os

def test_syntax_validation():
    """
    测试financial_analysis_toolkit.py的语法是否正确
    """
    print("开始验证financial_analysis_toolkit.py的语法修复...")
    
    # 获取文件路径
    file_path = os.path.join(os.path.dirname(__file__), 'utu', 'tools', 'financial_analysis_toolkit.py')
    
    if not os.path.exists(file_path):
        print(f"❌ 错误: 文件不存在 - {file_path}")
        return False
    
    try:
        # 使用Python解释器检查语法
        import subprocess
        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', file_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ 语法验证通过! financial_analysis_toolkit.py没有语法错误。")
            print("所有修复都已成功应用:")
            print("  1. 修复了第891行的缩进问题")
            print("  2. 修复了第2152行缺少except的try语句")
            print("  3. 修复了第2389行的缩进问题")
            return True
        else:
            print(f"❌ 语法验证失败!")
            print(f"错误输出: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 验证过程中发生错误: {str(e)}")
        return False

def test_import_validation():
    """
    测试是否能成功导入financial_analysis_toolkit模块
    """
    print("\n开始测试导入financial_analysis_toolkit模块...")
    
    try:
        # 尝试导入模块
        from utu.tools import financial_analysis_toolkit
        print("✅ 模块导入成功! financial_analysis_toolkit可以正常导入。")
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 导入过程中发生其他错误: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  financial_analysis_toolkit.py 错误修复验证")
    print("=" * 60)
    
    # 运行验证
    syntax_ok = test_syntax_validation()
    import_ok = test_import_validation()
    
    print("\n" + "=" * 60)
    if syntax_ok and import_ok:
        print("🎉 所有验证都通过了! 修复成功。")
        sys.exit(0)
    else:
        print("❌ 部分验证失败，请检查错误信息。")
        sys.exit(1)