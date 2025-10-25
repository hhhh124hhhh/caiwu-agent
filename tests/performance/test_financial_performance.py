#!/usr/bin/env python3
"""
财务分析性能和压力测试
测试系统在高负载和大数据量下的性能表现
"""

import pytest
import json
import time
import os
import tempfile
import shutil
import psutil
import asyncio
import threading
from pathlib import Path
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer
from utu.tools.tabular_data_toolkit import TabularDataToolkit
from utu.tools.report_saver_toolkit import ReportSaverToolkit
from tests.utils.financial_test_helpers import FinancialTestHelpers


class TestFinancialPerformance:
    """财务分析性能测试类"""

    @pytest.fixture
    def temp_workspace(self):
        """创建临时工作空间"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def performance_tools(self):
        """性能测试工具套件"""
        return {
            "analyzer": StandardFinancialAnalyzer(),
            "chart_generator": TabularDataToolkit(),
            "report_saver": ReportSaverToolkit()
        }

    @pytest.fixture
    def performance_baseline(self):
        """性能基准"""
        return {
            "single_company_analysis": 5.0,      # 秒
            "batch_companies_analysis": 30.0,    # 秒/10家公司
            "chart_generation": 3.0,             # 秒/图
            "report_generation": 2.0,            # 秒
            "memory_limit": 500.0,                # MB
            "cpu_limit": 80.0                    # CPU使用率限制
        }

    def test_single_company_analysis_performance(self, performance_tools, temp_workspace, performance_baseline):
        """测试单公司分析性能"""
        analyzer = performance_tools["analyzer"]

        # 创建测试数据
        test_data = FinancialTestHelpers.create_mock_financial_data("性能测试公司")

        # 多次测试取平均值
        durations = []
        for i in range(5):
            start_time = time.time()
            financial_data_json = json.dumps(test_data["financial_data"])
            ratios = analyzer.calculate_ratios(financial_data_json)
            end_time = time.time()
            durations.append(end_time - start_time)

        # 计算平均性能
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)

        print(f"单公司分析性能:")
        print(f"  平均耗时: {avg_duration:.3f}秒")
        print(f"  最快耗时: {min_duration:.3f}秒")
        print(f"  最慢耗时: {max_duration:.3f}秒")
        print(f"  基准要求: ≤{performance_baseline['single_company_analysis']}秒")

        # 性能验证
        assert avg_duration <= performance_baseline["single_company_analysis"], \
            f"单公司分析性能不达标: {avg_duration:.3f}s > {performance_baseline['single_company_analysis']}s"

        print("✓ 单公司分析性能测试通过")

    def test_batch_companies_analysis_performance(self, performance_tools, temp_workspace, performance_baseline):
        """测试批量公司分析性能"""
        analyzer = performance_tools["analyzer"]

        # 创建多个公司的测试数据
        companies_count = 10
        companies_data = []

        for i in range(companies_count):
            company_data = FinancialTestHelpers.create_mock_financial_data(f"性能测试公司{i+1}")
            companies_data.append(company_data)

        # 测试批量分析
        start_time = time.time()
        results = []

        for company_data in companies_data:
            financial_data_json = json.dumps(company_data["financial_data"])
            ratios = analyzer.calculate_ratios(financial_data_json)
            results.append(ratios)

        end_time = time.time()
        total_duration = end_time - start_time
        avg_per_company = total_duration / companies_count

        print(f"批量公司分析性能 ({companies_count}家公司):")
        print(f"  总耗时: {total_duration:.3f}秒")
        print(f"  平均每家耗时: {avg_per_company:.3f}秒")
        print(f"  批量基准: ≤{performance_baseline['batch_companies_analysis']}秒")

        # 性能验证
        assert total_duration <= performance_baseline["batch_companies_analysis"], \
            f"批量分析性能不达标: {total_duration:.3f}s > {performance_baseline['batch_companies_analysis']}s"

        # 验证所有公司都成功分析
        assert len(results) == companies_count, "所有公司都应该成功分析"

        successful_analyses = sum(1 for result in results if len(result) > 0)
        success_rate = successful_analyses / companies_count * 100
        print(f"  成功率: {success_rate:.1f}%")

        print("✓ 批量公司分析性能测试通过")

    def test_chart_generation_performance(self, performance_tools, temp_workspace, performance_baseline):
        """测试图表生成性能"""
        chart_generator = performance_tools["chart_generator"]

        # 创建测试数据
        chart_data = {
            "companies": [f"公司{i+1}" for i in range(3)],
            "revenue": [1000, 1500, 1200],
            "net_profit": [100, 180, 150],
            "roe": [8.0, 10.0, 9.0],
            "debt_ratio": [40.0, 45.0, 42.0]
        }

        chart_data_json = json.dumps(chart_data)
        chart_types = ["comparison", "radar", "trend", "scatter"]

        chart_durations = {}

        for chart_type in chart_types:
            start_time = time.time()
            result = chart_generator.generate_charts(
                data_json=chart_data_json,
                chart_type=chart_type,
                output_dir=temp_workspace
            )
            end_time = time.time()

            duration = end_time - start_time
            chart_durations[chart_type] = duration

            print(f"  {chart_type}图表: {duration:.3f}秒")

            # 验证生成成功
            assert result.get('success', False), f"{chart_type}图表生成应该成功"
            if result.get('success') and result.get('files'):
                assert len(result['files']) > 0, f"{chart_type}图表应该生成文件"

        avg_chart_duration = sum(chart_durations.values()) / len(chart_durations)
        total_chart_duration = sum(chart_durations.values())

        print(f"图表生成性能:")
        print(f"  平均每图耗时: {avg_chart_duration:.3f}秒")
        print(f"  总计耗时: {total_chart_duration:.3f}秒")
        print(f"  单图基准: ≤{performance_baseline['chart_generation']}秒")

        # 性能验证（单图基准）
        for chart_type, duration in chart_durations.items():
            assert duration <= performance_baseline["chart_generation"], \
                f"{chart_type}图表性能不达标: {duration:.3f}s > {performance_baseline['chart_generation']}s"

        print("✓ 图表生成性能测试通过")

    def test_report_generation_performance(self, performance_tools, temp_workspace, performance_baseline):
        """测试报告生成性能"""
        report_saver = performance_tools["report_saver"]

        # 创建测试报告内容
        report_content = """# 性能测试财务分析报告

## 测试内容
本报告用于测试报告生成的性能表现。

## 性能指标
- 生成速度测试
- 内存使用测试
- 文件大小测试

## 结论
报告生成性能测试完成。

---
*生成时间: {}
*测试工具: Youtu-Agent Enhanced*
""".format(time.strftime('%Y-%m-%d %H:%M:%S'))

        # 测试多种格式
        formats = ["md", "html", "json"]
        report_durations = {}

        for format_type in formats:
            start_time = time.time()
            result = report_saver.save_report(
                content=report_content,
                filename="performance_test_report",
                format_type=format_type,
                workspace=temp_workspace
            )
            end_time = time.time()

            duration = end_time - start_time
            report_durations[format_type] = duration

            print(f"  {format_type}格式报告: {duration:.3f}秒")

            # 验证生成成功
            assert result.get('success', False), f"{format_type}报告生成应该成功"
            if result.get('success') and result.get('file_path'):
                assert os.path.exists(result['file_path']), f"{format_type}报告文件应该存在"

        avg_report_duration = sum(report_durations.values()) / len(report_durations)

        print(f"报告生成性能:")
        print(f"  平均耗时: {avg_report_duration:.3f}秒")
        print(f"  基准要求: ≤{performance_baseline['report_generation']}秒")

        # 性能验证
        for format_type, duration in report_durations.items():
            assert duration <= performance_baseline["report_generation"], \
                f"{format_type}报告性能不达标: {duration:.3f}s > {performance_baseline['report_generation']}s"

        print("✓ 报告生成性能测试通过")

    def test_memory_usage_during_analysis(self, performance_tools, temp_workspace, performance_baseline):
        """测试分析过程中的内存使用"""
        analyzer = performance_tools["analyzer"]
        chart_generator = performance_tools["chart_generator"]

        # 监控内存使用
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        print(f"初始内存使用: {initial_memory:.1f}MB")

        # 执行多个分析任务
        memory_usage_samples = []

        for i in range(10):
            # 创建数据
            test_data = FinancialTestHelpers.create_mock_financial_data(f"内存测试公司{i+1}")

            # 财务分析
            financial_data_json = json.dumps(test_data["financial_data"])
            ratios = analyzer.calculate_ratios(financial_data_json)

            # 记录内存使用
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_usage_samples.append(current_memory)

            # 图表生成（每2次执行一次）
            if i % 2 == 0:
                chart_data = {
                    "companies": [f"公司{i+1}"],
                    "revenue": [1000],
                    "net_profit": [100]
                }
                chart_data_json = json.dumps(chart_data)
                chart_generator.generate_charts(
                    data_json=chart_data_json,
                    chart_type="comparison",
                    output_dir=temp_workspace
                )

        # 分析内存使用情况
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        peak_memory = max(memory_usage_samples)
        avg_memory = sum(memory_usage_samples) / len(memory_usage_samples)
        memory_increase = final_memory - initial_memory

        print(f"内存使用分析:")
        print(f"  初始内存: {initial_memory:.1f}MB")
        print(f"  最终内存: {final_memory:.1f}MB")
        print(f"  峰值内存: {peak_memory:.1f}MB")
        print(f"  平均内存: {avg_memory:.1f}MB")
        print(f"  内存增长: {memory_increase:.1f}MB")
        print(f"  内存基准: ≤{performance_baseline['memory_limit']}MB")

        # 内存使用验证
        assert peak_memory <= performance_baseline["memory_limit"], \
            f"内存使用超标: {peak_memory:.1f}MB > {performance_baseline['memory_limit']}MB"

        print("✓ 内存使用测试通过")

    def test_concurrent_analysis_performance(self, performance_tools, temp_workspace):
        """测试并发分析性能"""
        analyzer = performance_tools["analyzer"]

        def analyze_company(company_data):
            """单个公司的分析函数"""
            financial_data_json = json.dumps(company_data["financial_data"])
            return analyzer.calculate_ratios(financial_data_json)

        # 创建多个公司的测试数据
        companies_count = 20
        companies_data = []
        for i in range(companies_count):
            company_data = FinancialTestHelpers.create_mock_financial_data(f"并发测试公司{i+1}")
            companies_data.append(company_data)

        # 并发执行测试
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=5) as executor:
            # 提交所有任务
            futures = {executor.submit(analyze_company, data): i for i, data in enumerate(companies_data)}

            # 收集结果
            results = [None] * len(companies_data)
            for future in as_completed(futures):
                task_index = futures[future]
                try:
                    result = future.result()
                    results[task_index] = result
                except Exception as e:
                    print(f"并发任务{task_index}失败: {e}")

        end_time = time.time()
        total_duration = end_time - start_time

        # 分析结果
        successful_results = [r for r in results if r is not None and len(r) > 0]
        success_rate = len(successful_results) / companies_count * 100
        avg_per_company = total_duration / companies_count

        print(f"并发分析性能 ({companies_count}家公司, 5线程):")
        print(f"  总耗时: {total_duration:.3f}秒")
        print(f"  平均每家耗时: {avg_per_company:.3f}秒")
        print(f"  成功率: {success_rate:.1f}%")

        # 验证并发效果
        assert success_rate >= 80.0, f"并发分析成功率过低: {success_rate:.1f}%"
        assert len(successful_results) == companies_count, "所有公司都应该成功分析"

        print("✓ 并发分析性能测试通过")

    def test_stress_large_dataset(self, performance_tools, temp_workspace):
        """大数据集压力测试"""
        analyzer = performance_tools["analyzer"]

        # 创建大规模数据集
        large_dataset_size = 100
        print(f"开始大数据集压力测试 ({large_dataset_size}家公司)...")

        stress_results = []
        error_count = 0
        start_time = time.time()

        for i in range(large_dataset_size):
            try:
                # 创建大规模测试数据
                large_data = FinancialTestHelpers.create_mock_financial_data(
                    f"压力测试公司{i+1}",
                    revenue=100000 + i * 1000,  # 增加数据规模
                    assets=500000 + i * 5000
                )

                # 执行分析
                financial_data_json = json.dumps(large_data["financial_data"])
                ratios = analyzer.calculate_ratios(financial_data_json)

                stress_results.append({
                    "company_index": i,
                    "success": len(ratios) > 0,
                    "metrics_count": sum(len(dimension) for dimension in ratios.values())
                })

                if i % 20 == 0:
                    print(f"  已处理 {i+1}/{large_dataset_size}家公司")

            except Exception as e:
                error_count += 1
                if error_count <= 5:  # 只打印前5个错误
                    print(f"  处理第{i+1}家公司时出错: {e}")

        end_time = time.time()
        total_duration = end_time - start_time

        # 分析压力测试结果
        successful_stress = sum(1 for r in stress_results if r["success"])
        success_rate = successful_stress / large_dataset_size * 100
        avg_metrics = sum(r["metrics_count"] for r in stress_results if r["success"]) / successful_stress if successful_stress > 0 else 0

        print(f"大数据集压力测试结果:")
        print(f"  处理公司数量: {large_dataset_size}")
        print(f"  成功分析数量: {successful_stress}")
        print(f"  成功率: {success_rate:.1f}%")
        print(f"  错误数量: {error_count}")
        print(f"  总耗时: {total_duration:.3f}秒")
        print(f"  平均每家耗时: {total_duration/large_dataset_size:.3f}秒")
        print(f"  平均指标数量: {avg_metrics:.1f}")

        # 压力测试验证
        assert success_rate >= 80.0, f"大数据集压力测试成功率过低: {success_rate:.1f}%"
        assert error_count <= large_dataset_size * 0.05, f"错误率过高: {error_count/large_dataset_size*100:.1f}%"

        print("✓ 大数据集压力测试通过")

    def test_system_resource_limits(self, performance_tools, temp_workspace, performance_baseline):
        """测试系统资源限制"""
        import gc
        import time

        analyzer = performance_tools["analyzer"]
        chart_generator = performance_tools["chart_generator"]
        report_saver = performance_tools["report_saver"]

        process = psutil.Process()

        print("系统资源限制测试...")
        resource_samples = []

        # 持续执行任务并监控资源使用
        for cycle in range(10):
            cycle_start = time.time()

            # 执行分析任务
            test_data = FinancialTestHelpers.create_mock_financial_data(f"资源测试周期{cycle+1}")
            financial_data_json = json.dumps(test_data["financial_data"])
            ratios = analyzer.calculate_ratios(financial_data_json)

            # 执行图表生成
            chart_data = {
                "companies": [f"资源测试公司{cycle+1}"],
                "revenue": [1000 + cycle * 100],
                "net_profit": [100 + cycle * 10]
            }
            chart_data_json = json.dumps(chart_data)
            chart_generator.generate_charts(
                data_json=chart_data_json,
                chart_type="comparison",
                output_dir=temp_workspace
            )

            # 执行报告生成
            report_content = f"# 资源测试报告 {cycle+1}\n\n这是第{cycle+1}个周期的测试报告。"
            report_saver.save_report(
                content=report_content,
                filename=f"resource_test_report_{cycle+1}",
                format_type="md",
                workspace=temp_workspace
            )

            # 记录资源使用情况
            cycle_end = time.time()
            cpu_percent = process.cpu_percent()
            memory_mb = process.memory_info().rss / 1024 / 1024

            resource_samples.append({
                "cycle": cycle + 1,
                "duration": cycle_end - cycle_start,
                "cpu_percent": cpu_percent,
                "memory_mb": memory_mb
            })

            print(f"  周期{cycle+1}: CPU {cpu_percent:.1f}%, 内存 {memory_mb:.1f}MB, 耗时 {cycle_end-cycle_start:.3f}s")

            # 强制垃圾回收
            if cycle % 3 == 0:
                gc.collect()

        # 分析资源使用情况
        avg_cpu = sum(s["cpu_percent"] for s in resource_samples) / len(resource_samples)
        peak_cpu = max(s["cpu_percent"] for s in resource_samples)
        avg_memory = sum(s["memory_mb"] for s in resource_samples) / len(resource_samples)
        peak_memory = max(s["memory_mb"] for s in resource_samples)

        print(f"系统资源使用统计:")
        print(f"  平均CPU使用率: {avg_cpu:.1f}%")
        print(f"  峰值CPU使用率: {peak_cpu:.1f}%")
        print(f"  平均内存使用: {avg_memory:.1f}MB")
        print(f"  峰值内存使用: {peak_memory:.1f}MB")

        # 资源使用验证
        assert peak_cpu <= 90.0, f"CPU使用率过高: {peak_cpu:.1f}%"
        assert peak_memory <= performance_baseline["memory_limit"], \
            f"内存使用过高: {peak_memory:.1f}MB > {performance_baseline['memory_limit']}MB"

        print("✓ 系统资源限制测试通过")

    def test_performance_regression(self, performance_tools, temp_workspace, performance_baseline):
        """性能回归测试"""
        # 记录性能基准
        performance_record = {}

        print("性能回归测试...")

        # 单公司分析
        test_data = FinancialTestHelpers.create_mock_financial_data("回归测试公司")
        start_time = time.time()
        financial_data_json = json.dumps(test_data["financial_data"])
        analyzer = performance_tools["analyzer"]
        ratios = analyzer.calculate_ratios(financial_data_json)
        performance_record["single_company_analysis"] = time.time() - start_time

        # 图表生成
        chart_data = {
            "companies": ["回归测试公司"],
            "revenue": [1000],
            "net_profit": [100]
        }
        chart_data_json = json.dumps(chart_data)
        chart_generator = performance_tools["chart_generator"]
        start_time = time.time()
        chart_generator.generate_charts(
            data_json=chart_data_json,
            chart_type="comparison",
            output_dir=temp_workspace
        )
        performance_record["chart_generation"] = time.time() - start_time

        # 报告生成
        report_saver = performance_tools["report_saver"]
        start_time = time.time()
        report_saver.save_report(
            content="# 回归测试报告\n\n这是一个性能回归测试。",
            filename="regression_test_report",
            format_type="md",
            workspace=temp_workspace
        )
        performance_record["report_generation"] = time.time() - start_time

        # 输出性能记录
        print("性能测试结果:")
        for metric, duration in performance_record.items():
            benchmark = performance_baseline.get(metric.replace("_", "_"), 0)
            if benchmark > 0:
                status = "✓" if duration <= benchmark else "⚠"
                print(f"  {status} {metric}: {duration:.3f}s (基准: {benchmark}s)")
            else:
                print(f"  • {metric}: {duration:.3f}s")

        # 验证没有明显性能退化
        critical_metrics = ["single_company_analysis", "chart_generation", "report_generation"]
        for metric in critical_metrics:
            if metric in performance_baseline:
                actual = performance_record[metric]
                benchmark = performance_baseline[metric]
                # 允许20%的性能退化
                tolerance = benchmark * 0.2
                assert actual <= benchmark + tolerance, \
                    f"性能回归: {metric} 性能退化明显: {actual:.3f}s > {benchmark + tolerance:.3f}s"

        print("✓ 性能回归测试通过")


if __name__ == "__main__":
    # 运行性能测试
    pytest.main([__file__, "-v", "-s"])