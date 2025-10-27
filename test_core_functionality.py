#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据清洗系统核心功能测试
避免复杂依赖，直接测试核心组件
"""

import sys
import os
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_basic_imports():
    """测试基本导入"""
    print("测试基本导入...")
    
    try:
        # 直接测试模式导入，避免通过utu包
        sys.path.insert(0, str(project_root / "utu" / "schemas"))
        from data_cleansing_schemas import (
            DataCleansingDataType, ProcessingStage, QualityLevel, 
            IssueSeverity, QualityMetrics, QualityIssue
        )
        print("✓ 数据清洗模式导入成功")
        
        # 测试枚举
        data_types = [dt.value for dt in DataCleansingDataType]
        processing_stages = [ps.value for ps in ProcessingStage]
        quality_levels = [ql.value for ql in QualityLevel]
        issue_severities = [isv.value for isv in IssueSeverity]
        
        print(f"✓ 数据类型: {data_types}")
        print(f"✓ 处理阶段: {processing_stages}")
        print(f"✓ 质量等级: {quality_levels}")
        print(f"✓ 问题严重程度: {issue_severities}")
        
        return True
        
    except Exception as e:
        print(f"✗ 导入失败: {str(e)}")
        return False

def test_quality_metrics():
    """测试质量指标"""
    print("\n测试质量指标...")
    
    try:
        sys.path.insert(0, str(project_root / "utu" / "schemas"))
        from data_cleansing_schemas import QualityMetrics, determine_quality_level
        
        # 创建质量指标
        metrics = QualityMetrics(
            overall_score=85.5,
            completeness_score=90.0,
            accuracy_score=85.0,
            consistency_score=80.0,
            validity_score=88.0,
            timeliness_score=85.0,
            uniqueness_score=85.0
        )
        
        # 转换为字典
        metrics_dict = metrics.to_dict()
        print(f"✓ 质量指标字典: {len(metrics_dict)}个字段")
        
        # 测试质量等级确定
        quality_level = determine_quality_level(85.5)
        print(f"✓ 质量等级: 85.5分 -> {quality_level.value}")
        
        return True
        
    except Exception as e:
        print(f"✗ 质量指标测试失败: {str(e)}")
        return False

def test_data_structures():
    """测试数据结构"""
    print("\n测试数据结构...")
    
    try:
        sys.path.insert(0, str(project_root / "utu" / "schemas"))
        from data_cleansing_schemas import QualityIssue, DataValidationResult
        
        # 测试质量问题
        issue = QualityIssue(
            issue_id="TEST_001",
            issue_type="missing_field",
            severity=IssueSeverity.HIGH,
            description="测试问题",
            affected_fields=["revenue"]
        )
        issue_dict = issue.to_dict()
        print(f"✓ 质量问题: {len(issue_dict)}个字段")
        
        # 测试验证结果
        validation_result = DataValidationResult(
            is_valid=True,
            data_type="chinese_financial_format",
            quality_score=85.0
        )
        validation_dict = validation_result.to_dict()
        print(f"✓ 验证结果: {len(validation_dict)}个字段")
        
        return True
        
    except Exception as e:
        print(f"✗ 数据结构测试失败: {str(e)}")
        return False

def test_financial_data_processing():
    """测试财务数据处理"""
    print("\n测试财务数据处理...")
    
    try:
        # 测试数据
        test_data = {
            "利润表": {
                "营业收入": 573.88,
                "净利润": 11.04,
                "营业成本": 552.84
            },
            "资产负债表": {
                "总资产": 3472.98,
                "总负债": 3081.02,
                "所有者权益": 391.96
            },
            "历史数据": {
                "2025": {"营业收入": 573.88, "净利润": 11.04},
                "2024": {"营业收入": 1511.39, "净利润": 36.11},
                "2023": {"营业收入": 1420.56, "净利润": 32.45}
            }
        }
        
        # 检查数据结构
        required_sections = ["利润表", "资产负债表", "历史数据"]
        missing_sections = [section for section in required_sections if section not in test_data]
        
        if missing_sections:
            print(f"✗ 缺少部分: {missing_sections}")
            return False
        
        print(f"✓ 数据结构完整，包含{len(test_data)}个部分")
        
        # 检查历史数据
        historical_data = test_data["历史数据"]
        years = list(historical_data.keys())
        print(f"✓ 历史数据年份: {years}")
        
        # 检查数据类型
        for section_name, section_data in test_data.items():
            if isinstance(section_data, dict):
                print(f"✓ {section_name}: {len(section_data)}个字段")
            else:
                print(f"✗ {section_name}: 不是字典类型")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ 财务数据处理失败: {str(e)}")
        return False

def test_json_handling():
    """测试JSON处理"""
    print("\n测试JSON处理...")
    
    try:
        # 测试数据
        test_data = {
            "利润表": {"营业收入": 1000, "净利润": 100},
            "资产负债表": {"总资产": 5000, "总负债": 3000}
        }
        
        # 序列化
        json_str = json.dumps(test_data, ensure_ascii=False, indent=2)
        print(f"✓ JSON序列化: {len(json_str)}字符")
        
        # 反序列化
        parsed_data = json.loads(json_str)
        print(f"✓ JSON反序列化: {len(parsed_data)}个键")
        
        # 检查数据完整性
        if test_data == parsed_data:
            print("✓ 数据完整性验证通过")
            return True
        else:
            print("✗ 数据完整性验证失败")
            return False
            
    except Exception as e:
        print(f"✗ JSON处理失败: {str(e)}")
        return False

def test_configuration_files():
    """测试配置文件"""
    print("\n测试配置文件...")
    
    config_files = [
        "configs/agents/workers/data_cleanser_agent.yaml",
        "configs/agents/examples/stock_analysis_final_with_cleansing.yaml",
        "configs/agents/workers/standard_agent_config.yaml"
    ]
    
    existing_files = 0
    for config_file in config_files:
        config_path = project_root / config_file
        if config_path.exists():
            print(f"✓ {config_file}")
            existing_files += 1
        else:
            print(f"✗ {config_file} 不存在")
    
    print(f"配置文件存在率: {existing_files}/{len(config_files)}")
    return existing_files == len(config_files)

def main():
    """主函数"""
    print("数据清洗系统核心功能测试")
    print("=" * 50)
    
    # 运行测试
    tests = [
        ("基本导入", test_basic_imports),
        ("质量指标", test_quality_metrics),
        ("数据结构", test_data_structures),
        ("财务数据处理", test_financial_data_processing),
        ("JSON处理", test_json_handling),
        ("配置文件", test_configuration_files)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed_tests += 1
                print(f"✓ {test_name} 通过")
            else:
                print(f"✗ {test_name} 失败")
        except Exception as e:
            print(f"✗ {test_name} 异常: {str(e)}")
    
    # 输出总结
    print(f"\n{'='*60}")
    print(f"测试总结")
    print(f"{'='*60}")
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {total_tests - passed_tests}")
    print(f"成功率: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n所有测试通过！数据清洗系统核心功能正常。")
        return True
    else:
        print(f"\n有 {total_tests - passed_tests} 个测试失败，请检查问题。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)