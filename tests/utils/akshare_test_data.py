#!/usr/bin/env python3
"""
AKShare真实财务数据获取工具
用于测试的真实财务数据获取
"""

import sys
from pathlib import Path
import pandas as pd
import json
from typing import Dict, Any, List, Optional
import time

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    print("Warning: akshare not available. Using mock data.")


class AKShareTestData:
    """AKShare真实财务数据获取类"""

    def __init__(self):
        self.cache = {}
        self.use_mock = not AKSHARE_AVAILABLE

    def get_real_financial_data(self, stock_code: str, company_name: str = None) -> Dict[str, Any]:
        """获取真实财务数据

        Args:
            stock_code: 股票代码（如 '600248'）
            company_name: 公司名称（可选）

        Returns:
            格式化的财务数据字典
        """
        if self.use_mock:
            return self._create_mock_akshare_data(stock_code, company_name)

        cache_key = f"{stock_code}_{company_name}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            # 获取股票基本信息
            stock_info = self._get_stock_info(stock_code)

            # 获取财务报表数据
            income_data = self._get_income_statement(stock_code)
            balance_data = self._get_balance_sheet(stock_code)
            cashflow_data = self._get_cash_flow_statement(stock_code)

            # 格式化数据
            formatted_data = self._format_financial_data(
                stock_info, income_data, balance_data, cashflow_data, company_name
            )

            # 缓存数据
            self.cache[cache_key] = formatted_data

            return formatted_data

        except Exception as e:
            print(f"获取{stock_code}真实数据失败: {e}")
            print("使用模拟数据代替...")
            return self._create_mock_akshare_data(stock_code, company_name)

    def _get_stock_info(self, stock_code: str) -> Dict[str, Any]:
        """获取股票基本信息"""
        try:
            # 尝试获取股票基本信息
            info = ak.stock_individual_info_em(symbol=stock_code)
            if info is not None and not info.empty:
                return {
                    "stock_code": stock_code,
                    "stock_name": info.get('股票简称', '').iloc[0] if '股票简称' in info.columns else '',
                    "industry": info.get('所属行业', '').iloc[0] if '所属行业' in info.columns else '',
                    "list_date": info.get('上市日期', '').iloc[0] if '上市日期' in info.columns else ''
                }
        except Exception as e:
            print(f"获取股票信息失败: {e}")

        # 返回基础信息
        return {
            "stock_code": stock_code,
            "stock_name": f"股票{stock_code}",
            "industry": "未知",
            "list_date": "未知"
        }

    def _get_income_statement(self, stock_code: str) -> pd.DataFrame:
        """获取利润表数据"""
        try:
            # 获取最近一期利润表
            income_data = ak.stock_financial_analysis_indicator(symbol=stock_code)
            if income_data is not None and not income_data.empty:
                return income_data
        except Exception as e:
            print(f"获取利润表失败: {e}")

        # 返回空的DataFrame
        return pd.DataFrame()

    def _get_balance_sheet(self, stock_code: str) -> pd.DataFrame:
        """获取资产负债表数据"""
        try:
            # 获取资产负债表指标
            balance_data = ak.stock_financial_analysis_indicator(symbol=stock_code)
            if balance_data is not None and not balance_data.empty:
                return balance_data
        except Exception as e:
            print(f"获取资产负债表失败: {e}")

        return pd.DataFrame()

    def _get_cash_flow_statement(self, stock_code: str) -> pd.DataFrame:
        """获取现金流量表数据"""
        try:
            # 获取现金流量表指标
            cashflow_data = ak.stock_financial_analysis_indicator(symbol=stock_code)
            if cashflow_data is not None and not cashflow_data.empty:
                return cashflow_data
        except Exception as e:
            print(f"获取现金流量表失败: {e}")

        return pd.DataFrame()

    def _format_financial_data(self, stock_info: Dict[str, Any],
                             income_data: pd.DataFrame,
                             balance_data: pd.DataFrame,
                             cashflow_data: pd.DataFrame,
                             company_name: str = None) -> Dict[str, Any]:
        """格式化财务数据为标准格式"""

        # 如果没有提供公司名称，使用股票名称
        if company_name is None:
            company_name = stock_info.get('stock_name', f'公司{stock_info["stock_code"]}')

        # 获取最新一期的数据（通常在第一行）
        latest_income = income_data.iloc[0] if not income_data.empty else pd.Series()
        latest_balance = balance_data.iloc[0] if not balance_data.empty else pd.Series()
        latest_cashflow = cashflow_data.iloc[0] if not cashflow_data.empty else pd.Series()

        # 映射AKShare字段名到标准字段名
        field_mappings = {
            # 利润表字段映射
            '营业收入': ['营业收入', '主营业务收入', 'operating_revenue', 'revenue'],
            '营业成本': ['营业成本', '主营业务成本', 'operating_cost', 'cost_of_goods_sold'],
            '净利润': ['净利润', 'net_profit', 'net_income'],
            '归属于母公司所有者的净利润': ['归属于母公司所有者的净利润', '归属母公司净利润', 'parent_net_profit'],

            # 资产负债表字段映射
            '资产总计': ['资产总计', '总资产', 'total_assets', 'total_assets_liabilities_equity'],
            '负债合计': ['负债合计', '总负债', 'total_liabilities'],
            '所有者权益合计': ['所有者权益合计', '股东权益合计', 'total_equity', 'total_shareholders_equity'],
            '流动资产合计': ['流动资产合计', '流动资产', 'total_current_assets'],
            '流动负债合计': ['流动负债合计', '流动负债', 'total_current_liabilities'],
            '存货': ['存货', 'inventory'],
            '应收账款': ['应收账款', 'accounts_receivable'],
            '固定资产': ['固定资产', 'fixed_assets'],
            '长期投资': ['长期投资', 'long_term_investments'],

            # 现金流量表字段映射
            '经营活动产生的现金流量净额': ['经营活动产生的现金流量净额', '经营活动现金流量净额', 'net_cash_flows_operating'],
            '投资活动现金流出小计': ['投资活动现金流出小计', '投资活动现金流出', 'cash_paid_for_investments'],
            '分配股利、利润或偿付利息支付的现金': ['分配股利、利润或偿付利息支付的现金', '现金股利', 'dividend_paid']
        }

        def extract_value(data_series, field_names):
            """从数据系列中提取值"""
            for field_name in field_names:
                if field_name in data_series.index and pd.notna(data_series[field_name]):
                    try:
                        # 尝试转换为数值
                        value = data_series[field_name]
                        if isinstance(value, str):
                            # 移除逗号和空格
                            value = value.replace(',', '').replace(' ', '')
                        return float(value)
                    except (ValueError, TypeError):
                        continue
            return 0.0

        # 构建标准格式数据
        formatted_data = {
            "company_info": {
                "name": company_name,
                "stock_code": stock_info["stock_code"],
                "industry": stock_info["industry"],
                "analysis_date": time.strftime('%Y-%m-%d')
            },
            "financial_data": {
                "income": [
                    {
                        "营业收入": int(extract_value(latest_income, field_mappings['营业收入']) * 100000000) if not pd.isna(latest_income.get('营业收入', 0)) else 0,
                        "营业成本": int(extract_value(latest_income, field_mappings['营业成本']) * 100000000) if not pd.isna(latest_income.get('营业成本', 0)) else 0,
                        "净利润": int(extract_value(latest_income, field_mappings['净利润']) * 100000000) if not pd.isna(latest_income.get('净利润', 0)) else 0,
                        "归属于母公司所有者的净利润": int(extract_value(latest_income, field_mappings['归属于母公司所有者的净利润']) * 100000000) if not pd.isna(latest_income.get('归属于母公司所有者的净利润', 0)) else 0
                    }
                ],
                "balance": [
                    {
                        "资产总计": int(extract_value(latest_balance, field_mappings['资产总计']) * 100000000) if not pd.isna(latest_balance.get('资产总计', 0)) else 0,
                        "负债合计": int(extract_value(latest_balance, field_mappings['负债合计']) * 100000000) if not pd.isna(latest_balance.get('负债合计', 0)) else 0,
                        "所有者权益合计": int(extract_value(latest_balance, field_mappings['所有者权益合计']) * 100000000) if not pd.isna(latest_balance.get('所有者权益合计', 0)) else 0,
                        "流动资产合计": int(extract_value(latest_balance, field_mappings['流动资产合计']) * 100000000) if not pd.isna(latest_balance.get('流动资产合计', 0)) else 0,
                        "流动负债合计": int(extract_value(latest_balance, field_mappings['流动负债合计']) * 100000000) if not pd.isna(latest_balance.get('流动负债合计', 0)) else 0,
                        "存货": int(extract_value(latest_balance, field_mappings['存货']) * 100000000) if not pd.isna(latest_balance.get('存货', 0)) else 0,
                        "应收账款": int(extract_value(latest_balance, field_mappings['应收账款']) * 100000000) if not pd.isna(latest_balance.get('应收账款', 0)) else 0,
                        "固定资产": int(extract_value(latest_balance, field_mappings['固定资产']) * 100000000) if not pd.isna(latest_balance.get('固定资产', 0)) else 0,
                        "长期投资": int(extract_value(latest_balance, field_mappings['长期投资']) * 100000000) if not pd.isna(latest_balance.get('长期投资', 0)) else 0
                    }
                ],
                "cashflow": [
                    {
                        "经营活动产生的现金流量净额": int(extract_value(latest_cashflow, field_mappings['经营活动产生的现金流量净额']) * 100000000) if not pd.isna(latest_cashflow.get('经营活动产生的现金流量净额', 0)) else 0,
                        "投资活动现金流出小计": int(extract_value(latest_cashflow, field_mappings['投资活动现金流出小计']) * 100000000) if not pd.isna(latest_cashflow.get('投资活动现金流出小计', 0)) else 0,
                        "分配股利、利润或偿付利息支付的现金": int(extract_value(latest_cashflow, field_mappings['分配股利、利润或偿付利息支付的现金']) * 100000000) if not pd.isna(latest_cashflow.get('分配股利、利润或偿付利息支付的现金', 0)) else 0
                    }
                ]
            }
        }

        return formatted_data

    def _create_mock_akshare_data(self, stock_code: str, company_name: str = None) -> Dict[str, Any]:
        """创建模拟的AKShare格式数据"""
        if company_name is None:
            company_name = f"公司{stock_code}"

        # 根据股票代码生成不同的模拟数据
        stock_hash = hash(stock_code) % 1000
        base_revenue = 50000 + stock_hash * 100  # 500亿基础上增加变化

        return {
            "company_info": {
                "name": company_name,
                "stock_code": stock_code,
                "industry": "建筑工程",
                "analysis_date": time.strftime('%Y-%m-%d')
            },
            "financial_data": {
                "income": [
                    {
                        "营业收入": int(base_revenue * 100000000),  # 转换为元
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

    def get_multi_company_real_data(self, stock_codes: List[str]) -> Dict[str, Any]:
        """获取多个公司的真实数据

        Args:
            stock_codes: 股票代码列表

        Returns:
            多公司数据字典
        """
        multi_company_data = {
            "companies": [],
            "real_data": {}
        }

        for stock_code in stock_codes:
            try:
                company_data = self.get_real_financial_data(stock_code)
                company_name = company_data["company_info"]["name"]

                multi_company_data["companies"].append(company_name)
                multi_company_data["real_data"][company_name] = company_data["financial_data"]

                print(f"✓ 获取{company_name}({stock_code})数据成功")

            except Exception as e:
                print(f"✗ 获取{stock_code}数据失败: {e}")

        return multi_company_data

    def validate_real_data_quality(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证真实数据质量

        Args:
            financial_data: 财务数据

        Returns:
            数据质量报告
        """
        quality_report = {
            "completeness": 0.0,
            "data_quality": "unknown",
            "missing_fields": [],
            "abnormal_values": [],
            "recommendations": []
        }

        # 检查数据完整性
        required_sections = ["income", "balance", "cashflow"]
        available_sections = 0

        for section in required_sections:
            if section in financial_data and financial_data[section]:
                available_sections += 1
            else:
                quality_report["missing_fields"].append(f"Missing section: {section}")

        quality_report["completeness"] = (available_sections / len(required_sections)) * 100

        # 检查关键字段
        key_fields = [
            ("income", "营业收入"),
            ("income", "净利润"),
            ("balance", "资产总计"),
            ("balance", "负债合计"),
            ("cashflow", "经营活动产生的现金流量净额")
        ]

        for section, field in key_fields:
            if section in financial_data and financial_data[section]:
                if not financial_data[section][0].get(field):
                    quality_report["missing_fields"].append(f"Missing field: {section}.{field}")

        # 数据质量评估
        if quality_report["completeness"] >= 80 and len(quality_report["missing_fields"]) == 0:
            quality_report["data_quality"] = "excellent"
        elif quality_report["completeness"] >= 60:
            quality_report["data_quality"] = "good"
        elif quality_report["completeness"] >= 40:
            quality_report["data_quality"] = "fair"
        else:
            quality_report["data_quality"] = "poor"

        # 生成建议
        if quality_report["completeness"] < 100:
            quality_report["recommendations"].append("部分财务数据缺失，建议检查数据源")

        if len(quality_report["missing_fields"]) > 3:
            quality_report["recommendations"].append("关键字段缺失较多，可能影响分析准确性")

        return quality_report


# 常用股票代码列表
COMMON_STOCK_CODES = [
    ("600248", "陕西建工"),
    ("601668", "中国建筑"),
    ("601390", "中国中铁"),
    ("600019", "宝钢股份"),
    ("000858", "五粮液"),
    ("000002", "万科A"),
    ("600519", "贵州茅台"),
    ("600036", "招商银行"),
    ("000001", "平安银行"),
    ("601398", "工商银行")
]

def create_akshare_test_stock_data():
    """创建用于测试的AKShare股票数据"""
    akshare_data = AKShareTestData()

    print("开始获取AKShare真实财务数据...")

    # 选择几个有代表性的股票进行测试
    test_stocks = [
        ("600248", "陕西建工"),  # 建筑业
        ("601668", "中国建筑"),  # 建筑业
        ("000858", "五粮液"),   # 消费品
    ]

    real_data_collection = {}

    for stock_code, company_name in test_stocks:
        try:
            print(f"正在获取 {company_name}({stock_code}) 的财务数据...")
            data = akshare_data.get_real_financial_data(stock_code, company_name)
            real_data_collection[stock_code] = data

            # 验证数据质量
            quality_report = akshare_data.validate_real_data_quality(data["financial_data"])
            print(f"  数据质量: {quality_report['data_quality']} ({quality_report['completeness']:.1f}%)")

            if quality_report["missing_fields"]:
                print(f"  缺失字段: {len(quality_report['missing_fields'])}个")

        except Exception as e:
            print(f"  获取失败: {e}")

    print(f"\n成功获取 {len(real_data_collection)} 家公司的财务数据")
    return real_data_collection

if __name__ == "__main__":
    # 测试AKShare数据获取
    print("测试AKShare财务数据获取功能...")

    # 创建数据获取器
    akshare_test = AKShareTestData()

    # 测试单个股票数据获取
    print("\n=== 测试单个股票数据获取 ===")
    data = akshare_test.get_real_financial_data("600248", "陕西建工")
    print(f"公司名称: {data['company_info']['name']}")
    print(f"股票代码: {data['company_info']['stock_code']}")
    print(f"行业: {data['company_info']['industry']}")
    print(f"数据结构: {list(data['financial_data'].keys())}")

    # 测试数据质量验证
    quality = akshare_test.validate_real_data_quality(data["financial_data"])
    print(f"数据质量: {quality['data_quality']}")
    print(f"完整性: {quality['completeness']:.1f}%")

    # 创建测试数据集合
    print("\n=== 创建测试数据集合 ===")
    test_collection = create_akshare_test_stock_data()
    print(f"测试集合包含 {len(test_collection)} 个股票数据")

    print("\nAKShare数据获取功能测试完成！")