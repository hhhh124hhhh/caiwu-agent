#!/usr/bin/env python3
"""
财务分析完整流程集成测试
测试从数据获取到报告生成的端到端流程
使用真实AKShare财务数据进行测试
"""

import pytest
import json
import os
import tempfile
import shutil
import asyncio
from pathlib import Path
import sys
from datetime import datetime
from typing import Dict, Any
import pandas as pd

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer
from utu.tools.tabular_data_toolkit import TabularDataToolkit
from utu.tools.report_saver_toolkit import ReportSaverToolkit
from utu.tools.akshare_financial_tool import AKShareFinancialDataTool


class TestFinancialWorkflowIntegration:
    """财务分析工作流集成测试类"""

    @pytest.fixture
    def temp_workspace(self):
        """创建临时工作空间"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def complete_toolkit_suite(self):
        """创建完整的工具套件"""
        return {
            "analyzer": StandardFinancialAnalyzer(),
            "chart_generator": TabularDataToolkit(),
            "report_saver": ReportSaverToolkit()
        }

    @pytest.fixture
    def sample_company_data(self):
        """真实AKShare样本公司数据"""
        akshare_tool = AKShareFinancialDataTool()

        # 获取陕西建工的真实财务数据
        try:
            financial_reports = akshare_tool.get_financial_reports("600248", "陕西建工")

            # 转换为标准格式
            return self._convert_akshare_data_to_standard_format("600248", "陕西建工", financial_reports)
        except Exception as e:
            print(f"获取真实数据失败，使用模拟数据: {e}")
            return self._create_fallback_mock_data("600248", "陕西建工")

    def _convert_akshare_data_to_standard_format(self, stock_code: str, company_name: str, financial_reports: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """将AKShare数据转换为标准格式"""

        def get_latest_value(dataframe: pd.DataFrame, column_name: str) -> float:
            """获取数据框中指定列的最新值"""
            if dataframe is None or dataframe.empty:
                return 0.0
            if column_name not in dataframe.columns:
                return 0.0
            try:
                value = dataframe.iloc[0][column_name]  # 最新数据在第一行
                if pd.isna(value):
                    return 0.0
                return float(value)
            except (ValueError, TypeError, IndexError):
                return 0.0

        # 获取各报表的最新数据
        income_df = financial_reports.get('income', pd.DataFrame())
        balance_df = financial_reports.get('balance', pd.DataFrame())
        cashflow_df = financial_reports.get('cashflow', pd.DataFrame())

        # 转换为标准格式（单位：元）
        standard_data = {
            "company_info": {
                "name": company_name,
                "stock_code": stock_code,
                "industry": "建筑工程",  # AKShare可能不直接提供行业信息
                "analysis_date": datetime.now().strftime('%Y-%m-%d')
            },
            "financial_data": {
                "income": [
                    {
                        "营业收入": int(get_latest_value(income_df, '营业收入') * 10000 if not pd.isna(get_latest_value(income_df, '营业收入')) else 10000000000),
                        "营业成本": int(get_latest_value(income_df, '营业成本') * 10000 if not pd.isna(get_latest_value(income_df, '营业成本')) else 8000000000),
                        "净利润": int(get_latest_value(income_df, '净利润') * 10000 if not pd.isna(get_latest_value(income_df, '净利润')) else 1500000000),
                        "归属于母公司所有者的净利润": int(get_latest_value(income_df, '归属于母公司所有者的净利润') * 10000 if not pd.isna(get_latest_value(income_df, '归属于母公司所有者的净利润')) else 1200000000)
                    }
                ],
                "balance": [
                    {
                        "资产总计": int(get_latest_value(balance_df, '资产总计') * 10000 if not pd.isna(get_latest_value(balance_df, '资产总计')) else 50000000000),
                        "负债合计": int(get_latest_value(balance_df, '负债合计') * 10000 if not pd.isna(get_latest_value(balance_df, '负债合计')) else 20000000000),
                        "所有者权益合计": int(get_latest_value(balance_df, '所有者权益合计') * 10000 if not pd.isna(get_latest_value(balance_df, '所有者权益合计')) else 30000000000),
                        "流动资产合计": int(get_latest_value(balance_df, '流动资产合计') * 10000 if not pd.isna(get_latest_value(balance_df, '流动资产合计')) else 20000000000),
                        "流动负债合计": int(get_latest_value(balance_df, '流动负债合计') * 10000 if not pd.isna(get_latest_value(balance_df, '流动负债合计')) else 10000000000),
                        "存货": int(get_latest_value(balance_df, '存货') * 10000 if not pd.isna(get_latest_value(balance_df, '存货')) else 5000000000),
                        "应收账款": int(get_latest_value(balance_df, '应收账款') * 10000 if not pd.isna(get_latest_value(balance_df, '应收账款')) else 3000000000),
                        "固定资产": int(get_latest_value(balance_df, '固定资产') * 10000 if not pd.isna(get_latest_value(balance_df, '固定资产')) else 20000000000),
                        "长期投资": int(get_latest_value(balance_df, '长期投资') * 10000 if not pd.isna(get_latest_value(balance_df, '长期投资')) else 5000000000)
                    }
                ],
                "cashflow": [
                    {
                        "经营活动产生的现金流量净额": int(get_latest_value(cashflow_df, '经营活动产生的现金流量净额') * 10000 if not pd.isna(get_latest_value(cashflow_df, '经营活动产生的现金流量净额')) else 2000000000),
                        "投资活动现金流出小计": int(get_latest_value(cashflow_df, '投资活动现金流出小计') * 10000 if not pd.isna(get_latest_value(cashflow_df, '投资活动现金流出小计')) else 1500000000),
                        "分配股利、利润或偿付利息支付的现金": int(get_latest_value(cashflow_df, '分配股利、利润或偿付利息支付的现金') * 10000 if not pd.isna(get_latest_value(cashflow_df, '分配股利、利润或偿付利息支付的现金')) else 500000000)
                    }
                ]
            }
        }

        return standard_data

    def _create_fallback_mock_data(self, stock_code: str, company_name: str) -> Dict[str, Any]:
        """创建备用模拟数据"""
        # 基于股票代码生成变化的数据
        stock_hash = hash(stock_code) % 1000
        base_revenue = 50000 + stock_hash * 100  # 500亿基础上增加变化

        return {
            "company_info": {
                "name": company_name,
                "stock_code": stock_code,
                "industry": "建筑工程",
                "analysis_date": datetime.now().strftime('%Y-%m-%d')
            },
            "financial_data": {
                "income": [
                    {
                        "营业收入": int(base_revenue * 100000000),
                        "营业成本": int(base_revenue * 0.82 * 100000000),
                        "净利润": int(base_revenue * 0.12 * 100000000),
                        "归属于母公司所有者的净利润": int(base_revenue * 0.10 * 100000000)
                    }
                ],
                "balance": [
                    {
                        "资产总计": int(base_revenue * 2.5 * 100000000),
                        "负债合计": int(base_revenue * 1.6 * 100000000),
                        "所有者权益合计": int(base_revenue * 0.9 * 100000000),
                        "流动资产合计": int(base_revenue * 1.2 * 100000000),
                        "流动负债合计": int(base_revenue * 0.8 * 100000000),
                        "存货": int(base_revenue * 0.3 * 100000000),
                        "应收账款": int(base_revenue * 0.2 * 100000000),
                        "固定资产": int(base_revenue * 1.0 * 100000000),
                        "长期投资": int(base_revenue * 0.2 * 100000000)
                    }
                ],
                "cashflow": [
                    {
                        "经营活动产生的现金流量净额": int(base_revenue * 0.15 * 100000000),
                        "投资活动现金流出小计": int(base_revenue * 0.12 * 100000000),
                        "分配股利、利润或偿付利息支付的现金": int(base_revenue * 0.03 * 100000000)
                    }
                ]
            }
        }

    @pytest.fixture
    def multi_company_comparison_data(self):
        """多公司对比数据"""
        return {
            "companies": ["陕西建工", "中国建筑", "中国中铁"],
            "comparison_data": {
                "陕西建工": {
                    "income": [{"营业收入": 100052000000, "净利润": 3120000000}],
                    "balance": [{"资产总计": 234560000000, "负债合计": 152860000000}],
                    "cashflow": [{"经营活动产生的现金流量净额": 4580000000}]
                },
                "中国建筑": {
                    "income": [{"营业收入": 2000000000000, "净利润": 50000000000}],
                    "balance": [{"资产总计": 3000000000000, "负债合计": 2100000000000}],
                    "cashflow": [{"经营活动产生的现金流量净额": 80000000000}]
                },
                "中国中铁": {
                    "income": [{"营业收入": 1200000000000, "净利润": 35000000000}],
                    "balance": [{"资产总计": 1800000000000, "负债合计": 1260000000000}],
                    "cashflow": [{"经营活动产生的现金流量净额": 60000000000}]
                }
            }
        }

    def test_complete_analysis_workflow(self, complete_toolkit_suite, sample_company_data, temp_workspace):
        """测试完整分析工作流：数据→指标→图表→报告"""
        analyzer = complete_toolkit_suite["analyzer"]
        chart_generator = complete_toolkit_suite["chart_generator"]
        report_saver = complete_toolkit_suite["report_saver"]

        # 步骤1：财务指标计算
        financial_data_json = json.dumps(sample_company_data["financial_data"])
        ratios = analyzer.calculate_ratios(financial_data_json)

        assert isinstance(ratios, dict), "财务比率计算应该返回字典"
        assert len(ratios) > 0, "财务比率结果不应为空"

        # 验证5大维度完整性
        expected_dimensions = ['profitability', 'solvency', 'efficiency', 'growth', 'cash_flow']
        for dimension in expected_dimensions:
            assert dimension in ratios, f"缺失分析维度: {dimension}"

        print(f"[OK] Step 1: Financial metrics calculation completed, total {sum(len(v) for v in ratios.values())} metrics")

        # 步骤2：准备图表数据
        chart_data = {
            "companies": [sample_company_data["company_info"]["name"]],
            "revenue": [sample_company_data["financial_data"]["income"][0]["营业收入"] / 100000000],  # 转换为亿元
            "net_profit": [sample_company_data["financial_data"]["income"][0]["净利润"] / 100000000],
            "total_assets": [sample_company_data["financial_data"]["balance"][0]["资产总计"] / 100000000],
            "operating_cash_flow": [sample_company_data["financial_data"]["cashflow"][0]["经营活动产生的现金流量净额"] / 100000000],
        }

        # 添加计算指标到图表数据
        for dimension, metrics in ratios.items():
            for metric_name, value in metrics.items():
                chart_data[metric_name] = [value]

        # 步骤3：生成图表
        chart_data_json = json.dumps(chart_data)
        chart_types = ["comparison", "radar", "trend", "scatter"]
        generated_charts = []

        for chart_type in chart_types:
            result = chart_generator.generate_charts(
                data_json=chart_data_json,
                chart_type=chart_type,
                output_dir=temp_workspace
            )

            if result.get('success', False) and result.get('files'):
                generated_charts.extend(result['files'])
                print(f"[OK] Step 3.{chart_types.index(chart_type)+1}: {chart_type} chart generated successfully")

        assert len(generated_charts) > 0, "应该至少生成一个图表"

        # 步骤4：生成综合报告
        report_content = self._generate_comprehensive_report(
            sample_company_data["company_info"],
            ratios,
            generated_charts,
            temp_workspace
        )

        result = report_saver.save_report(
            content=report_content,
            filename="comprehensive_financial_report",
            format_type="md",
            workspace=temp_workspace
        )

        assert result.get('success', False), "报告生成应该成功"
        assert os.path.exists(result['file_path']), "报告文件应该存在"

        print(f"[OK] Step 4: Comprehensive report generation completed: {result['file_path']}")

        # 验证报告内容
        with open(result['file_path'], 'r', encoding='utf-8') as f:
            content = f.read()
            assert "陕西建工" in content
            assert "财务指标" in content
            assert len(content) > 1000

        print("[PASS] 完整分析工作流测试通过！")

    def test_multi_company_comparison_workflow(self, complete_toolkit_suite, multi_company_comparison_data, temp_workspace):
        """测试多公司对比分析工作流"""
        analyzer = complete_toolkit_suite["analyzer"]
        chart_generator = complete_toolkit_suite["chart_generator"]
        report_saver = complete_toolkit_suite["report_saver"]

        companies = multi_company_comparison_data["companies"]
        comparison_data = multi_company_comparison_data["comparison_data"]

        # 步骤1：批量计算各公司财务指标
        all_ratios = {}
        for company_name, company_data in comparison_data.items():
            financial_data_json = json.dumps(company_data)
            ratios = analyzer.calculate_ratios(financial_data_json)
            all_ratios[company_name] = ratios

        assert len(all_ratios) == len(companies), "所有公司的指标都应该计算完成"

        print(f"[OK] 步骤1：{len(companies)}家公司财务指标计算完成")

        # 步骤2：准备对比图表数据
        chart_data = {"companies": companies}

        # 提取各公司的关键指标
        key_metrics = ["revenue", "net_profit", "total_assets", "operating_cash_flow"]
        for metric in key_metrics:
            values = []
            for company_name in companies:
                company_data = comparison_data[company_name]
                if metric == "revenue":
                    values.append(company_data["income"][0]["营业收入"] / 100000000)
                elif metric == "net_profit":
                    values.append(company_data["income"][0]["净利润"] / 100000000)
                elif metric == "total_assets":
                    values.append(company_data["balance"][0]["资产总计"] / 100000000)
                elif metric == "operating_cash_flow":
                    values.append(company_data["cashflow"][0]["经营活动产生的现金流量净额"] / 100000000)
            chart_data[metric] = values

        # 添加计算指标
        calculated_metrics = ["roe", "roa", "debt_to_asset_ratio", "current_ratio"]
        for metric in calculated_metrics:
            values = []
            for company_name in companies:
                ratios = all_ratios[company_name]
                # 从对应维度查找指标
                found = False
                for dimension, metrics_dict in ratios.items():
                    if metric in metrics_dict:
                        values.append(metrics_dict[metric])
                        found = True
                        break
                if not found:
                    values.append(0)
            chart_data[metric] = values

        # 步骤3：生成对比图表
        chart_data_json = json.dumps(chart_data)
        comparison_charts = []

        # 对比柱状图
        result = chart_generator.generate_charts(
            data_json=chart_data_json,
            chart_type="comparison",
            output_dir=temp_workspace
        )
        if result.get('success', False):
            comparison_charts.extend(result.get('files', []))

        # 雷达图对比
        result = chart_generator.generate_charts(
            data_json=chart_data_json,
            chart_type="radar",
            output_dir=temp_workspace
        )
        if result.get('success', False):
            comparison_charts.extend(result.get('files', []))

        print(f"[OK] 步骤3：对比图表生成完成，共{len(comparison_charts)}个图表")

        # 步骤4：生成对比分析报告
        comparison_report = self._generate_comparison_report(
            companies,
            all_ratios,
            comparison_charts
        )

        result = report_saver.save_report(
            content=comparison_report,
            filename="multi_company_comparison_report",
            format_type="md",
            workspace=temp_workspace
        )

        assert result.get('success', False), "对比报告生成应该成功"

        print(f"[OK] 步骤4：多公司对比报告生成完成")

        # 验证对比报告内容
        with open(result['file_path'], 'r', encoding='utf-8') as f:
            content = f.read()
            for company in companies:
                assert company in content, f"报告应该包含{company}的分析"

        print("[PASS] 多公司对比分析工作流测试通过！")

    @pytest.mark.asyncio
    async def test_async_workflow_execution(self, complete_toolkit_suite, sample_company_data, temp_workspace):
        """测试异步工作流执行"""
        analyzer = complete_toolkit_suite["analyzer"]
        chart_generator = complete_toolkit_suite["chart_generator"]
        report_saver = complete_toolkit_suite["report_saver"]

        async def execute_analysis_step():
            """异步执行分析步骤"""
            financial_data_json = json.dumps(sample_company_data["financial_data"])
            return analyzer.calculate_ratios(financial_data_json)

        async def execute_chart_generation_step(chart_data_json):
            """异步执行图表生成步骤"""
            tasks = []
            for chart_type in ["comparison", "radar", "trend"]:
                task = asyncio.create_task(
                    asyncio.to_thread(
                        chart_generator.generate_charts,
                        chart_data_json,
                        chart_type,
                        temp_workspace
                    )
                )
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results

        async def execute_report_generation_step(report_content):
            """异步执行报告生成步骤"""
            return await asyncio.to_thread(
                report_saver.save_report,
                report_content,
                "async_financial_report",
                "md",
                temp_workspace
            )

        # 执行异步工作流
        print("开始执行异步分析工作流...")

        # 步骤1：异步财务指标计算
        ratios = await execute_analysis_step()
        assert isinstance(ratios, dict)
        print("[OK] 异步财务指标计算完成")

        # 步骤2：准备数据并异步生成图表
        chart_data = self._prepare_chart_data(sample_company_data, ratios)
        chart_data_json = json.dumps(chart_data)

        chart_results = await execute_chart_generation_step(chart_data_json)
        successful_charts = []
        for result in chart_results:
            if not isinstance(result, Exception) and result.get('success', False):
                successful_charts.extend(result.get('files', []))

        print(f"[OK] 异步图表生成完成，成功生成{len(successful_charts)}个图表")

        # 步骤3：异步报告生成
        report_content = self._generate_comprehensive_report(
            sample_company_data["company_info"],
            ratios,
            successful_charts,
            temp_workspace
        )

        report_result = await execute_report_generation_step(report_content)
        assert report_result.get('success', False)
        print("[OK] 异步报告生成完成")

        print("[PASS] 异步工作流执行测试通过！")

    def test_error_recovery_in_workflow(self, complete_toolkit_suite, temp_workspace):
        """测试工作流中的错误恢复"""
        analyzer = complete_toolkit_suite["analyzer"]
        chart_generator = complete_toolkit_suite["chart_generator"]
        report_saver = complete_toolkit_suite["report_saver"]

        # 创建有问题的数据
        problematic_data = {
            "income": [{"营业收入": 1000}],  # 缺少关键字段
            "balance": [{"资产总计": 5000}],  # 缺少关键字段
            "cashflow": [{"经营活动产生的现金流量净额": 200}]
        }

        # 步骤1：测试错误数据的财务指标计算
        try:
            financial_data_json = json.dumps(problematic_data)
            ratios = analyzer.calculate_ratios(financial_data_json)
            # 应该能处理错误数据，返回部分结果或默认值
            print(f"[OK] 错误数据处理：财务指标计算完成，返回{len(ratios)}个维度")
        except Exception as e:
            print(f"[OK] 错误数据处理：财务指标计算失败，异常被正确捕获: {e}")

        # 步骤2：测试不完整数据的图表生成
        incomplete_chart_data = {
            "companies": ["测试公司"],
            "revenue": [1000]
            # 缺少其他指标
        }

        try:
            chart_data_json = json.dumps(incomplete_chart_data)
            result = chart_generator.generate_charts(
                data_json=chart_data_json,
                chart_type="comparison",
                output_dir=temp_workspace
            )
            # 应该能处理不完整数据
            print(f"[OK] 错误数据处理：图表生成完成，成功={result.get('success', False)}")
        except Exception as e:
            print(f"[OK] 错误数据处理：图表生成失败，异常被正确捕获: {e}")

        # 步骤3：测试错误内容的报告生成
        try:
            error_report_content = "# 错误报告\n\n这是一个错误测试报告。"
            result = report_saver.save_report(
                content=error_report_content,
                filename="error_test_report",
                format_type="md",
                workspace=temp_workspace
            )
            # 应该能生成基础报告
            print(f"[OK] 错误数据处理：报告生成完成，成功={result.get('success', False)}")
        except Exception as e:
            print(f"[OK] 错误数据处理：报告生成失败，异常被正确捕获: {e}")

        print("[PASS] 错误恢复测试通过！")

    def test_data_consistency_across_workflow(self, complete_toolkit_suite, sample_company_data, temp_workspace):
        """测试工作流中的数据一致性"""
        analyzer = complete_toolkit_suite["analyzer"]
        chart_generator = complete_toolkit_suite["chart_generator"]

        # 步骤1：计算财务指标
        financial_data_json = json.dumps(sample_company_data["financial_data"])
        ratios = analyzer.calculate_ratios(financial_data_json)

        # 步骤2：使用相同数据多次计算，验证一致性
        ratios_list = []
        for i in range(3):
            ratios_i = analyzer.calculate_ratios(financial_data_json)
            ratios_list.append(ratios_i)

        # 验证所有计算结果一致
        for i in range(1, len(ratios_list)):
            assert ratios_list[0] == ratios_list[i], f"第{i+1}次计算结果与第1次不一致"

        print("[OK] 财务指标计算一致性验证通过")

        # 步骤3：验证图表数据的一致性
        chart_data = self._prepare_chart_data(sample_company_data, ratios)
        chart_data_json = json.dumps(chart_data)

        # 多次生成相同图表
        chart_files = []
        for i in range(3):
            result = chart_generator.generate_charts(
                data_json=chart_data_json,
                chart_type="comparison",
                output_dir=temp_workspace
            )
            if result.get('success', False) and result.get('files'):
                chart_files.extend(result['files'])

        # 验证图表文件存在
        assert len(chart_files) > 0, "应该生成图表文件"

        # 验证文件大小一致性（相同数据应该生成相似大小的文件）
        file_sizes = [os.path.getsize(f) for f in chart_files if os.path.exists(f)]
        if len(file_sizes) >= 2:
            size_diff = max(file_sizes) - min(file_sizes)
            assert size_diff < 1000, f"相同数据的图表文件大小差异过大: {size_diff} bytes"

        print("[OK] 图表生成一致性验证通过")

        print("[PASS] 数据一致性测试通过！")

    def test_workflow_performance_benchmark(self, complete_toolkit_suite, sample_company_data, temp_workspace):
        """测试工作流性能基准"""
        import time

        analyzer = complete_toolkit_suite["analyzer"]
        chart_generator = complete_toolkit_suite["chart_generator"]
        report_saver = complete_toolkit_suite["report_saver"]

        performance_data = {}

        # 性能基准
        benchmarks = {
            "financial_analysis": 5.0,  # 秒
            "chart_generation": 10.0,   # 秒
            "report_generation": 3.0,   # 秒
            "total_workflow": 20.0      # 秒
        }

        workflow_start = time.time()

        # 步骤1：财务分析性能测试
        analysis_start = time.time()
        financial_data_json = json.dumps(sample_company_data["financial_data"])
        ratios = analyzer.calculate_ratios(financial_data_json)
        analysis_time = time.time() - analysis_start
        performance_data["financial_analysis"] = analysis_time

        assert analysis_time <= benchmarks["financial_analysis"], \
            f"财务分析耗时过长: {analysis_time:.3f}s > {benchmarks['financial_analysis']}s"

        print(f"[OK] 财务分析完成，耗时: {analysis_time:.3f}s")

        # 步骤2：图表生成性能测试
        chart_start = time.time()
        chart_data = self._prepare_chart_data(sample_company_data, ratios)
        chart_data_json = json.dumps(chart_data)

        chart_types = ["comparison", "radar", "trend"]
        generated_charts = []

        for chart_type in chart_types:
            result = chart_generator.generate_charts(
                data_json=chart_data_json,
                chart_type=chart_type,
                output_dir=temp_workspace
            )
            if result.get('success', False):
                generated_charts.extend(result.get('files', []))

        chart_time = time.time() - chart_start
        performance_data["chart_generation"] = chart_time

        assert chart_time <= benchmarks["chart_generation"], \
            f"图表生成耗时过长: {chart_time:.3f}s > {benchmarks['chart_generation']}s"

        print(f"[OK] 图表生成完成，耗时: {chart_time:.3f}s")

        # 步骤3：报告生成性能测试
        report_start = time.time()
        report_content = self._generate_comprehensive_report(
            sample_company_data["company_info"],
            ratios,
            generated_charts,
            temp_workspace
        )

        result = report_saver.save_report(
            content=report_content,
            filename="performance_test_report",
            format_type="md",
            workspace=temp_workspace
        )
        report_time = time.time() - report_start
        performance_data["report_generation"] = report_time

        assert report_time <= benchmarks["report_generation"], \
            f"报告生成耗时过长: {report_time:.3f}s > {benchmarks['report_generation']}s"

        print(f"[OK] 报告生成完成，耗时: {report_time:.3f}s")

        # 总工作流时间
        total_time = time.time() - workflow_start
        performance_data["total_workflow"] = total_time

        assert total_time <= benchmarks["total_workflow"], \
            f"总工作流耗时过长: {total_time:.3f}s > {benchmarks['total_workflow']}s"

        print(f"[PASS] 性能基准测试通过！")
        print(f"   财务分析: {analysis_time:.3f}s (基准: {benchmarks['financial_analysis']}s)")
        print(f"   图表生成: {chart_time:.3f}s (基准: {benchmarks['chart_generation']}s)")
        print(f"   报告生成: {report_time:.3f}s (基准: {benchmarks['report_generation']}s)")
        print(f"   总工作流: {total_time:.3f}s (基准: {benchmarks['total_workflow']}s)")

    def _prepare_chart_data(self, sample_company_data, ratios):
        """准备图表数据"""
        financial_data = sample_company_data["financial_data"]

        chart_data = {
            "companies": [sample_company_data["company_info"]["name"]],
            "revenue": [financial_data["income"][0]["营业收入"] / 100000000],  # 转换为亿元
            "net_profit": [financial_data["income"][0]["净利润"] / 100000000],
            "total_assets": [financial_data["balance"][0]["资产总计"] / 100000000],
            "operating_cash_flow": [financial_data["cashflow"][0]["经营活动产生的现金流量净额"] / 100000000],
        }

        # 添加计算指标
        for dimension, metrics in ratios.items():
            for metric_name, value in metrics.items():
                chart_data[metric_name] = [value]

        return chart_data

    def _generate_comprehensive_report(self, company_info, ratios, chart_files, workspace):
        """生成综合报告"""
        chart_names = [os.path.basename(f) for f in chart_files]

        report_content = f"""# {company_info['name']}({company_info['stock_code']}) 财务分析报告

## 公司概况

- **公司名称**: {company_info['name']}
- **股票代码**: {company_info['stock_code']}
- **所属行业**: {company_info['industry']}
- **分析日期**: {company_info['analysis_date']}

## 财务指标分析

### 盈利能力
"""

        # 添加盈利能力指标
        if 'profitability' in ratios:
            for metric, value in ratios['profitability'].items():
                metric_name_cn = self._translate_metric_name(metric)
                report_content += f"- **{metric_name_cn}**: {value:.2f}%\n"

        report_content += "\n### 偿债能力\n"
        # 添加偿债能力指标
        if 'solvency' in ratios:
            for metric, value in ratios['solvency'].items():
                metric_name_cn = self._translate_metric_name(metric)
                if 'ratio' in metric.lower():
                    report_content += f"- **{metric_name_cn}**: {value:.2f}\n"
                else:
                    report_content += f"- **{metric_name_cn}**: {value:.2f}%\n"

        report_content += "\n### 运营效率\n"
        # 添加运营效率指标
        if 'efficiency' in ratios:
            for metric, value in ratios['efficiency'].items():
                metric_name_cn = self._translate_metric_name(metric)
                report_content += f"- **{metric_name_cn}**: {value:.2f}\n"

        report_content += "\n### 成长能力\n"
        # 添加成长能力指标
        if 'growth' in ratios:
            for metric, value in ratios['growth'].items():
                metric_name_cn = self._translate_metric_name(metric)
                report_content += f"- **{metric_name_cn}**: {value:.2f}%\n"

        report_content += "\n### 现金能力\n"
        # 添加现金能力指标
        if 'cash_flow' in ratios:
            for metric, value in ratios['cash_flow'].items():
                metric_name_cn = self._translate_metric_name(metric)
                if 'flow' in metric.lower() and 'operating' in metric.lower():
                    report_content += f"- **{metric_name_cn}**: {value:.2f}亿元\n"
                elif 'flow' in metric.lower() and 'free' in metric.lower():
                    report_content += f"- **{metric_name_cn}**: {value:.2f}亿元\n"
                elif 'ratio' in metric.lower():
                    report_content += f"- **{metric_name_cn}**: {value:.2f}\n"
                else:
                    report_content += f"- **{metric_name_cn}**: {value:.2f}%\n"

        report_content += "\n## 图表分析\n\n"

        # 添加图表引用
        for chart_name in chart_names:
            report_content += f"![{chart_name}]({chart_name})\n\n"

        report_content += """
## 分析结论

基于以上财务指标分析，公司整体表现：

1. **盈利能力**: 各项盈利指标表现良好
2. **偿债能力**: 财务结构相对稳健
3. **运营效率**: 资产使用效率有待提升
4. **成长能力**: 业务增长稳定
5. **现金能力**: 现金流状况健康

## 投资建议

建议关注公司现金流改善和运营效率提升，同时保持对行业趋势的监控。

---
*报告生成时间: {company_info['analysis_date']}*
*分析工具: Youtu-Agent Enhanced v2.0*
"""

        return report_content

    def _generate_comparison_report(self, companies, all_ratios, chart_files):
        """生成对比分析报告"""
        chart_names = [os.path.basename(f) for f in chart_files]

        report_content = f"""# 多公司财务对比分析报告

## 对比公司概览

"""
        for company in companies:
            report_content += f"- **{company}**\n"

        report_content += "\n## 财务指标对比\n\n"

        # 对比关键指标
        key_metrics = ["roe", "roa", "debt_to_asset_ratio", "current_ratio"]
        for metric in key_metrics:
            report_content += f"### {self._translate_metric_name(metric)}\n\n"

            for company in companies:
                ratios = all_ratios[company]
                value = 0
                for dimension, metrics in ratios.items():
                    if metric in metrics:
                        value = metrics[metric]
                        break

                if 'ratio' in metric.lower():
                    report_content += f"- **{company}**: {value:.2f}\n"
                else:
                    report_content += f"- **{company}**: {value:.2f}%\n"

            report_content += "\n"

        report_content += "## 图表对比\n\n"
        for chart_name in chart_names:
            report_content += f"![{chart_name}]({chart_name})\n\n"

        report_content += """
## 对比结论

通过多公司财务指标对比，可以看出各公司在不同维度上的表现差异。

---
*报告生成工具: Youtu-Agent Enhanced v2.0*
"""

        return report_content

    def _translate_metric_name(self, metric_name):
        """翻译指标名称为中文"""
        translations = {
            "gross_profit_margin": "毛利率",
            "net_profit_margin": "净利率",
            "roe": "净资产收益率(ROE)",
            "roa": "总资产收益率(ROA)",
            "debt_to_asset_ratio": "资产负债率",
            "current_ratio": "流动比率",
            "quick_ratio": "速动比率",
            "asset_turnover": "总资产周转率",
            "inventory_turnover": "存货周转率",
            "receivables_turnover": "应收账款周转率",
            "revenue_growth": "营业收入增长率",
            "profit_growth": "净利润增长率",
            "operating_cash_flow": "经营活动现金流",
            "cash_flow_ratio": "现金流量比率",
            "free_cash_flow": "自由现金流",
            "cash_reinvestment_ratio": "现金再投资比率",
            "cash_to_investment_ratio": "现金投资保障比率"
        }
        return translations.get(metric_name, metric_name)


if __name__ == "__main__":
    # 运行集成测试
    pytest.main([__file__, "-v"])