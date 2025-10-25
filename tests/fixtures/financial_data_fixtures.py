#!/usr/bin/env python3
"""
财务测试数据fixtures
提供各种测试场景的标准化财务数据
"""

import pytest
import json
import pandas as pd
from typing import Dict, Any, List


class FinancialDataFixtures:
    """财务测试数据管理类"""

    @staticmethod
    def create_perfect_financial_data(company_name: str = "测试公司", **kwargs) -> Dict[str, Any]:
        """创建完美的标准财务数据"""
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
            if key in data:
                if isinstance(data[key], list) and len(data[key]) > 0:
                    data[key][0].update(value)
                else:
                    data[key] = value
            else:
                data[key] = value

        return data

    @staticmethod
    def create_multi_company_data(companies: List[str] = None, **kwargs) -> Dict[str, Any]:
        """创建多公司对比数据"""
        if companies is None:
            companies = ["公司A", "公司B", "公司C"]

        base_values = {
            "revenue": [10000, 15000, 12000],  # 亿元
            "net_profit": [1000, 1800, 1500],
            "total_assets": [50000, 60000, 55000],
            "debt_ratio": [40.0, 45.0, 42.0],
            "current_ratio": [1.5, 1.8, 1.6],
            "roe": [8.0, 10.0, 9.0],
            "roa": [2.0, 3.0, 2.7],
            "gross_profit_margin": [20.0, 18.0, 19.0],
            "net_profit_margin": [10.0, 12.0, 12.5],
            "asset_turnover": [0.5, 0.6, 0.55],
            "inventory_turnover": [3.0, 4.0, 3.5],
            "receivables_turnover": [4.0, 5.0, 4.5],
            "revenue_growth": [10.0, 15.0, 12.0],
            "profit_growth": [12.0, 18.0, 15.0],
            "operating_cash_flow": [2000, 3000, 2500],  # 亿元
            "investing_cash_flow": [-1500, -2000, -1800],
            "financing_cash_flow": [-500, -800, -600]
        }

        data = {"companies": companies}

        # 为每个指标生成数据
        for metric, values in base_values.items():
            if metric in kwargs:
                data[metric] = kwargs[metric]
            else:
                # 根据公司数量调整数据
                if len(companies) != len(values):
                    # 重新生成合适长度的数据
                    data[metric] = [values[i % len(values)] * (1 + 0.1 * i) for i in range(len(companies))]
                else:
                    data[metric] = values[:len(companies)]

        return data

    @staticmethod
    def create_multi_period_data(years: List[int] = None, **kwargs) -> Dict[str, Any]:
        """创建多期时间序列数据"""
        if years is None:
            years = [2020, 2021, 2022, 2023]

        num_periods = len(years)

        # 基础增长趋势
        growth_rates = {
            "revenue_growth": 0.10,  # 10%年增长
            "profit_growth": 0.12,   # 12%年增长
            "asset_growth": 0.08     # 8%年增长
        }

        # 初始值
        initial_values = {
            "revenue": 8000,      # 亿元
            "cost": 6400,
            "net_profit": 800,
            "parent_net_profit": 750,
            "total_assets": 40000,
            "total_liabilities": 16000,
            "total_equity": 24000,
            "current_assets": 16000,
            "current_liabilities": 8000,
            "inventory": 4000,
            "receivables": 2400,
            "fixed_assets": 16000,
            "long_investment": 4000,
            "operating_cash_flow": 1600,
            "investing_cash_outflow": 1200,
            "dividend_payment": 400
        }

        data = {"income": [], "balance": [], "cashflow": []}

        for i, year in enumerate(years):
            # 计算当期值（考虑增长）
            multiplier = (1 + growth_rates["revenue_growth"]) ** i
            revenue = initial_values["revenue"] * multiplier
            cost = initial_values["cost"] * multiplier
            net_profit = initial_values["net_profit"] * (1 + growth_rates["profit_growth"]) ** i
            parent_net_profit = initial_values["parent_net_profit"] * (1 + growth_rates["profit_growth"]) ** i

            data["income"].append({
                "营业收入": int(revenue * 100000000),  # 转换为元
                "营业成本": int(cost * 100000000),
                "净利润": int(net_profit * 100000000),
                "归属于母公司所有者的净利润": int(parent_net_profit * 100000000)
            })

            # 资产负债表数据
            asset_multiplier = (1 + growth_rates["asset_growth"]) ** i
            total_assets = initial_values["total_assets"] * asset_multiplier
            total_liabilities = initial_values["total_liabilities"] * asset_multiplier
            total_equity = initial_values["total_equity"] * asset_multiplier

            data["balance"].append({
                "资产总计": int(total_assets * 100000000),
                "负债合计": int(total_liabilities * 100000000),
                "所有者权益合计": int(total_equity * 100000000),
                "流动资产合计": int(initial_values["current_assets"] * asset_multiplier * 100000000),
                "流动负债合计": int(initial_values["current_liabilities"] * asset_multiplier * 100000000),
                "存货": int(initial_values["inventory"] * asset_multiplier * 100000000),
                "应收账款": int(initial_values["receivables"] * asset_multiplier * 100000000),
                "固定资产": int(initial_values["fixed_assets"] * asset_multiplier * 100000000),
                "长期投资": int(initial_values["long_investment"] * asset_multiplier * 100000000)
            })

            # 现金流量表数据
            cash_multiplier = multiplier
            data["cashflow"].append({
                "经营活动产生的现金流量净额": int(initial_values["operating_cash_flow"] * cash_multiplier * 100000000),
                "投资活动现金流出小计": int(initial_values["investing_cash_outflow"] * cash_multiplier * 100000000),
                "分配股利、利润或偿付利息支付的现金": int(initial_values["dividend_payment"] * cash_multiplier * 100000000)
            })

        return data

    @staticmethod
    def create_partial_missing_data(missing_fields: List[str] = None) -> Dict[str, Any]:
        """创建部分字段缺失的数据"""
        if missing_fields is None:
            missing_fields = ["应收账款", "长期投资"]

        data = FinancialDataFixtures.create_perfect_financial_data()

        # 删除指定字段
        for field in missing_fields:
            if field in data["balance"][0]:
                del data["balance"][0][field]

        return data

    @staticmethod
    def create_abnormal_data(abnormal_settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """创建包含异常值的数据"""
        if abnormal_settings is None:
            abnormal_settings = {
                "超低毛利率": True,
                "超高负债率": True,
                "负现金流": True,
                "零值字段": True
            }

        data = FinancialDataFixtures.create_perfect_financial_data()

        if abnormal_settings.get("超低毛利率", False):
            # 设置异常低的毛利率
            data["income"][0]["营业成本"] = data["income"][0]["营业收入"] * 0.95  # 95%成本

        if abnormal_settings.get("超高负债率", False):
            # 设置异常高的负债率
            data["balance"][0]["负债合计"] = data["balance"][0]["资产总计"] * 0.95  # 95%负债

        if abnormal_settings.get("负现金流", False):
            # 设置负的现金流
            data["cashflow"][0]["经营活动产生的现金流量净额"] = -500000000  # -5亿

        if abnormal_settings.get("零值字段", False):
            # 设置一些字段为零
            data["income"][0]["净利润"] = 0
            data["balance"][0]["存货"] = 0

        return data

    @staticmethod
    def create_industry_specific_data(industry: str = "construction") -> Dict[str, Any]:
        """创建行业特定数据"""
        industry_profiles = {
            "construction": {
                "characteristics": {
                    "资产周转率": (0.3, 0.8),  # 范围
                    "资产负债率": (60, 85),     # 百分比范围
                    "毛利率": (8, 25),          # 百分比范围
                    "应收账款周转率": (2, 6)    # 范围
                },
                "name": "建筑业"
            },
            "technology": {
                "characteristics": {
                    "资产周转率": (0.8, 2.0),
                    "资产负债率": (20, 50),
                    "毛利率": (40, 80),
                    "应收账款周转率": (4, 12)
                },
                "name": "科技业"
            },
            "manufacturing": {
                "characteristics": {
                    "资产周转率": (0.5, 1.5),
                    "资产负债率": (40, 70),
                    "毛利率": (15, 35),
                    "应收账款周转率": (3, 8)
                },
                "name": "制造业"
            },
            "finance": {
                "characteristics": {
                    "资产周转率": (0.05, 0.15),
                    "资产负债率": (80, 95),
                    "毛利率": (20, 40),
                    "应收账款周转率": (1, 4)
                },
                "name": "金融业"
            }
        }

        if industry not in industry_profiles:
            industry = "construction"

        profile = industry_profiles[industry]
        characteristics = profile["characteristics"]

        # 根据行业特征生成数据
        data = FinancialDataFixtures.create_perfect_financial_data()

        # 调整指标以符合行业特征
        # 这里可以添加更复杂的行业特定逻辑

        return data

    @staticmethod
    def create_edge_case_data(edge_case_type: str = "minimal") -> Dict[str, Any]:
        """创建边界情况数据"""
        if edge_case_type == "minimal":
            # 最小有效数据
            return {
                "income": [{"营业收入": 1000, "净利润": 100}],
                "balance": [{"资产总计": 5000, "负债合计": 2000}],
                "cashflow": [{"经营活动产生的现金流量净额": 200}]
            }

        elif edge_case_type == "single_period":
            # 单期数据
            return FinancialDataFixtures.create_perfect_financial_data()

        elif edge_case_type == "large_scale":
            # 大规模数据
            return FinancialDataFixtures.create_perfect_financial_data(
                income=[{
                    "营业收入": 100000000000,  # 1000亿
                    "营业成本": 80000000000,   # 800亿
                    "净利润": 15000000000,     # 150亿
                }],
                balance=[{
                    "资产总计": 500000000000,  # 5000亿
                    "负债合计": 200000000000,  # 2000亿
                }]
            )

        else:
            return FinancialDataFixtures.create_perfect_financial_data()

    @staticmethod
    def create_real_world_sample_data() -> Dict[str, Any]:
        """创建真实世界样本数据（基于实际A股公司特征）"""
        # 模拟陕西建工类型的建筑公司数据
        return {
            "income": [
                {
                    "营业收入": 100052000000,  # 1000.52亿
                    "营业成本": 88043000000,   # 880.43亿
                    "净利润": 3120000000,      # 31.2亿
                    "归属于母公司所有者的净利润": 2890000000  # 28.9亿
                }
            ],
            "balance": [
                {
                    "资产总计": 234560000000,  # 2345.6亿
                    "负债合计": 152860000000,  # 1528.6亿
                    "所有者权益合计": 81700000000,   # 817亿
                    "流动资产合计": 156780000000,    # 1567.8亿
                    "流动负债合计": 112340000000,    # 1123.4亿
                    "存货": 67890000000,   # 678.9亿
                    "应收账款": 23450000000,  # 234.5亿
                    "固定资产": 45670000000,  # 456.7亿
                    "长期投资": 12340000000   # 123.4亿
                }
            ],
            "cashflow": [
                {
                    "经营活动产生的现金流量净额": 4580000000,   # 45.8亿
                    "投资活动现金流出小计": 2850000000,     # 28.5亿
                    "分配股利、利润或偿付利息支付的现金": 1230000000  # 12.3亿
                }
            ]
        }


# Pytest fixtures
@pytest.fixture
def perfect_financial_data():
    """完美的标准财务数据fixture"""
    return FinancialDataFixtures.create_perfect_financial_data()


@pytest.fixture
def multi_company_data():
    """多公司对比数据fixture"""
    return FinancialDataFixtures.create_multi_company_data()


@pytest.fixture
def multi_period_data():
    """多期时间序列数据fixture"""
    return FinancialDataFixtures.create_multi_period_data()


@pytest.fixture
def partial_missing_data():
    """部分字段缺失数据fixture"""
    return FinancialDataFixtures.create_partial_missing_data()


@pytest.fixture
def abnormal_data():
    """异常值数据fixture"""
    return FinancialDataFixtures.create_abnormal_data()


@pytest.fixture
def construction_industry_data():
    """建筑业数据fixture"""
    return FinancialDataFixtures.create_industry_specific_data("construction")


@pytest.fixture
def technology_industry_data():
    """科技业数据fixture"""
    return FinancialDataFixtures.create_industry_specific_data("technology")


@pytest.fixture
def minimal_data():
    """最小有效数据fixture"""
    return FinancialDataFixtures.create_edge_case_data("minimal")


@pytest.fixture
def large_scale_data():
    """大规模数据fixture"""
    return FinancialDataFixtures.create_edge_case_data("large_scale")


@pytest.fixture
def real_world_sample_data():
    """真实世界样本数据fixture"""
    return FinancialDataFixtures.create_real_world_sample_data()


@pytest.fixture
def json_perfect_data(perfect_financial_data):
    """JSON格式的完美数据fixture"""
    return json.dumps(perfect_financial_data)


@pytest.fixture
def json_multi_company_data(multi_company_data):
    """JSON格式的多公司数据fixture"""
    return json.dumps(multi_company_data)


@pytest.fixture
def json_multi_period_data(multi_period_data):
    """JSON格式的多期数据fixture"""
    return json.dumps(multi_period_data)


class TestDataValidation:
    """测试数据验证工具类"""

    @staticmethod
    def validate_financial_data_structure(data: Dict[str, Any]) -> bool:
        """验证财务数据结构"""
        required_sections = ["income", "balance", "cashflow"]
        for section in required_sections:
            if section not in data:
                return False
            if not isinstance(data[section], list) or len(data[section]) == 0:
                return False

        return True

    @staticmethod
    def validate_metric_ranges(calculated_metrics: Dict[str, Any],
                               expected_ranges: Dict[str, tuple]) -> Dict[str, bool]:
        """验证指标范围"""
        validation_results = {}

        for metric_name, (min_val, max_val) in expected_ranges.items():
            if metric_name in calculated_metrics:
                value = calculated_metrics[metric_name]
                validation_results[metric_name] = min_val <= value <= max_val
            else:
                validation_results[metric_name] = False

        return validation_results

    @staticmethod
    def create_benchmark_data():
        """创建基准测试数据"""
        return {
            "companies": ["基准公司A", "基准公司B", "基准公司C"],
            "revenue": [10000, 15000, 12000],
            "net_profit": [1000, 1800, 1500],
            "total_assets": [50000, 60000, 55000],
            "current_ratio": [1.5, 2.0, 1.8],
            "roe": [15.0, 18.0, 16.5],
            "debt_ratio": [40.0, 35.0, 38.0],
            "operating_cash_flow": [2000, 3000, 2500]
        }


if __name__ == "__main__":
    # 测试fixtures功能
    print("测试财务数据fixtures...")

    # 测试完美数据
    perfect_data = FinancialDataFixtures.create_perfect_financial_data()
    print(f"完美数据结构验证: {TestDataValidation.validate_financial_data_structure(perfect_data)}")

    # 测试多公司数据
    multi_data = FinancialDataFixtures.create_multi_company_data()
    print(f"多公司数据公司数量: {len(multi_data['companies'])}")

    # 测试多期数据
    period_data = FinancialDataFixtures.create_multi_period_data([2020, 2021, 2022])
    print(f"多期数据年份数量: {len(period_data['income'])}")

    print("Fixtures测试完成！")