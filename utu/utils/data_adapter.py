"""
智能数据适配器
自动检测和转换各种数据格式，解决工具间的数据传递问题
"""

import pandas as pd
import numpy as np
import json
import logging
from typing import Dict, Any, Union, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class FinancialDataAdapter:
    """财务数据智能适配器"""

    def __init__(self):
        # 列名映射表 - 中文到英文
        self.column_mappings = {
            # 利润表
            '营业收入': 'TOTAL_OPERATE_INCOME',
            '营业总收入': 'TOTAL_OPERATE_INCOME',
            '收入': 'TOTAL_OPERATE_INCOME',
            'revenue': 'TOTAL_OPERATE_INCOME',
            '营业成本': 'COST_OF_GOODS_SOLD',
            'cost_of_goods_sold': 'COST_OF_GOODS_SOLD',
            '销售费用': 'SELLING_EXPENSES',
            'selling_expenses': 'SELLING_EXPENSES',
            '管理费用': 'ADMIN_EXPENSES',
            'admin_expenses': 'ADMIN_EXPENSES',
            '财务费用': 'FINANCING_EXPENSES',
            'financial_expenses': 'FINANCING_EXPENSES',
            '营业利润': 'OPERATING_PROFIT',
            'operating_profit': 'OPERATING_PROFIT',
            '利润总额': 'TOTAL_PROFIT',
            'total_profit': 'TOTAL_PROFIT',
            '净利润': 'NETPROFIT',
            'net_profit': 'NETPROFIT',
            '归属于母公司所有者的净利润': 'PARENT_NETPROFIT',
            'parent_net_profit': 'PARENT_NETPROFIT',
            '基本每股收益': 'BASIC_EPS',
            'basic_eps': 'BASIC_EPS',

            # 资产负债表
            '资产总计': 'TOTAL_ASSETS',
            '总资产': 'TOTAL_ASSETS',
            'total_assets': 'TOTAL_ASSETS',
            '负债合计': 'TOTAL_LIABILITIES',
            '总负债': 'TOTAL_LIABILITIES',
            'total_liabilities': 'TOTAL_LIABILITIES',
            '所有者权益合计': 'TOTAL_EQUITY',
            '股东权益合计': 'TOTAL_EQUITY',
            'total_equity': 'TOTAL_EQUITY',
            '流动资产合计': 'TOTAL_CURRENT_ASSETS',
            'current_assets': 'TOTAL_CURRENT_ASSETS',
            '非流动资产合计': 'TOTAL_NON_CURRENT_ASSETS',
            'non_current_assets': 'TOTAL_NON_CURRENT_ASSETS',
            '流动负债合计': 'TOTAL_CURRENT_LIABILITIES',
            'current_liabilities': 'TOTAL_CURRENT_LIABILITIES',
            '非流动负债合计': 'TOTAL_NON_CURRENT_LIABILITIES',
            'non_current_liabilities': 'TOTAL_NON_CURRENT_LIABILITIES',
            '货币资金': 'CASH',
            'cash': 'CASH',
            '应收账款': 'ACCOUNTS_RECEIVABLE',
            'accounts_receivable': 'ACCOUNTS_RECEIVABLE',
            '存货': 'INVENTORY',
            'inventory': 'INVENTORY',
            '固定资产': 'FIXED_ASSETS',
            'fixed_assets': 'FIXED_ASSETS',

            # 现金流量表
            '经营活动产生的现金流量净额': 'OPERATING_CASH_FLOW',
            'operating_cash_flow': 'OPERATING_CASH_FLOW',
            '投资活动产生的现金流量净额': 'INVESTING_CASH_FLOW',
            'investing_cash_flow': 'INVESTING_CASH_FLOW',
            '筹资活动产生的现金流量净额': 'FINANCING_CASH_FLOW',
            'financing_cash_flow': 'FINANCING_CASH_FLOW',
            '现金及现金等价物净增加额': 'NET_CASH_FLOW',
            'net_cash_flow': 'NET_CASH_FLOW',

            # 报告期
            '报告期': 'REPORT_DATE',
            'REPORT_DATE': 'REPORT_DATE'
        }

    def normalize_financial_data(self, data: Any) -> str:
        """
        将各种格式的财务数据标准化为JSON字符串

        Args:
            data: 输入数据（DataFrame字典、JSON字符串、普通字典等）

        Returns:
            标准化的JSON字符串
        """
        try:
            if isinstance(data, str):
                # 已经是JSON字符串，验证格式
                try:
                    parsed = json.loads(data)
                    logger.info("输入已经是JSON字符串格式")
                    return self._standardize_financial_structure(parsed)
                except json.JSONDecodeError:
                    logger.error("输入字符串不是有效的JSON格式")
                    return self._generate_error_response("INVALID_JSON", "输入字符串不是有效的JSON格式")

            elif isinstance(data, dict):
                if 'income' in data or 'balance' in data or 'cashflow' in data:
                    # DataFrame字典格式
                    logger.info("检测到DataFrame字典格式，进行序列化")
                    return self._serialize_dataframe_dict(data)
                else:
                    # 普通字典格式（扁平化指标）
                    logger.info("检测到扁平化指标字典格式")
                    return self._standardize_financial_structure(data)

            elif isinstance(data, pd.DataFrame):
                # 单个DataFrame
                logger.info("检测到单个DataFrame格式")
                return self._serialize_single_dataframe(data)

            else:
                logger.error(f"不支持的数据格式: {type(data)}")
                return self._generate_error_response("UNSUPPORTED_FORMAT", f"不支持的数据格式: {type(data)}")

        except Exception as e:
            logger.error(f"数据标准化失败: {e}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")
            return self._generate_error_response("NORMALIZATION_ERROR", str(e))

    def _serialize_dataframe_dict(self, data: Dict[str, pd.DataFrame]) -> str:
        """安全地序列化DataFrame字典"""
        try:
            serialized = {}

            for key, df in data.items():
                if isinstance(df, pd.DataFrame) and not df.empty:
                    # 标准化列名
                    df_standardized = self.standardize_column_names(df)

                    # 安全序列化DataFrame
                    serialized[key] = self._serialize_dataframe_safe(df_standardized)
                    logger.info(f"成功序列化 {key}: {df.shape} -> {len(serialized[key])} 行数据")
                else:
                    logger.warning(f"跳过空的DataFrame: {key}")
                    serialized[key] = []

            return json.dumps(serialized, ensure_ascii=False, default=str)

        except Exception as e:
            logger.error(f"DataFrame字典序列化失败: {e}")
            return self._generate_error_response("SERIALIZATION_ERROR", str(e))

    def _serialize_dataframe_safe(self, df: pd.DataFrame) -> List[Dict]:
        """安全地将DataFrame转换为可序列化的字典列表"""
        try:
            # 重置索引以避免索引问题
            df_reset = df.reset_index(drop=True)

            # 转换为记录格式
            records = []
            for _, row in df_reset.iterrows():
                record = {}
                for col in df_reset.columns:
                    value = row[col]
                    # 处理特殊数据类型
                    if pd.isna(value):
                        record[col] = None
                    elif isinstance(value, (pd.Timestamp, datetime)):
                        record[col] = value.isoformat() if hasattr(value, 'isoformat') else str(value)
                    elif isinstance(value, (np.integer, np.floating)):
                        record[col] = float(value) if not np.isnan(value) else None
                    elif isinstance(value, np.ndarray):
                        record[col] = value.tolist()
                    else:
                        record[col] = value
                records.append(record)

            return records

        except Exception as e:
            logger.error(f"DataFrame安全序列化失败: {e}")
            return []

    def _serialize_single_dataframe(self, df: pd.DataFrame) -> str:
        """序列化单个DataFrame"""
        try:
            df_standardized = self.standardize_column_names(df)
            records = self._serialize_dataframe_safe(df_standardized)
            return json.dumps(records, ensure_ascii=False, default=str)
        except Exception as e:
            logger.error(f"单个DataFrame序列化失败: {e}")
            return self._generate_error_response("SINGLE_DF_ERROR", str(e))

    def standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """标准化列名"""
        try:
            df_copy = df.copy()

            # 创建列名映射
            column_mapping = {}
            for col in df_copy.columns:
                # 查找匹配的映射
                mapped_col = self.column_mappings.get(str(col), str(col))
                if mapped_col != str(col):
                    column_mapping[col] = mapped_col
                    logger.debug(f"列名映射: {col} -> {mapped_col}")

            # 应用列名映射
            if column_mapping:
                df_copy = df_copy.rename(columns=column_mapping)
                logger.info(f"应用了 {len(column_mapping)} 个列名映射")

            return df_copy

        except Exception as e:
            logger.error(f"列名标准化失败: {e}")
            return df

    def _standardize_financial_structure(self, data: Dict) -> str:
        """标准化财务数据结构"""
        try:
            # 确保有基本的财务结构
            standardized = {}

            # 如果没有财务报表结构，创建默认结构
            if not any(key in data for key in ['income', 'balance', 'cashflow']):
                # 扁平化数据，需要转换为财务报表结构
                standardized = self._convert_flat_to_financial_structure(data)
            else:
                # 已经有财务报表结构，直接使用
                standardized = data

            return json.dumps(standardized, ensure_ascii=False, default=str)

        except Exception as e:
            logger.error(f"财务结构标准化失败: {e}")
            return self._generate_error_response("STRUCTURE_ERROR", str(e))

    def _convert_flat_to_financial_structure(self, flat_data: Dict) -> Dict:
        """将扁平化数据转换为财务报表结构"""
        try:
            # 分类指标
            income_data = {}
            balance_data = {}
            cashflow_data = {}

            # 利润表指标
            income_indicators = [
                'revenue', 'net_profit', 'gross_profit', 'operating_profit',
                '营业收入', '净利润', '毛利润', '营业利润', 'TOTAL_OPERATE_INCOME',
                'NETPROFIT', 'OPERATING_PROFIT'
            ]

            # 资产负债表指标
            balance_indicators = [
                'total_assets', 'total_liabilities', 'total_equity', 'current_assets',
                'current_liabilities', 'cash', 'accounts_receivable', 'inventory',
                '总资产', '总负债', '股东权益', '流动资产', '流动负债', '货币资金',
                '应收账款', '存货', 'TOTAL_ASSETS', 'TOTAL_LIABILITIES', 'TOTAL_EQUITY'
            ]

            # 现金流量表指标
            cashflow_indicators = [
                'operating_cash_flow', 'investing_cash_flow', 'financing_cash_flow',
                '经营活动现金流', '投资活动现金流', '筹资活动现金流',
                'OPERATING_CASH_FLOW', 'INVESTING_CASH_FLOW', 'FINANCING_CASH_FLOW'
            ]

            # 分配指标到对应报表
            for key, value in flat_data.items():
                key_lower = str(key).lower()

                if any(indicator.lower() in key_lower for indicator in income_indicators):
                    income_data[key] = value
                elif any(indicator.lower() in key_lower for indicator in balance_indicators):
                    balance_data[key] = value
                elif any(indicator.lower() in key_lower for indicator in cashflow_indicators):
                    cashflow_data[key] = value
                else:
                    # 默认放入利润表
                    income_data[key] = value

            # 构建标准化结构
            result = {}
            if income_data:
                result['income'] = income_data
            if balance_data:
                result['balance'] = balance_data
            if cashflow_data:
                result['cashflow'] = cashflow_data

            logger.info(f"扁平化数据转换完成: income({len(income_data)}), balance({len(balance_data)}), cashflow({len(cashflow_data)})")

            return result

        except Exception as e:
            logger.error(f"扁平化数据转换失败: {e}")
            return {'income': {}, 'balance': {}, 'cashflow': {}}

    def extract_key_metrics(self, financial_data: Dict) -> Dict:
        """从财务数据中提取关键指标"""
        try:
            metrics = {}

            # 处理不同格式的数据
            if isinstance(financial_data, str):
                data_dict = json.loads(financial_data)
            else:
                data_dict = financial_data

            # 从income表提取
            if 'income' in data_dict:
                income_data = data_dict['income']
                if isinstance(income_data, list) and income_data:
                    # DataFrame序列化后的格式
                    latest = income_data[0]
                    metrics.update({
                        'revenue': self._safe_get_value(latest, ['TOTAL_OPERATE_INCOME', 'revenue', '营业收入']),
                        'net_profit': self._safe_get_value(latest, ['NETPROFIT', 'net_profit', '净利润']),
                        'operating_profit': self._safe_get_value(latest, ['OPERATING_PROFIT', 'operating_profit', '营业利润'])
                    })
                elif isinstance(income_data, dict):
                    # 直接的字典格式
                    metrics.update({
                        'revenue': self._safe_get_value(income_data, ['TOTAL_OPERATE_INCOME', 'revenue', '营业收入']),
                        'net_profit': self._safe_get_value(income_data, ['NETPROFIT', 'net_profit', '净利润']),
                        'operating_profit': self._safe_get_value(income_data, ['OPERATING_PROFIT', 'operating_profit', '营业利润'])
                    })

            # 从balance表提取
            if 'balance' in data_dict:
                balance_data = data_dict['balance']
                if isinstance(balance_data, list) and balance_data:
                    latest = balance_data[0]
                    metrics.update({
                        'total_assets': self._safe_get_value(latest, ['TOTAL_ASSETS', 'total_assets', '总资产']),
                        'total_liabilities': self._safe_get_value(latest, ['TOTAL_LIABILITIES', 'total_liabilities', '总负债']),
                        'current_assets': self._safe_get_value(latest, ['TOTAL_CURRENT_ASSETS', 'current_assets', '流动资产']),
                        'current_liabilities': self._safe_get_value(latest, ['TOTAL_CURRENT_LIABILITIES', 'current_liabilities', '流动负债'])
                    })
                elif isinstance(balance_data, dict):
                    metrics.update({
                        'total_assets': self._safe_get_value(balance_data, ['TOTAL_ASSETS', 'total_assets', '总资产']),
                        'total_liabilities': self._safe_get_value(balance_data, ['TOTAL_LIABILITIES', 'total_liabilities', '总负债']),
                        'current_assets': self._safe_get_value(balance_data, ['TOTAL_CURRENT_ASSETS', 'current_assets', '流动资产']),
                        'current_liabilities': self._safe_get_value(balance_data, ['TOTAL_CURRENT_LIABILITIES', 'current_liabilities', '流动负债'])
                    })

            # 从cashflow表提取
            if 'cashflow' in data_dict:
                cashflow_data = data_dict['cashflow']
                if isinstance(cashflow_data, list) and cashflow_data:
                    latest = cashflow_data[0]
                    metrics.update({
                        'operating_cash_flow': self._safe_get_value(latest, ['OPERATING_CASH_FLOW', 'operating_cash_flow', '经营活动现金流'])
                    })
                elif isinstance(cashflow_data, dict):
                    metrics.update({
                        'operating_cash_flow': self._safe_get_value(cashflow_data, ['OPERATING_CASH_FLOW', 'operating_cash_flow', '经营活动现金流'])
                    })

            # 过滤掉None值
            metrics = {k: v for k, v in metrics.items() if v is not None}
            logger.info(f"提取到 {len(metrics)} 个关键指标: {list(metrics.keys())}")

            return metrics

        except Exception as e:
            logger.error(f"关键指标提取失败: {e}")
            return {}

    def _safe_get_value(self, data: Dict, possible_keys: List[str]) -> Optional[float]:
        """安全地从字典中获取值"""
        for key in possible_keys:
            if key in data:
                value = data[key]
                try:
                    if value is None or (isinstance(value, float) and np.isnan(value)):
                        continue
                    return float(value)
                except (ValueError, TypeError):
                    continue
        return None

    def _generate_error_response(self, error_code: str, error_msg: str) -> str:
        """生成错误响应"""
        error_response = {
            'error': True,
            'error_code': error_code,
            'message': error_msg,
            'suggestions': [
                '检查数据格式是否正确',
                '确保数据包含必要的财务指标',
                '参考标准格式示例'
            ],
            'example': {
                'income': {
                    'revenue': 1000.0,
                    'net_profit': 100.0
                },
                'balance': {
                    'total_assets': 5000.0,
                    'total_liabilities': 3000.0
                }
            }
        }
        return json.dumps(error_response, ensure_ascii=False)


# 创建全局实例
_data_adapter = None

def get_data_adapter() -> FinancialDataAdapter:
    """获取数据适配器实例"""
    global _data_adapter
    if _data_adapter is None:
        _data_adapter = FinancialDataAdapter()
    return _data_adapter