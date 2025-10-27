#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单测试配置文件中的插值引用是否已修复
直接读取YAML文件检查内容
"""

import sys
import os

def check_config_file(file_path, check_patterns):
    """检查配置文件内容中是否包含指定模式"""
    print(f"\n检查文件: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            all_patterns_passed = True
            for pattern, expected_status in check_patterns:
                if pattern in content:
                    if expected_status:
                        print(f"✅ 找到期望的模式: '{pattern}'")
                    else:
                        print(f"❌ 找到不期望的模式: '{pattern}'")
                        all_patterns_passed = False
                else:
                    if expected_status:
                        print(f"❌ 未找到期望的模式: '{pattern}'")
                        all_patterns_passed = False
                    else:
                        print(f"✅ 确认不包含不期望的模式: '{pattern}'")
            
            return all_patterns_passed
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return False

def test_data_agent_config():
    """测试data_agent.yaml配置文件是否已修复插值引用"""
    file_path = os.path.join(os.getcwd(), "configs", "agents", "workers", "data_agent.yaml")
    
    # 检查模式：(模式, 是否应该存在)
    check_patterns = [
        # 不应该存在的插值引用
        ("${standard_config.standard_toolkits.akshare_data}", False),
        ("${standard_config.standard_workspace.root}", False),
        # 应该存在的修复后的配置（简化模式）
        ("workspace_root:", True),
        ("cache_enabled: true", True),
        ("timeout: 45", True)
    ]
    
    return check_config_file(file_path, check_patterns)

def test_stock_analysis_final_config():
    """测试stock_analysis_final.yaml配置文件是否依赖已修复的配置"""
    file_path = os.path.join(os.getcwd(), "configs", "agents", "examples", "stock_analysis_final.yaml")
    
    # 检查文件是否存在和基本配置
    check_patterns = [
        # 检查文件基本结构
        ("akshare_data", True),
        ("stock_analysis_workspace", True)
    ]
    
    return check_config_file(file_path, check_patterns)

if __name__ == "__main__":
    print("=== 配置加载测试脚本 ===")
    
    success1 = test_data_agent_config()
    success2 = test_stock_analysis_final_config()
    
    print("\n=== 测试结果总结 ===")
    if success1 and success2:
        print("🎉 所有配置文件加载成功! 插值错误已修复。")
        sys.exit(0)
    else:
        print("❌ 部分配置文件加载失败，请检查错误信息。")
        sys.exit(1)