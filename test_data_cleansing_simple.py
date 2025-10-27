#!/usr/bin/env python3
"""
数据清洗系统简化测试脚本
测试核心数据清洗功能，避免复杂依赖
"""

import sys
import os
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_data_format_standards():
    """测试数据格式标准"""
    print("测试数据格式标准...")
    
    try:
        from utu.schemas.data_cleansing_schemas import DataFormatStandards, QualityLevel
        
        # 检查支持的输入格式
        input_formats = DataFormatStandards.SUPPORTED_INPUT_FORMATS
        print(f"✅ 支持的输入格式: {len(input_formats)}种")
        
        # 检查支持的输出格式
        output_formats = DataFormatStandards.SUPPORTED_OUTPUT_FORMATS
        print(f"✅ 支持的输出格式: {len(output_formats)}种")
        
        # 检查质量等级阈值
        thresholds = DataFormatStandards.QUALITY_LEVEL_THRESHOLDS
        print(f"✅ 质量等级阈值: {len(thresholds)}个等级")
        
        # 检查字段映射
        field_mappings = DataFormatStandards.FIELD_MAPPINGS
        print(f"✅ 字段映射: {len(field_mappings)}个类别")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据格式标准测试失败: {str(e)}")
        return False

def test_quality_metrics():
    """测试质量指标"""
    print("\n测试质量指标...")
    
    try:
        from utu.schemas.data_cleansing_schemas import QualityMetrics, QualityLevel, determine_quality_level
        
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
        print(f"✅ 质量指标转换为字典: {len(metrics_dict)}个字段")
        
        # 测试质量等级确定
        quality_level = determine_quality_level(85.5)
        print(f"✅ 质量等级确定: 85.5分 -> {quality_level.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ 质量指标测试失败: {str(e)}")
        return False

def test_data_cleansing_schemas():
    """测试数据清洗模式"""
    print("\n测试数据清洗模式...")
    
    try:
        from utu.schemas.data_cleansing_schemas import (
            DataCleansingDataType, ProcessingStage, QualityLevel, 
            IssueSeverity, QualityIssue, DataValidationResult,
            DataTransformResult, DataQualityReport, DataCleansingResult
        )
        
        # 测试枚举类型
        data_types = list(DataCleansingDataType)
        print(f"✅ 数据清洗数据类型: {len(data_types)}种")
        
        processing_stages = list(ProcessingStage)
        print(f"✅ 处理阶段: {len(processing_stages)}个")
        
        quality_levels = list(QualityLevel)
        print(f"✅ 质量等级: {len(quality_levels)}个")
        
        issue_severities = list(IssueSeverity)
        print(f"✅ 问题严重程度: {len(issue_severities)}个")
        
        # 测试质量问题
        issue = QualityIssue(
            issue_id="TEST_001",
            issue_type="missing_field",
            severity=IssueSeverity.HIGH,
            description="测试问题",
            affected_fields=["revenue"]
        )
        issue_dict = issue.to_dict()
        print(f"✅ 质量问题转换: {len(issue_dict)}个字段")
        
        # 测试验证结果
        validation_result = DataValidationResult(
            is_valid=True,
            data_type="chinese_financial_format",
            quality_score=85.0
        )
        validation_dict = validation_result.to_dict()
        print(f"✅ 验证结果转换: {len(validation_dict)}个字段")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据清洗模式测试失败: {str(e)}")
        return False

def test_message_factory():
    """测试消息工厂"""
    print("\n测试消息工厂...")
    
    try:
        from utu.schemas.data_cleansing_schemas import DataCleansingMessageFactory, create_cleansing_message
        
        # 测试创建验证请求
        test_data = {"利润表": {"营业收入": 1000, "净利润": 100}}
        validation_msg = DataCleansingMessageFactory.create_validation_request(
            test_data, "TestAgent"
        )
        print(f"✅ 验证请求消息: {validation_msg.processing_stage.value}")
        
        # 测试创建转换请求
        transform_msg = DataCleansingMessageFactory.create_transformation_request(
            test_data, "TestAgent", "data_analysis_agent_compatible"
        )
        print(f"✅ 转换请求消息: {transform_msg.processing_stage.value}")
        
        # 测试便捷函数
        convenient_msg = create_cleansing_message(
            "validation_request", test_data, "TestAgent"
        )
        print(f"✅ 便捷函数创建消息: {convenient_msg.processing_stage.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ 消息工厂测试失败: {str(e)}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    print("\n测试基本功能...")
    
    try:
        # 测试数据示例
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
                "2024": {"营业收入": 1511.39, "净利润": 36.11}
            }
        }
        
        # 测试JSON序列化
        json_str = json.dumps(test_data, ensure_ascii=False, indent=2)
        print(f"✅ JSON序列化: {len(json_str)}字符")
        
        # 测试JSON反序列化
        parsed_data = json.loads(json_str)
        print(f"✅ JSON反序列化: {len(parsed_data)}个键")
        
        # 测试数据结构检查
        has_income = '利润表' in parsed_data
        has_balance = '资产负债表' in parsed_data
        has_historical = '历史数据' in parsed_data
        print(f"✅ 数据结构检查: 利润表={has_income}, 资产负债表={has_balance}, 历史数据={has_historical}")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本功能测试失败: {str(e)}")
        return False

def test_import_dependencies():
    """测试导入依赖"""
    print("测试导入依赖...")
    
    dependencies = [
        ("utu.schemas.data_cleansing_schemas", "数据清洗模式"),
        ("utu.schemas.agent_schemas", "基础代理模式"),
        ("json", "JSON处理"),
        ("pathlib", "路径处理"),
        ("datetime", "日期时间"),
        ("typing", "类型提示"),
        ("dataclasses", "数据类"),
        ("enum", "枚举")
    ]
    
    success_count = 0
    for module_name, description in dependencies:
        try:
            __import__(module_name)
            print(f"✅ {description}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {description}: {str(e)}")
    
    print(f"\n导入成功率: {success_count}/{len(dependencies)} ({success_count/len(dependencies)*100:.1f}%)")
    return success_count == len(dependencies)

def main():
    """主函数"""
    print("数据清洗系统简化测试")
    print("=" * 50)
    
    # 运行测试
    tests = [
        ("导入依赖", test_import_dependencies),
        ("数据格式标准", test_data_format_standards),
        ("质量指标", test_quality_metrics),
        ("数据清洗模式", test_data_cleansing_schemas),
        ("消息工厂", test_message_factory),
        ("基本功能", test_basic_functionality)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {str(e)}")
    
    # 输出总结
    print(f"\n{'='*60}")
    print(f"测试总结")
    print(f"{'='*60}")
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {total_tests - passed_tests}")
    print(f"成功率: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 所有测试通过！数据清洗系统基础功能正常。")
        return True
    else:
        print(f"\n⚠️ 有 {total_tests - passed_tests} 个测试失败，请检查问题。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)