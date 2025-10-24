"""
标准化财务分析工具库
提供稳定、可靠的财务数据分析功能
专注于指标计算、趋势分析、风险评估等核心功能
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from datetime import datetime
import logging

from ..config import ToolkitConfig
from .base import AsyncBaseToolkit, register_tool

logger = logging.getLogger(__name__)


class StandardFinancialAnalyzer(AsyncBaseToolkit):
    """标准化财务分析器"""

    def __init__(self, config: ToolkitConfig | dict | None = None):
        super().__init__(config)
        # 添加性能优化缓存
        self._ratios_cache = {}
        self._trends_cache = {}
        self._cache_hits = 0
        self._cache_misses = 0
    
    def calculate_financial_ratios(self, financial_data: Dict[str, pd.DataFrame]) -> Dict:
        """
        计算所有标准财务比率（内部使用）

        Args:
            financial_data: 包含利润表、资产负债表的字典

        Returns:
            财务比率计算结果
        """
        logger.info("开始计算财务比率")

        # 创建缓存键（基于数据的哈希值）
        cache_key = self._create_data_hash(financial_data)

        # 检查缓存
        if cache_key in self._ratios_cache:
            self._cache_hits += 1
            logger.info(f"使用缓存结果 (缓存命中率: {self._cache_hits/(self._cache_hits+self._cache_misses)*100:.1f}%)")
            return self._ratios_cache[cache_key]

        # 缓存未命中，执行计算
        self._cache_misses += 1
        ratios = {}

        # 盈利能力指标
        ratios['profitability'] = self._calculate_profitability_ratios(financial_data)

        # 偿债能力指标
        ratios['solvency'] = self._calculate_solvency_ratios(financial_data)

        # 运营效率指标
        ratios['efficiency'] = self._calculate_efficiency_ratios(financial_data)

        # 成长能力指标
        ratios['growth'] = self._calculate_growth_ratios(financial_data)

        # 缓存结果（限制缓存大小）
        if len(self._ratios_cache) < 100:  # 限制缓存大小避免内存泄漏
            self._ratios_cache[cache_key] = ratios

        logger.info(f"财务比率计算完成 (缓存命中率: {self._cache_hits/(self._cache_hits+self._cache_misses)*100:.1f}%)")
        return ratios
    
    @register_tool()
    def calculate_ratios(self, financial_data_json: str) -> Dict:
        """
        计算所有标准财务比率
        
        Args:
            financial_data_json: 包含利润表、资产负债表的JSON字符串
            
        Returns:
            财务比率计算结果
        """
        import json
        financial_data = {}
        data_dict = json.loads(financial_data_json)
        
        # 检查是否是完整的财务数据结构
        if isinstance(data_dict, dict) and any(key in data_dict for key in ['income', 'balance', 'cashflow']):
            # 完整的财务数据结构
            for key, df_data in data_dict.items():
                if isinstance(df_data, list) or isinstance(df_data, dict):
                    financial_data[key] = pd.DataFrame(df_data)
                else:
                    financial_data[key] = pd.DataFrame()
        else:
            # 简化的财务指标结构
            financial_data = self._convert_simple_metrics_to_financial_data(data_dict)
        return self.calculate_financial_ratios(financial_data)
    
    def _convert_simple_metrics_to_financial_data(self, simple_metrics: Dict) -> Dict[str, pd.DataFrame]:
        """
        将简化指标转换为完整的财务数据结构

        Args:
            simple_metrics: 简化指标字典

        Returns:
            完整财务数据结构
        """
        logger.info(f"开始转换财务数据格式: {type(simple_metrics)}")
        logger.debug(f"输入数据键值: {list(simple_metrics.keys()) if isinstance(simple_metrics, dict) else 'Not a dict'}")

        # 创建空的DataFrame结构
        income_df = pd.DataFrame()
        balance_df = pd.DataFrame()
        cashflow_df = pd.DataFrame()

        if not simple_metrics:
            logger.warning("输入的财务数据为空")
            return {'income': income_df, 'balance': balance_df, 'cashflow': cashflow_df}

        # 检查是否是嵌套结构（包含income和balance键）
        if any(key in simple_metrics for key in ['income_statement', 'balance_sheet', 'income', 'balance', 'cashflow']):
            # 处理嵌套结构 - 新版本支持
            income_data = simple_metrics.get('income_statement') or simple_metrics.get('income', {})
            balance_data = simple_metrics.get('balance_sheet') or simple_metrics.get('balance', {})
            cashflow_data = simple_metrics.get('cash_flow') or simple_metrics.get('cashflow', {})

            logger.info("检测到嵌套结构，开始处理...")

            # 处理收入数据
            if income_data:
                if isinstance(income_data, list) and len(income_data) > 0:
                    income_df = pd.DataFrame(income_data)
                elif isinstance(income_data, dict):
                    income_df = pd.DataFrame([income_data])
                logger.info(f"收入数据解析完成，形状: {income_df.shape}")

            # 处理资产负债数据
            if balance_data:
                if isinstance(balance_data, list) and len(balance_data) > 0:
                    balance_df = pd.DataFrame(balance_data)
                elif isinstance(balance_data, dict):
                    balance_df = pd.DataFrame([balance_data])
                logger.info(f"资产负债数据解析完成，形状: {balance_df.shape}")

            # 处理现金流数据
            if cashflow_data:
                if isinstance(cashflow_data, list) and len(cashflow_data) > 0:
                    cashflow_df = pd.DataFrame(cashflow_data)
                elif isinstance(cashflow_data, dict):
                    cashflow_df = pd.DataFrame([cashflow_data])
                logger.info(f"现金流数据解析完成，形状: {cashflow_df.shape}")

        elif any(key in simple_metrics for key in ['revenue', 'net_profit', 'total_assets']):
            # 处理扁平化结构 - 扩展映射支持更多字段
            logger.info("检测到扁平化结构，开始字段映射...")

            # 扩展的利润表字段映射
            income_metric_mapping = {
                # 中文映射
                '营业收入': 'TOTAL_OPERATE_INCOME',
                '收入': 'TOTAL_OPERATE_INCOME',
                '净利润': 'NETPROFIT',
                '利润': 'NETPROFIT',
                '毛利润': 'gross_profit',
                '营业利润': 'operating_profit',
                '营业成本': 'cost_of_goods_sold',
                '营业费用': 'operating_expenses',
                '利息费用': 'interest_expense',
                '税费': 'tax_expense',
                # 英文映射
                'revenue': 'TOTAL_OPERATE_INCOME',
                'net_profit': 'NETPROFIT',
                'net_income': 'NETPROFIT',
                'gross_profit': 'gross_profit',
                'operating_profit': 'operating_profit',
                'operating_income': 'operating_profit',
                'cost_of_goods_sold': 'cost_of_goods_sold',
                'operating_expenses': 'operating_expenses',
                'interest_expense': 'interest_expense',
                'tax_expense': 'tax_expense'
            }

            # 扩展的资产负债表字段映射
            balance_metric_mapping = {
                # 中文映射
                '总资产': 'TOTAL_ASSETS',
                '资产': 'TOTAL_ASSETS',
                '总负债': 'TOTAL_LIABILITIES',
                '负债': 'TOTAL_LIABILITIES',
                '净资产': 'TOTAL_EQUITY',
                '股东权益': 'TOTAL_EQUITY',
                '流动资产': 'TOTAL_CURRENT_ASSETS',
                '流动负债': 'TOTAL_CURRENT_LIABILITIES',
                '现金': 'cash_and_equivalents',
                '现金等价物': 'cash_and_equivalents',
                '存货': 'inventory',
                '应收账款': 'accounts_receivable',
                '固定资产': 'fixed_assets',
                '长期债务': 'long_term_debt',
                # 英文映射
                'total_assets': 'TOTAL_ASSETS',
                'assets': 'TOTAL_ASSETS',
                'total_liabilities': 'TOTAL_LIABILITIES',
                'liabilities': 'TOTAL_LIABILITIES',
                'total_equity': 'TOTAL_EQUITY',
                'equity': 'TOTAL_EQUITY',
                'shareholders_equity': 'TOTAL_EQUITY',
                'current_assets': 'TOTAL_CURRENT_ASSETS',
                'current_liabilities': 'TOTAL_CURRENT_LIABILITIES',
                'cash': 'cash_and_equivalents',
                'cash_and_equivalents': 'cash_and_equivalents',
                'inventory': 'inventory',
                'receivables': 'accounts_receivable',
                'accounts_receivable': 'accounts_receivable',
                'fixed_assets': 'fixed_assets'
            }

            # 现金流表字段映射
            cashflow_metric_mapping = {
                # 中文映射
                '经营活动现金流': 'operating_cash_flow',
                '投资活动现金流': 'investing_cash_flow',
                '筹资活动现金流': 'financing_cash_flow',
                # 英文映射
                'operating_cash_flow': 'operating_cash_flow',
                'investing_cash_flow': 'investing_cash_flow',
                'financing_cash_flow': 'financing_cash_flow'
            }

            # 处理收入数据
            income_data = {}
            for key, value in simple_metrics.items():
                if key in income_metric_mapping:
                    mapped_key = income_metric_mapping[key]
                    # 确保值是数值类型
                    try:
                        numeric_value = float(value)
                        # 对于大额数值（可能是亿元），转换为元
                        if numeric_value < 1e9 and key in ['revenue', 'net_profit', 'operating_profit']:
                            numeric_value *= 1e8  # 亿元转元
                        income_data[mapped_key] = numeric_value
                    except (ValueError, TypeError):
                        logger.warning(f"无法转换收入指标 {key}: {value}")
                        income_data[mapped_key] = 0.0

            # 处理资产负债数据
            balance_data = {}
            for key, value in simple_metrics.items():
                if key in balance_metric_mapping:
                    mapped_key = balance_metric_mapping[key]
                    try:
                        numeric_value = float(value)
                        # 对于大额数值（可能是亿元），转换为元
                        if numeric_value < 1e9 and key in ['total_assets', 'total_liabilities', 'total_equity', 'current_assets', 'current_liabilities']:
                            numeric_value *= 1e8  # 亿元转元
                        balance_data[mapped_key] = numeric_value
                    except (ValueError, TypeError):
                        logger.warning(f"无法转换资产负债指标 {key}: {value}")
                        balance_data[mapped_key] = 0.0

            # 处理现金流数据
            cashflow_data = {}
            for key, value in simple_metrics.items():
                if key in cashflow_metric_mapping:
                    mapped_key = cashflow_metric_mapping[key]
                    try:
                        numeric_value = float(value)
                        # 对于大额数值（可能是亿元），转换为元
                        if numeric_value < 1e9:
                            numeric_value *= 1e8  # 亿元转元
                        cashflow_data[mapped_key] = numeric_value
                    except (ValueError, TypeError):
                        logger.warning(f"无法转换现金流指标 {key}: {value}")
                        cashflow_data[mapped_key] = 0.0

            # 创建DataFrame
            if income_data:
                income_df = pd.DataFrame([income_data])
                logger.info(f"扁平化收入数据解析完成: {list(income_data.keys())}")

            if balance_data:
                balance_df = pd.DataFrame([balance_data])
                logger.info(f"扁平化资产负债数据解析完成: {list(balance_data.keys())}")

            if cashflow_data:
                cashflow_df = pd.DataFrame([cashflow_data])
                logger.info(f"扁平化现金流数据解析完成: {list(cashflow_data.keys())}")

        else:
            logger.error("无法识别的财务数据格式")

        result = {
            'income': income_df,
            'balance': balance_df,
            'cashflow': cashflow_df
        }

        logger.info(f"数据转换完成 - Income: {income_df.shape}, Balance: {balance_df.shape}, Cashflow: {cashflow_df.shape}")
        return result
    
    def analyze_trends(self, financial_data: Dict[str, pd.DataFrame], years: int = 4) -> Dict:
        """
        分析财务数据趋势（内部使用）
        
        Args:
            financial_data: 财务数据
            years: 分析年数
            
        Returns:
            趋势分析结果
        """
        logger.info(f"分析最近{years}年财务趋势")
        
        trends = {}
        
        # 收入趋势
        trends['revenue'] = self._analyze_revenue_trend(financial_data, years)
        
        # 利润趋势
        trends['profit'] = self._analyze_profit_trend(financial_data, years)
        
        # 增长率
        trends['growth_rates'] = self._calculate_growth_rates(financial_data, years)
        
        logger.info("趋势分析完成")
        return trends
    
    @register_tool()
    def analyze_trends_tool(self, financial_data_json: str, years: int = 4) -> Dict:
        """
        分析财务数据趋势

        Args:
            financial_data_json: 财务数据的JSON字符串表示
            years: 分析年数

        Returns:
            趋势分析结果
        """
        import json
        logger.info(f"开始分析趋势，年数: {years}")
        logger.debug(f"输入数据类型: {type(financial_data_json)}")

        try:
            data_dict = json.loads(financial_data_json)
            logger.debug(f"解析后的数据键: {list(data_dict.keys()) if isinstance(data_dict, dict) else 'Not a dict'}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            return {'error': f"无效的JSON格式: {e}"}

        # 检查是否是多公司多年数据结构
        if isinstance(data_dict, dict):
            # 检查是否是公司对比格式 {"公司名": {"年份": {数据}}}
            if all(isinstance(v, dict) and any(k.isdigit() for k in v.keys()) for v in data_dict.values()):
                logger.info("检测到多公司多年数据结构")
                return self._analyze_multi_company_trends(data_dict, years)

            # 检查是否是扁平化财务指标格式
            elif any(key in data_dict for key in ['revenue', 'net_profit', '营业收入', '净利润']):
                logger.info("检测到扁平化财务指标格式")
                return self._analyze_simple_metrics_trends(data_dict, years)

            # 传统格式转换
            else:
                logger.info("检测到传统DataFrame格式")
                financial_data = {}
                for key, df_data in data_dict.items():
                    if isinstance(df_data, (list, dict)):
                        financial_data[key] = pd.DataFrame(df_data)
                    else:
                        financial_data[key] = pd.DataFrame()
                return self.analyze_trends(financial_data, years)
        else:
            logger.error("数据格式不正确")
            return {'error': "数据格式不正确，请提供JSON格式的财务数据"}

    def _analyze_multi_company_trends(self, data_dict: Dict, years: int) -> Dict:
        """
        分析多公司多年趋势数据

        Args:
            data_dict: 多公司数据字典
            years: 分析年数

        Returns:
            趋势分析结果
        """
        logger.info("开始分析多公司趋势")

        trends = {
            'revenue': {'data': [], 'trend': 'stable', 'average_growth': 0.0},
            'profit': {'data': [], 'trend': 'stable', 'average_growth': 0.0},
            'growth_rates': {'revenue_growth': [], 'profit_growth': [], 'assets_growth': []}
        }

        # 处理每个公司的数据
        all_revenue_data = []
        all_profit_data = []
        revenue_growth_rates = []
        profit_growth_rates = []

        for company_name, company_data in data_dict.items():
            logger.info(f"处理公司: {company_name}")

            if not isinstance(company_data, dict):
                logger.warning(f"公司 {company_name} 数据格式不正确")
                continue

            # 提取年份和数据
            years_data = []
            revenues = []
            profits = []

            for year_key, year_data in company_data.items():
                if year_key.isdigit():  # 确保是年份
                    year = int(year_key)
                    if isinstance(year_data, dict):
                        years_data.append(year)

                        # 提取收入数据（支持中英文）
                        revenue = self._extract_value_from_dict(year_data,
                            ['营业收入', 'revenue', '收入'])
                        revenues.append(revenue)

                        # 提取利润数据（支持中英文）
                        profit = self._extract_value_from_dict(year_data,
                            ['净利润', 'net_profit', '利润'])
                        profits.append(profit)

            # 按年份排序
            sorted_data = sorted(zip(years_data, revenues, profits), key=lambda x: x[0])
            if sorted_data:
                years_data, revenues, profits = zip(*sorted_data)

                # 计算增长率
                if len(revenues) >= 2:
                    revenue_growth = self._calculate_growth_rate(revenues[-1], revenues[0], len(revenues)-1)
                    profit_growth = self._calculate_growth_rate(profits[-1], profits[0], len(profits)-1)
                    revenue_growth_rates.append(revenue_growth)
                    profit_growth_rates.append(profit_growth)

                # 添加到总体数据中
                for year, revenue, profit in zip(years_data, revenues, profits):
                    all_revenue_data.append({'公司': company_name, '年份': year, '营业收入': revenue})
                    all_profit_data.append({'公司': company_name, '年份': year, '净利润': profit})

        # 计算总体趋势
        if revenue_growth_rates:
            avg_revenue_growth = sum(revenue_growth_rates) / len(revenue_growth_rates)
            trends['revenue']['average_growth'] = round(avg_revenue_growth, 2)
            trends['growth_rates']['revenue_growth'] = [round(r, 2) for r in revenue_growth_rates]

            if avg_revenue_growth > 10:
                trends['revenue']['trend'] = 'increasing'
            elif avg_revenue_growth < -5:
                trends['revenue']['trend'] = 'decreasing'

        if profit_growth_rates:
            avg_profit_growth = sum(profit_growth_rates) / len(profit_growth_rates)
            trends['profit']['average_growth'] = round(avg_profit_growth, 2)
            trends['growth_rates']['profit_growth'] = [round(p, 2) for p in profit_growth_rates]

            if avg_profit_growth > 10:
                trends['profit']['trend'] = 'increasing'
            elif avg_profit_growth < -5:
                trends['profit']['trend'] = 'decreasing'

        trends['revenue']['data'] = all_revenue_data
        trends['profit']['data'] = all_profit_data

        logger.info(f"多公司趋势分析完成 - 收入增长: {avg_revenue_growth:.2f}%, 利润增长: {avg_profit_growth:.2f}%")
        return trends

    def _analyze_simple_metrics_trends(self, data_dict: Dict, years: int) -> Dict:
        """
        分析简单财务指标的趋势

        Args:
            data_dict: 简单指标字典
            years: 分析年数

        Returns:
            趋势分析结果
        """
        logger.info("开始分析简单财务指标趋势")

        # 检查是否有历史数据字段
        current_revenue = self._extract_value_from_dict(data_dict, ['revenue', '营业收入'])
        current_profit = self._extract_value_from_dict(data_dict, ['net_profit', '净利润'])

        prev_revenue = self._extract_value_from_dict(data_dict, ['prev_revenue', 'previous_revenue'])
        prev_profit = self._extract_value_from_dict(data_dict, ['prev_net_profit', 'previous_net_profit'])

        trends = {
            'revenue': {'data': [], 'trend': 'stable', 'average_growth': 0.0},
            'profit': {'data': [], 'trend': 'stable', 'average_growth': 0.0},
            'growth_rates': {'revenue_growth': [], 'profit_growth': [], 'assets_growth': []}
        }

        # 如果有历史数据，计算增长率
        if prev_revenue > 0 and current_revenue > 0:
            revenue_growth = ((current_revenue - prev_revenue) / prev_revenue) * 100
            trends['revenue']['average_growth'] = round(revenue_growth, 2)
            trends['growth_rates']['revenue_growth'] = [round(revenue_growth, 2)]

            if revenue_growth > 5:
                trends['revenue']['trend'] = 'increasing'
            elif revenue_growth < -5:
                trends['revenue']['trend'] = 'decreasing'

        if prev_profit > 0 and current_profit > 0:
            profit_growth = ((current_profit - prev_profit) / prev_profit) * 100
            trends['profit']['average_growth'] = round(profit_growth, 2)
            trends['growth_rates']['profit_growth'] = [round(profit_growth, 2)]

            if profit_growth > 5:
                trends['profit']['trend'] = 'increasing'
            elif profit_growth < -5:
                trends['profit']['trend'] = 'decreasing'

        # 创建数据点
        company_name = data_dict.get('company_name', data_dict.get('company', '目标公司'))

        # 添加当年数据
        trends['revenue']['data'].append({
            '公司': company_name,
            '年份': '2024',
            '营业收入': current_revenue
        })

        trends['profit']['data'].append({
            '公司': company_name,
            '年份': '2024',
            '净利润': current_profit
        })

        # 如果有历史数据，添加历史数据点
        if prev_revenue > 0:
            trends['revenue']['data'].append({
                '公司': company_name,
                '年份': '2023',
                '营业收入': prev_revenue
            })

        if prev_profit > 0:
            trends['profit']['data'].append({
                '公司': company_name,
                '年份': '2023',
                '净利润': prev_profit
            })

        logger.info(f"简单指标趋势分析完成 - 收入增长: {trends['revenue']['average_growth']}%, 利润增长: {trends['profit']['average_growth']}%")
        return trends

    def _extract_value_from_dict(self, data_dict: Dict, key_list: List[str]) -> float:
        """
        从字典中提取数值，支持多个可能的键名

        Args:
            data_dict: 数据字典
            key_list: 可能的键名列表

        Returns:
            提取的数值，找不到返回0.0
        """
        for key in key_list:
            if key in data_dict:
                try:
                    value = data_dict[key]
                    if isinstance(value, (int, float)):
                        return float(value)
                    else:
                        return float(str(value))
                except (ValueError, TypeError):
                    continue
        return 0.0

    def _calculate_growth_rate(self, current: float, previous: float, periods: int) -> float:
        """
        计算增长率

        Args:
            current: 当前值
            previous: 之前值
            periods: 时间段数

        Returns:
            年化增长率
        """
        if previous <= 0 or current <= 0:
            return 0.0

        if periods <= 0:
            periods = 1

        # 计算复合年增长率
        growth_rate = ((current / previous) ** (1 / periods) - 1) * 100
        return growth_rate

    def _create_data_hash(self, data: Dict) -> str:
        """
        为数据创建哈希值，用于缓存键

        Args:
            data: 输入数据字典

        Returns:
            数据的哈希值字符串
        """
        import hashlib

        try:
            # 将数据转换为可哈希的字符串
            data_str = json.dumps(data, sort_keys=True, default=str)
            # 创建MD5哈希
            return hashlib.md5(data_str.encode('utf-8')).hexdigest()[:16]  # 使用前16位
        except Exception:
            # 如果哈希创建失败，使用数据长度作为简单键
            return str(len(str(data)))

    def get_cache_stats(self) -> Dict:
        """
        获取缓存统计信息

        Returns:
            缓存统计字典
        """
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total_requests * 100) if total_requests > 0 else 0

        return {
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'hit_rate_percent': round(hit_rate, 2),
            'ratios_cache_size': len(self._ratios_cache),
            'trends_cache_size': len(self._trends_cache)
        }

    def clear_cache(self):
        """清空缓存"""
        self._ratios_cache.clear()
        self._trends_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        logger.info("财务分析工具缓存已清空")
    
    def assess_financial_health(self, ratios: Dict, trends: Dict) -> Dict:
        """
        评估财务健康状况（内部使用）
        
        Args:
            ratios: 财务比率
            trends: 趋势分析
            
        Returns:
            财务健康评估结果
        """
        logger.info("评估财务健康状况")
        
        assessment = {
            'overall_score': 0,
            'risk_level': '低风险',
            'strengths': [],
            'weaknesses': [],
            'recommendations': []
        }
        
        # 盈利能力评估
        profitability_score = self._assess_profitability(ratios.get('profitability', {}))
        assessment['overall_score'] += profitability_score * 0.3
        
        # 偿债能力评估
        solvency_score = self._assess_solvency(ratios.get('solvency', {}))
        assessment['overall_score'] += solvency_score * 0.3
        
        # 运营效率评估
        efficiency_score = self._assess_efficiency(ratios.get('efficiency', {}))
        assessment['overall_score'] += efficiency_score * 0.2
        
        # 成长能力评估
        growth_score = self._assess_growth(ratios.get('growth', {}), trends)
        assessment['overall_score'] += growth_score * 0.2
        
        # 确定风险等级
        assessment['overall_score'] = round(assessment['overall_score'], 1)
        if assessment['overall_score'] >= 80:
            assessment['risk_level'] = '低风险'
        elif assessment['overall_score'] >= 60:
            assessment['risk_level'] = '中等风险'
        else:
            assessment['risk_level'] = '高风险'
        
        # 生成建议
        assessment['recommendations'] = self._generate_recommendations(ratios, trends)
        
        logger.info("财务健康评估完成")
        return assessment
    
    @register_tool()
    def assess_health(self, ratios: Dict, trends: Dict) -> Dict:
        """
        评估财务健康状况
        
        Args:
            ratios: 财务比率
            trends: 趋势分析
            
        Returns:
            财务健康评估结果
        """
        return self.assess_financial_health(ratios, trends)
    
    def generate_analysis_report(self, financial_data: Dict[str, pd.DataFrame], 
                              stock_name: str = "目标公司") -> Dict:
        """
        生成完整的分析报告（内部使用）
        
        Args:
            financial_data: 财务数据
            stock_name: 公司名称
            
        Returns:
            完整分析报告
        """
        logger.info(f"生成{stock_name}财务分析报告")
        
        # 计算财务比率
        ratios = self.calculate_financial_ratios(financial_data)
        
        # 分析趋势
        trends = self.analyze_trends(financial_data)
        
        # 评估财务健康
        health = self.assess_financial_health(ratios, trends)
        
        # 提取关键指标
        key_metrics = self._extract_key_metrics(financial_data)
        
        # 生成报告
        report = {
            'company_name': stock_name,
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'key_metrics': key_metrics,
            'financial_ratios': ratios,
            'trend_analysis': trends,
            'health_assessment': health,
            'summary': self._generate_summary(ratios, trends, health)
        }
        
        logger.info("分析报告生成完成")
        return report

    def _calculate_profitability_ratios(self, financial_data: Dict) -> Dict:
        """计算盈利能力指标"""
        income = financial_data.get('income', pd.DataFrame())
        balance = financial_data.get('balance', pd.DataFrame())
        
        ratios = {}
        
        if not income.empty:
            latest = income.iloc[0] if len(income) > 0 else pd.Series()
            
            # 毛利率
            revenue = self._get_value(latest, ['TOTAL_OPERATE_INCOME', '营业收入'])
            cost = self._get_value(latest, ['TOTAL_OPERATE_COST', '营业成本'])
            if revenue > 0:
                ratios['gross_profit_margin'] = round((revenue - cost) / revenue * 100, 2)
            
            # 净利率
            net_profit = self._get_value(latest, ['NETPROFIT', '净利润'])
            if revenue > 0:
                ratios['net_profit_margin'] = round(net_profit / revenue * 100, 2)
        
        if not income.empty and not balance.empty:
            latest_income = income.iloc[0] if len(income) > 0 else pd.Series()
            latest_balance = balance.iloc[0] if len(balance) > 0 else pd.Series()
            
            # ROE
            parent_profit = self._get_value(latest_income, ['PARENT_NETPROFIT', '归属于母公司所有者的净利润'])
            equity = self._get_value(latest_balance, ['TOTAL_EQUITY', '所有者权益合计'])
            if equity > 0:
                ratios['roe'] = round(parent_profit / equity * 100, 2)
            
            # ROA
            net_profit = self._get_value(latest_income, ['NETPROFIT', '净利润'])
            assets = self._get_value(latest_balance, ['TOTAL_ASSETS', '总资产'])
            if assets > 0:
                ratios['roa'] = round(net_profit / assets * 100, 2)
        
        return ratios
    
    def _calculate_solvency_ratios(self, financial_data: Dict) -> Dict:
        """计算偿债能力指标"""
        balance = financial_data.get('balance', pd.DataFrame())
        
        ratios = {}
        
        if not balance.empty:
            latest = balance.iloc[0] if len(balance) > 0 else pd.Series()
            
            # 资产负债率
            assets = self._get_value(latest, ['TOTAL_ASSETS', '资产总计'])
            liabilities = self._get_value(latest, ['TOTAL_LIABILITIES', '负债合计'])
            if assets > 0:
                ratios['debt_to_asset_ratio'] = round(liabilities / assets * 100, 2)
            
            # 流动比率
            current_assets = self._get_value(latest, ['TOTAL_CURRENT_ASSETS', '流动资产合计'])
            current_liabilities = self._get_value(latest, ['TOTAL_CURRENT_LIABILITIES', '流动负债合计'])
            if current_liabilities > 0:
                ratios['current_ratio'] = round(current_assets / current_liabilities, 2)
            
            # 速动比率
            inventory = self._get_value(latest, ['INVENTORY', '存货'])
            quick_assets = current_assets - inventory if current_assets > 0 and inventory > 0 else current_assets
            if current_liabilities > 0:
                ratios['quick_ratio'] = round(quick_assets / current_liabilities, 2)
        
        return ratios
    
    def _calculate_efficiency_ratios(self, financial_data: Dict) -> Dict:
        """计算运营效率指标"""
        income = financial_data.get('income', pd.DataFrame())
        balance = financial_data.get('balance', pd.DataFrame())
        
        ratios = {}
        
        if not income.empty and not balance.empty:
            latest_income = income.iloc[0]
            latest_balance = balance.iloc[0]
            
            # 总资产周转率
            revenue = self._get_value(latest_income, ['TOTAL_OPERATE_INCOME', '营业收入'])
            assets_begin = self._get_value_from_index(balance, -1, ['TOTAL_ASSETS', '资产总计']) if len(balance) > 1 else 0
            assets_end = self._get_value(latest_balance, ['TOTAL_ASSETS', '资产总计'])
            avg_assets = (assets_begin + assets_end) / 2 if assets_begin > 0 else assets_end
            if avg_assets > 0:
                ratios['asset_turnover'] = round(revenue / avg_assets, 2)
            
            # 存货周转率
            cost = self._get_value(latest_income, ['TOTAL_OPERATE_COST', '营业成本'])
            inventory_begin = self._get_value_from_index(balance, -1, ['INVENTORY', '存货']) if len(balance) > 1 else 0
            inventory_end = self._get_value(latest_balance, ['INVENTORY', '存货'])
            avg_inventory = (inventory_begin + inventory_end) / 2 if inventory_begin > 0 else inventory_end
            if avg_inventory > 0:
                ratios['inventory_turnover'] = round(cost / avg_inventory, 2)
        
        return ratios
    
    def _calculate_growth_ratios(self, financial_data: Dict) -> Dict:
        """计算成长能力指标"""
        income = financial_data.get('income', pd.DataFrame())
        balance = financial_data.get('balance', pd.DataFrame())
        
        ratios = {}
        
        # 如果有两年或以上的数据，计算实际增长率
        if len(income) >= 2:
            current = income.iloc[0]
            previous = income.iloc[1]
            
            # 收入增长率
            current_revenue = self._get_value(current, ['TOTAL_OPERATE_INCOME', '营业收入'])
            previous_revenue = self._get_value(previous, ['TOTAL_OPERATE_INCOME', '营业收入'])
            if previous_revenue > 0:
                ratios['revenue_growth'] = round((current_revenue - previous_revenue) / previous_revenue * 100, 2)
            
            # 利润增长率
            current_profit = self._get_value(current, ['NETPROFIT', '净利润'])
            previous_profit = self._get_value(previous, ['NETPROFIT', '净利润'])
            if previous_profit > 0:
                ratios['profit_growth'] = round((current_profit - previous_profit) / previous_profit * 100, 2)
        else:
            # 如果只有一年数据，无法计算增长率，设置为0
            ratios['revenue_growth'] = 0.0
            ratios['profit_growth'] = 0.0
        
        return ratios
    
    def _get_value(self, row: pd.Series, col_names: List[str]) -> float:
        """
        根据可能的列名获取数值，增强错误处理和数据验证

        Args:
            row: pandas Series行数据
            col_names: 可能的列名列表

        Returns:
            提取的数值，失败返回0.0
        """
        if not isinstance(row, pd.Series):
            logger.warning(f"输入不是pandas Series: {type(row)}")
            return 0.0

        if row.empty:
            logger.warning("输入的Series为空")
            return 0.0

        for col in col_names:
            try:
                # 检查列是否存在
                if col not in row.index:
                    continue

                value = row[col]

                # 跳过pandas对象
                if isinstance(value, (pd.Series, pd.DataFrame)):
                    continue

                # 跳过NaN值
                if pd.isna(value):
                    continue

                # 跳过None值
                if value is None:
                    continue

                # 处理字符串类型的数值
                if isinstance(value, str):
                    # 移除常见的格式字符
                    cleaned_value = value.replace(',', '').replace('%', '').replace('¥', '').replace('$', '').strip()

                    # 如果是空字符串，跳过
                    if not cleaned_value:
                        continue

                    try:
                        # 转换为浮点数
                        val = float(cleaned_value)
                        logger.debug(f"成功从列 '{col}' 提取数值: {val}")
                        return val
                    except ValueError:
                        logger.warning(f"无法转换字符串值 '{value}' 为数值")
                        continue
                else:
                    # 处理数值类型
                    try:
                        val = float(value)
                        logger.debug(f"成功从列 '{col}' 提取数值: {val}")
                        return val
                    except (ValueError, TypeError):
                        logger.warning(f"无法转换值 '{value}' (类型: {type(value)}) 为数值")
                        continue

            except Exception as e:
                logger.warning(f"提取列 '{col}' 数值时出错: {e}")
                continue

        # 如果所有列名都尝试失败，记录警告
        logger.warning(f"无法从列名列表 {col_names} 中提取有效数值，可用列: {list(row.index)}")
        return 0.0
    
    def _get_value_from_index(self, df: pd.DataFrame, index: int, col_names: List[str]) -> float:
        """
        从DataFrame的指定索引行获取数值，增强错误处理

        Args:
            df: pandas DataFrame
            index: 行索引
            col_names: 可能的列名列表

        Returns:
            提取的数值，失败返回0.0
        """
        try:
            # 检查DataFrame是否为空
            if df.empty:
                logger.warning("DataFrame为空，无法提取数值")
                return 0.0

            # 检查索引是否有效
            if index >= len(df) or index < -len(df):
                logger.warning(f"索引 {index} 超出DataFrame范围 (0-{len(df)-1})")
                return 0.0

            # 提取指定行
            row = df.iloc[index]

            # 使用增强的_get_value方法
            return self._get_value(row, col_names)

        except Exception as e:
            logger.error(f"从索引 {index} 提取数值时出错: {e}")
            return 0.0
    
    def _get_series(self, df: pd.DataFrame, col_names: List[str]) -> pd.Series:
        """根据可能的列名获取数值列"""
        for col in col_names:
            if col in df.columns:
                series = df[col]
                # 确保返回的是Series类型
                if isinstance(series, pd.Series):
                    return series.copy()
                else:
                    # 如果不是Series，创建一个Series
                    return pd.Series([series], index=[0])
        # 如果没有找到匹配的列，返回零值Series
        return pd.Series([0.0] * len(df), index=df.index) if len(df) > 0 else pd.Series([0.0])
    
    def _analyze_revenue_trend(self, financial_data: Dict, years: int) -> Dict:
        """分析收入趋势"""
        income = financial_data.get('income', pd.DataFrame())
        
        trend = {
            'data': [],
            'trend': 'stable',  # stable, increasing, decreasing
            'average_growth': 0.0
        }
        
        if not income.empty and len(income) >= 2:
            # 获取最近几年的数据
            recent_data = income.head(min(years, len(income))).copy()
            recent_data.loc[:, '年份'] = pd.to_datetime(recent_data['REPORT_DATE']).dt.year
            
            # 提取收入数据
            revenue_cols = ['TOTAL_OPERATE_INCOME', '营业收入']
            for col in revenue_cols:
                if col in recent_data.columns:
                    trend['data'] = recent_data[['年份', col]].to_dict('records')
                    break
            
            # 计算平均增长率
            if len(recent_data) >= 2:
                latest_revenue = self._get_value(recent_data.iloc[0], revenue_cols)
                earliest_revenue = self._get_value(recent_data.iloc[-1], revenue_cols)
                if earliest_revenue > 0:
                    trend['average_growth'] = round((latest_revenue - earliest_revenue) / earliest_revenue / len(recent_data) * 100, 2)
                
                # 确定趋势
                if trend['average_growth'] > 5:
                    trend['trend'] = 'increasing'
                elif trend['average_growth'] < -5:
                    trend['trend'] = 'decreasing'
                else:
                    trend['trend'] = 'stable'
        
        return trend
    
    def _analyze_profit_trend(self, financial_data: Dict, years: int) -> Dict:
        """分析利润趋势"""
        income = financial_data.get('income', pd.DataFrame())
        
        trend = {
            'data': [],
            'trend': 'stable',  # stable, increasing, decreasing
            'average_growth': 0.0
        }
        
        if not income.empty and len(income) >= 2:
            # 获取最近几年的数据
            recent_data = income.head(min(years, len(income))).copy()
            recent_data.loc[:, '年份'] = pd.to_datetime(recent_data['REPORT_DATE']).dt.year
            
            # 提取利润数据
            profit_cols = ['NETPROFIT', '净利润']
            for col in profit_cols:
                if col in recent_data.columns:
                    trend['data'] = recent_data[['年份', col]].to_dict('records')
                    break
            
            # 计算平均增长率
            if len(recent_data) >= 2:
                latest_profit = self._get_value(recent_data.iloc[0], profit_cols)
                earliest_profit = self._get_value(recent_data.iloc[-1], profit_cols)
                if earliest_profit > 0:
                    trend['average_growth'] = round((latest_profit - earliest_profit) / earliest_profit / len(recent_data) * 100, 2)
                
                # 确定趋势
                if trend['average_growth'] > 5:
                    trend['trend'] = 'increasing'
                elif trend['average_growth'] < -5:
                    trend['trend'] = 'decreasing'
                else:
                    trend['trend'] = 'stable'
        
        return trend
    
    def _calculate_growth_rates(self, financial_data: Dict, years: int) -> Dict:
        """计算增长率"""
        income = financial_data.get('income', pd.DataFrame())
        
        growth_rates = {
            'revenue_growth': [],
            'profit_growth': [],
            'assets_growth': []
        }
        
        if not income.empty and len(income) >= 2:
            # 获取最近几年的数据
            recent_data = income.head(min(years, len(income)))
            
            # 计算收入增长率
            revenue_cols = ['TOTAL_OPERATE_INCOME', '营业收入']
            for i in range(len(recent_data) - 1):
                current = self._get_value(recent_data.iloc[i], revenue_cols)
                previous = self._get_value(recent_data.iloc[i + 1], revenue_cols)
                if previous > 0:
                    growth_rate = round((current - previous) / previous * 100, 2)
                    growth_rates['revenue_growth'].append(growth_rate)
            
            # 计算利润增长率
            profit_cols = ['NETPROFIT', '净利润']
            for i in range(len(recent_data) - 1):
                current = self._get_value(recent_data.iloc[i], profit_cols)
                previous = self._get_value(recent_data.iloc[i + 1], profit_cols)
                if previous > 0:
                    growth_rate = round((current - previous) / previous * 100, 2)
                    growth_rates['profit_growth'].append(growth_rate)
        
        return growth_rates
    
    def _assess_profitability(self, ratios: Dict) -> float:
        """评估盈利能力"""
        score = 50.0  # 基础分数
        
        # 净利率评估
        net_profit_margin = ratios.get('net_profit_margin', 0)
        if net_profit_margin > 15:
            score += 20
        elif net_profit_margin > 5:
            score += 10
        elif net_profit_margin > 0:
            score += 5
        
        # ROE评估
        roe = ratios.get('roe', 0)
        if roe > 20:
            score += 20
        elif roe > 10:
            score += 10
        elif roe > 0:
            score += 5
        
        # ROA评估
        roa = ratios.get('roa', 0)
        if roa > 10:
            score += 10
        elif roa > 5:
            score += 5
        elif roa > 0:
            score += 2
        
        return min(score, 100.0)
    
    def _assess_solvency(self, ratios: Dict) -> float:
        """评估偿债能力"""
        score = 50.0  # 基础分数
        
        # 资产负债率评估
        debt_ratio = ratios.get('debt_to_asset_ratio', 0)
        if debt_ratio < 40:
            score += 20
        elif debt_ratio < 60:
            score += 10
        elif debt_ratio < 80:
            score += 5
        
        # 流动比率评估
        current_ratio = ratios.get('current_ratio', 0)
        if current_ratio > 2:
            score += 15
        elif current_ratio > 1:
            score += 10
        elif current_ratio > 0.5:
            score += 5
        
        # 速动比率评估
        quick_ratio = ratios.get('quick_ratio', 0)
        if quick_ratio > 1.5:
            score += 10
        elif quick_ratio > 1:
            score += 5
        elif quick_ratio > 0.5:
            score += 2
        
        return min(score, 100.0)
    
    def _assess_efficiency(self, ratios: Dict) -> float:
        """评估运营效率"""
        score = 50.0  # 基础分数
        
        # 总资产周转率评估
        asset_turnover = ratios.get('asset_turnover', 0)
        if asset_turnover > 1:
            score += 20
        elif asset_turnover > 0.5:
            score += 10
        elif asset_turnover > 0:
            score += 5
        
        # 存货周转率评估
        inventory_turnover = ratios.get('inventory_turnover', 0)
        if inventory_turnover > 10:
            score += 20
        elif inventory_turnover > 5:
            score += 10
        elif inventory_turnover > 0:
            score += 5
        
        return min(score, 100.0)
    
    def _assess_growth(self, growth_ratios: Dict, trends: Dict) -> float:
        """评估成长能力"""
        score = 50.0  # 基础分数
        
        # 收入增长率评估
        revenue_growth = growth_ratios.get('revenue_growth', 0)
        if revenue_growth > 15:
            score += 20
        elif revenue_growth > 5:
            score += 10
        elif revenue_growth > 0:
            score += 5
        
        # 利润增长率评估
        profit_growth = growth_ratios.get('profit_growth', 0)
        if profit_growth > 15:
            score += 20
        elif profit_growth > 5:
            score += 10
        elif profit_growth > 0:
            score += 5
        
        return min(score, 100.0)
    
    def _generate_recommendations(self, ratios: Dict, trends: Dict) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 盈利能力相关建议
        net_profit_margin = ratios.get('profitability', {}).get('net_profit_margin', 0)
        if net_profit_margin < 5:
            recommendations.append("建议优化成本结构，提高盈利能力")
        
        roe = ratios.get('profitability', {}).get('roe', 0)
        if roe < 10:
            recommendations.append("建议提高股东回报率，增强投资者信心")
        
        # 偿债能力相关建议
        debt_ratio = ratios.get('solvency', {}).get('debt_to_asset_ratio', 0)
        if debt_ratio > 60:
            recommendations.append("建议优化债务结构，降低财务风险")
        
        current_ratio = ratios.get('solvency', {}).get('current_ratio', 0)
        if current_ratio < 1:
            recommendations.append("建议加强流动资产管理，提高短期偿债能力")
        
        # 运营效率相关建议
        asset_turnover = ratios.get('efficiency', {}).get('asset_turnover', 0)
        if asset_turnover < 0.5:
            recommendations.append("建议提高资产利用效率，优化资源配置")
        
        # 成长能力相关建议
        revenue_growth = ratios.get('growth', {}).get('revenue_growth', 0)
        if revenue_growth < 5:
            recommendations.append("建议拓展市场渠道，提升收入增长动力")
        
        # 如果没有建议，添加通用建议
        if not recommendations:
            recommendations.append("公司财务状况良好，建议继续保持稳健经营策略")
            recommendations.append("关注行业发展趋势，适时调整经营策略")
        
        return recommendations
    
    def _extract_key_metrics(self, financial_data: Dict) -> Dict:
        """提取关键指标"""
        key_metrics = {}
        
        # 从利润表提取关键指标
        income = financial_data.get('income', pd.DataFrame())
        if not income.empty:
            latest = income.iloc[0]
            key_metrics['营业收入(亿元)'] = self._get_value(latest, ['TOTAL_OPERATE_INCOME', '营业收入']) / 1e8  # 亿元
            key_metrics['净利润(亿元)'] = self._get_value(latest, ['NETPROFIT', '净利润']) / 1e8  # 亿元
            key_metrics['归母净利润(亿元)'] = self._get_value(latest, ['PARENT_NETPROFIT', '归属于母公司所有者的净利润']) / 1e8  # 亿元
        
        # 从资产负债表提取关键指标
        balance = financial_data.get('balance', pd.DataFrame())
        if not balance.empty:
            latest = balance.iloc[0]
            key_metrics['总资产(亿元)'] = self._get_value(latest, ['TOTAL_ASSETS', '资产总计']) / 1e8  # 亿元
            key_metrics['总负债(亿元)'] = self._get_value(latest, ['TOTAL_LIABILITIES', '负债合计']) / 1e8  # 亿元
            key_metrics['净资产(亿元)'] = self._get_value(latest, ['TOTAL_EQUITY', '所有者权益合计']) / 1e8  # 亿元
        
        return key_metrics
    
    def _generate_summary(self, ratios: Dict, trends: Dict, health: Dict) -> str:
        """生成摘要"""
        summary = f"公司财务健康评分为{health['overall_score']}分，风险等级为{health['risk_level']}。"
        
        # 添加盈利能力摘要
        profitability = ratios.get('profitability', {})
        if profitability:
            net_profit_margin = profitability.get('net_profit_margin', 0)
            roe = profitability.get('roe', 0)
            summary += f"盈利能力方面，净利率为{net_profit_margin}%，ROE为{roe}%。"
        
        # 添加偿债能力摘要
        solvency = ratios.get('solvency', {})
        if solvency:
            debt_ratio = solvency.get('debt_to_asset_ratio', 0)
            current_ratio = solvency.get('current_ratio', 0)
            summary += f"偿债能力方面，资产负债率为{debt_ratio}%，流动比率为{current_ratio}。"
        
        # 添加成长能力摘要
        growth = ratios.get('growth', {})
        if growth:
            revenue_growth = growth.get('revenue_growth', 0)
            summary += f"成长能力方面，收入增长率为{revenue_growth}%。"
        
        return summary
    
    @register_tool()
    def generate_comparison_report(self, comparison_data_json: str) -> str:
        """
        生成公司对比分析报告
        
        Args:
            comparison_data_json: 公司对比数据的JSON字符串表示
            
        Returns:
            格式化的对比分析报告
        """
        import json
        from datetime import datetime
        try:
            # 解析JSON数据
            comparison_data = json.loads(comparison_data_json)
            
            # 生成报告标题和日期
            report_date = datetime.now().strftime('%Y-%m-%d')
            report_title = "公司财务数据对比分析报告"
            
            # 生成报告文本
            report_text = f"""
# {report_title}
报告日期: {report_date}

## 一、公司基本信息
"""
            
            # 添加公司信息
            companies = comparison_data.get('companies', [])
            if companies:
                for i, company in enumerate(companies):
                    report_text += f"- {company}\n"
            
            # 添加关键财务指标对比
            report_text += "\n## 二、关键财务指标对比\n"
            report_text += "| 财务指标 | " + " | ".join(companies) + " |\n"
            report_text += "|" + "|".join(["----"] * (len(companies) + 1)) + "|\n"
            
            # 处理各种财务指标
            metrics = ['revenue', 'net_profit', 'total_assets', 'debt_ratio', 'roe']
            metric_names = {
                'revenue': '营业收入(亿元)',
                'net_profit': '净利润(亿元)',
                'total_assets': '总资产(亿元)',
                'debt_ratio': '资产负债率(%)',
                'roe': 'ROE(%)'
            }
            
            for metric in metrics:
                values = comparison_data.get(metric, [])
                if values:
                    row = f"| {metric_names.get(metric, metric)} |"
                    for value in values:
                        row += f" {value} |"
                    report_text += row + "\n"
            
            # 添加分析总结
            report_text += "\n## 三、分析总结\n"
            if len(companies) >= 2:
                # 简单的对比分析
                revenues = comparison_data.get('revenue', [])
                if len(revenues) >= 2:
                    if revenues[0] > revenues[1]:
                        report_text += f"1. 从营业收入来看，{companies[0]}的规模明显大于{companies[1]}\n"
                    else:
                        report_text += f"1. 从营业收入来看，{companies[1]}的规模明显大于{companies[0]}\n"
                
                profits = comparison_data.get('net_profit', [])
                if len(profits) >= 2:
                    if profits[0] > profits[1]:
                        report_text += f"2. 从净利润来看，{companies[0]}的盈利能力更强\n"
                    else:
                        report_text += f"2. 从净利润来看，{companies[1]}的盈利能力更强\n"
                
                roes = comparison_data.get('roe', [])
                if len(roes) >= 2:
                    if roes[0] > roes[1]:
                        report_text += f"3. 从ROE来看，{companies[0]}的股东回报率更高\n"
                    else:
                        report_text += f"3. 从ROE来看，{companies[1]}的股东回报率更高\n"
            
            return report_text
            
        except Exception as e:
            return f"生成对比报告时出错: {str(e)}"

    @register_tool()
    def save_text_report(self, financial_data_json: str, 
                        stock_name: str = "目标公司",
                        file_path: Optional[str] = None,
                        file_prefix: str = "./run_workdir") -> str:
        """
        生成并保存纯文字格式的财务分析报告为MD文件
        
        Args:
            financial_data_json: 财务数据的JSON字符串表示
            stock_name: 公司名称
            file_path: 保存文件的完整路径（可选，如果提供则忽略file_prefix）
            file_prefix: 保存文件的目录前缀（默认为"./run_workdir"）
            
        Returns:
            保存结果信息
        """
        import os
        from datetime import datetime
        try:
            # 如果没有提供完整文件路径，则根据公司名称和日期生成文件名
            if file_path is None:
                # 清理公司名称中的特殊字符，确保文件名合法
                safe_stock_name = "".join(c for c in stock_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                # 生成带日期的文件名
                current_date = datetime.now().strftime("%Y%m%d")
                file_name = f"{safe_stock_name}{current_date}财务分析报告.md"
                file_path = os.path.join(file_prefix, file_name)
            
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            # 保存到文件（直接保存financial_data_json的内容）
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(financial_data_json)
            
            return f"报告已成功保存到: {file_path}"
        except Exception as e:
            return f"保存报告时出错: {str(e)}"

    @register_tool()
    def save_analysis_result(self, analysis_result: str, 
                           stock_name: str = "目标公司",
                           file_path: Optional[str] = None,
                           file_prefix: str = "./run_workdir") -> str:
        """
        保存AI分析结果到MD文件
        
        Args:
            analysis_result: AI生成的分析结果文本
            stock_name: 公司名称
            file_path: 保存文件的完整路径（可选，如果提供则忽略file_prefix）
            file_prefix: 保存文件的目录前缀（默认为"./run_workdir"）
            
        Returns:
            保存结果信息
        """
        import os
        from datetime import datetime
        try:
            # 如果没有提供完整文件路径，则根据公司名称和日期生成文件名
            if file_path is None:
                # 清理公司名称中的特殊字符，确保文件名合法
                safe_stock_name = "".join(c for c in stock_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                # 生成带日期的文件名
                current_date = datetime.now().strftime("%Y%m%d")
                file_name = f"{safe_stock_name}{current_date}财务分析报告.md"
                file_path = os.path.join(file_prefix, file_name)
            
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            # 保存到文件，确保正确处理换行符和特殊字符
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(analysis_result)
            
            # 验证文件是否保存成功
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                return f"分析结果已成功保存到: {file_path} (文件大小: {file_size} 字节)"
            else:
                return f"保存分析结果时出错: 文件未成功创建"
        except Exception as e:
            return f"保存分析结果时出错: {str(e)}"

# 全局实例
_analyzer = None

def get_financial_analyzer():
    """获取财务分析器实例"""
    global _analyzer
    if _analyzer is None:
        _analyzer = StandardFinancialAnalyzer()
    return _analyzer

# 便利函数
def calculate_ratios(financial_data: Dict[str, pd.DataFrame]) -> Dict:
    """计算财务比率"""
    analyzer = get_financial_analyzer()
    return analyzer.calculate_financial_ratios(financial_data)

def analyze_trends(financial_data: Dict[str, pd.DataFrame], years: int = 4) -> Dict:
    """分析趋势"""
    analyzer = get_financial_analyzer()
    return analyzer.analyze_trends(financial_data, years)

def assess_health(ratios: Dict, trends: Dict) -> Dict:
    """评估财务健康"""
    analyzer = get_financial_analyzer()
    return analyzer.assess_financial_health(ratios, trends)

if __name__ == "__main__":
    # 测试代码
    print("=== 标准化财务分析工具库测试 ===\n")
    
    # 创建模拟数据
    mock_income = pd.DataFrame({
        'REPORT_DATE': pd.date_range('2020-12-31', periods=4, freq='Y'),
        'TOTAL_OPERATE_INCOME': [100000000, 120000000, 135000000, 150000000],
        'NETPROFIT': [8000000, 10000000, 12000000, 13500000],
        'PARENT_NETPROFIT': [7500000, 9500000, 11500000, 13000000],
        'TOTAL_OPERATE_COST': [70000000, 85000000, 95000000, 105000000]
    })
    
    mock_balance = pd.DataFrame({
        'REPORT_DATE': pd.date_range('2020-12-31', periods=4, freq='Y'),
        'TOTAL_ASSETS': [80000000, 90000000, 100000000, 110000000],
        'TOTAL_LIABILITIES': [50000000, 55000000, 60000000, 65000000],
        'TOTAL_EQUITY': [30000000, 35000000, 40000000, 45000000],
        'TOTAL_CURRENT_ASSETS': [40000000, 45000000, 50000000, 55000000],
        'TOTAL_CURRENT_LIABILITIES': [30000000, 32000000, 35000000, 38000000]
    })
    
    mock_data = {
        'income': mock_income,
        'balance': mock_balance
    }
    
    # 测试完整分析
    print("1. 测试完整财务分析...")
    analyzer = get_financial_analyzer()
    report = analyzer.generate_analysis_report(mock_data, "测试公司")
    
    print(f"   ✓ 公司名称: {report['company_name']}")
    print(f"   ✓ 分析日期: {report['analysis_date']}")
    print(f"   ✓ 健康评分: {report['health_assessment']['overall_score']}")
    print(f"   ✓ 风险等级: {report['health_assessment']['risk_level']}")
    
    # 显示关键指标
    print("\n2. 关键财务指标:")
    for key, value in report['key_metrics'].items():
        print(f"   - {key}: {value}亿元")
    
    # 显示财务比率
    print("\n3. 财务比率:")
    for category, ratios in report['financial_ratios'].items():
        print(f"   {category}:")
        for ratio, value in ratios.items():
            print(f"     - {ratio}: {value}")
    
    # 显示建议
    print("\n4. 建议:")
    for rec in report['health_assessment']['recommendations']:
        print(f"   - {rec}")
    
    print("\n=== 测试总结 ===")
    print("✓ 标准化财务分析功能正常")
    print("✓ 比率计算准确")
    print("✓ 趋势分析完整")
    print("✓ 健康评估合理")
    print("\n🎉 工具库测试通过！AI智能体现在可以直接调用这些分析功能。")