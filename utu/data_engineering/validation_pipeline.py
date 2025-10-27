"""
数据验证管道
扩展现有data_validator.py，提供更全面的数据验证功能
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import re
import logging

from ...utils.data_validator import ValidationResult, DataValidator

logger = logging.getLogger(__name__)


@dataclass
class EnhancedValidationResult:
    """增强验证结果数据类"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    data: Optional[Dict[str, Any]] = None
    normalized_data: Optional[Dict[str, Any]] = None
    
    # 增强字段
    quality_score: float = 0.0
    data_type: str = "unknown"
    completeness_score: float = 0.0
    consistency_score: float = 0.0
    validity_score: float = 0.0
    processing_suggestions: List[str] = field(default_factory=list)
    detected_issues: List[str] = field(default_factory=list)
    
    def calculate_overall_score(self) -> float:
        """计算总体质量分数"""
        weights = {
            'completeness': 0.3,
            'consistency': 0.2,
            'validity': 0.3,
            'accuracy': 0.2
        }
        return (
            self.completeness_score * weights['completeness'] +
            self.consistency_score * weights['consistency'] +
            self.validity_score * weights['validity'] +
            min(100, 100 - len(self.errors) * 10) * weights['accuracy']
        )


class DataValidationPipeline:
    """数据验证管道 - 基于现有DataValidator扩展"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化数据验证管道"""
        self.config = config or {}
        self.base_validator = DataValidator()
        
        # 财务数据验证规则
        self.financial_validation_rules = {
            'required_sections': {
                'income_statement': ['营业收入', '净利润'],
                'balance_sheet': ['总资产', '总负债', '所有者权益'],
                'cash_flow': ['经营活动现金流量净额'],
                'historical_data': []  # 可选
            },
            'field_mappings': {
                # 利润表字段映射
                'income_statement': {
                    '营业收入': ['revenue', 'operating_revenue', 'sales_revenue', '主营业务收入', '营业总收入'],
                    '净利润': ['net_profit', 'net_income', 'net_earnings', '利润总额'],
                    '营业成本': ['cost_of_goods_sold', 'operating_cost', 'cogs', '主营业务成本'],
                    '营业利润': ['operating_profit', 'operating_income', 'operating_result'],
                    '毛利润': ['gross_profit', 'gross_income', '毛利']
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
                    '固定资产': ['fixed_assets', 'property_plant_equipment', 'ppe']
                },
                # 现金流量表字段映射
                'cash_flow': {
                    '经营活动现金流量净额': ['operating_cash_flow', 'cash_from_operations', 'ocf'],
                    '投资活动现金流量净额': ['investing_cash_flow', 'cash_from_investing', 'icf'],
                    '筹资活动现金流量净额': ['financing_cash_flow', 'cash_from_financing', 'fcf'],
                    '现金及现金等价物净增加额': ['net_change_in_cash', 'change_in_cash']
                }
            },
            'data_types': {
                'monetary_fields': {
                    'min_value': 0,  # 货币字段通常非负
                    'max_value': 1e15,  # 最大值限制
                    'allow_negative': ['净利润', '现金流量净额']  # 允许负值的字段
                },
                'percentage_fields': {
                    'min_value': -1,  # 百分比字段最小值
                    'max_value': 10   # 百分比字段最大值（1000%）
                }
            }
        }
    
    def validate_financial_data_comprehensive(self, 
                                            financial_data: Union[str, Dict[str, Any]], 
                                            strict_mode: bool = False) -> EnhancedValidationResult:
        """
        全面验证财务数据
        
        Args:
            financial_data: 财务数据（JSON字符串或字典）
            strict_mode: 严格模式验证
            
        Returns:
            EnhancedValidationResult: 增强验证结果
        """
        errors = []
        warnings = []
        processing_suggestions = []
        detected_issues = []
        
        try:
            # 使用基础验证器
            base_result = self.base_validator.validate_financial_data(financial_data)
            
            if not base_result.is_valid:
                return EnhancedValidationResult(
                    is_valid=False,
                    errors=base_result.errors,
                    warnings=base_result.warnings,
                    data=base_result.data
                )
            
            # 解析数据
            if isinstance(financial_data, str):
                try:
                    data = json.loads(financial_data)
                except json.JSONDecodeError as e:
                    return EnhancedValidationResult(
                        is_valid=False,
                        errors=[f"JSON解析失败: {str(e)}"],
                        warnings=[]
                    )
            else:
                data = base_result.data or financial_data
            
            # 1. 数据类型识别
            data_type = self._detect_data_type(data)
            
            # 2. 完整性验证
            completeness_result = self._validate_completeness(data, data_type)
            errors.extend(completeness_result['errors'])
            warnings.extend(completeness_result['warnings'])
            
            # 3. 一致性验证
            consistency_result = self._validate_consistency(data, data_type)
            errors.extend(consistency_result['errors'])
            warnings.extend(consistency_result['warnings'])
            
            # 4. 有效性验证
            validity_result = self._validate_validity(data, data_type, strict_mode)
            errors.extend(validity_result['errors'])
            warnings.extend(validity_result['warnings'])
            detected_issues.extend(validity_result['issues'])
            
            # 5. 业务逻辑验证
            business_result = self._validate_business_logic(data, data_type)
            errors.extend(business_result['errors'])
            warnings.extend(business_result['warnings'])
            processing_suggestions.extend(business_result['suggestions'])
            
            # 6. 计算质量分数
            completeness_score = completeness_result['score']
            consistency_score = consistency_result['score']
            validity_score = validity_result['score']
            quality_score = min(100, 100 - len(errors) * 5 - len(warnings) * 2)
            
            # 7. 标准化数据
            normalized_data = self._normalize_data_enhanced(data, data_type)
            
            # 8. 生成处理建议
            if not processing_suggestions:
                processing_suggestions = self._generate_processing_suggestions(
                    errors, warnings, detected_issues, data_type
                )
            
            is_valid = len(errors) == 0 or (not strict_mode and len(errors) < 3)
            
            return EnhancedValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                data=data,
                normalized_data=normalized_data,
                quality_score=quality_score,
                data_type=data_type,
                completeness_score=completeness_score,
                consistency_score=consistency_score,
                validity_score=validity_score,
                processing_suggestions=processing_suggestions,
                detected_issues=detected_issues
            )
            
        except Exception as e:
            logger.error(f"数据验证管道执行失败: {str(e)}")
            return EnhancedValidationResult(
                is_valid=False,
                errors=[f"数据验证过程中发生错误: {str(e)}"],
                warnings=[]
            )
    
    def _detect_data_type(self, data: Dict[str, Any]) -> str:
        """检测数据类型"""
        if 'historical_data' in data and isinstance(data['historical_data'], dict):
            return "user_custom_format"
        elif '利润表' in data or '资产负债表' in data or '现金流量表' in data:
            return "chinese_financial_format"
        elif 'income_statement' in data and 'balance_sheet' in data:
            return "standard_financial_format"
        elif 'ratios' in data or 'profitability' in data:
            return "financial_ratios_format"
        elif 'years' in data and any(key in data for key in ['revenue', 'profit', 'assets']):
            return "array_format"
        else:
            return "unknown_format"
    
    def _validate_completeness(self, data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """验证数据完整性"""
        errors = []
        warnings = []
        
        # 根据数据类型选择验证规则
        if data_type in ["user_custom_format", "chinese_financial_format"]:
            required_sections = self.financial_validation_rules['required_sections']
            total_required = 0
            total_present = 0
            
            for section, required_fields in required_sections.items():
                if section == 'historical_data':
                    continue  # 历史数据是可选的
                    
                # 检查中英文字段名
                section_found = False
                section_data = None
                
                # 优先检查中文字段名
                if section in data:
                    section_found = True
                    section_data = data[section]
                else:
                    # 检查对应的英文字段名
                    english_mapping = {
                        'income_statement': '利润表',
                        'balance_sheet': '资产负债表',
                        'cash_flow': '现金流量表'
                    }
                    if section in english_mapping and english_mapping[section] in data:
                        section_found = True
                        section_data = data[english_mapping[section]]
                
                if section_found and section_data and isinstance(section_data, dict):
                    field_present = 0
                    for field in required_fields:
                        if field in section_data:
                            total_present += 1
                            field_present += 1
                        else:
                            # 检查字段映射
                            field_mappings = self.financial_validation_rules['field_mappings'].get(section, {})
                            if field in field_mappings:
                                for alias in field_mappings[field]:
                                    if alias in section_data:
                                        total_present += 1
                                        field_present += 1
                                        break
                    
                    total_required += len(required_fields)
                    if field_present < len(required_fields):
                        missing_fields = len(required_fields) - field_present
                        warnings.append(f"{section}缺少{missing_fields}个关键字段")
                else:
                    warnings.append(f"缺少{section}数据")
                    total_required += len(required_fields)
            
            # 计算完整性分数
            if total_required > 0:
                completeness_score = (total_present / total_required) * 100
            else:
                completeness_score = 0
                
        else:
            # 其他数据类型的完整性检查
            completeness_score = 80  # 默认分数
            if not data:
                errors.append("数据为空")
                completeness_score = 0
            elif len(data) < 3:
                warnings.append("数据内容较少，可能影响分析质量")
                completeness_score = 60
        
        return {
            'errors': errors,
            'warnings': warnings,
            'score': completeness_score
        }
    
    def _validate_consistency(self, data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """验证数据一致性"""
        errors = []
        warnings = []
        
        try:
            # 检查数值一致性
            monetary_fields = ['营业收入', '净利润', '总资产', '总负债', '所有者权益']
            for field in monetary_fields:
                if field in data:
                    value = data[field]
                    if isinstance(value, (int, float)) and value < 0:
                        if field not in ['净利润', '现金流量净额']:
                            warnings.append(f"{field}为负值，请确认数据准确性")
            
            # 检查历史数据一致性
            if 'historical_data' in data:
                historical_data = data['historical_data']
                if isinstance(historical_data, dict):
                    years = []
                    for key, value in historical_data.items():
                        if str(key).isdigit() and len(str(key)) == 4:
                            years.append(key)
                        elif isinstance(value, dict):
                            # 检查是否是年份数据
                            for sub_key in value.keys():
                                if str(sub_key).isdigit() and len(str(sub_key)) == 4:
                                    years.append(sub_key)
                    
                    if len(years) > 1:
                        years.sort()
                        year_gaps = []
                        for i in range(1, len(years)):
                            gap = int(years[i]) - int(years[i-1])
                            if gap > 1:
                                year_gaps.append(gap)
                        
                        if year_gaps:
                            warnings.append(f"历史数据存在年份间隔: {year_gaps}")
            
            # 检查财务比率一致性
            if 'profitability' in data or 'ratios' in data:
                ratios_data = data.get('profitability') or data.get('ratios', {})
                if isinstance(ratios_data, dict):
                    for ratio_name, ratio_value in ratios_data.items():
                        if isinstance(ratio_value, (int, float)):
                            if 'margin' in ratio_name.lower() or 'ratio' in ratio_name.lower():
                                if abs(ratio_value) > 10:  # 比率通常在-1000%到1000%之间
                                    warnings.append(f"{ratio_name}值异常: {ratio_value}")
            
            consistency_score = 100 - len(warnings) * 5
            consistency_score = max(0, consistency_score)
            
        except Exception as e:
            logger.error(f"一致性验证失败: {str(e)}")
            errors.append(f"一致性验证过程中发生错误: {str(e)}")
            consistency_score = 0
        
        return {
            'errors': errors,
            'warnings': warnings,
            'score': consistency_score
        }
    
    def _validate_validity(self, data: Dict[str, Any], data_type: str, strict_mode: bool) -> Dict[str, Any]:
        """验证数据有效性"""
        errors = []
        warnings = []
        issues = []
        
        try:
            # 检查数据类型有效性
            for key, value in data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        validation_result = self._validate_field_value(sub_key, sub_value, strict_mode)
                        errors.extend(validation_result['errors'])
                        warnings.extend(validation_result['warnings'])
                        issues.extend(validation_result['issues'])
                else:
                    validation_result = self._validate_field_value(key, value, strict_mode)
                    errors.extend(validation_result['errors'])
                    warnings.extend(validation_result['warnings'])
                    issues.extend(validation_result['issues'])
            
            # 检查特殊格式
            if data_type == "user_custom_format":
                if '历史数据' in data:
                    historical_validation = self._validate_historical_data_format(data['历史数据'])
                    errors.extend(historical_validation['errors'])
                    warnings.extend(historical_validation['warnings'])
                    issues.extend(historical_validation['issues'])
            
            validity_score = 100 - len(errors) * 10 - len(warnings) * 3
            validity_score = max(0, validity_score)
            
        except Exception as e:
            logger.error(f"有效性验证失败: {str(e)}")
            errors.append(f"有效性验证过程中发生错误: {str(e)}")
            validity_score = 0
        
        return {
            'errors': errors,
            'warnings': warnings,
            'issues': issues,
            'score': validity_score
        }
    
    def _validate_field_value(self, field_name: str, value: Any, strict_mode: bool) -> Dict[str, Any]:
        """验证单个字段值"""
        errors = []
        warnings = []
        issues = []
        
        # 跳过非数值字段的验证
        if not isinstance(value, (int, float)):
            return {'errors': errors, 'warnings': warnings, 'issues': issues}
        
        # 检查货币字段
        monetary_indicators = ['收入', '利润', '资产', '负债', '权益', '现金', '流量']
        if any(indicator in field_name for indicator in monetary_indicators):
            if value < 0:
                if '净利润' not in field_name and '流量' not in field_name:
                    issues.append(f"{field_name}为负值: {value}")
                elif strict_mode:
                    warnings.append(f"{field_name}为负值: {value}")
            
            if abs(value) > 1e15:  # 超过千万亿
                issues.append(f"{field_name}值过大: {value}")
            elif abs(value) < 0.01 and value != 0:  # 小于1分钱
                if strict_mode:
                    warnings.append(f"{field_name}值过小: {value}")
        
        # 检查比率字段
        ratio_indicators = ['率', 'ratio', 'margin', 'ROE', 'ROA', '周转率']
        if any(indicator in field_name.lower() for indicator in ratio_indicators):
            if abs(value) > 10:  # 比率超过1000%
                issues.append(f"{field_name}比率异常: {value}")
            elif abs(value) > 1 and '率' in field_name:  # 中文"率"字段通常是百分比
                if not (0.01 <= value <= 100):  # 如果不在1%到100%之间
                    if strict_mode:
                        warnings.append(f"{field_name}可能需要单位转换: {value}")
        
        return {'errors': errors, 'warnings': warnings, 'issues': issues}
    
    def _validate_historical_data_format(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证历史数据格式"""
        errors = []
        warnings = []
        issues = []
        
        if not isinstance(historical_data, dict):
            errors.append("历史数据必须是字典格式")
            return {'errors': errors, 'warnings': warnings, 'issues': issues}
        
        # 检查年份键名
        year_keys = []
        for key in historical_data.keys():
            if str(key).isdigit() and len(str(key)) == 4:
                year_keys.append(key)
            else:
                # 检查是否是嵌套的年份数据
                year_data = historical_data[key]
                if isinstance(year_data, dict):
                    for sub_key in year_data.keys():
                        if str(sub_key).isdigit() and len(str(sub_key)) == 4:
                            year_keys.append(sub_key)
        
        if not year_keys:
            errors.append("历史数据中未找到有效的年份数据")
        else:
            # 检查年份范围
            years = [int(year) for year in year_keys]
            current_year = datetime.now().year
            min_year = min(years)
            max_year = max(years)
            
            if max_year > current_year + 1:
                warnings.append(f"历史数据包含未来年份: {max_year}")
            
            if min_year < 1990:
                warnings.append(f"历史数据年份过早: {min_year}")
            
            # 检查数据完整性
            for year in year_keys:
                year_data = historical_data.get(year) or historical_data.get(str(year), {})
                if isinstance(year_data, dict):
                    required_fields = ['营业收入', '净利润']
                    missing_fields = [field for field in required_fields if field not in year_data]
                    if missing_fields:
                        issues.append(f"年份{year}缺少字段: {missing_fields}")
        
        return {'errors': errors, 'warnings': warnings, 'issues': issues}
    
    def _validate_business_logic(self, data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """验证业务逻辑"""
        errors = []
        warnings = []
        suggestions = []
        
        try:
            # 检查基本财务逻辑
            revenue = self._extract_field_value(data, ['营业收入', 'revenue', '收入'])
            net_profit = self._extract_field_value(data, ['净利润', 'net_profit', '利润'])
            total_assets = self._extract_field_value(data, ['总资产', 'total_assets', '资产'])
            total_liabilities = self._extract_field_value(data, ['总负债', 'total_liabilities', '负债'])
            equity = self._extract_field_value(data, ['所有者权益', 'total_equity', '股东权益', '权益'])
            
            # 检查净利润率合理性
            if revenue is not None and net_profit is not None:
                if revenue > 0:
                    profit_margin = (net_profit / revenue) * 100
                    if profit_margin > 100:
                        warnings.append(f"净利润率异常高: {profit_margin:.2f}%")
                    elif profit_margin < -100:
                        warnings.append(f"净利润率异常低: {profit_margin:.2f}%")
            
            # 检查资产负债平衡
            if total_assets is not None and total_liabilities is not None and equity is not None:
                balance_diff = abs(total_assets - (total_liabilities + equity))
                if balance_diff > total_assets * 0.05:  # 差异超过5%
                    warnings.append("资产负债不平衡，差异较大")
                    suggestions.append("建议检查资产负债表数据的准确性")
            
            # 检查历史数据逻辑
            if 'historical_data' in data:
                historical_data = data['historical_data']
                if isinstance(historical_data, dict):
                    revenue_trend = []
                    profit_trend = []
                    
                    for year, year_data in historical_data.items():
                        if isinstance(year_data, dict):
                            year_revenue = year_data.get('营业收入') or year_data.get('revenue')
                            year_profit = year_data.get('净利润') or year_data.get('net_profit')
                            
                            if year_revenue is not None:
                                revenue_trend.append((int(year), year_revenue))
                            if year_profit is not None:
                                profit_trend.append((int(year), year_profit))
                    
                    # 检查趋势异常
                    if len(revenue_trend) > 1:
                        revenue_trend.sort()
                        for i in range(1, len(revenue_trend)):
                            prev_year, prev_revenue = revenue_trend[i-1]
                            curr_year, curr_revenue = revenue_trend[i]
                            
                            if prev_revenue > 0:
                                growth_rate = ((curr_revenue - prev_revenue) / prev_revenue) * 100
                                if abs(growth_rate) > 200:  # 增长率超过200%
                                    warnings.append(f"{prev_year}到{curr_year}年收入变化异常: {growth_rate:.2f}%")
            
            # 生成处理建议
            if not suggestions:
                if warnings:
                    suggestions.append("建议检查数据来源和录入准确性")
                else:
                    suggestions.append("数据质量良好，可以进行后续分析")
        
        except Exception as e:
            logger.error(f"业务逻辑验证失败: {str(e)}")
            errors.append(f"业务逻辑验证过程中发生错误: {str(e)}")
        
        return {
            'errors': errors,
            'warnings': warnings,
            'suggestions': suggestions
        }
    
    def _extract_field_value(self, data: Dict[str, Any], field_names: List[str]) -> Optional[float]:
        """提取字段值"""
        for field_name in field_names:
            if field_name in data:
                value = data[field_name]
                if isinstance(value, (int, float)):
                    return value
            # 也检查嵌套结构
            for key, value in data.items():
                if isinstance(value, dict) and field_name in value:
                    field_value = value[field_name]
                    if isinstance(field_value, (int, float)):
                        return field_value
        return None
    
    def _normalize_data_enhanced(self, data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """增强数据标准化"""
        try:
            # 使用基础标准化
            base_normalized = self.base_validator.normalize_financial_data(data)
            
            # 根据数据类型进行特殊处理
            if data_type == "user_custom_format":
                # 处理中文键名映射
                normalized = self._normalize_chinese_fields(data)
                # 合并基础标准化结果
                for key, value in base_normalized.items():
                    if key not in normalized:
                        normalized[key] = value
                return normalized
            else:
                return base_normalized
        except Exception as e:
            logger.error(f"数据标准化失败: {str(e)}")
            return data
    
    def _normalize_chinese_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """标准化中文字段名"""
        normalized = {}
        
        # 财务报表映射
        statement_mapping = {
            '利润表': 'income_statement',
            '资产负债表': 'balance_sheet', 
            '现金流量表': 'cash_flow',
            '历史数据': 'historical_data'
        }
        
        # 字段映射
        field_mapping = self.financial_validation_rules['field_mappings']
        
        for key, value in data.items():
            # 标准化报表类型
            if key in statement_mapping:
                normalized_key = statement_mapping[key]
                if isinstance(value, dict):
                    normalized[normalized_key] = self._normalize_fields_in_section(value, field_mapping.get(normalized_key, {}))
                else:
                    normalized[normalized_key] = value
            else:
                # 检查是否已经是标准字段名
                if key in ['income_statement', 'balance_sheet', 'cash_flow', 'historical_data']:
                    if isinstance(value, dict):
                        normalized[key] = self._normalize_fields_in_section(value, field_mapping.get(key, {}))
                    else:
                        normalized[key] = value
                else:
                    normalized[key] = value
        
        return normalized
    
    def _normalize_fields_in_section(self, section_data: Dict[str, Any], field_mapping: Dict[str, List[str]]) -> Dict[str, Any]:
        """标准化section中的字段名"""
        normalized = {}
        
        for field_name, field_value in section_data.items():
            # 查找标准字段名
            standard_name = None
            for standard_field, aliases in field_mapping.items():
                if field_name in aliases:
                    standard_name = standard_field
                    break
            
            if standard_name:
                normalized[standard_name] = field_value
            else:
                # 保留原字段名
                normalized[field_name] = field_value
        
        return normalized
    
    def _generate_processing_suggestions(self, 
                                       errors: List[str], 
                                       warnings: List[str], 
                                       issues: List[str],
                                       data_type: str) -> List[str]:
        """生成处理建议"""
        suggestions = []
        
        if errors:
            suggestions.append("数据存在严重错误，建议先修复错误后再进行分析")
        
        if warnings:
            suggestions.append("数据存在一些警告，建议检查数据准确性")
        
        if issues:
            suggestions.append("发现一些数据质量问题，建议进行数据清洗")
        
        if data_type == "unknown_format":
            suggestions.append("数据格式未被识别，建议使用标准财务数据格式")
        
        if not errors and not warnings and not issues:
            suggestions.append("数据质量良好，可以直接进行财务分析")
        
        # 根据具体问题生成建议
        for error in errors[:3]:  # 只处理前3个错误
            if "JSON解析失败" in error:
                suggestions.append("请检查JSON格式的正确性")
            elif "缺少必需字段" in error:
                suggestions.append("请补充缺失的财务数据字段")
        
        for warning in warnings[:3]:  # 只处理前3个警告
            if "负值" in warning:
                suggestions.append("请确认负值数据的业务合理性")
            elif "异常" in warning:
                suggestions.append("请检查异常数值的准确性")
        
        return suggestions