#!/usr/bin/env python3
"""
AKShare真实数据测试
测试使用真实AKShare API获取的财务数据
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utu.tools.akshare_financial_tool import AKShareFinancialDataTool
from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer


class TestAKShareRealData:
    """AKShare真实数据测试类"""

    @pytest.fixture
    def akshare_tool(self):
        """AKShare工具实例"""
        return AKShareFinancialDataTool()

    @pytest.fixture
    def test_stocks(self):
        """测试股票列表"""
        return [
            ("600248", "陕西建工"),  # 建筑业
            ("601668", "中国建筑"),  # 建筑业
            ("000858", "五粮液"),   # 消费品
        ]

    def test_akshare_data_retrieval(self, akshare_tool, test_stocks):
        """测试AKShare数据获取"""
        for stock_code, company_name in test_stocks:
            print(f"\n=== 测试 {company_name}({stock_code}) 数据获取 ===")

            try:
                # 获取财务报表数据
                financial_reports = akshare_tool.get_financial_reports(stock_code, company_name)

                # 验证数据结构
                assert isinstance(financial_reports, dict), "财务报表应该是字典格式"
                assert len(financial_reports) > 0, "应该获取到至少一种报表"

                # 检查必需的报表类型
                expected_reports = ['income', 'balance', 'cashflow']
                available_reports = list(financial_reports.keys())

                print(f"获取到的报表类型: {available_reports}")

                # 至少应该有部分报表数据
                assert len(available_reports) > 0, f"{company_name} 应该至少有一种报表数据"

                # 验证每种报表的数据质量
                for report_type, df in financial_reports.items():
                    print(f"  {report_type} 报表: {len(df)} 行数据")

                    if not df.empty:
                        # 检查是否有数据列
                        assert len(df.columns) > 0, f"{report_type} 报表应该有数据列"

                        # 检查第一行数据（最新数据）
                        first_row = df.iloc[0]
                        non_null_count = first_row.count()

                        print(f"    最新数据有效字段数: {non_null_count}/{len(first_row)}")

                        # 至少应该有一些有效数据
                        assert non_null_count > 0, f"{report_type} 报表应该有有效数据"

                print(f"✓ {company_name} 数据获取成功")

            except Exception as e:
                pytest.fail(f"获取 {company_name}({stock_code}) 数据失败: {e}")

    def test_financial_analysis_with_real_data(self, akshare_tool, test_stocks):
        """测试使用真实数据进行财务分析"""
        analyzer = StandardFinancialAnalyzer()

        for stock_code, company_name in test_stocks:
            print(f"\n=== 测试 {company_name}({stock_code}) 财务分析 ===")

            try:
                # 获取真实财务数据
                financial_reports = akshare_tool.get_financial_reports(stock_code, company_name)

                # 转换为标准格式
                standard_data = self._convert_to_standard_format(financial_reports)

                # 计算财务指标
                ratios = analyzer.calculate_ratios(json.dumps(standard_data))

                # 验证计算结果
                assert isinstance(ratios, dict), "财务比率应该是字典格式"
                assert len(ratios) > 0, "应该计算出财务指标"

                # 检查5大维度
                expected_dimensions = ['profitability', 'solvency', 'efficiency', 'growth', 'cash_flow']
                available_dimensions = list(ratios.keys())

                print(f"分析维度: {available_dimensions}")

                # 至少应该有部分分析维度
                assert len(available_dimensions) > 0, f"{company_name} 应该至少有一个分析维度"

                # 验证指标计算
                total_metrics = sum(len(dimension) for dimension in ratios.values())
                print(f"计算出的指标数量: {total_metrics}")

                if total_metrics > 0:
                    # 检查指标值的合理性
                    for dimension, metrics in ratios.items():
                        for metric_name, value in metrics.items():
                            assert isinstance(value, (int, float)), f"指标值应该是数值: {dimension}.{metric_name}"
                            print(f"    {dimension}.{metric_name}: {value}")

                print(f"✓ {company_name} 财务分析成功")

            except Exception as e:
                pytest.fail(f"分析 {company_name}({stock_code}) 财务数据失败: {e}")

    def test_data_quality_validation(self, akshare_tool, test_stocks):
        """测试数据质量验证"""
        for stock_code, company_name in test_stocks:
            print(f"\n=== 测试 {company_name}({stock_code}) 数据质量 ===")

            try:
                financial_reports = akshare_tool.get_financial_reports(stock_code, company_name)

                quality_score = self._calculate_data_quality(financial_reports)
                print(f"数据质量评分: {quality_score:.2f}/100")

                # 数据质量应该达到基本要求
                assert quality_score >= 30.0, f"{company_name} 数据质量过低: {quality_score:.2f}"

                if quality_score >= 80.0:
                    print(f"✓ {company_name} 数据质量优秀")
                elif quality_score >= 60.0:
                    print(f"✓ {company_name} 数据质量良好")
                elif quality_score >= 40.0:
                    print(f"⚠ {company_name} 数据质量一般")
                else:
                    print(f"⚠ {company_name} 数据质量较差，但可用")

            except Exception as e:
                pytest.fail(f"验证 {company_name}({stock_code}) 数据质量失败: {e}")

    def test_multi_company_comparison(self, akshare_tool, test_stocks):
        """测试多公司对比分析"""
        print(f"\n=== 多公司对比分析测试 ===")

        analyzer = StandardFinancialAnalyzer()
        companies_data = {}

        # 获取所有公司的数据
        for stock_code, company_name in test_stocks:
            try:
                financial_reports = akshare_tool.get_financial_reports(stock_code, company_name)
                standard_data = self._convert_to_standard_format(financial_reports)
                ratios = analyzer.calculate_ratios(json.dumps(standard_data))
                companies_data[company_name] = ratios
                print(f"✓ {company_name} 数据处理完成")
            except Exception as e:
                print(f"✗ {company_name} 数据处理失败: {e}")

        # 验证对比分析数据
        assert len(companies_data) >= 2, "至少需要两家公司数据进行对比"

        print(f"\n可用于对比的公司数量: {len(companies_data)}")

        # 检查关键指标对比
        key_metrics = ['roe', 'roa', 'debt_to_asset_ratio']
        for metric in key_metrics:
            print(f"\n{metric} 对比:")
            for company_name, ratios in companies_data.items():
                value = self._find_metric_value(ratios, metric)
                if value is not None:
                    print(f"  {company_name}: {value:.2f}")

        print(f"✓ 多公司对比分析测试完成")

    def test_cache_functionality(self, akshare_tool, test_stocks):
        """测试缓存功能"""
        if len(test_stocks) == 0:
            pytest.skip("没有测试股票数据")

        stock_code, company_name = test_stocks[0]

        print(f"\n=== 测试 {company_name}({stock_code}) 缓存功能 ===")

        # 第一次获取（应该从API获取）
        import time
        start_time = time.time()
        financial_reports_1 = akshare_tool.get_financial_reports(stock_code, company_name)
        first_fetch_time = time.time() - start_time

        # 第二次获取（应该从缓存获取）
        start_time = time.time()
        financial_reports_2 = akshare_tool.get_financial_reports(stock_code, company_name)
        second_fetch_time = time.time() - start_time

        print(f"首次获取耗时: {first_fetch_time:.3f}秒")
        print(f"缓存获取耗时: {second_fetch_time:.3f}秒")

        # 验证缓存效果（第二次应该更快）
        if second_fetch_time < first_fetch_time:
            speed_improvement = (first_fetch_time - second_fetch_time) / first_fetch_time * 100
            print(f"缓存提速: {speed_improvement:.1f}%")
            assert speed_improvement > 10, "缓存应该显著提升获取速度"

        # 验证数据一致性
        assert len(financial_reports_1) == len(financial_reports_2), "缓存数据应该与原始数据一致"

        print(f"✓ {company_name} 缓存功能测试完成")

    def _convert_to_standard_format(self, financial_reports: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """将AKShare数据转换为标准格式"""

        def get_latest_value(dataframe: pd.DataFrame, column_name: str) -> float:
            """获取数据框中指定列的最新值"""
            if dataframe is None or dataframe.empty:
                return 0.0
            if column_name not in dataframe.columns:
                return 0.0
            try:
                value = dataframe.iloc[0][column_name]
                if pd.isna(value):
                    return 0.0
                return float(value)
            except (ValueError, TypeError, IndexError):
                return 0.0

        # 获取各报表数据
        income_df = financial_reports.get('income', pd.DataFrame())
        balance_df = financial_reports.get('balance', pd.DataFrame())
        cashflow_df = financial_reports.get('cashflow', pd.DataFrame())

        # 创建标准格式数据
        standard_data = {
            "income": [
                {
                    "营业收入": int(get_latest_value(income_df, '营业收入') * 10000),
                    "营业成本": int(get_latest_value(income_df, '营业成本') * 10000),
                    "净利润": int(get_latest_value(income_df, '净利润') * 10000),
                    "归属于母公司所有者的净利润": int(get_latest_value(income_df, '归属于母公司所有者的净利润') * 10000)
                }
            ],
            "balance": [
                {
                    "资产总计": int(get_latest_value(balance_df, '资产总计') * 10000),
                    "负债合计": int(get_latest_value(balance_df, '负债合计') * 10000),
                    "所有者权益合计": int(get_latest_value(balance_df, '所有者权益合计') * 10000),
                    "流动资产合计": int(get_latest_value(balance_df, '流动资产合计') * 10000),
                    "流动负债合计": int(get_latest_value(balance_df, '流动负债合计') * 10000),
                    "存货": int(get_latest_value(balance_df, '存货') * 10000),
                    "应收账款": int(get_latest_value(balance_df, '应收账款') * 10000),
                    "固定资产": int(get_latest_value(balance_df, '固定资产') * 10000),
                    "长期投资": int(get_latest_value(balance_df, '长期投资') * 10000)
                }
            ],
            "cashflow": [
                {
                    "经营活动产生的现金流量净额": int(get_latest_value(cashflow_df, '经营活动产生的现金流量净额') * 10000),
                    "投资活动现金流出小计": int(get_latest_value(cashflow_df, '投资活动现金流出小计') * 10000),
                    "分配股利、利润或偿付利息支付的现金": int(get_latest_value(cashflow_df, '分配股利、利润或偿付利息支付的现金') * 10000)
                }
            ]
        }

        return standard_data

    def _calculate_data_quality(self, financial_reports: Dict[str, pd.DataFrame]) -> float:
        """计算数据质量评分"""
        if not financial_reports:
            return 0.0

        score = 0.0
        max_score = 100.0

        # 数据完整性评分 (40分)
        expected_reports = ['income', 'balance', 'cashflow']
        available_reports = len(financial_reports)
        completeness_score = (available_reports / len(expected_reports)) * 40
        score += completeness_score

        # 数据有效性评分 (30分)
        valid_data_count = 0
        total_data_count = 0

        for report_type, df in financial_reports.items():
            if not df.empty:
                total_data_count += len(df.columns)
                first_row = df.iloc[0]
                valid_count = first_row.count()
                valid_data_count += valid_count

        if total_data_count > 0:
            validity_score = (valid_data_count / total_data_count) * 30
            score += validity_score

        # 数据量评分 (20分)
        data_volume_score = 0.0
        for report_type, df in financial_reports.items():
            if not df.empty and len(df) >= 1:
                data_volume_score += min(len(df) / 4 * 20, 20)  # 最多4年数据

        score += min(data_volume_score, 20)

        # 数据时效性评分 (10分)
        # 这里假设最新数据就是最好的
        recency_score = 10.0
        score += recency_score

        return min(score, max_score)

    def _find_metric_value(self, ratios: Dict[str, Any], metric_name: str) -> float:
        """在财务比率中查找特定指标的值"""
        for dimension, metrics in ratios.items():
            if metric_name in metrics:
                return metrics[metric_name]
        return None


if __name__ == "__main__":
    # 运行AKShare真实数据测试
    pytest.main([__file__, "-v", "-s"])