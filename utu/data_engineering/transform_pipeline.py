"""
数据转换管道
提供财务数据的格式转换、标准化和结构化功能
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class TransformResult:
    """数据转换结果"""
    success: bool
    transformed_data: Optional[Dict[str, Any]] = None
    original_data: Optional[Dict[str, Any]] = None
    transformation_log: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 转换统计
    fields_transformed: int = 0
    fields_added: int = 0
    fields_removed: int = 0
    values_converted: int = 0
    conversion_rate: float = 0.0


class DataTransformPipeline:
    """数据转换管道"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化数据转换管道"""
        self.config = config or {}
        
        # 财务字段映射配置
        self.field_mappings = {
            # 利润表字段映射
            'income_statement': {
                '营业收入': ['revenue', 'operating_revenue', 'sales_revenue', '主营业务收入', '营业总收入'],
                '营业成本': ['cost_of_goods_sold', 'operating_cost', 'cogs', '主营业务成本'],
                '营业利润': ['operating_profit', 'operating_income', 'operating_result'],
                '利润总额': ['total_profit', 'profit_before_tax', 'pre_tax_profit'],
                '净利润': ['net_profit', 'net_income', 'net_earnings'],
                '毛利润': ['gross_profit', 'gross_income', '毛利'],
                '息税前利润': ['ebit', 'earnings_before_interest_tax'],
                '息税折旧摊销前利润': ['ebitda']
            },
            # 资产负债表字段映射
            'balance_sheet': {
                '总资产': ['total_assets', 'assets', 'asset_total'],
                '总负债': ['total_liabilities', 'liabilities', 'liability_total'],
                '所有者权益': ['total_equity', 'shareholders_equity', 'owner_equity', '股东权益'],
                '流动资产': ['current_assets', 'current_asset_total'],
                '流动负债': ['current_liabilities', 'current_liability_total'],
                '应收账款': ['accounts_receivable', 'ar'],
                '存货': ['inventory', 'inventories'],
                '固定资产': ['fixed_assets', 'property_plant_equipment', 'ppe'],
                '货币资金': ['cash_and_cash_equivalents', 'cash', '货币资金'],
                '无形资产': ['intangible_assets'],
                '递延所得税资产': ['deferred_tax_assets']
            },
            # 现金流量表字段映射
            'cash_flow': {
                '经营活动现金流量净额': ['operating_cash_flow', 'cash_from_operations', 'ocf'],
                '投资活动现金流量净额': ['investing_cash_flow', 'cash_from_investing', 'icf'],
                '筹资活动现金流量净额': ['financing_cash_flow', 'cash_from_financing', 'fcf'],
                '现金及现金等价物净增加额': ['net_change_in_cash', 'change_in_cash'],
                '期初现金余额': ['beginning_cash_balance'],
                '期末现金余额': ['ending_cash_balance']
            }
        }
        
        # 数据类型转换规则
        self.type_conversion_rules = {
            'numeric_fields': {
                'pattern': r'(收入|利润|资产|负债|权益|现金|流量|费用|成本)',
                'target_type': 'float',
                'multipliers': {
                    '万': 10000,
                    '亿': 100000000,
                    '千元': 1000,
                    '百万': 1000000
                }
            },
            'percentage_fields': {
                'pattern': r'(率|ratio|margin)',
                'target_type': 'float',
                'multipliers': {
                    '%': 0.01
                }
            },
            'date_fields': {
                'pattern': r'(日期|时间|date|time)',
                'target_type': 'datetime',
                'formats': ['%Y-%m-%d', '%Y/%m/%d', '%Y%m%d']
            }
        }
    
    def transform_financial_data(self, 
                               financial_data: Union[str, Dict[str, Any]], 
                               target_format: str = "data_analysis_agent_compatible") -> TransformResult:
        """
        转换财务数据格式
        
        Args:
            financial_data: 原始财务数据
            target_format: 目标格式
            
        Returns:
            TransformResult: 转换结果
        """
        transformation_log = []
        errors = []
        warnings = []
        metadata = {
            'transformation_time': datetime.now().isoformat(),
            'original_format': 'unknown',
            'target_format': target_format,
            'pipeline_version': '1.0'
        }
        
        try:
            # 解析输入数据
            if isinstance(financial_data, str):
                try:
                    data = json.loads(financial_data)
                    transformation_log.append("成功解析JSON数据")
                except json.JSONDecodeError as e:
                    errors.append(f"JSON解析失败: {str(e)}")
                    return TransformResult(
                        success=False,
                        errors=errors,
                        transformation_log=transformation_log,
                        metadata=metadata
                    )
            else:
                data = financial_data
                transformation_log.append("使用字典格式数据")
            
            # 识别原始数据格式
            original_format = self._detect_data_format(data)
            metadata['original_format'] = original_format
            transformation_log.append(f"识别数据格式: {original_format}")
            
            # 复制原始数据
            original_data = json.loads(json.dumps(data, ensure_ascii=False))
            
            # 执行转换步骤
            transformed_data = data.copy()
            fields_transformed = 0
            fields_added = 0
            fields_removed = 0
            values_converted = 0
            
            # 步骤1: 标准化财务报表结构
            step1_result = self._standardize_financial_statements(transformed_data)
            transformed_data = step1_result['data']
            transformation_log.extend(step1_result['log'])
            fields_transformed += step1_result.get('fields_transformed', 0)
            fields_added += step1_result.get('fields_added', 0)
            
            # 步骤2: 字段名映射和标准化
            step2_result = self._map_and_normalize_field_names(transformed_data)
            transformed_data = step2_result['data']
            transformation_log.extend(step2_result['log'])
            fields_transformed += step2_result.get('fields_transformed', 0)
            values_converted += step2_result.get('values_converted', 0)
            
            # 步骤3: 处理历史数据
            step3_result = self._process_historical_data(transformed_data)
            transformed_data = step3_result['data']
            transformation_log.extend(step3_result['log'])
            fields_transformed += step3_result.get('fields_transformed', 0)
            fields_added += step3_result.get('fields_added', 0)
            
            # 步骤4: 数据类型转换
            step4_result = self._convert_data_types(transformed_data)
            transformed_data = step4_result['data']
            transformation_log.extend(step4_result['log'])
            values_converted += step4_result.get('values_converted', 0)
            
            # 步骤5: 格式适配
            step5_result = self._adapt_to_target_format(transformed_data, target_format)
            transformed_data = step5_result['data']
            transformation_log.extend(step5_result['log'])
            fields_added += step5_result.get('fields_added', 0)
            
            # 步骤6: 添加元数据
            metadata_result = self._add_metadata(transformed_data, metadata, original_format)
            transformed_data = metadata_result['data']
            transformation_log.extend(metadata_result['log'])
            
            # 计算转换统计
            total_fields = len(self._flatten_dict(original_data))
            conversion_rate = (fields_transformed + fields_added) / max(total_fields, 1) * 100
            
            # 验证转换结果
            validation_result = self._validate_transformation(transformed_data, target_format)
            if not validation_result['valid']:
                warnings.extend(validation_result['warnings'])
            
            transformation_log.append(f"转换完成 - 处理字段: {fields_transformed}, 新增字段: {fields_added}, 转换值: {values_converted}")
            
            return TransformResult(
                success=True,
                transformed_data=transformed_data,
                original_data=original_data,
                transformation_log=transformation_log,
                errors=errors,
                warnings=warnings,
                metadata=metadata,
                fields_transformed=fields_transformed,
                fields_added=fields_added,
                fields_removed=fields_removed,
                values_converted=values_converted,
                conversion_rate=conversion_rate
            )
            
        except Exception as e:
            logger.error(f"数据转换失败: {str(e)}")
            errors.append(f"数据转换过程中发生错误: {str(e)}")
            transformation_log.append(f"转换失败: {str(e)}")
            
            return TransformResult(
                success=False,
                original_data=data if 'data' in locals() else None,
                transformation_log=transformation_log,
                errors=errors,
                metadata=metadata
            )
    
    def _detect_data_format(self, data: Dict[str, Any]) -> str:
        """检测数据格式"""
        if not isinstance(data, dict):
            return "invalid"
        
        # 检查中文格式
        chinese_keys = ['利润表', '资产负债表', '现金流量表', '历史数据']
        if any(key in data for key in chinese_keys):
            return "chinese_financial_format"
        
        # 检查标准英文格式
        english_keys = ['income_statement', 'balance_sheet', 'cash_flow', 'historical_data']
        if any(key in data for key in english_keys):
            return "standard_financial_format"
        
        # 检查数组格式
        if 'years' in data and 'data' in data:
            return "array_format"
        
        # 检查比率格式
        if 'ratios' in data or 'profitability' in data or 'solvency' in data:
            return "financial_ratios_format"
        
        # 检查历史数据格式
        if 'historical_data' in data:
            return "historical_data_format"
        
        return "unknown_format"
    
    def _standardize_financial_statements(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """标准化财务报表结构"""
        log = []
        fields_transformed = 0
        fields_added = 0
        transformed_data = data.copy()
        
        # 中文到英文的报表映射
        statement_mapping = {
            '利润表': 'income_statement',
            '资产负债表': 'balance_sheet',
            '现金流量表': 'cash_flow',
            '历史数据': 'historical_data',
            '关键指标': 'key_metrics'
        }
        
        for chinese_name, english_name in statement_mapping.items():
            if chinese_name in transformed_data and english_name not in transformed_data:
                transformed_data[english_name] = transformed_data[chinese_name]
                del transformed_data[chinese_name]
                log.append(f"映射报表名称: {chinese_name} -> {english_name}")
                fields_transformed += 1
            elif chinese_name in transformed_data and english_name in transformed_data:
                # 如果两者都存在，合并数据
                chinese_data = transformed_data[chinese_name]
                english_data = transformed_data[english_name]
                if isinstance(chinese_data, dict) and isinstance(english_data, dict):
                    merged_data = {**english_data, **chinese_data}
                    transformed_data[english_name] = merged_data
                    del transformed_data[chinese_name]
                    log.append(f"合并报表数据: {chinese_name} + {english_name}")
                    fields_transformed += 1
        
        # 确保基本结构存在
        basic_statements = ['income_statement', 'balance_sheet', 'cash_flow']
        for statement in basic_statements:
            if statement not in transformed_data:
                transformed_data[statement] = {}
                log.append(f"创建空的{statement}结构")
                fields_added += 1
        
        return {
            'data': transformed_data,
            'log': log,
            'fields_transformed': fields_transformed,
            'fields_added': fields_added
        }
    
    def _map_and_normalize_field_names(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """映射和标准化字段名"""
        log = []
        fields_transformed = 0
        values_converted = 0
        transformed_data = data.copy()
        
        for statement_name, statement_data in transformed_data.items():
            if isinstance(statement_data, dict) and statement_name in self.field_mappings:
                field_mapping = self.field_mappings[statement_name]
                new_statement_data = {}
                
                for field_name, field_value in statement_data.items():
                    # 查找标准字段名
                    standard_name = self._find_standard_field_name(field_name, field_mapping)
                    
                    if standard_name and standard_name != field_name:
                        new_statement_data[standard_name] = field_value
                        log.append(f"映射字段: {statement_name}.{field_name} -> {standard_name}")
                        fields_transformed += 1
                    else:
                        new_statement_data[field_name] = field_value
                
                transformed_data[statement_name] = new_statement_data
        
        return {
            'data': transformed_data,
            'log': log,
            'fields_transformed': fields_transformed,
            'values_converted': values_converted
        }
    
    def _find_standard_field_name(self, field_name: str, field_mapping: Dict[str, List[str]]) -> Optional[str]:
        """查找标准字段名"""
        # 直接匹配
        if field_name in field_mapping:
            return field_name
        
        # 反向查找
        for standard_name, aliases in field_mapping.items():
            if field_name in aliases:
                return standard_name
        
        # 模糊匹配
        field_lower = field_name.lower()
        for standard_name, aliases in field_mapping.items():
            if any(field_lower in alias.lower() for alias in aliases):
                return standard_name
        
        return None
    
    def _process_historical_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理历史数据"""
        log = []
        fields_transformed = 0
        fields_added = 0
        transformed_data = data.copy()
        
        if 'historical_data' in transformed_data:
            historical_data = transformed_data['historical_data']
            
            if isinstance(historical_data, dict):
                processed_historical = {}
                
                for year_key, year_data in historical_data.items():
                    # 标准化年份键名
                    if str(year_key).isdigit() and len(str(year_key)) == 4:
                        processed_year_data = year_data.copy()
                        
                        # 应用字段映射到年份数据
                        if isinstance(year_data, dict):
                            for statement_name, statement_mapping in self.field_mappings.items():
                                if any(field in year_data for field in statement_mapping.values()):
                                    # 创建或更新对应statement的数据
                                    if statement_name not in processed_historical:
                                        processed_historical[statement_name] = {}
                                    
                                    for field_name, field_value in year_data.items():
                                        standard_name = self._find_standard_field_name(field_name, statement_mapping)
                                        if standard_name:
                                            processed_historical[statement_name][standard_name] = field_value
                                            log.append(f"历史数据字段映射: {year_key}.{field_name} -> {standard_name}")
                                            fields_transformed += 1
                        
                        processed_historical[str(year_key)] = processed_year_data
                    else:
                        processed_historical[str(year_key)] = year_data
                
                transformed_data['historical_data'] = processed_historical
                log.append("历史数据处理完成")
        
        return {
            'data': transformed_data,
            'log': log,
            'fields_transformed': fields_transformed,
            'fields_added': fields_added
        }
    
    def _convert_data_types(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """转换数据类型"""
        log = []
        values_converted = 0
        transformed_data = data.copy()
        
        def convert_value(key: str, value: Any) -> Any:
            nonlocal values_converted
            
            if isinstance(value, str):
                # 转换数值类型
                for rule_name, rule in self.type_conversion_rules.items():
                    if 'pattern' in rule and re.search(rule['pattern'], key, re.IGNORECASE):
                        target_type = rule['target_type']
                        
                        if target_type == 'float':
                            # 移除单位并转换
                            converted_value = value
                            for unit, multiplier in rule.get('multipliers', {}).items():
                                if unit in converted_value:
                                    converted_value = converted_value.replace(unit, '')
                                    converted_value = float(converted_value) * multiplier
                                    values_converted += 1
                                    log.append(f"数值类型转换: {key} {value} -> {converted_value}")
                                    return converted_value
                            
                            # 尝试直接转换为float
                            try:
                                converted_value = float(converted_value)
                                values_converted += 1
                                return converted_value
                            except ValueError:
                                pass
                        
                        elif target_type == 'datetime':
                            for fmt in rule.get('formats', []):
                                try:
                                    converted_value = datetime.strptime(value, fmt)
                                    values_converted += 1
                                    log.append(f"日期类型转换: {key} {value} -> {converted_value}")
                                    return converted_value
                                except ValueError:
                                    pass
            
            return value
        
        # 递归转换所有值
        transformed_data = self._recursive_convert(transformed_data, convert_value)
        
        return {
            'data': transformed_data,
            'log': log,
            'values_converted': values_converted
        }
    
    def _recursive_convert(self, data: Any, convert_func) -> Any:
        """递归转换数据"""
        if isinstance(data, dict):
            return {key: self._recursive_convert(value, convert_func) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._recursive_convert(item, convert_func) for item in data]
        else:
            return convert_func("", data)
    
    def _adapt_to_target_format(self, data: Dict[str, Any], target_format: str) -> Dict[str, Any]:
        """适配到目标格式"""
        log = []
        fields_added = 0
        transformed_data = data.copy()
        
        if target_format == "data_analysis_agent_compatible":
            # 为DataAnalysisAgent优化的格式
            adapted_data = self._adapt_for_data_analysis_agent(transformed_data)
            log.append("适配DataAnalysisAgent格式")
            fields_added = len(adapted_data) - len(transformed_data)
            transformed_data = adapted_data
        
        elif target_format == "chart_generator_compatible":
            # 为ChartGeneratorAgent优化的格式
            adapted_data = self._adapt_for_chart_generator(transformed_data)
            log.append("适配ChartGeneratorAgent格式")
            fields_added = len(adapted_data) - len(transformed_data)
            transformed_data = adapted_data
        
        return {
            'data': transformed_data,
            'log': log,
            'fields_added': fields_added
        }
    
    def _adapt_for_data_analysis_agent(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """适配DataAnalysisAgent格式"""
        adapted_data = data.copy()
        
        # 确保历史数据格式正确
        if 'historical_data' in adapted_data:
            historical_data = adapted_data['historical_data']
            if isinstance(historical_data, dict):
                # 检查是否需要转换为DataAnalysisAgent期望的格式
                years = [key for key in historical_data.keys() if str(key).isdigit() and len(str(key)) == 4]
                
                if years:
                    # 创建years数组格式（DataAnalysisAgent支持）
                    years_list = [int(year) for year in sorted(years, reverse=True)]
                    
                    # 如果需要，可以创建数组格式的数据
                    # 但目前保持原格式，因为DataAnalysisAgent已经被修复支持
                    
        # 添加数据质量标记
        adapted_data['_data_quality'] = {
            'processed_by': 'DataTransformPipeline',
            'processing_time': datetime.now().isoformat(),
            'format_compatibility': 'data_analysis_agent_compatible',
            'quality_score': 85  # 默认质量分数
        }
        
        return adapted_data
    
    def _adapt_for_chart_generator(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """适配ChartGeneratorAgent格式"""
        adapted_data = data.copy()
        
        # 为图表生成添加格式化的比率数据
        if 'income_statement' in adapted_data or 'balance_sheet' in adapted_data:
            # 创建图表友好的数据结构
            chart_data = {
                'profitability_metrics': {},
                'solvency_metrics': {},
                'efficiency_metrics': {}
            }
            
            # 从现有数据提取图表指标
            income_stmt = adapted_data.get('income_statement', {})
            balance_sheet = adapted_data.get('balance_sheet', {})
            
            # 盈利能力指标
            if 'revenue' in income_stmt and 'net_profit' in income_stmt:
                revenue = income_stmt['revenue']
                net_profit = income_stmt['net_profit']
                if revenue > 0:
                    chart_data['profitability_metrics']['net_profit_margin'] = (net_profit / revenue) * 100
            
            # 偿债能力指标
            if 'total_assets' in balance_sheet and 'total_liabilities' in balance_sheet:
                total_assets = balance_sheet['total_assets']
                total_liabilities = balance_sheet['total_liabilities']
                if total_assets > 0:
                    chart_data['solvency_metrics']['debt_to_asset_ratio'] = (total_liabilities / total_assets) * 100
            
            adapted_data['chart_data'] = chart_data
        
        return adapted_data
    
    def _add_metadata(self, data: Dict[str, Any], metadata: Dict[str, Any], original_format: str) -> Dict[str, Any]:
        """添加元数据"""
        log = []
        
        # 添加转换元数据
        data['_transformation_metadata'] = {
            **metadata,
            'original_format': original_format,
            'transformation_pipeline': 'DataTransformPipeline',
            'data_schema_version': '1.0',
            'quality_indicators': {
                'has_income_statement': 'income_statement' in data,
                'has_balance_sheet': 'balance_sheet' in data,
                'has_cash_flow': 'cash_flow' in data,
                'has_historical_data': 'historical_data' in data
            }
        }
        
        log.append("添加转换元数据")
        
        return {
            'data': data,
            'log': log
        }
    
    def _validate_transformation(self, data: Dict[str, Any], target_format: str) -> Dict[str, Any]:
        """验证转换结果"""
        warnings = []
        
        # 基本结构验证
        required_sections = ['income_statement', 'balance_sheet']
        for section in required_sections:
            if section not in data or not data[section]:
                warnings.append(f"缺少{section}数据")
        
        # 数据完整性验证
        if 'historical_data' in data:
            historical_data = data['historical_data']
            if isinstance(historical_data, dict):
                if len(historical_data) == 0:
                    warnings.append("历史数据为空")
        
        # 数值验证
        for section_name, section_data in data.items():
            if isinstance(section_data, dict) and section_name != '_transformation_metadata':
                for field_name, field_value in section_data.items():
                    if isinstance(field_value, (int, float)):
                        if abs(field_value) > 1e15:  # 数值过大
                            warnings.append(f"{section_name}.{field_name}数值异常大: {field_value}")
                        elif abs(field_value) < 0.01 and field_value != 0:  # 数值过小
                            if 'ratio' not in field_name.lower() and 'margin' not in field_name.lower():
                                warnings.append(f"{section_name}.{field_name}数值异常小: {field_value}")
        
        return {
            'valid': len(warnings) == 0,
            'warnings': warnings
        }
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """扁平化字典"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)