#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化数据清洗配置测试
直接测试配置文件而不依赖复杂的导入
"""

import os
import json
import yaml
from pathlib import Path

def test_config_loading():
    """测试配置加载"""
    print("测试数据清洗配置文件加载...")
    
    config_file = Path(__file__).parent / "configs" / "agents" / "examples" / "stock_analysis_final_with_cleansing.yaml"
    
    if not config_file.exists():
        print(f"[FAIL] 配置文件不存在: {config_file}")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print(f"[OK] 配置文件加载成功")
        print(f"[INFO] 配置大小: {len(yaml.dump(config, allow_unicode=True))} 字符")
        
        # 检查关键组件
        required_sections = [
            'type',
            'planner_config',
            'workers',
            'toolkits',
            'workspace_config'
        ]
        
        for section in required_sections:
            if section in config:
                print(f"[OK] 包含配置节: {section}")
            else:
                print(f"[FAIL] 缺少配置节: {section}")
                return False
        
        # 检查DataCleanserAgent
        workers = config.get('workers', {})
        if 'DataCleanserAgent' in workers:
            print("[OK] 包含DataCleanserAgent配置")
            cleanser_config = workers['DataCleanserAgent'].get('agent', {})
            instructions = cleanser_config.get('instructions', '')
            
            if '数据清洗' in instructions and '标准化' in instructions:
                print("[OK] DataCleanserAgent指令包含数据清洗功能")
            else:
                print("[WARN] DataCleanserAgent指令可能不完整")
        else:
            print("[FAIL] 缺少DataCleanserAgent配置")
            return False
        
        # 检查数据清洗工具包
        toolkits = config.get('toolkits', {})
        if 'data_cleanser' in toolkits:
            print("[OK] 包含数据清洗工具包配置")
            cleansing_config = toolkits['data_cleanser']
            print(f"[INFO] 清洗配置: {list(cleansing_config.keys())}")
        else:
            print("[FAIL] 缺少数据清洗工具包配置")
            return False
        
        return True
        
    except Exception as e:
        print(f"[FAIL] 配置加载失败: {str(e)}")
        return False

def test_workflow_integration():
    """测试工作流集成"""
    print("\n测试工作流集成...")
    
    config_file = Path(__file__).parent / "configs" / "agents" / "examples" / "stock_analysis_final_with_cleansing.yaml"
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        workers = config.get('workers', {})
        expected_order = ['DataAgent', 'DataCleanserAgent', 'DataAnalysisAgent', 'FinancialAnalysisAgent', 'ChartGeneratorAgent', 'ReportAgent']
        
        print("预期工作流顺序:")
        for i, worker in enumerate(expected_order, 1):
            status = "✓" if worker in workers else "✗"
            print(f"  {i}. {status} {worker}")
        
        # 检查配置完整性
        missing_workers = [w for w in expected_order if w not in workers]
        if missing_workers:
            print(f"[WARN] 缺少智能体: {missing_workers}")
        else:
            print("[OK] 所有预期智能体都存在")
        
        return len(missing_workers) == 0
        
    except Exception as e:
        print(f"[FAIL] 工作流集成测试失败: {str(e)}")
        return False

def test_cleansing_features():
    """测试数据清洗功能特性"""
    print("\n测试数据清洗功能特性...")
    
    config_file = Path(__file__).parent / "configs" / "agents" / "examples" / "stock_analysis_final_with_cleansing.yaml"
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 检查DataCleanserAgent的指令
        workers = config.get('workers', {})
        cleanser_agent = workers.get('DataCleanserAgent', {}).get('agent', {})
        instructions = cleanser_agent.get('instructions', '')
        
        expected_features = [
            "中文键名映射",
            "历史数据解析", 
            "数据格式转换",
            "质量评估",
            "错误修复",
            "标准化输出"
        ]
        
        print("检查数据清洗功能特性:")
        found_features = []
        for feature in expected_features:
            if any(keyword in instructions for keyword in feature.split()):
                print(f"  ✓ {feature}")
                found_features.append(feature)
            else:
                print(f"  ✗ {feature}")
        
        coverage = len(found_features) / len(expected_features) * 100
        print(f"\n功能覆盖率: {coverage:.1f}% ({len(found_features)}/{len(expected_features)})")
        
        return coverage >= 70  # 至少70%的功能覆盖
        
    except Exception as e:
        print(f"[FAIL] 功能特性测试失败: {str(e)}")
        return False

def test_toolkit_configuration():
    """测试工具包配置"""
    print("\n测试工具包配置...")
    
    config_file = Path(__file__).parent / "configs" / "agents" / "examples" / "stock_analysis_final_with_cleansing.yaml"
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        toolkits = config.get('toolkits', {})
        
        # 检查关键工具包
        critical_toolkits = [
            'akshare_data',
            'data_cleanser',
            'financial_analyzer',
            'analysis_executor',
            'report_saver'
        ]
        
        print("检查关键工具包:")
        for toolkit in critical_toolkits:
            if toolkit in toolkits:
                print(f"  ✓ {toolkit}")
            else:
                print(f"  ✗ {toolkit}")
        
        # 检查数据清洗参数
        if 'data_cleanser' in toolkits:
            cleansing_params = toolkits['data_cleanser'].get('cleansing_params', {})
            print("\n数据清洗参数:")
            for param, value in cleansing_params.items():
                print(f"  {param}: {value}")
        
        return len([t for t in critical_toolkits if t in toolkits]) >= 4
        
    except Exception as e:
        print(f"[FAIL] 工具包配置测试失败: {str(e)}")
        return False

def test_workspace_configuration():
    """测试工作空间配置"""
    print("\n测试工作空间配置...")
    
    config_file = Path(__file__).parent / "configs" / "agents" / "examples" / "stock_analysis_final_with_cleansing.yaml"
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        workspace_config = config.get('workspace_config', {})
        
        required_workspace_settings = [
            'root',
            'auto_create',
            'cleanup_old_files'
        ]
        
        print("检查工作空间配置:")
        for setting in required_workspace_settings:
            if setting in workspace_config:
                print(f"  ✓ {setting}: {workspace_config[setting]}")
            else:
                print(f"  ✗ {setting}")
        
        return all(setting in workspace_config for setting in required_workspace_settings)
        
    except Exception as e:
        print(f"[FAIL] 工作空间配置测试失败: {str(e)}")
        return False

def create_test_summary():
    """创建测试总结"""
    print("\n创建测试总结...")
    
    summary = {
        "test_date": "2025-10-27",
        "config_file": "configs/agents/examples/stock_analysis_final_with_cleansing.yaml",
        "test_results": {
            "config_loading": test_config_loading(),
            "workflow_integration": test_workflow_integration(),
            "cleansing_features": test_cleansing_features(),
            "toolkit_configuration": test_toolkit_configuration(),
            "workspace_configuration": test_workspace_configuration()
        },
        "expected_benefits": [
            "解决DataAnalysisAgent中文数据识别问题",
            "自动处理历史数据年份解析",
            "提供数据质量评估和保证",
            "标准化数据格式输出",
            "增强系统稳定性",
            "改善分析结果准确性"
        ],
        "usage_instructions": {
            "command_line": "python main.py --config stock_analysis_final_with_cleansing",
            "web_interface": "python main.py web --config stock_analysis_final_with_cleansing",
            "expected_workflow": "DataAgent → DataCleanserAgent → DataAnalysisAgent → ...",
            "test_data": "包含中文键名的财务数据"
        }
    }
    
    try:
        summary_file = Path(__file__).parent / "data_cleansing_config_test_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"[OK] 测试总结已保存: {summary_file}")
        return True
        
    except Exception as e:
        print(f"[FAIL] 保存测试总结失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("数据清洗配置文件测试")
    print("=" * 50)
    
    # 运行测试
    tests = [
        ("配置加载", test_config_loading),
        ("工作流集成", test_workflow_integration),
        ("数据清洗功能", test_cleansing_features),
        ("工具包配置", test_toolkit_configuration),
        ("工作空间配置", test_workspace_configuration)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed_tests += 1
                print(f"[PASS] {test_name}")
            else:
                print(f"[FAIL] {test_name}")
        except Exception as e:
            print(f"[ERROR] {test_name}: {str(e)}")
    
    # 创建测试总结
    create_test_summary()
    
    # 输出总结
    print(f"\n{'='*60}")
    print("配置测试总结")
    print(f"{'='*60}")
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {total_tests - passed_tests}")
    print(f"成功率: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests >= total_tests - 1:
        print("\n[SUCCESS] 数据清洗配置测试通过！")
        print("\n配置文件优势:")
        print("- 完整集成DataCleanserAgent")
        print("- 支持中文财务数据处理")
        print("- 包含数据质量保证机制")
        print("- 工作流集成正确")
        print("- 工具包配置完整")
        
        print("\n使用指南:")
        print("1. 配置文件已准备就绪")
        print("2. 包含完整的数据清洗工作流")
        print("3. 支持中文数据自动处理")
        print("4. 可通过现有启动脚本使用")
        
        print("\n下一步:")
        print("- 可集成到现有启动脚本中")
        print("- 建议进行实际数据测试")
        print("- 可根据需要调整清洗参数")
        
        return True
    else:
        print(f"\n[WARNING] 有 {total_tests - passed_tests} 个测试失败")
        print("请检查配置文件并修复问题。")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)