#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文财务数据测试用例 (简化版)
为数据清洗智能体提供完整的中文测试数据集
"""

import json
import sys
import pathlib
from typing import Dict, Any, List
from datetime import datetime

# 添加项目根目录到Python路径
project_root = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class ChineseFinancialDataTestCases:
    """中文财务数据测试用例生成器"""
    
    def __init__(self):
        self.test_cases = []
        self.validation_results = []
    
    def create_basic_chinese_test_case(self) -> Dict[str, Any]:
        """创建基础中文测试用例"""
        return {
            "test_id": "basic_chinese_001",
            "name": "基础中文财务数据",
            "description": "包含标准中文键名的基础财务数据",
            "data": {
                "公司基本信息": {
                    "公司名称": "测试股份有限公司",
                    "股票代码": "600000.SH",
                    "所属行业": "制造业",
                    "上市日期": "2000-01-01"
                },
                "利润表": {
                    "营业收入": 573.88,
                    "营业成本": 552.84,
                    "营业利润": 11.04,
                    "利润总额": 11.04,
                    "净利润": 11.04,
                    "基本每股收益": 0.15,
                    "稀释每股收益": 0.15
                },
                "资产负债表": {
                    "总资产": 3472.98,
                    "流动资产": 2500.45,
                    "固定资产": 650.34,
                    "无形资产": 322.19,
                    "总负债": 3081.02,
                    "流动负债": 2800.12,
                    "非流动负债": 280.90,
                    "所有者权益": 391.96,
                    "归属于母公司所有者权益": 391.96
                },
                "现金流量表": {
                    "经营活动现金流量净额": 25.67,
                    "投资活动现金流量净额": -15.23,
                    "筹资活动现金流量净额": -8.45,
                    "现金及现金等价物净增加额": 1.99,
                    "期末现金及现金等价物余额": 180.56
                },
                "关键指标": {
                    "净利润率(%)": 1.92,
                    "毛利率(%)": 3.67,
                    "资产负债率(%)": 88.71,
                    "流动比率": 0.89,
                    "速动比率": 0.75,
                    "ROE(%)": 2.68,
                    "ROA(%)": 0.32
                },
                "历史数据": {
                    "2025": {
                        "营业收入": 573.88,
                        "净利润": 11.04,
                        "总资产": 3472.98,
                        "所有者权益": 391.96
                    },
                    "2024": {
                        "营业收入": 1511.39,
                        "净利润": 36.11,
                        "总资产": 3250.45,
                        "所有者权益": 368.20
                    },
                    "2023": {
                        "营业收入": 1420.56,
                        "净利润": 32.45,
                        "总资产": 3120.89,
                        "所有者权益": 351.34
                    },
                    "2022": {
                        "营业收入": 1280.23,
                        "净利润": 28.67,
                        "总资产": 2980.12,
                        "所有者权益": 332.45
                    }
                }
            },
            "expected_cleansing_results": {
                "mapped_fields": [
                    "利润表 -> income_statement",
                    "资产负债表 -> balance_sheet",
                    "现金流量表 -> cash_flow_statement",
                    "历史数据 -> historical_data",
                    "营业收入 -> revenue",
                    "净利润 -> net_profit",
                    "总资产 -> total_assets",
                    "总负债 -> total_liabilities"
                ],
                "parsed_years": ["2025", "2024", "2023", "2022"],
                "quality_score_range": [80, 95],
                "standardized_structure": True
            },
            "test_focus": [
                "中文键名识别和映射",
                "历史数据年份解析",
                "财务比率计算",
                "数据质量评估"
            ]
        }
    
    def create_mixed_format_test_case(self) -> Dict[str, Any]:
        """创建混合格式测试用例"""
        return {
            "test_id": "mixed_format_002",
            "name": "混合格式财务数据",
            "description": "包含中英文混合、格式不一致的复杂数据",
            "data": {
                "company_info": {
                    "company_name": "混合格式测试公司",
                    "stock_code": "600001.SH",
                    "industry": "综合企业"
                },
                # 英文格式的利润表
                "income_statement": {
                    "revenue": 2500.0,
                    "gross_profit": 800.0,
                    "operating_profit": 350.0,
                    "net_profit": 300.0
                },
                # 中文格式的利润表（重复数据）
                "利润表": {
                    "营业收入": 1500.0,
                    "毛利润": 500.0,
                    "营业利润": 280.0,
                    "净利润": 180.0
                },
                # 混合格式的资产负债表
                "资产负债表": {
                    "total_assets": 8000.0,
                    "current_assets": 4000.0,
                    "non_current_assets": 4000.0,
                    "total_liabilities": 5000.0,
                    "current_liabilities": 2500.0,
                    "total_equity": 3000.0
                },
                # 混合格式的历史数据
                "历史数据": {
                    "2024": {
                        "revenue": 2000.0,
                        "net_profit": 250.0,
                        "营业收入": 1500.0,
                        "净利润": 180.0,
                        "total_assets": 7000.0,
                        "total_equity": 2800.0
                    },
                    "2023": {
                        "revenue": 1800.0,
                        "net_profit": 220.0,
                        "营业收入": 1700.0,
                        "净利润": 200.0,
                        "total_assets": 6500.0,
                        "total_equity": 2600.0
                    }
                },
                # 补充的财务指标
                "财务指标": {
                    "净利润率": 12.0,
                    "毛利率": 32.0,
                    "资产负债率": 62.5
                }
            },
            "expected_cleansing_results": {
                "data_consolidation": True,
                "field_deduplication": True,
                "format_standardization": True,
                "year_format_normalization": True,
                "quality_score_range": [75, 90]
            },
            "test_focus": [
                "数据去重",
                "格式标准化",
                "年份格式统一",
                "中英文字段合并"
            ]
        }
    
    def create_problematic_data_test_case(self) -> Dict[str, Any]:
        """创建问题数据测试用例"""
        return {
            "test_id": "problematic_data_003",
            "name": "问题数据修复测试",
            "description": "包含各种数据问题的复杂用例，测试错误检测和修复功能",
            "data": {
                "公司名称": "问题数据测试公司",
                "股票代码": None,  # 缺少股票代码
                
                # 问题利润表
                "利润表": {
                    "营业收入": 0,  # 收入为0（异常）
                    "净利润": -500.0,  # 严重亏损
                    "营业成本": "invalid_value",  # 无效字符串值
                    "营业利润": None,  # 空值
                    "财务费用": float('inf'),  # 无穷大值
                    "所得税费用": float('nan'),  # 非数值
                    "其他收益": "N/A",  # 字符串N/A
                    "未分配利润": ""  # 空字符串
                },
                
                # 不完整的资产负债表
                "资产负债表": {
                    "流动资产": None,  # 关键字段缺失
                    "固定资产": 1000.0,
                    "无形资产": 200.0
                    # 缺少总资产、总负债、所有者权益等关键字段
                },
                
                # 问题历史数据
                "历史数据": {
                    "2024": {
                        "营业收入": 1000.0,
                        # 缺少净利润
                        "总资产": 5000.0
                    },
                    "2023": {
                        "营业收入": 0,  # 收入为0
                        "净利润": -200.0,  # 亏损
                        "总资产": None  # 缺少资产数据
                    },
                    "2022": {
                        # 完全空的记录
                    }
                },
                
                # 异常的财务指标
                "财务指标": {
                    "净利润率": "很高",  # 非数值字符串
                    "毛利率": -150.0,  # 负毛利率
                    "资产负债率": 999.99,  # 异常高比率
                    "流动比率": 0.0,  # 零比率
                    "ROE": None  # 空值
                }
            },
            "expected_cleansing_results": {
                "issues_detected": [
                    "缺失关键字段",
                    "无效数据类型",
                    "异常数值检测",
                    "空值处理"
                ],
                "auto_fixes_applied": [
                    "数据类型转换",
                    "默认值填充",
                    "异常值处理",
                    "缺失字段推断"
                ],
                "quality_score_range": [60, 80],
                "data_usability": "基本可用"
            },
            "test_focus": [
                "错误数据检测",
                "自动修复功能",
                "数据验证机制",
                "质量评估准确性"
            ]
        }
    
    def generate_all_test_cases(self) -> List[Dict[str, Any]]:
        """生成所有测试用例"""
        print("生成中文财务数据测试用例...")
        
        test_cases = [
            self.create_basic_chinese_test_case(),
            self.create_mixed_format_test_case(),
            self.create_problematic_data_test_case()
        ]
        
        self.test_cases = test_cases
        print(f"[OK] 生成完成 {len(test_cases)} 个测试用例")
        
        return test_cases
    
    def save_test_cases_to_file(self, file_path: str = None) -> str:
        """保存测试用例到文件"""
        if file_path is None:
            file_path = pathlib.Path(__file__).parent / "chinese_financial_test_cases.json"
        else:
            file_path = pathlib.Path(file_path)
        
        try:
            test_cases_data = {
                "generation_info": {
                    "created_at": datetime.now().isoformat(),
                    "generator": "ChineseFinancialDataTestCases",
                    "version": "1.0.0",
                    "description": "数据清洗智能体中文财务数据测试用例集"
                },
                "test_cases": self.test_cases,
                "summary": {
                    "total_cases": len(self.test_cases),
                    "test_categories": [
                        "基础中文数据",
                        "混合格式数据", 
                        "问题数据修复"
                    ],
                    "data_formats": [
                        "中文键名",
                        "英文键名", 
                        "混合格式",
                        "异常数据",
                        "缺失数据"
                    ],
                    "test_focuses": [
                        "字段映射",
                        "历史数据解析",
                        "错误检测修复",
                        "性能压力测试",
                        "边界条件处理"
                    ]
                }
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(test_cases_data, f, ensure_ascii=False, indent=2)
            
            print(f"[OK] 测试用例已保存到: {file_path}")
            return str(file_path)
            
        except Exception as e:
            print(f"[FAIL] 保存测试用例失败: {str(e)}")
            return None
    
    def validate_test_cases(self) -> Dict[str, Any]:
        """验证测试用例"""
        print("验证测试用例完整性...")
        
        validation_results = {
            "total_cases": len(self.test_cases),
            "validation_details": [],
            "issues_found": [],
            "recommendations": []
        }
        
        for i, test_case in enumerate(self.test_cases):
            case_validation = {
                "case_id": test_case["test_id"],
                "name": test_case["name"],
                "issues": [],
                "warnings": []
            }
            
            # 验证必需字段
            required_fields = ["test_id", "name", "description", "data", "expected_cleansing_results", "test_focus"]
            for field in required_fields:
                if field not in test_case:
                    case_validation["issues"].append(f"缺少必需字段: {field}")
            
            # 验证数据结构
            if "data" in test_case:
                data = test_case["data"]
                
                # 检查财务报表
                financial_statements = ["利润表", "资产负债表", "现金流量表", "历史数据"]
                found_statements = [stmt for stmt in financial_statements if stmt in data]
                case_validation["found_statements"] = found_statements
                
                if not found_statements:
                    case_validation["warnings"].append("未找到任何财务报表")
            
            # 验证预期结果
            if "expected_cleansing_results" in test_case:
                expected = test_case["expected_cleansing_results"]
                if "test_focus" not in expected:
                    case_validation["warnings"].append("缺少测试重点说明")
            
            validation_results["validation_details"].append(case_validation)
            
            if case_validation["issues"]:
                validation_results["issues_found"].append({
                    "case_id": test_case["test_id"],
                    "issues": case_validation["issues"]
                })
        
        # 生成建议
        if validation_results["issues_found"]:
            validation_results["recommendations"].append("修复发现的测试用例问题")
        
        if len(validation_results["validation_details"]) == validation_results["total_cases"]:
            validation_results["recommendations"].append("所有测试用例验证通过")
        
        try:
            validation_file = pathlib.Path(__file__).parent / "test_cases_validation_report.json"
            with open(validation_file, 'w', encoding='utf-8') as f:
                json.dump(validation_results, f, ensure_ascii=False, indent=2)
            
            print(f"[OK] 验证报告已保存: {validation_file}")
            
        except Exception as e:
            print(f"[FAIL] 保存验证报告失败: {str(e)}")
        
        print(f"验证完成: {validation_results['total_cases']} 个测试用例")
        if validation_results["issues_found"]:
            print(f"发现问题: {len(validation_results['issues_found'])} 个")
        else:
            print("[OK] 所有测试用例验证通过")
        
        return validation_results


def main():
    """主函数"""
    print("中文财务数据测试用例生成器")
    print("=" * 50)
    
    try:
        # 创建测试用例生成器
        generator = ChineseFinancialDataTestCases()
        
        # 生成所有测试用例
        test_cases = generator.generate_all_test_cases()
        
        # 保存测试用例
        file_path = generator.save_test_cases_to_file()
        
        # 验证测试用例
        validation_results = generator.validate_test_cases()
        
        # 输出总结
        print(f"\n{'='*60}")
        print("测试用例生成总结")
        print(f"{'='*60}")
        print(f"生成的测试用例数量: {len(test_cases)}")
        print(f"文件保存位置: {file_path}")
        print(f"验证状态: {'通过' if not validation_results['issues_found'] else '需要修复'}")
        
        if validation_results['issues_found']:
            print(f"\n发现的问题:")
            for issue in validation_results['issues_found']:
                print(f"  - 测试用例 {issue['case_id']}: {', '.join(issue['issues'])}")
        
        print(f"\n测试用例分类:")
        categories = {}
        for test_case in test_cases:
            category = test_case.get('name', '未分类')
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        
        for category, count in categories.items():
            print(f"  - {category}: {count}个")
        
        print(f"\n使用方法:")
        print(f"1. 测试用例文件: {file_path}")
        print(f"2. 可用于数据清洗智能体测试")
        print(f"3. 验证中文数据处理能力")
        print(f"4. 检查错误检测和修复功能")
        
        return len(test_cases) > 0
        
    except Exception as e:
        print(f"[FAIL] 生成测试用例失败: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)