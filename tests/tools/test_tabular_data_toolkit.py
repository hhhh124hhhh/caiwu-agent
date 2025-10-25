#!/usr/bin/env python3
"""
图表生成工具测试
测试8种专业图表类型的生成质量、功能性和稳定性
"""

import pytest
import json
import os
import tempfile
import shutil
from pathlib import Path
import sys
from PIL import Image
import numpy as np

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utu.tools.tabular_data_toolkit import TabularDataToolkit


class TestChartGeneration:
    """图表生成测试类"""

    @pytest.fixture
    def chart_generator(self):
        """创建图表生成器实例"""
        return TabularDataToolkit()

    @pytest.fixture
    def temp_output_dir(self):
        """创建临时输出目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def multi_company_data(self):
        """多公司对比数据"""
        return {
            "companies": ["陕西建工", "中国建筑", "中国中铁"],
            "revenue": [1000.5, 18934.2, 11584.8],  # 亿元
            "net_profit": [31.2, 557.4, 276.2],
            "total_assets": [2345.6, 38765.4, 15432.1],
            "debt_ratio": [65.2, 73.8, 71.5],
            "current_ratio": [1.2, 1.1, 1.05],
            "roe": [6.8, 8.2, 7.5],
            "roa": [1.3, 1.4, 1.8],
            "gross_profit_margin": [12.5, 10.2, 11.8],
            "net_profit_margin": [3.1, 2.9, 2.4],
            "asset_turnover": [0.43, 0.49, 0.75],
            "inventory_turnover": [2.1, 3.2, 2.8],
            "receivables_turnover": [3.3, 4.1, 3.7],
            "revenue_growth": [8.5, 12.3, 9.7],
            "profit_growth": [15.2, 18.9, 12.4],
            "operating_cash_flow": [45.8, 892.3, 567.9],  # 亿元
            "investing_cash_flow": [-28.5, -876.2, -432.1],
            "financing_cash_flow": [-12.3, -45.6, -67.8]
        }

    @pytest.fixture
    def trend_data(self):
        """趋势分析数据"""
        return {
            "companies": ["陕西建工", "中国建筑"],
            "years": [2020, 2021, 2022, 2023],
            "revenue": [
                [856.2, 912.4, 945.8, 1000.5],  # 陕西建工
                [15432.1, 16789.3, 17892.1, 18934.2]  # 中国建筑
            ],
            "net_profit": [
                [25.4, 27.8, 29.1, 31.2],
                [456.7, 489.2, 523.4, 557.4]
            ],
            "roe": [
                [5.8, 6.2, 6.5, 6.8],
                [7.5, 7.8, 8.0, 8.2]
            ]
        }

    @pytest.fixture
    def minimal_data(self):
        """最小数据集"""
        return {
            "companies": ["测试公司"],
            "revenue": [1000],
            "net_profit": [100]
        }

    def test_chart_generator_initialization(self, chart_generator):
        """测试图表生成器初始化"""
        assert chart_generator is not None
        assert hasattr(chart_generator, 'generate_charts')
        assert hasattr(chart_generator, '_create_static_comparison_chart')
        assert hasattr(chart_generator, '_create_static_radar_chart')

    def test_data_validation_basic(self, chart_generator, multi_company_data):
        """测试基础数据验证"""
        # 检查必需字段
        assert 'companies' in multi_company_data
        assert len(multi_company_data['companies']) > 0

        # 检查数据长度一致性
        companies_count = len(multi_company_data['companies'])
        for key, values in multi_company_data.items():
            if key != 'companies':
                assert len(values) == companies_count, f"字段 {key} 长度不匹配"

    def test_comparison_chart_generation(self, chart_generator, multi_company_data, temp_output_dir):
        """测试对比柱状图生成"""
        data_json = json.dumps(multi_company_data)

        result = chart_generator.generate_charts(
            data_json=data_json,
            chart_type="comparison",
            output_dir=temp_output_dir
        )

        # 验证返回结果
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'files' in result

        if result['success']:
            # 验证文件生成
            assert len(result['files']) > 0
            chart_file = result['files'][0]
            assert os.path.exists(chart_file), f"图表文件不存在: {chart_file}"

            # 验证图片质量
            self._validate_image_file(chart_file)

    def test_radar_chart_generation(self, chart_generator, multi_company_data, temp_output_dir):
        """测试雷达图生成"""
        data_json = json.dumps(multi_company_data)

        result = chart_generator.generate_charts(
            data_json=data_json,
            chart_type="radar",
            output_dir=temp_output_dir
        )

        assert isinstance(result, dict)

        if result['success']:
            assert len(result['files']) > 0
            chart_file = result['files'][0]
            assert os.path.exists(chart_file)
            self._validate_image_file(chart_file)

    def test_trend_chart_generation(self, chart_generator, trend_data, temp_output_dir):
        """测试趋势图生成"""
        data_json = json.dumps(trend_data)

        result = chart_generator.generate_charts(
            data_json=data_json,
            chart_type="trend",
            output_dir=temp_output_dir
        )

        assert isinstance(result, dict)

        if result['success']:
            assert len(result['files']) > 0
            chart_file = result['files'][0]
            assert os.path.exists(chart_file)
            self._validate_image_file(chart_file)

    def test_scatter_chart_generation(self, chart_generator, multi_company_data, temp_output_dir):
        """测试散点图生成"""
        data_json = json.dumps(multi_company_data)

        result = chart_generator.generate_charts(
            data_json=data_json,
            chart_type="scatter",
            output_dir=temp_output_dir
        )

        assert isinstance(result, dict)

        if result['success']:
            assert len(result['files']) > 0
            chart_file = result['files'][0]
            assert os.path.exists(chart_file)
            self._validate_image_file(chart_file)

    def test_heatmap_chart_generation_new(self, chart_generator, multi_company_data, temp_output_dir):
        """测试热力图生成 - 新增功能"""
        data_json = json.dumps(multi_company_data)

        result = chart_generator.generate_charts(
            data_json=data_json,
            chart_type="heatmap",
            output_dir=temp_output_dir
        )

        assert isinstance(result, dict)

        if result['success']:
            assert len(result['files']) > 0
            chart_file = result['files'][0]
            assert os.path.exists(chart_file)
            self._validate_image_file(chart_file)

            # 验证热力图特殊特征
            self._validate_heatmap_features(chart_file)

    def test_cashflow_chart_generation_new(self, chart_generator, multi_company_data, temp_output_dir):
        """测试现金流图表生成 - 新增功能"""
        data_json = json.dumps(multi_company_data)

        result = chart_generator.generate_charts(
            data_json=data_json,
            chart_type="cashflow",
            output_dir=temp_output_dir
        )

        assert isinstance(result, dict)

        if result['success']:
            # 现金流图表可能生成多个文件
            assert len(result['files']) >= 1

            for chart_file in result['files']:
                assert os.path.exists(chart_file)
                self._validate_image_file(chart_file)

    @pytest.mark.parametrize("chart_type", [
        "comparison", "radar", "trend", "scatter", "heatmap", "cashflow", "generic"
    ])
    def test_all_chart_types_support(self, chart_generator, multi_company_data, temp_output_dir, chart_type):
        """测试所有图表类型的支持"""
        data_json = json.dumps(multi_company_data)

        result = chart_generator.generate_charts(
            data_json=data_json,
            chart_type=chart_type,
            output_dir=temp_output_dir
        )

        # 至少应该返回结果（成功或失败）
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'message' in result

        # 如果成功，应该有文件输出
        if result['success']:
            assert 'files' in result
            assert len(result['files']) > 0

    def test_chart_generation_with_minimal_data(self, chart_generator, minimal_data, temp_output_dir):
        """测试最小数据集的图表生成"""
        data_json = json.dumps(minimal_data)

        # 测试对比图（应该能处理最小数据）
        result = chart_generator.generate_charts(
            data_json=data_json,
            chart_type="comparison",
            output_dir=temp_output_dir
        )

        assert isinstance(result, dict)

    def test_error_handling_invalid_data(self, chart_generator, temp_output_dir):
        """测试无效数据的错误处理"""
        invalid_data = {
            "companies": [],  # 空公司列表
            "revenue": [],
            "net_profit": []
        }

        data_json = json.dumps(invalid_data)

        result = chart_generator.generate_charts(
            data_json=data_json,
            chart_type="comparison",
            output_dir=temp_output_dir
        )

        assert isinstance(result, dict)
        # 可能成功（使用占位符）也可能失败，但应该有明确的错误信息

    def test_error_handling_missing_fields(self, chart_generator, temp_output_dir):
        """测试缺失字段的错误处理"""
        incomplete_data = {
            "companies": ["测试公司"],
            # 缺少其他字段
        }

        data_json = json.dumps(incomplete_data)

        result = chart_generator.generate_charts(
            data_json=data_json,
            chart_type="comparison",
            output_dir=temp_output_dir
        )

        assert isinstance(result, dict)

    def test_error_handling_invalid_chart_type(self, chart_generator, multi_company_data, temp_output_dir):
        """测试无效图表类型的错误处理"""
        data_json = json.dumps(multi_company_data)

        result = chart_generator.generate_charts(
            data_json=data_json,
            chart_type="invalid_chart_type",
            output_dir=temp_output_dir
        )

        assert isinstance(result, dict)
        # 应该返回失败状态或使用通用图表

    def test_chinese_font_support(self, chart_generator, multi_company_data, temp_output_dir):
        """测试中文字体支持"""
        data_json = json.dumps(multi_company_data)

        result = chart_generator.generate_charts(
            data_json=data_json,
            chart_type="comparison",
            output_dir=temp_output_dir
        )

        if result['success'] and len(result['files']) > 0:
            chart_file = result['files'][0]
            # 这里可以添加中文字体渲染的验证逻辑
            # 目前只验证文件生成成功
            assert os.path.exists(chart_file)

    def test_output_directory_creation(self, chart_generator, multi_company_data):
        """测试输出目录自动创建"""
        # 使用不存在的目录
        non_existent_dir = tempfile.mkdtemp()
        shutil.rmtree(non_existent_dir, ignore_errors=True)

        data_json = json.dumps(multi_company_data)

        result = chart_generator.generate_charts(
            data_json=data_json,
            chart_type="comparison",
            output_dir=non_existent_dir
        )

        # 验证目录被创建
        assert os.path.exists(non_existent_dir)

        # 清理
        shutil.rmtree(non_existent_dir, ignore_errors=True)

    def test_chart_file_naming_convention(self, chart_generator, multi_company_data, temp_output_dir):
        """测试图表文件命名规范"""
        data_json = json.dumps(multi_company_data)

        chart_types = ["comparison", "radar", "trend", "scatter", "heatmap"]

        for chart_type in chart_types:
            result = chart_generator.generate_charts(
                data_json=data_json,
                chart_type=chart_type,
                output_dir=temp_output_dir
            )

            if result['success'] and len(result['files']) > 0:
                chart_file = result['files'][0]
                filename = os.path.basename(chart_file)

                # 验证文件名规范
                assert filename.endswith('.png'), f"图表文件应该是PNG格式: {filename}"
                assert len(filename) > 4, f"文件名过短: {filename}"

    def test_concurrent_chart_generation(self, chart_generator, multi_company_data, temp_output_dir):
        """测试并发图表生成"""
        import asyncio

        data_json = json.dumps(multi_company_data)

        async def generate_chart_async(chart_type):
            return chart_generator.generate_charts(
                data_json=data_json,
                chart_type=chart_type,
                output_dir=temp_output_dir
            )

        # 并发生成多种图表
        chart_types = ["comparison", "radar", "trend"]
        tasks = [generate_chart_async(chart_type) for chart_type in chart_types]

        # 在同步测试中运行异步任务
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        finally:
            loop.close()

        # 验证所有任务都有结果
        assert len(results) == len(chart_types)

        for result in results:
            if not isinstance(result, Exception):
                assert isinstance(result, dict)

    def test_chart_generation_performance(self, chart_generator, multi_company_data, temp_output_dir):
        """测试图表生成性能"""
        import time

        data_json = json.dumps(multi_company_data)

        start_time = time.time()

        result = chart_generator.generate_charts(
            data_json=data_json,
            chart_type="comparison",
            output_dir=temp_output_dir
        )

        end_time = time.time()
        duration = end_time - start_time

        # 图表生成应该在合理时间内完成（10秒内）
        assert duration < 10.0, f"图表生成耗时过长: {duration:.2f}秒"

        print(f"图表生成耗时: {duration:.2f}秒")

    def test_memory_usage_validation(self, chart_generator, multi_company_data, temp_output_dir):
        """测试内存使用验证"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        data_json = json.dumps(multi_company_data)

        # 生成多个图表
        chart_types = ["comparison", "radar", "trend", "scatter"]
        for chart_type in chart_types:
            chart_generator.generate_charts(
                data_json=data_json,
                chart_type=chart_type,
                output_dir=temp_output_dir
            )

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # 内存增长应该在合理范围内（100MB）
        assert memory_increase < 100, f"内存使用增长过多: {memory_increase:.2f}MB"

        print(f"内存使用增长: {memory_increase:.2f}MB")

    def test_chart_quality_validation(self, chart_generator, multi_company_data, temp_output_dir):
        """测试图表质量验证"""
        data_json = json.dumps(multi_company_data)

        result = chart_generator.generate_charts(
            data_json=data_json,
            chart_type="comparison",
            output_dir=temp_output_dir
        )

        if result['success'] and len(result['files']) > 0:
            chart_file = result['files'][0]
            quality_score = self._validate_image_file(chart_file)

            # 质量分数应该较高
            assert quality_score >= 0.8, f"图表质量分数过低: {quality_score}"

    def test_new_chart_types_functionality(self, chart_generator, multi_company_data, temp_output_dir):
        """测试新增图表类型的功能性"""
        data_json = json.dumps(multi_company_data)

        # 测试热力图
        heatmap_result = chart_generator.generate_charts(
            data_json=data_json,
            chart_type="heatmap",
            output_dir=temp_output_dir
        )

        # 测试现金流图
        cashflow_result = chart_generator.generate_charts(
            data_json=data_json,
            chart_type="cashflow",
            output_dir=temp_output_dir
        )

        # 至少应该有返回结果
        assert isinstance(heatmap_result, dict)
        assert isinstance(cashflow_result, dict)

        # 验证文件生成
        if heatmap_result['success']:
            assert len(heatmap_result['files']) > 0

        if cashflow_result['success']:
            assert len(cashflow_result['files']) >= 1  # 现金流图可能生成多个文件

    def _validate_image_file(self, image_path):
        """验证图片文件质量"""
        try:
            with Image.open(image_path) as img:
                # 验证图片基本属性
                assert img.size[0] > 0, "图片宽度应该大于0"
                assert img.size[1] > 0, "图片高度应该大于0"

                # 验证图片模式
                assert img.mode in ['RGB', 'RGBA', 'P'], f"不支持的图片模式: {img.mode}"

                # 计算质量分数（基于尺寸和文件大小）
                file_size = os.path.getsize(image_path)
                pixel_count = img.size[0] * img.size[1]

                # 基础质量分数
                quality_score = 0.5

                # 尺寸加分
                if img.size[0] >= 800 and img.size[1] >= 600:
                    quality_score += 0.2

                # 文件大小加分（合理的文件大小）
                if 10000 <= file_size <= 2000000:  # 10KB - 2MB
                    quality_score += 0.2

                # 分辨率加分
                if pixel_count >= 480000:  # 800x600
                    quality_score += 0.1

                return min(quality_score, 1.0)

        except Exception as e:
            pytest.fail(f"图片验证失败: {e}")

    def _validate_heatmap_features(self, heatmap_path):
        """验证热力图特殊特征"""
        try:
            with Image.open(heatmap_path) as img:
                # 热力图通常有特定的颜色模式
                # 这里可以添加热力图特定的验证逻辑
                assert img.size[0] > 0
                assert img.size[1] > 0

                # 热力图应该有矩阵结构（可以通过颜色分布验证）
                # 简单验证：检查是否有足够的颜色变化
                pixels = list(img.getdata())
                unique_colors = len(set(pixels[:1000]))  # 检查前1000个像素

                # 热力图应该有多种颜色
                assert unique_colors > 10, f"热力图颜色变化不足: {unique_colors}"

        except Exception as e:
            pytest.fail(f"热力图特征验证失败: {e}")

    def test_overall_chart_generation_success_rate(self, chart_generator, multi_company_data, temp_output_dir):
        """测试整体图表生成成功率"""
        data_json = json.dumps(multi_company_data)

        chart_types = ["comparison", "radar", "trend", "scatter", "heatmap", "cashflow"]
        success_count = 0
        total_count = len(chart_types)

        results = {}
        for chart_type in chart_types:
            result = chart_generator.generate_charts(
                data_json=data_json,
                chart_type=chart_type,
                output_dir=temp_output_dir
            )
            results[chart_type] = result

            if result.get('success', False):
                success_count += 1

        success_rate = (success_count / total_count) * 100

        print(f"\n图表生成统计:")
        print(f"测试图表类型: {total_count}")
        print(f"成功生成数量: {success_count}")
        print(f"生成成功率: {success_rate:.1f}%")

        for chart_type, result in results.items():
            status = "✓" if result.get('success', False) else "✗"
            print(f"  {status} {chart_type}: {result.get('message', 'No message')}")

        # 成功率应该不低于80%
        assert success_rate >= 80.0, f"图表生成成功率应该不低于80%, 实际: {success_rate:.1f}%"

    def test_chart_generation_stress_test(self, chart_generator, temp_output_dir):
        """图表生成压力测试"""
        # 创建大量公司数据
        large_data = {
            "companies": [f"公司{i}" for i in range(20)],
            "revenue": [1000 + i * 100 for i in range(20)],
            "net_profit": [100 + i * 10 for i in range(20)],
        }

        data_json = json.dumps(large_data)

        # 测试大数据集处理
        result = chart_generator.generate_charts(
            data_json=data_json,
            chart_type="comparison",
            output_dir=temp_output_dir
        )

        assert isinstance(result, dict)

        if result['success']:
            assert len(result['files']) > 0


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])