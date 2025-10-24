"""
数据验证和格式转换模块
为多智能体系统提供统一的数据格式验证和转换功能
"""

import json
import pandas as pd
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """验证结果数据类"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    data: Optional[Dict[str, Any]] = None
    normalized_data: Optional[Dict[str, Any]] = None


class DataValidationError(Exception):
    """数据验证异常"""
    pass


class DataValidator:
    """数据验证器"""

    @staticmethod
    def validate_financial_data(financial_data: Union[str, Dict[str, Any]]) -> ValidationResult:
        """
        验证财务数据格式

        Args:
            financial_data: JSON字符串或字典格式的财务数据

        Returns:
            ValidationResult: 验证结果
        """
        errors = []
        warnings = []

        try:
            # 如果是字符串，尝试解析为JSON
            if isinstance(financial_data, str):
                try:
                    data = json.loads(financial_data)
                except json.JSONDecodeError as e:
                    return ValidationResult(
                        is_valid=False,
                        errors=[f"JSON解析失败: {str(e)}"],
                        warnings=[]
                    )
            else:
                data = financial_data

            # 基本结构验证
            if not isinstance(data, dict):
                errors.append("数据必须是字典格式")
                return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

            # 检查必需的财务数据字段
            required_fields = ['income_statement', 'balance_sheet']
            for field in required_fields:
                if field not in data:
                    errors.append(f"缺少必需字段: {field}")

            # 验证历史数据格式
            if 'historical_data' in data:
                historical_data = data['historical_data']
                if not isinstance(historical_data, dict):
                    errors.append("historical_data必须是字典格式")
                else:
                    # 检查历史数据是否包含数组格式
                    for year, year_data in historical_data.items():
                        if not isinstance(year_data, dict):
                            warnings.append(f"年份 {year} 的数据格式不正确")

            # 如果没有错误，尝试标准化数据格式
            if not errors:
                normalized_data = DataValidator.normalize_financial_data(data)
                return ValidationResult(
                    is_valid=True,
                    errors=[],
                    warnings=warnings,
                    data=data,
                    normalized_data=normalized_data
                )
            else:
                return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        except Exception as e:
            errors.append(f"数据验证过程中发生错误: {str(e)}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    @staticmethod
    def normalize_financial_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        标准化财务数据格式

        Args:
            data: 原始财务数据

        Returns:
            Dict[str, Any]: 标准化后的数据
        """
        normalized = {
            'company_name': data.get('company_name', 'Unknown'),
            'stock_code': data.get('stock_code', ''),
            'periods': [],
            'income_statement': {
                'revenue': [],
                'net_profit': [],
                'operating_profit': [],
                'gross_profit': []
            },
            'balance_sheet': {
                'total_assets': [],
                'total_liabilities': [],
                'equity': []
            },
            'profitability_ratios': {
                'net_profit_margin': [],
                'roe': [],
                'roa': [],
                'gross_profit_margin': []
            }
        }

        # 处理历史数据
        if 'historical_data' in data:
            historical_data = data['historical_data']
            years = sorted(historical_data.keys())

            for year in years:
                year_data = historical_data[year]
                normalized['periods'].append(year)

                # 提取利润表数据
                if 'revenue' in year_data:
                    normalized['income_statement']['revenue'].append(year_data['revenue'])
                if 'net_profit' in year_data:
                    normalized['income_statement']['net_profit'].append(year_data['net_profit'])
                if 'operating_profit' in year_data:
                    normalized['income_statement']['operating_profit'].append(year_data['operating_profit'])

                # 提取资产负债表数据
                if 'total_assets' in year_data:
                    normalized['balance_sheet']['total_assets'].append(year_data['total_assets'])
                if 'equity' in year_data:
                    normalized['balance_sheet']['equity'].append(year_data['equity'])

                # 提取盈利能力指标
                if 'roe' in year_data:
                    normalized['profitability_ratios']['roe'].append(year_data['roe'])
                if 'roa' in year_data:
                    normalized['profitability_ratios']['roa'].append(year_data['roa'])
                if 'net_margin' in year_data:
                    normalized['profitability_ratios']['net_profit_margin'].append(year_data['net_margin'])

        # 处理数组格式的数据
        if 'periods' in data and 'income_statement' in data:
            periods = data['periods']
            income_stmt = data['income_statement']

            normalized['periods'] = periods

            for key in ['revenue', 'net_profit', 'operating_profit']:
                if key in income_stmt and isinstance(income_stmt[key], list):
                    normalized['income_statement'][key] = income_stmt[key]

        # 处理平衡表数据
        if 'balance_sheet' in data:
            balance_sheet = data['balance_sheet']
            for key in ['total_assets', 'total_liabilities', 'equity']:
                if key in balance_sheet and isinstance(balance_sheet[key], list):
                    normalized['balance_sheet'][key] = balance_sheet[key]

        # 处理比率数据
        if 'profitability_ratios' in data:
            ratios = data['profitability_ratios']
            for key in ['net_profit_margin', 'roe', 'roa', 'gross_profit_margin']:
                if key in ratios and isinstance(ratios[key], list):
                    normalized['profitability_ratios'][key] = ratios[key]

        return normalized

    @staticmethod
    def create_dataframe_from_normalized(normalized_data: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        从标准化数据创建DataFrame

        Args:
            normalized_data: 标准化的财务数据

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: (利润表, 资产负债表, 比率表)
        """
        periods = normalized_data.get('periods', [])

        if not periods:
            # 如果没有期间数据，使用默认期间
            periods = ['Current']

        # 创建利润表DataFrame
        income_data = {
            'Period': periods,
            'Revenue': normalized_data['income_statement']['revenue'] or [0] * len(periods),
            'Net_Profit': normalized_data['income_statement']['net_profit'] or [0] * len(periods),
            'Operating_Profit': normalized_data['income_statement']['operating_profit'] or [0] * len(periods)
        }
        income_df = pd.DataFrame(income_data)

        # 创建资产负债表DataFrame
        balance_data = {
            'Period': periods,
            'Total_Assets': normalized_data['balance_sheet']['total_assets'] or [0] * len(periods),
            'Equity': normalized_data['balance_sheet']['equity'] or [0] * len(periods)
        }
        balance_df = pd.DataFrame(balance_data)

        # 创建比率表DataFrame
        ratios_data = {
            'Period': periods,
            'ROE': normalized_data['profitability_ratios']['roe'] or [0] * len(periods),
            'ROA': normalized_data['profitability_ratios']['roa'] or [0] * len(periods),
            'Net_Profit_Margin': normalized_data['profitability_ratios']['net_profit_margin'] or [0] * len(periods)
        }
        ratios_df = pd.DataFrame(ratios_data)

        return income_df, balance_df, ratios_df

    @staticmethod
    def validate_chart_data(chart_data: Union[str, Dict[str, Any]], min_data_points: int = 2) -> ValidationResult:
        """
        验证图表数据格式

        Args:
            chart_data: 图表数据
            min_data_points: 最少数据点数量

        Returns:
            ValidationResult: 验证结果
        """
        errors = []
        warnings = []

        try:
            # 解析JSON数据
            if isinstance(chart_data, str):
                try:
                    data = json.loads(chart_data)
                except json.JSONDecodeError as e:
                    return ValidationResult(
                        is_valid=False,
                        errors=[f"图表数据JSON解析失败: {str(e)}"],
                        warnings=[]
                    )
            else:
                data = chart_data

            # 验证基本结构
            if not isinstance(data, dict):
                errors.append("图表数据必须是字典格式")
                return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

            # 检查是否有数据
            if not data:
                errors.append("图表数据为空")
                return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

            # 验证数据点数量
            for dataset_name, dataset in data.items():
                if isinstance(dataset, dict):
                    # 检查数值数组
                    for key, values in dataset.items():
                        if isinstance(values, list):
                            if len(values) < min_data_points:
                                warnings.append(f"数据集 '{dataset_name}' 的 '{key}' 只有 {len(values)} 个数据点，建议至少 {min_data_points} 个")
                        elif isinstance(values, (int, float)):
                            # 单个数值点
                            if min_data_points > 1:
                                warnings.append(f"数据集 '{dataset_name}' 的 '{key}' 只有 1 个数据点，建议至少 {min_data_points} 个")
                elif isinstance(dataset, list):
                    if len(dataset) < min_data_points:
                        warnings.append(f"数据集 '{dataset_name}' 只有 {len(dataset)} 个数据点，建议至少 {min_data_points} 个")

            # 如果没有错误，数据有效
            return ValidationResult(
                is_valid=True,
                errors=[],
                warnings=warnings,
                data=data
            )

        except Exception as e:
            errors.append(f"图表数据验证过程中发生错误: {str(e)}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    @staticmethod
    def safe_execute_python_code(code: str, context: Dict[str, Any] = None) -> ValidationResult:
        """
        安全执行Python代码

        Args:
            code: 要执行的Python代码
            context: 执行上下文变量

        Returns:
            ValidationResult: 执行结果
        """
        errors = []
        warnings = []

        try:
            # 准备执行环境
            exec_context = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'range': range,
                    'enumerate': enumerate,
                    'zip': zip,
                    'max': max,
                    'min': min,
                    'sum': sum,
                    'abs': abs,
                    'round': round,
                    'sorted': sorted,
                    'reversed': reversed,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                },
                'plt': None,  # 需要在调用方提供
                'np': None,   # 需要在调用方提供
                'pd': None,   # 需要在调用方提供
            }

            # 添加用户提供的上下文
            if context:
                exec_context.update(context)

            # 执行代码
            exec(code, exec_context)

            return ValidationResult(
                is_valid=True,
                errors=[],
                warnings=warnings
            )

        except NameError as e:
            errors.append(f"变量未定义: {str(e)}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        except SyntaxError as e:
            errors.append(f"代码语法错误: {str(e)}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        except Exception as e:
            errors.append(f"代码执行错误: {str(e)}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)


def validate_and_normalize_financial_data(financial_data: Union[str, Dict[str, Any]]) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    验证并标准化财务数据的便捷函数

    Args:
        financial_data: 财务数据

    Returns:
        Tuple[bool, Dict[str, Any], List[str]]: (是否有效, 标准化数据, 错误列表)
    """
    result = DataValidator.validate_financial_data(financial_data)

    if result.is_valid and result.normalized_data:
        return True, result.normalized_data, result.errors
    else:
        return False, result.data or {}, result.errors


def create_safe_dataframe(data: Dict[str, Any], fallback_index: List[str] = None) -> Optional[pd.DataFrame]:
    """
    安全创建DataFrame的便捷函数

    Args:
        data: 数据字典
        fallback_index: 备用索引

    Returns:
        Optional[pd.DataFrame]: 创建的DataFrame或None
    """
    try:
        df = pd.DataFrame(data)

        # 如果DataFrame为空，添加备用索引
        if df.empty and fallback_index:
            df = pd.DataFrame(data, index=fallback_index)

        return df
    except Exception as e:
        logger.error(f"创建DataFrame失败: {str(e)}")
        return None