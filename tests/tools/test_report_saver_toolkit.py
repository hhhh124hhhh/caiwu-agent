#!/usr/bin/env python3
"""
报告保存工具测试
测试4种格式报告生成的完整性、可用性和质量
"""

import pytest
import json
import os
import tempfile
import shutil
from pathlib import Path
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utu.tools.report_saver_toolkit import ReportSaverToolkit


class TestReportGeneration:
    """报告生成测试类"""

    @pytest.fixture
    def report_saver(self):
        """创建报告保存器实例"""
        return ReportSaverToolkit()

    @pytest.fixture
    def temp_workspace(self):
        """创建临时工作空间"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def sample_financial_data(self):
        """示例财务数据"""
        return {
            "company_name": "陕西建工",
            "stock_code": "600248",
            "analysis_date": "2025-10-25",
            "financial_metrics": {
                "profitability": {
                    "gross_profit_margin": 20.0,
                    "net_profit_margin": 15.0,
                    "roe": 6.8,
                    "roa": 1.3
                },
                "solvency": {
                    "debt_to_asset_ratio": 65.2,
                    "current_ratio": 1.2,
                    "quick_ratio": 0.8
                },
                "efficiency": {
                    "asset_turnover": 0.43,
                    "inventory_turnover": 2.1,
                    "receivables_turnover": 3.3
                },
                "growth": {
                    "revenue_growth": 8.5,
                    "profit_growth": 15.2
                },
                "cash_flow": {
                    "operating_cash_flow": 45.8,
                    "cash_flow_ratio": 0.22,
                    "free_cash_flow": 12.3,
                    "cash_reinvestment_ratio": 4.5,
                    "cash_to_investment_ratio": 1.2
                }
            },
            "analysis_summary": {
                "overall_score": 75.5,
                "risk_level": "中等风险",
                "recommendations": [
                    "关注现金流改善",
                    "优化资产结构",
                    "提升运营效率"
                ]
            },
            "charts": [
                "comparison_chart.png",
                "radar_chart.png",
                "trend_chart.png"
            ]
        }

    @pytest.fixture
    def sample_report_content(self):
        """示例报告内容"""
        return """# 陕西建工(600248) 财务分析报告

## 执行摘要

本报告对陕西建工(600248)的财务状况进行了全面分析，包括盈利能力、偿债能力、运营效率、成长能力和现金能力五个维度。

## 财务指标分析

### 盈利能力
- **毛利率**: 20.0%
- **净利率**: 15.0%
- **净资产收益率(ROE)**: 6.8%
- **总资产收益率(ROA)**: 1.3%

### 偿债能力
- **资产负债率**: 65.2%
- **流动比率**: 1.2
- **速动比率**: 0.8

### 运营效率
- **总资产周转率**: 0.43
- **存货周转率**: 2.1
- **应收账款周转率**: 3.3

### 成长能力
- **营业收入增长率**: 8.5%
- **净利润增长率**: 15.2%

### 现金能力
- **经营活动现金流**: 45.8亿元
- **现金流量比率**: 0.22
- **自由现金流**: 12.3亿元
- **现金再投资比率**: 4.5%
- **现金投资保障比率**: 1.2

## 分析结论

综合评分为75.5分，风险等级为中等风险。建议关注现金流改善，优化资产结构，提升运营效率。

## 图表分析

![对比分析图](comparison_chart.png)
![雷达图](radar_chart.png)
![趋势图](trend_chart.png)

---
*报告生成时间: 2025-10-25*
*分析工具: Youtu-Agent Enhanced v2.0*
"""

    def test_report_saver_initialization(self, report_saver):
        """测试报告保存器初始化"""
        assert report_saver is not None
        # 检查实际存在的方法
        assert hasattr(report_saver, 'save_analysis_report')
        assert hasattr(report_saver, 'save_json_report')
        assert hasattr(report_saver, 'save_pdf_report')
        assert hasattr(report_saver, 'workspace_root')

    def test_markdown_report_generation(self, report_saver, sample_report_content, temp_workspace):
        """测试Markdown格式报告生成"""
        # 使用save_analysis_report方法
        result = report_saver.save_analysis_report(
            content=sample_report_content,
            filename="test_financial_report",
            format_type="md",
            workspace=temp_workspace
        )

        assert isinstance(result, dict)
        assert 'success' in result
        assert 'file_path' in result

        if result['success']:
            file_path = result['file_path']
            assert os.path.exists(file_path), f"报告文件不存在: {file_path}"
            assert file_path.endswith('.md'), f"文件扩展名错误: {file_path}"

            # 验证文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "陕西建工" in content
                assert "财务分析报告" in content
                assert len(content) > 100

    def test_html_report_generation(self, report_saver, sample_report_content, temp_workspace):
        """测试HTML格式报告生成"""
        result = report_saver.save_analysis_report(
            content=sample_report_content,
            filename="test_financial_report",
            format_type="html",
            workspace=temp_workspace
        )

        assert isinstance(result, dict)

        if result['success']:
            file_path = result['file_path']
            assert os.path.exists(file_path)
            assert file_path.endswith('.html')

            # 验证HTML内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "<html" in content.lower()
                assert "<body" in content.lower()
                assert "陕西建工" in content

    def test_json_report_generation(self, report_saver, sample_financial_data, temp_workspace):
        """测试JSON格式报告生成"""
        result = report_saver.save_analysis_result(
            data=sample_financial_data,
            filename="test_financial_data",
            format_type="json",
            workspace=temp_workspace
        )

        assert isinstance(result, dict)

        if result['success']:
            file_path = result['file_path']
            assert os.path.exists(file_path)
            assert file_path.endswith('.json')

            # 验证JSON内容
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert "company_name" in data
                assert "financial_metrics" in data
                assert data["company_name"] == "陕西建工"

    @pytest.mark.skipif(
        not os.environ.get('RUN_PDF_TESTS', False),
        reason="PDF测试需要特定环境，设置RUN_PDF_TESTS=1来启用"
    )
    def test_pdf_report_generation(self, report_saver, sample_report_content, temp_workspace):
        """测试PDF格式报告生成"""
        result = report_saver.save_analysis_report(
            content=sample_report_content,
            filename="test_financial_report",
            format_type="pdf",
            workspace=temp_workspace
        )

        assert isinstance(result, dict)

        if result['success']:
            file_path = result['file_path']
            assert os.path.exists(file_path)
            assert file_path.endswith('.pdf')

            # 验证PDF文件大小
            file_size = os.path.getsize(file_path)
            assert file_size > 1000, f"PDF文件过小: {file_size} bytes"

    def test_chinese_content_support(self, report_saver, temp_workspace):
        """测试中文内容支持"""
        chinese_content = """# 中文财务分析报告

## 公司概况
- 公司名称：陕西建工股份有限公司
- 股票代码：600248.SH
- 所属行业：建筑工程

## 财务指标
- 毛利率：20.0%
- 净利率：15.0%
- ROE：6.8%

## 分析结论
公司整体财务状况良好，建议继续关注现金流管理。

---
*报告生成时间：2025年10月25日*
"""

        # 测试Markdown中文支持
        result = report_saver.save_analysis_report(
            content=chinese_content,
            filename="test_chinese_report",
            format_type="md",
            workspace=temp_workspace
        )

        if result['success']:
            file_path = result['file_path']
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "陕西建工股份有限公司" in content
                assert "建筑工程" in content

    def test_structured_data_integration(self, report_saver, sample_financial_data, temp_workspace):
        """测试结构化数据集成"""
        # 生成包含财务数据的报告
        metrics = sample_financial_data['financial_metrics']

        report_content = f"""# {sample_financial_data['company_name']} 财务分析报告

## 财务指标概览

### 盈利能力
- 毛利率: {metrics['profitability']['gross_profit_margin']}%
- 净利率: {metrics['profitability']['net_profit_margin']}%
- ROE: {metrics['profitability']['roe']}%
- ROA: {metrics['profitability']['roa']}%

### 现金能力
- 经营现金流: {metrics['cash_flow']['operating_cash_flow']}亿元
- 现金流量比率: {metrics['cash_flow']['cash_flow_ratio']}
- 自由现金流: {metrics['cash_flow']['free_cash_flow']}亿元

## 分析结论
综合评分: {sample_financial_data['analysis_summary']['overall_score']}分
风险等级: {sample_financial_data['analysis_summary']['risk_level']}
"""

        result = report_saver.save_analysis_report(
            content=report_content,
            filename="test_structured_report",
            format_type="md",
            workspace=temp_workspace
        )

        if result['success']:
            file_path = result['file_path']
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "75.5分" in content
                assert "中等风险" in content
                assert "45.8亿元" in content

    def test_chart_integration_in_report(self, report_saver, temp_workspace):
        """测试图表在报告中的集成"""
        # 首先创建一些模拟图表文件
        chart_files = ["comparison_chart.png", "radar_chart.png", "trend_chart.png"]

        for chart_file in chart_files:
            chart_path = os.path.join(temp_workspace, chart_file)
            # 创建一个简单的图片文件（模拟）
            with open(chart_path, 'wb') as f:
                f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82')

        # 生成包含图表的报告
        report_with_charts = """# 财务分析报告

## 图表分析

### 对比分析图
![对比分析图](comparison_chart.png)

### 综合能力雷达图
![综合能力雷达图](radar_chart.png)

### 历史趋势图
![历史趋势图](trend_chart.png)

## 结论
基于以上图表分析，公司财务状况整体良好。
"""

        result = report_saver.save_analysis_report(
            content=report_with_charts,
            filename="test_report_with_charts",
            format_type="md",
            workspace=temp_workspace
        )

        if result['success']:
            file_path = result['file_path']
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 验证图表引用存在
                assert "comparison_chart.png" in content
                assert "radar_chart.png" in content
                assert "trend_chart.png" in content

    def test_report_format_consistency(self, report_saver, sample_report_content, temp_workspace):
        """测试报告格式一致性"""
        formats = ["md", "html", "json"]
        results = {}

        for format_type in formats:
            result = report_saver.save_analysis_report(
                content=sample_report_content,
                filename=f"test_report_consistency",
                format_type=format_type,
                workspace=temp_workspace
            )
            results[format_type] = result

        # 验证所有格式都有返回结果
        for format_type, result in results.items():
            assert isinstance(result, dict), f"{format_type} 格式应该返回字典"
            assert 'success' in result, f"{format_type} 格式应该有success字段"

    def test_error_handling_invalid_format(self, report_saver, sample_report_content, temp_workspace):
        """测试无效格式的错误处理"""
        result = report_saver.save_analysis_report(
            content=sample_report_content,
            filename="test_report",
            format_type="invalid_format",
            workspace=temp_workspace
        )

        assert isinstance(result, dict)
        # 应该返回失败状态或使用默认格式

    def test_error_handling_empty_content(self, report_saver, temp_workspace):
        """测试空内容的错误处理"""
        result = report_saver.save_analysis_report(
            content="",
            filename="test_empty_report",
            format_type="md",
            workspace=temp_workspace
        )

        assert isinstance(result, dict)

    def test_error_handling_invalid_workspace(self, report_saver, sample_report_content):
        """测试无效工作空间的错误处理"""
        invalid_workspace = "/invalid/path/that/does/not/exist"

        result = report_saver.save_analysis_report(
            content=sample_report_content,
            filename="test_report",
            format_type="md",
            workspace=invalid_workspace
        )

        assert isinstance(result, dict)

    def test_filename_sanitization(self, report_saver, sample_report_content, temp_workspace):
        """测试文件名清理"""
        # 测试包含特殊字符的文件名
        special_filename = "test@report#$%^&*()_with_special_chars"

        result = report_saver.save_analysis_report(
            content=sample_report_content,
            filename=special_filename,
            format_type="md",
            workspace=temp_workspace
        )

        if result['success']:
            file_path = result['file_path']
            assert os.path.exists(file_path)
            # 文件名应该被清理，只包含安全字符
            filename = os.path.basename(file_path)
            assert all(c.isalnum() or c in '._-' for c in filename.split('.')[0])

    def test_workspace_directory_creation(self, report_saver, sample_report_content):
        """测试工作目录自动创建"""
        # 使用不存在的目录
        non_existent_dir = tempfile.mkdtemp()
        shutil.rmtree(non_existent_dir, ignore_errors=True)

        result = report_saver.save_analysis_report(
            content=sample_report_content,
            filename="test_report",
            format_type="md",
            workspace=non_existent_dir
        )

        # 验证目录被创建
        assert os.path.exists(non_existent_dir)

        # 清理
        shutil.rmtree(non_existent_dir, ignore_errors=True)

    def test_report_overwrite_handling(self, report_saver, sample_report_content, temp_workspace):
        """测试报告覆盖处理"""
        filename = "test_overwrite_report"

        # 第一次生成报告
        result1 = report_saver.save_analysis_report(
            content=sample_report_content,
            filename=filename,
            format_type="md",
            workspace=temp_workspace
        )

        # 修改内容后再次生成
        modified_content = sample_report_content + "\n\n## 更新内容\n报告已更新。"
        result2 = report_saver.save_analysis_report(
            content=modified_content,
            filename=filename,
            format_type="md",
            workspace=temp_workspace
        )

        if result1['success'] and result2['success']:
            # 验证文件被覆盖
            file_path = result2['file_path']
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "更新内容" in content
                assert "报告已更新" in content

    def test_large_content_handling(self, report_saver, temp_workspace):
        """测试大内容处理"""
        # 生成大量内容
        large_content = "# 大型财务分析报告\n\n"

        for i in range(1000):
            large_content += f"## 第{i+1}部分\n"
            large_content += f"这是第{i+1}部分的内容，包含大量的财务数据和分析结果。\n"
            large_content += f"指标{i+1}: {i * 1.5}%\n"
            large_content += f"分析{i+1}: 这是一个详细的分析段落。\n\n"

        result = report_saver.save_analysis_report(
            content=large_content,
            filename="test_large_report",
            format_type="md",
            workspace=temp_workspace
        )

        if result['success']:
            file_path = result['file_path']
            file_size = os.path.getsize(file_path)

            # 验证文件大小合理
            assert file_size > 50000, f"大文件大小不符合预期: {file_size} bytes"

    def test_concurrent_report_generation(self, report_saver, sample_report_content, temp_workspace):
        """测试并发报告生成"""
        import asyncio
        import threading

        results = []
        errors = []

        def generate_report(thread_id):
            try:
                content = f"{sample_report_content}\n\n## 线程{thread_id}生成\n"
                result = report_saver.save_analysis_report(
                    content=content,
                    filename=f"test_concurrent_report_{thread_id}",
                    format_type="md",
                    workspace=temp_workspace
                )
                results.append((thread_id, result))
            except Exception as e:
                errors.append((thread_id, str(e)))

        # 创建多个线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=generate_report, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证结果
        assert len(errors) == 0, f"并发生成出现错误: {errors}"
        assert len(results) == 5, f"并发结果数量不正确: {len(results)}"

        for thread_id, result in results:
            assert isinstance(result, dict), f"线程{thread_id}结果格式错误"

    def test_report_file_naming_convention(self, report_saver, sample_report_content, temp_workspace):
        """测试报告文件命名规范"""
        base_filename = "test_financial_analysis_report"
        formats = ["md", "html", "json"]

        for format_type in formats:
            result = report_saver.save_analysis_report(
                content=sample_report_content,
                filename=base_filename,
                format_type=format_type,
                workspace=temp_workspace
            )

            if result['success']:
                file_path = result['file_path']
                filename = os.path.basename(file_path)

                # 验证文件名规范
                expected_extension = f".{format_type}"
                assert filename.endswith(expected_extension), f"文件扩展名错误: {filename}"

                base_name = filename[:-len(expected_extension)]
                assert base_filename in base_name, f"基础文件名不匹配: {filename}"

    def test_overall_report_generation_success_rate(self, report_saver, sample_report_content, temp_workspace):
        """测试整体报告生成成功率"""
        formats = ["md", "html", "json"]
        if os.environ.get('RUN_PDF_TESTS', False):
            formats.append("pdf")

        success_count = 0
        total_count = len(formats)
        results = {}

        for format_type in formats:
            result = report_saver.save_analysis_report(
                content=sample_report_content,
                filename="test_success_rate_report",
                format_type=format_type,
                workspace=temp_workspace
            )
            results[format_type] = result

            if result.get('success', False):
                success_count += 1

        success_rate = (success_count / total_count) * 100

        print(f"\n报告生成统计:")
        print(f"测试格式数量: {total_count}")
        print(f"成功生成数量: {success_count}")
        print(f"生成成功率: {success_rate:.1f}%")

        for format_type, result in results.items():
            status = "✓" if result.get('success', False) else "✗"
            print(f"  {status} {format_type}: {result.get('message', 'No message')}")

        # 成功率应该不低于80%
        assert success_rate >= 80.0, f"报告生成成功率应该不低于80%, 实际: {success_rate:.1f}%"

    def test_report_quality_validation(self, report_saver, sample_report_content, temp_workspace):
        """测试报告质量验证"""
        result = report_saver.save_analysis_report(
            content=sample_report_content,
            filename="test_quality_report",
            format_type="md",
            workspace=temp_workspace
        )

        if result['success']:
            file_path = result['file_path']

            # 验证文件质量
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 质量检查
            quality_score = 0.0
            max_score = 5.0

            # 1. 内容完整性 (1分)
            if len(content) > 500:
                quality_score += 1.0

            # 2. 结构化程度 (1分)
            if "##" in content and "###" in content:
                quality_score += 1.0

            # 3. 数据准确性 (1分)
            if "20.0%" in content and "陕西建工" in content:
                quality_score += 1.0

            # 4. 格式规范性 (1分)
            if content.startswith("#") and content.endswith("2025-10-25"):
                quality_score += 1.0

            # 5. 可读性 (1分)
            lines = content.split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            if len(non_empty_lines) > 20:
                quality_score += 1.0

            quality_percentage = (quality_score / max_score) * 100
            print(f"报告质量分数: {quality_percentage:.1f}%")

            # 质量分数应该不低于80%
            assert quality_percentage >= 80.0, f"报告质量分数过低: {quality_percentage:.1f}%"

    def test_template_based_report_generation(self, report_saver, sample_financial_data, temp_workspace):
        """测试基于模板的报告生成"""
        # 创建财务分析报告模板
        template_content = """# {company_name}({stock_code}) 财务分析报告

## 执行摘要

本报告生成于 {analysis_date}，对 {company_name} 进行全面财务分析。

## 财务指标概览

### 盈利能力
- 毛利率: {gross_profit_margin}%
- 净利率: {net_profit_margin}%
- ROE: {roe}%
- ROA: {roa}%

### 偿债能力
- 资产负债率: {debt_to_asset_ratio}%
- 流动比率: {current_ratio}
- 速动比率: {quick_ratio}

### 运营效率
- 总资产周转率: {asset_turnover}
- 存货周转率: {inventory_turnover}
- 应收账款周转率: {receivables_turnover}

### 成长能力
- 营业收入增长率: {revenue_growth}%
- 净利润增长率: {profit_growth}%

### 现金能力
- 经营活动现金流: {operating_cash_flow}亿元
- 现金流量比率: {cash_flow_ratio}
- 自由现金流: {free_cash_flow}亿元

## 分析结论

综合评分: {overall_score}分
风险等级: {risk_level}

### 投资建议
{recommendations}

---
*报告由 Youtu-Agent Enhanced v2.0 自动生成*
*生成时间: {analysis_date}*
"""

        # 准备模板变量
        metrics = sample_financial_data['financial_metrics']
        template_vars = {
            "company_name": sample_financial_data["company_name"],
            "stock_code": sample_financial_data["stock_code"],
            "analysis_date": sample_financial_data["analysis_date"],
            "gross_profit_margin": metrics["profitability"]["gross_profit_margin"],
            "net_profit_margin": metrics["profitability"]["net_profit_margin"],
            "roe": metrics["profitability"]["roe"],
            "roa": metrics["profitability"]["roa"],
            "debt_to_asset_ratio": metrics["solvency"]["debt_to_asset_ratio"],
            "current_ratio": metrics["solvency"]["current_ratio"],
            "quick_ratio": metrics["solvency"]["quick_ratio"],
            "asset_turnover": metrics["efficiency"]["asset_turnover"],
            "inventory_turnover": metrics["efficiency"]["inventory_turnover"],
            "receivables_turnover": metrics["efficiency"]["receivables_turnover"],
            "revenue_growth": metrics["growth"]["revenue_growth"],
            "profit_growth": metrics["growth"]["profit_growth"],
            "operating_cash_flow": metrics["cash_flow"]["operating_cash_flow"],
            "cash_flow_ratio": metrics["cash_flow"]["cash_flow_ratio"],
            "free_cash_flow": metrics["cash_flow"]["free_cash_flow"],
            "overall_score": sample_financial_data["analysis_summary"]["overall_score"],
            "risk_level": sample_financial_data["analysis_summary"]["risk_level"],
            "recommendations": "\n".join([f"- {rec}" for rec in sample_financial_data["analysis_summary"]["recommendations"]])
        }

        # 使用模板生成报告
        formatted_content = template_content.format(**template_vars)

        result = report_saver.save_analysis_report(
            content=formatted_content,
            filename="template_based_report",
            format_type="md",
            workspace=temp_workspace
        )

        if result['success']:
            file_path = result['file_path']
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 验证模板变量被正确替换
            assert "陕西建工(600248)" in content
            assert "75.5分" in content
            assert "中等风险" in content
            assert "20.0%" in content
            assert "45.8亿元" in content


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])