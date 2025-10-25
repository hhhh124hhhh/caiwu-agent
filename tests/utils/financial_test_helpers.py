#!/usr/bin/env python3
"""
财务测试辅助工具
提供测试过程中常用的辅助函数和验证工具
"""

import os
import json
import time
import psutil
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
import numpy as np


class FinancialTestHelpers:
    """财务测试辅助工具类"""

    @staticmethod
    def create_mock_financial_data(company_name: str = "测试公司", **kwargs) -> Dict[str, Any]:
        """创建模拟财务数据

        Args:
            company_name: 公司名称
            **kwargs: 自定义参数

        Returns:
            格式化的财务数据字典
        """
        defaults = {
            "income": [
                {
                    "营业收入": 10000000000,  # 100亿
                    "营业成本": 8000000000,   # 80亿
                    "净利润": 1500000000,     # 15亿
                    "归属于母公司所有者的净利润": 1200000000  # 12亿
                }
            ],
            "balance": [
                {
                    "资产总计": 50000000000,  # 500亿
                    "负债合计": 20000000000,  # 200亿
                    "所有者权益合计": 30000000000,  # 300亿
                    "流动资产合计": 20000000000,     # 200亿
                    "流动负债合计": 10000000000,     # 100亿
                    "存货": 5000000000,  # 50亿
                    "应收账款": 3000000000,  # 30亿
                    "固定资产": 20000000000,  # 200亿
                    "长期投资": 5000000000  # 50亿
                }
            ],
            "cashflow": [
                {
                    "经营活动产生的现金流量净额": 2000000000,  # 20亿
                    "投资活动现金流出小计": 1500000000,  # 15亿
                    "分配股利、利润或偿付利息支付的现金": 500000000  # 5亿
                }
            ]
        }

        # 合并自定义参数
        data = defaults.copy()
        for key, value in kwargs.items():
            if key in data and isinstance(data[key], list):
                data[key][0].update(value)
            else:
                data[key] = value

        return data

    @staticmethod
    def validate_calculation_accuracy(calculated: Any, expected: Any, tolerance: float = 0.01) -> bool:
        """验证计算准确性

        Args:
            calculated: 计算值
            expected: 期望值
            tolerance: 容差范围（相对误差）

        Returns:
            验证结果
        """
        if calculated is None or expected is None:
            return False

        try:
            if isinstance(expected, (int, float)) and isinstance(calculated, (int, float)):
                if expected == 0:
                    return abs(calculated) <= tolerance
                relative_error = abs(calculated - expected) / abs(expected)
                return relative_error <= tolerance
            else:
                return calculated == expected
        except (TypeError, ValueError, ZeroDivisionError):
            return False

    @staticmethod
    def validate_chart_file(chart_path: str, min_size: int = 1000) -> Dict[str, Any]:
        """验证图表文件完整性

        Args:
            chart_path: 图表文件路径
            min_size: 最小文件大小（字节）

        Returns:
            验证结果字典
        """
        result = {
            "exists": False,
            "readable": False,
            "valid_size": False,
            "valid_format": False,
            "dimensions": None,
            "file_size": 0,
            "error": None
        }

        try:
            # 检查文件是否存在
            if not os.path.exists(chart_path):
                result["error"] = "文件不存在"
                return result
            result["exists"] = True

            # 检查文件大小
            file_size = os.path.getsize(chart_path)
            result["file_size"] = file_size
            result["valid_size"] = file_size >= min_size

            # 尝试读取图片
            with Image.open(chart_path) as img:
                result["readable"] = True
                result["dimensions"] = img.size
                result["valid_format"] = img.format in ['PNG', 'JPEG', 'JPG', 'BMP']

        except Exception as e:
            result["error"] = str(e)

        return result

    @staticmethod
    def validate_report_content(report_path: str, expected_content: List[str] = None) -> Dict[str, Any]:
        """验证报告内容完整性

        Args:
            report_path: 报告文件路径
            expected_content: 期望包含的内容列表

        Returns:
            验证结果字典
        """
        result = {
            "exists": False,
            "readable": False,
            "content_found": {},
            "file_size": 0,
            "error": None
        }

        try:
            # 检查文件是否存在
            if not os.path.exists(report_path):
                result["error"] = "文件不存在"
                return result
            result["exists"] = True

            # 检查文件大小
            result["file_size"] = os.path.getsize(report_path)

            # 读取文件内容
            encoding = 'utf-8'
            try:
                with open(report_path, 'r', encoding=encoding) as f:
                    content = f.read()
            except UnicodeDecodeError:
                encoding = 'gbk'
                with open(report_path, 'r', encoding=encoding) as f:
                    content = f.read()

            result["readable"] = True

            # 检查期望内容
            if expected_content:
                for expected in expected_content:
                    found = expected in content
                    result["content_found"][expected] = found

        except Exception as e:
            result["error"] = str(e)

        return result

    @staticmethod
    def cleanup_test_files(file_paths: List[str]) -> int:
        """清理测试文件

        Args:
            file_paths: 文件路径列表

        Returns:
            清理成功的文件数量
        """
        cleaned_count = 0

        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    cleaned_count += 1
            except Exception:
                pass

        return cleaned_count

    @staticmethod
    def measure_performance(func, *args, **kwargs) -> Tuple[Any, float]:
        """测量函数执行性能

        Args:
            func: 要测量的函数
            *args: 函数参数
            **kwargs: 函数关键字参数

        Returns:
            (函数结果, 执行时间)
        """
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time

        return result, duration

    @staticmethod
    def measure_memory_usage(func, *args, **kwargs) -> Tuple[Any, float]:
        """测量函数内存使用

        Args:
            func: 要测量的函数
            *args: 函数参数
            **kwargs: 函数关键字参数

        Returns:
            (函数结果, 内存使用量MB)
        """
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        result = func(*args, **kwargs)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = final_memory - initial_memory

        return result, memory_used

    @staticmethod
    def create_test_directory(base_name: str = "test_financial") -> str:
        """创建测试目录

        Args:
            base_name: 基础目录名

        Returns:
            测试目录路径
        """
        import tempfile
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        test_dir = os.path.join(tempfile.gettempdir(), f"{base_name}_{unique_id}")
        os.makedirs(test_dir, exist_ok=True)

        return test_dir

    @staticmethod
    def generate_test_report(test_results: Dict[str, Any], output_path: str = None) -> str:
        """生成测试报告

        Args:
            test_results: 测试结果字典
            output_path: 输出路径（可选）

        Returns:
            报告文件路径
        """
        if output_path is None:
            output_path = FinancialTestHelpers.create_test_directory("test_report")
            output_path = os.path.join(output_path, "test_report.md")

        report_content = f"""# 财务智能体测试报告

## 测试概览

- 测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
- 总测试数量: {len(test_results)}
- 成功数量: {sum(1 for r in test_results.values() if r.get('success', False))}
- 失败数量: {sum(1 for r in test_results.values() if not r.get('success', False))}

## 详细测试结果

"""

        for test_name, result in test_results.items():
            status = "✓ 通过" if result.get('success', False) else "✗ 失败"
            report_content += f"### {test_name} - {status}\n\n"

            if 'message' in result:
                report_content += f"**信息**: {result['message']}\n\n"

            if 'duration' in result:
                report_content += f"**耗时**: {result['duration']:.3f}秒\n\n"

            if 'error' in result:
                report_content += f"**错误**: {result['error']}\n\n"

            report_content += "---\n\n"

        # 写入报告文件
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        return output_path

    @staticmethod
    def compare_financial_data(data1: Dict[str, Any], data2: Dict[str, Any]) -> Dict[str, Any]:
        """比较两组财务数据

        Args:
            data1: 第一组数据
            data2: 第二组数据

        Returns:
            比较结果字典
        """
        comparison = {
            "identical": True,
            "differences": {},
            "summary": {
                "total_sections": 0,
                "different_sections": 0,
                "identical_sections": 0
            }
        }

        sections = ["income", "balance", "cashflow"]

        for section in sections:
            comparison["summary"]["total_sections"] += 1

            if section in data1 and section in data2:
                # 简单比较序列化后的内容
                str1 = json.dumps(data1[section], sort_keys=True)
                str2 = json.dumps(data2[section], sort_keys=True)

                if str1 != str2:
                    comparison["identical"] = False
                    comparison["differences"][section] = "内容不同"
                    comparison["summary"]["different_sections"] += 1
                else:
                    comparison["summary"]["identical_sections"] += 1
            else:
                comparison["identical"] = False
                missing_in = "data1" if section not in data1 else "data2"
                comparison["differences"][section] = f"在{missing_in}中缺失"
                comparison["summary"]["different_sections"] += 1

        return comparison

    @staticmethod
    def validate_financial_ratios(ratios: Dict[str, Any]) -> Dict[str, Any]:
        """验证财务比率的合理性

        Args:
            ratios: 财务比率字典

        Returns:
            验证结果字典
        """
        validation = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "summary": {
                "total_dimensions": 0,
                "total_metrics": 0,
                "valid_metrics": 0
            }
        }

        expected_dimensions = ["profitability", "solvency", "efficiency", "growth", "cash_flow"]
        metric_ranges = {
            "profitability": {
                "gross_profit_margin": (0, 100),
                "net_profit_margin": (-50, 50),
                "roe": (-100, 100),
                "roa": (-50, 50)
            },
            "solvency": {
                "debt_to_asset_ratio": (0, 100),
                "current_ratio": (0.1, 10),
                "quick_ratio": (0.1, 5)
            },
            "efficiency": {
                "asset_turnover": (0, 5),
                "inventory_turnover": (0, 20),
                "receivables_turnover": (0, 50)
            },
            "growth": {
                "revenue_growth": (-100, 1000),
                "profit_growth": (-100, 1000)
            },
            "cash_flow": {
                "operating_cash_flow": (-1000, 1000),  # 亿元
                "cash_flow_ratio": (-10, 10),
                "free_cash_flow": (-1000, 1000),
                "cash_reinvestment_ratio": (0, 100),
                "cash_to_investment_ratio": (0, 10)
            }
        }

        for dimension in expected_dimensions:
            if dimension in ratios:
                validation["summary"]["total_dimensions"] += 1

                for metric_name, value in ratios[dimension].items():
                    validation["summary"]["total_metrics"] += 1

                    # 检查数值类型
                    if not isinstance(value, (int, float)):
                        validation["errors"].append(f"{dimension}.{metric_name}: 不是数值类型")
                        continue

                    # 检查范围
                    if dimension in metric_ranges and metric_name in metric_ranges[dimension]:
                        min_val, max_val = metric_ranges[dimension][metric_name]
                        if not (min_val <= value <= max_val):
                            validation["warnings"].append(
                                f"{dimension}.{metric_name}: {value} 超出正常范围 [{min_val}, {max_val}]"
                            )
                        else:
                            validation["summary"]["valid_metrics"] += 1
                    else:
                        validation["warnings"].append(f"{dimension}.{metric_name}: 未定义验证范围")

        # 判断整体有效性
        if len(validation["errors"]) > 0:
            validation["valid"] = False

        return validation

    @staticmethod
    def create_performance_baseline() -> Dict[str, float]:
        """创建性能基准

        Returns:
            性能基准字典
        """
        return {
            "single_company_analysis": 5.0,  # 秒
            "multi_company_analysis": 15.0,  # 秒
            "chart_generation": 3.0,         # 秒/图
            "report_generation": 2.0,        # 秒
            "memory_usage_limit": 500.0      # MB
        }

    @staticmethod
    def check_performance_compliance(performance_data: Dict[str, float],
                                   baseline: Dict[str, float] = None) -> Dict[str, Any]:
        """检查性能合规性

        Args:
            performance_data: 性能数据
            baseline: 性能基准（可选）

        Returns:
            合规性检查结果
        """
        if baseline is None:
            baseline = FinancialTestHelpers.create_performance_baseline()

        compliance = {
            "compliant": True,
            "violations": [],
            "summary": {
                "total_checks": 0,
                "passed_checks": 0,
                "failed_checks": 0
            }
        }

        for metric, actual_value in performance_data.items():
            if metric in baseline:
                compliance["summary"]["total_checks"] += 1
                baseline_value = baseline[metric]

                if actual_value <= baseline_value:
                    compliance["summary"]["passed_checks"] += 1
                else:
                    compliance["summary"]["failed_checks"] += 1
                    compliance["violations"].append({
                        "metric": metric,
                        "actual": actual_value,
                        "baseline": baseline_value,
                        "exceeded_by": actual_value - baseline_value
                    })
                    compliance["compliant"] = False

        return compliance


class TestDataGenerator:
    """测试数据生成器"""

    @staticmethod
    def generate_financial_data_with_variations(base_data: Dict[str, Any],
                                                variations: Dict[str, float]) -> Dict[str, Any]:
        """生成带有变化的财务数据

        Args:
            base_data: 基础财务数据
            variations: 变化比例字典

        Returns:
            变化后的财务数据
        """
        data = json.loads(json.dumps(base_data))  # 深拷贝

        for section, section_data in data.items():
            if isinstance(section_data, list) and len(section_data) > 0:
                for field, variation_ratio in variations.items():
                    if field in section_data[0]:
                        original_value = section_data[0][field]
                        if isinstance(original_value, (int, float)):
                            section_data[0][field] = int(original_value * variation_ratio)

        return data

    @staticmethod
    def generate_time_series_data(start_year: int, years: int,
                                  base_values: Dict[str, float],
                                  growth_rates: Dict[str, float]) -> Dict[str, Any]:
        """生成时间序列数据

        Args:
            start_year: 起始年份
            years: 年数
            base_values: 基础值字典
            growth_rates: 增长率字典

        Returns:
            时间序列财务数据
        """
        data = {"income": [], "balance": [], "cashflow": []}

        for i in range(years):
            year = start_year + i
            multiplier = (1 + growth_rates.get("revenue", 0.1)) ** i

            # 收入表
            income_entry = {
                "营业收入": int(base_values["revenue"] * multiplier * 100000000),
                "营业成本": int(base_values["cost"] * multiplier * 100000000),
                "净利润": int(base_values["profit"] * (1 + growth_rates.get("profit", 0.12)) ** i * 100000000),
                "归属于母公司所有者的净利润": int(base_values["parent_profit"] * (1 + growth_rates.get("profit", 0.12)) ** i * 100000000)
            }
            data["income"].append(income_entry)

            # 资产负债表
            asset_multiplier = (1 + growth_rates.get("assets", 0.08)) ** i
            balance_entry = {
                "资产总计": int(base_values["assets"] * asset_multiplier * 100000000),
                "负债合计": int(base_values["liabilities"] * asset_multiplier * 100000000),
                "所有者权益合计": int(base_values["equity"] * asset_multiplier * 100000000),
                "流动资产合计": int(base_values["current_assets"] * asset_multiplier * 100000000),
                "流动负债合计": int(base_values["current_liabilities"] * asset_multiplier * 100000000),
                "存货": int(base_values["inventory"] * asset_multiplier * 100000000),
                "应收账款": int(base_values["receivables"] * asset_multiplier * 100000000),
                "固定资产": int(base_values["fixed_assets"] * asset_multiplier * 100000000),
                "长期投资": int(base_values["long_investment"] * asset_multiplier * 100000000)
            }
            data["balance"].append(balance_entry)

            # 现金流量表
            cash_multiplier = multiplier
            cashflow_entry = {
                "经营活动产生的现金流量净额": int(base_values["operating_cf"] * cash_multiplier * 100000000),
                "投资活动现金流出小计": int(base_values["investing_cf"] * cash_multiplier * 100000000),
                "分配股利、利润或偿付利息支付的现金": int(base_values["dividend"] * cash_multiplier * 100000000)
            }
            data["cashflow"].append(cashflow_entry)

        return data


if __name__ == "__main__":
    # 测试辅助工具功能
    print("测试财务测试辅助工具...")

    # 测试模拟数据生成
    mock_data = FinancialTestHelpers.create_mock_financial_data("测试公司")
    print(f"模拟数据生成: {len(mock_data)} 个部分")

    # 测试计算准确性验证
    accuracy = FinancialTestHelpers.validate_calculation_accuracy(20.1, 20.0, 0.01)
    print(f"计算准确性验证: {accuracy}")

    # 测试性能测量
    def dummy_function():
        time.sleep(0.1)
        return "result"

    result, duration = FinancialTestHelpers.measure_performance(dummy_function)
    print(f"性能测量: {duration:.3f}秒")

    print("辅助工具测试完成！")