"""
数据质量监控器
提供全面的数据质量评估、监控和报告功能
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import logging

logger = logging.getLogger(__name__)


@dataclass
class QualityMetrics:
    """数据质量指标"""
    overall_score: float = 0.0
    completeness_score: float = 0.0
    accuracy_score: float = 0.0
    consistency_score: float = 0.0
    timeliness_score: float = 0.0
    validity_score: float = 0.0
    uniqueness_score: float = 0.0
    
    # 详细指标
    total_records: int = 0
    valid_records: int = 0
    missing_values: int = 0
    duplicate_records: int = 0
    outlier_count: int = 0
    
    # 质量等级
    quality_level: str = "unknown"  # excellent, good, acceptable, poor, unknown


@dataclass
class QualityIssue:
    """数据质量问题"""
    issue_type: str
    severity: str  # critical, high, medium, low
    description: str
    affected_fields: List[str] = field(default_factory=list)
    affected_records: int = 0
    recommendation: str = ""
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class QualityReport:
    """数据质量报告"""
    data_id: str
    assessment_time: str
    metrics: QualityMetrics
    issues: List[QualityIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    processing_summary: Dict[str, Any] = field(default_factory=dict)
    
    def get_critical_issues(self) -> List[QualityIssue]:
        """获取严重问题"""
        return [issue for issue in self.issues if issue.severity == "critical"]
    
    def get_high_priority_issues(self) -> List[QualityIssue]:
        """获取高优先级问题"""
        return [issue for issue in self.issues if issue.severity in ["critical", "high"]]


class DataQualityMonitor:
    """数据质量监控器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化数据质量监控器"""
        self.config = config or {}
        
        # 质量评分权重
        self.quality_weights = {
            'completeness': 0.25,
            'accuracy': 0.25,
            'consistency': 0.20,
            'validity': 0.15,
            'timeliness': 0.10,
            'uniqueness': 0.05
        }
        
        # 质量阈值
        self.quality_thresholds = {
            'excellent': 90,
            'good': 75,
            'acceptable': 60,
            'poor': 0
        }
        
        # 财务数据特定规则
        self.financial_quality_rules = {
            'required_fields': {
                'income_statement': ['revenue', 'net_profit'],
                'balance_sheet': ['total_assets', 'total_liabilities', 'total_equity']
            },
            'value_ranges': {
                'revenue': {'min': 0, 'max': 1e15},
                'net_profit': {'min': -1e12, 'max': 1e12},
                'total_assets': {'min': 0, 'max': 1e15},
                'ratios': {'min': -10, 'max': 10}
            },
            'consistency_checks': {
                'balance_sheet_balance': True,  # 资产 = 负债 + 权益
                'profit_margin_range': True,    # 净利润率合理性
                'growth_rate_range': True       # 增长率合理性
            }
        }
    
    def assess_data_quality(self, 
                           data: Union[str, Dict[str, Any]], 
                           data_context: Optional[Dict[str, Any]] = None) -> QualityReport:
        """
        评估数据质量
        
        Args:
            data: 要评估的数据
            data_context: 数据上下文信息
            
        Returns:
            QualityReport: 数据质量报告
        """
        try:
            # 解析数据
            if isinstance(data, str):
                try:
                    parsed_data = json.loads(data)
                except json.JSONDecodeError as e:
                    logger.error(f"数据解析失败: {str(e)}")
                    return self._create_error_report(f"数据解析失败: {str(e)}")
            else:
                parsed_data = data
            
            # 生成数据ID
            data_id = self._generate_data_id(parsed_data)
            
            # 初始化质量指标
            metrics = QualityMetrics()
            issues = []
            recommendations = []
            processing_summary = {}
            
            # 执行各项质量检查
            completeness_result = self._assess_completeness(parsed_data)
            metrics.completeness_score = completeness_result['score']
            issues.extend(completeness_result['issues'])
            
            accuracy_result = self._assess_accuracy(parsed_data)
            metrics.accuracy_score = accuracy_result['score']
            issues.extend(accuracy_result['issues'])
            
            consistency_result = self._assess_consistency(parsed_data)
            metrics.consistency_score = consistency_result['score']
            issues.extend(consistency_result['issues'])
            
            validity_result = self._assess_validity(parsed_data)
            metrics.validity_score = validity_result['score']
            issues.extend(validity_result['issues'])
            
            timeliness_result = self._assess_timeliness(parsed_data, data_context)
            metrics.timeliness_score = timeliness_result['score']
            issues.extend(timeliness_result['issues'])
            
            uniqueness_result = self._assess_uniqueness(parsed_data)
            metrics.uniqueness_score = uniqueness_result['score']
            issues.extend(uniqueness_result['issues'])
            
            # 更新统计信息
            metrics.total_records = self._count_total_records(parsed_data)
            metrics.valid_records = metrics.total_records - len(issues)
            metrics.missing_values = self._count_missing_values(parsed_data)
            metrics.duplicate_records = uniqueness_result.get('duplicate_count', 0)
            metrics.outlier_count = self._count_outliers(parsed_data)
            
            # 计算总体质量分数
            metrics.overall_score = self._calculate_overall_score(metrics)
            
            # 确定质量等级
            metrics.quality_level = self._determine_quality_level(metrics.overall_score)
            
            # 生成建议
            recommendations = self._generate_recommendations(issues, metrics)
            
            # 创建处理摘要
            processing_summary = {
                'assessment_time': datetime.now().isoformat(),
                'data_size_kb': len(json.dumps(parsed_data, ensure_ascii=False).encode('utf-8')) / 1024,
                'processing_duration_ms': 0,  # 可以添加计时
                'quality_checks_performed': 6,
                'issues_found': len(issues),
                'critical_issues': len([i for i in issues if i.severity == 'critical'])
            }
            
            return QualityReport(
                data_id=data_id,
                assessment_time=datetime.now().isoformat(),
                metrics=metrics,
                issues=issues,
                recommendations=recommendations,
                processing_summary=processing_summary
            )
            
        except Exception as e:
            logger.error(f"数据质量评估失败: {str(e)}")
            return self._create_error_report(f"质量评估失败: {str(e)}")
    
    def _assess_completeness(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """评估数据完整性"""
        issues = []
        score = 100.0
        total_fields = 0
        missing_fields = 0
        
        try:
            # 检查必需的财务报表
            required_statements = ['income_statement', 'balance_sheet', 'cash_flow']
            for statement in required_statements:
                if statement in data and data[statement]:
                    statement_data = data[statement]
                    if isinstance(statement_data, dict):
                        # 检查必需字段
                        required_fields = self.financial_quality_rules['required_fields'].get(statement, [])
                        for field in required_fields:
                            total_fields += 1
                            if field not in statement_data:
                                missing_fields += 1
                                issues.append(QualityIssue(
                                    issue_type="missing_required_field",
                                    severity="high",
                                    description=f"{statement}缺少必需字段: {field}",
                                    affected_fields=[f"{statement}.{field}"],
                                    recommendation=f"请添加{field}数据"
                                ))
                            else:
                                # 检查字段值是否为空
                                value = statement_data[field]
                                if value is None or (isinstance(value, str) and not value.strip()):
                                    missing_fields += 1
                                    issues.append(QualityIssue(
                                        issue_type="empty_field",
                                        severity="medium",
                                        description=f"{statement}.{field}字段为空",
                                        affected_fields=[f"{statement}.{field}"],
                                        recommendation=f"请填写{field}的有效值"
                                    ))
                else:
                    total_fields += 3  # 假设每个报表平均3个必需字段
                    missing_fields += 3
                    issues.append(QualityIssue(
                        issue_type="missing_statement",
                        severity="high",
                        description=f"缺少{statement}数据",
                        affected_fields=[statement],
                        recommendation=f"请提供{statement}数据"
                    ))
            
            # 检查历史数据
            if 'historical_data' in data:
                historical_data = data['historical_data']
                if isinstance(historical_data, dict):
                    if len(historical_data) == 0:
                        issues.append(QualityIssue(
                            issue_type="empty_historical_data",
                            severity="medium",
                            description="历史数据为空",
                            affected_fields=['historical_data'],
                            recommendation="建议添加历史数据以支持趋势分析"
                        ))
                    else:
                        # 检查历史数据完整性
                        for year, year_data in historical_data.items():
                            if isinstance(year_data, dict) and len(year_data) == 0:
                                issues.append(QualityIssue(
                                    issue_type="empty_year_data",
                                    severity="low",
                                    description=f"年份{year}的历史数据为空",
                                    affected_fields=[f"historical_data.{year}"],
                                    recommendation=f"请补充年份{year}的数据"
                                ))
            
            # 计算完整性分数
            if total_fields > 0:
                score = ((total_fields - missing_fields) / total_fields) * 100
            else:
                score = 0
                issues.append(QualityIssue(
                    issue_type="no_structured_data",
                    severity="critical",
                    description="未发现结构化的财务数据",
                    affected_fields=[],
                    recommendation="请提供标准格式的财务数据"
                ))
            
        except Exception as e:
            logger.error(f"完整性评估失败: {str(e)}")
            issues.append(QualityIssue(
                issue_type="assessment_error",
                severity="medium",
                description=f"完整性评估过程中发生错误: {str(e)}",
                recommendation="请检查数据格式"
            ))
            score = 50
        
        return {
            'score': max(0, score),
            'issues': issues
        }
    
    def _assess_accuracy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """评估数据准确性"""
        issues = []
        score = 100.0
        
        try:
            # 检查数值范围
            for statement_name, statement_data in data.items():
                if isinstance(statement_data, dict) and statement_name in ['income_statement', 'balance_sheet', 'cash_flow']:
                    for field_name, field_value in statement_data.items():
                        if isinstance(field_value, (int, float)):
                            # 检查财务数值的合理性
                            if 'revenue' in field_name.lower() or '收入' in field_name:
                                if field_value < 0:
                                    issues.append(QualityIssue(
                                        issue_type="negative_revenue",
                                        severity="high",
                                        description=f"{field_name}为负值: {field_value}",
                                        affected_fields=[f"{statement_name}.{field_name}"],
                                        recommendation="请检查收入数据的准确性"
                                    ))
                                elif field_value > 1e15:  # 超过千万亿
                                    issues.append(QualityIssue(
                                        issue_type="unrealistic_value",
                                        severity="high",
                                        description=f"{field_name}值异常大: {field_value}",
                                        affected_fields=[f"{statement_name}.{field_name}"],
                                        recommendation="请检查数值单位和数据录入"
                                    ))
                            
                            elif 'profit' in field_name.lower() or '利润' in field_name:
                                if abs(field_value) > 1e12:  # 利润超过万亿
                                    issues.append(QualityIssue(
                                        issue_type="unrealistic_profit",
                                        severity="medium",
                                        description=f"{field_name}值异常: {field_value}",
                                        affected_fields=[f"{statement_name}.{field_name}"],
                                        recommendation="请检查利润数据的合理性"
                                    ))
                            
                            elif 'ratio' in field_name.lower() or '率' in field_name:
                                if abs(field_value) > 1000:  # 比率超过1000%
                                    issues.append(QualityIssue(
                                        issue_type="unrealistic_ratio",
                                        severity="medium",
                                        description=f"{field_name}比率异常: {field_value}%",
                                        affected_fields=[f"{statement_name}.{field_name}"],
                                        recommendation="请检查比率计算或单位转换"
                                    ))
            
            # 检查资产负债平衡
            if 'balance_sheet' in data:
                balance_sheet = data['balance_sheet']
                if isinstance(balance_sheet, dict):
                    total_assets = balance_sheet.get('total_assets') or balance_sheet.get('总资产')
                    total_liabilities = balance_sheet.get('total_liabilities') or balance_sheet.get('总负债')
                    total_equity = balance_sheet.get('total_equity') or balance_sheet.get('所有者权益')
                    
                    if all(isinstance(v, (int, float)) for v in [total_assets, total_liabilities, total_equity]):
                        balance_diff = abs(total_assets - (total_liabilities + total_equity))
                        if balance_diff > total_assets * 0.05:  # 差异超过5%
                            issues.append(QualityIssue(
                                issue_type="balance_sheet_imbalance",
                                severity="high",
                                description=f"资产负债不平衡，差异: {balance_diff:,.2f}",
                                affected_fields=['balance_sheet'],
                                recommendation="请检查资产负债表数据的准确性"
                            ))
            
            # 计算准确性分数
            if issues:
                high_severity_issues = len([i for i in issues if i.severity in ['critical', 'high']])
                score = max(0, 100 - high_severity_issues * 15 - len(issues) * 5)
            
        except Exception as e:
            logger.error(f"准确性评估失败: {str(e)}")
            issues.append(QualityIssue(
                issue_type="assessment_error",
                severity="medium",
                description=f"准确性评估过程中发生错误: {str(e)}",
                recommendation="请检查数据格式和数值"
            ))
            score = 50
        
        return {
            'score': score,
            'issues': issues
        }
    
    def _assess_consistency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """评估数据一致性"""
        issues = []
        score = 100.0
        
        try:
            # 检查历史数据一致性
            if 'historical_data' in data:
                historical_data = data['historical_data']
                if isinstance(historical_data, dict):
                    # 检查数据单位一致性
                    revenue_values = []
                    profit_values = []
                    
                    for year, year_data in historical_data.items():
                        if isinstance(year_data, dict):
                            revenue = year_data.get('revenue') or year_data.get('营业收入')
                            profit = year_data.get('net_profit') or year_data.get('净利润')
                            
                            if revenue is not None:
                                revenue_values.append(revenue)
                            if profit is not None:
                                profit_values.append(profit)
                    
                    # 检查数值数量级一致性
                    if len(revenue_values) > 1:
                        revenue_magnitudes = [self._get_magnitude(v) for v in revenue_values if v != 0]
                        if len(set(revenue_magnitudes)) > 1:
                            issues.append(QualityIssue(
                                issue_type="inconsistent_units",
                                severity="medium",
                                description="历史数据中收入数值单位不一致",
                                affected_fields=['historical_data'],
                                recommendation="请统一历史数据的数值单位"
                            ))
                    
                    # 检查趋势合理性
                    if len(revenue_values) > 2:
                        growth_rates = []
                        for i in range(1, len(revenue_values)):
                            if revenue_values[i-1] != 0:
                                growth_rate = (revenue_values[i] - revenue_values[i-1]) / abs(revenue_values[i-1])
                                growth_rates.append(growth_rate)
                        
                        if growth_rates:
                            avg_growth = np.mean(growth_rates)
                            if abs(avg_growth) > 5:  # 平均增长率超过500%
                                issues.append(QualityIssue(
                                    issue_type="unrealistic_growth",
                                    severity="medium",
                                    description=f"历史收入增长异常，平均增长率: {avg_growth:.2%}",
                                    affected_fields=['historical_data'],
                                    recommendation="请检查历史数据的准确性和一致性"
                                ))
            
            # 检查字段名一致性
            field_names = set()
            for statement_name, statement_data in data.items():
                if isinstance(statement_data, dict):
                    for field_name in statement_data.keys():
                        field_names.add(field_name)
            
            # 检查是否有重复或相似的字段名
            similar_fields = self._find_similar_field_names(list(field_names))
            for similar_group in similar_fields:
                if len(similar_group) > 1:
                    issues.append(QualityIssue(
                        issue_type="similar_field_names",
                        severity="low",
                        description=f"发现相似字段名: {similar_group}",
                        affected_fields=[f"fields.{name}" for name in similar_group],
                        recommendation="考虑统一字段命名规范"
                    ))
            
            # 计算一致性分数
            if issues:
                medium_severity_issues = len([i for i in issues if i.severity == 'medium'])
                score = max(0, 100 - medium_severity_issues * 10 - len(issues) * 3)
            
        except Exception as e:
            logger.error(f"一致性评估失败: {str(e)}")
            issues.append(QualityIssue(
                issue_type="assessment_error",
                severity="medium",
                description=f"一致性评估过程中发生错误: {str(e)}",
                recommendation="请检查数据格式一致性"
            ))
            score = 50
        
        return {
            'score': score,
            'issues': issues
        }
    
    def _assess_validity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """评估数据有效性"""
        issues = []
        score = 100.0
        
        try:
            # 检查数据类型有效性
            for statement_name, statement_data in data.items():
                if isinstance(statement_data, dict):
                    for field_name, field_value in statement_data.items():
                        # 检查数据类型
                        if field_name in ['revenue', 'net_profit', 'total_assets', 'total_liabilities']:
                            if not isinstance(field_value, (int, float, str)):
                                issues.append(QualityIssue(
                                    issue_type="invalid_data_type",
                                    severity="medium",
                                    description=f"{field_name}数据类型无效",
                                    affected_fields=[f"{statement_name}.{field_name}"],
                                    recommendation="数值字段应为数字或数字字符串"
                                ))
                        
                        # 检查字符串数值的转换性
                        if isinstance(field_value, str):
                            try:
                                float(field_value)
                            except ValueError:
                                if any(keyword in field_name.lower() for keyword in ['revenue', 'profit', 'assets', 'ratio']):
                                    issues.append(QualityIssue(
                                        issue_type="non_numeric_string",
                                        severity="medium",
                                        description=f"{field_name}字符串无法转换为数值: {field_value}",
                                        affected_fields=[f"{statement_name}.{field_name}"],
                                        recommendation="请确保数值字段包含有效数字"
                                    ))
            
            # 检查结构有效性
            if not any(key in data for key in ['income_statement', 'balance_sheet', 'cash_flow']):
                issues.append(QualityIssue(
                    issue_type="invalid_structure",
                    severity="high",
                    description="数据结构不符合财务数据格式",
                    affected_fields=['structure'],
                    recommendation="请使用标准财务数据格式"
                ))
            
            # 计算有效性分数
            if issues:
                high_severity_issues = len([i for i in issues if i.severity in ['critical', 'high']])
                score = max(0, 100 - high_severity_issues * 20 - len(issues) * 5)
            
        except Exception as e:
            logger.error(f"有效性评估失败: {str(e)}")
            issues.append(QualityIssue(
                issue_type="assessment_error",
                severity="medium",
                description=f"有效性评估过程中发生错误: {str(e)}",
                recommendation="请检查数据结构和格式"
            ))
            score = 50
        
        return {
            'score': score,
            'issues': issues
        }
    
    def _assess_timeliness(self, data: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """评估数据时效性"""
        issues = []
        score = 100.0
        
        try:
            current_date = datetime.now()
            
            # 检查数据中的时间信息
            data_dates = []
            
            # 从历史数据中提取日期
            if 'historical_data' in data:
                historical_data = data['historical_data']
                if isinstance(historical_data, dict):
                    for year_key in historical_data.keys():
                        if str(year_key).isdigit() and len(str(year_key)) == 4:
                            year = int(year_key)
                            # 假设数据是年底的
                            data_date = datetime(year, 12, 31)
                            data_dates.append(data_date)
            
            # 从上下文中提取日期信息
            if context:
                if 'report_date' in context:
                    try:
                        report_date = datetime.fromisoformat(context['report_date'])
                        data_dates.append(report_date)
                    except ValueError:
                        pass
                elif 'period' in context:
                    # 处理期间信息
                    period = context['period']
                    if isinstance(period, str) and len(period) == 6:  # YYYYMM格式
                        year = int(period[:4])
                        month = int(period[4:])
                        data_dates.append(datetime(year, month, 1))
            
            # 计算时效性分数
            if data_dates:
                latest_date = max(data_dates)
                days_old = (current_date - latest_date).days
                
                if days_old <= 30:  # 一个月内
                    score = 100
                elif days_old <= 90:  # 三个月内
                    score = 85
                elif days_old <= 180:  # 六个月内
                    score = 70
                elif days_old <= 365:  # 一年内
                    score = 50
                else:  # 超过一年
                    score = 30
                    issues.append(QualityIssue(
                        issue_type="outdated_data",
                        severity="medium",
                        description=f"数据过时，最新数据来自{latest_date.strftime('%Y-%m-%d')}",
                        affected_fields=['timeliness'],
                        recommendation="建议更新到最新的财务数据"
                    ))
            else:
                # 无法确定数据时间
                score = 70
                issues.append(QualityIssue(
                    issue_type="unknown_timeliness",
                    severity="low",
                    description="无法确定数据的时效性",
                    affected_fields=['timeliness'],
                    recommendation="建议在数据中包含时间信息"
                ))
            
        except Exception as e:
            logger.error(f"时效性评估失败: {str(e)}")
            issues.append(QualityIssue(
                issue_type="assessment_error",
                severity="low",
                description=f"时效性评估过程中发生错误: {str(e)}",
                recommendation="请检查数据中的时间信息"
            ))
            score = 70
        
        return {
            'score': score,
            'issues': issues
        }
    
    def _assess_uniqueness(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """评估数据唯一性"""
        issues = []
        score = 100.0
        duplicate_count = 0
        
        try:
            # 检查重复的记录
            all_records = []
            
            # 从历史数据中提取记录
            if 'historical_data' in data:
                historical_data = data['historical_data']
                if isinstance(historical_data, dict):
                    for year, year_data in historical_data.items():
                        if isinstance(year_data, dict):
                            record_str = json.dumps(year_data, sort_keys=True)
                            all_records.append((f"historical_{year}", record_str))
            
            # 检查重复记录
            record_hashes = {}
            for record_id, record_str in all_records:
                record_hash = hashlib.md5(record_str.encode()).hexdigest()
                if record_hash in record_hashes:
                    duplicate_count += 1
                    issues.append(QualityIssue(
                        issue_type="duplicate_record",
                        severity="low",
                        description=f"发现重复记录: {record_id} 和 {record_hashes[record_hash]}",
                        affected_fields=[record_id],
                        recommendation="请检查并移除重复的数据记录"
                    ))
                else:
                    record_hashes[record_hash] = record_id
            
            # 检查重复的字段
            field_names = []
            for statement_name, statement_data in data.items():
                if isinstance(statement_data, dict):
                    for field_name in statement_data.keys():
                        field_names.append(f"{statement_name}.{field_name}")
            
            duplicate_fields = len(field_names) - len(set(field_names))
            if duplicate_fields > 0:
                issues.append(QualityIssue(
                    issue_type="duplicate_fields",
                    severity="low",
                    description=f"发现{duplicate_fields}个重复字段名",
                    affected_fields=[],
                    recommendation="请检查字段命名的唯一性"
                ))
            
            # 计算唯一性分数
            if all_records:
                unique_rate = (len(all_records) - duplicate_count) / len(all_records)
                score = unique_rate * 100
            else:
                score = 100  # 没有记录不算唯一性问题
            
        except Exception as e:
            logger.error(f"唯一性评估失败: {str(e)}")
            issues.append(QualityIssue(
                issue_type="assessment_error",
                severity="low",
                description=f"唯一性评估过程中发生错误: {str(e)}",
                recommendation="请检查数据结构"
            ))
            score = 90
        
        return {
            'score': score,
            'issues': issues,
            'duplicate_count': duplicate_count
        }
    
    def _calculate_overall_score(self, metrics: QualityMetrics) -> float:
        """计算总体质量分数"""
        overall_score = (
            metrics.completeness_score * self.quality_weights['completeness'] +
            metrics.accuracy_score * self.quality_weights['accuracy'] +
            metrics.consistency_score * self.quality_weights['consistency'] +
            metrics.validity_score * self.quality_weights['validity'] +
            metrics.timeliness_score * self.quality_weights['timeliness'] +
            metrics.uniqueness_score * self.quality_weights['uniqueness']
        )
        return round(overall_score, 2)
    
    def _determine_quality_level(self, score: float) -> str:
        """确定质量等级"""
        if score >= self.quality_thresholds['excellent']:
            return "excellent"
        elif score >= self.quality_thresholds['good']:
            return "good"
        elif score >= self.quality_thresholds['acceptable']:
            return "acceptable"
        elif score >= self.quality_thresholds['poor']:
            return "poor"
        else:
            return "unknown"
    
    def _generate_recommendations(self, issues: List[QualityIssue], metrics: QualityMetrics) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于问题类型生成建议
        critical_issues = [i for i in issues if i.severity == 'critical']
        high_issues = [i for i in issues if i.severity == 'high']
        
        if critical_issues:
            recommendations.append("存在严重数据质量问题，建议优先修复这些问题")
        
        if high_issues:
            recommendations.append("建议检查数据来源和录入过程，提高数据准确性")
        
        # 基于质量分数生成建议
        if metrics.completeness_score < 80:
            recommendations.append("建议补充缺失的财务数据字段，提高数据完整性")
        
        if metrics.accuracy_score < 80:
            recommendations.append("建议验证数值的准确性，检查单位和计算方法")
        
        if metrics.consistency_score < 80:
            recommendations.append("建议统一数据格式和命名规范，确保数据一致性")
        
        if metrics.timeliness_score < 70:
            recommendations.append("建议更新到最新的财务数据，确保分析的时效性")
        
        # 通用建议
        if metrics.overall_score >= 90:
            recommendations.append("数据质量优秀，可以直接用于财务分析")
        elif metrics.overall_score >= 75:
            recommendations.append("数据质量良好，建议修复发现的问题后使用")
        elif metrics.overall_score >= 60:
            recommendations.append("数据质量一般，建议进行数据清洗和验证")
        else:
            recommendations.append("数据质量较差，强烈建议进行全面的数据清洗和修复")
        
        return recommendations
    
    def _generate_data_id(self, data: Dict[str, Any]) -> str:
        """生成数据ID"""
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(data_str.encode()).hexdigest()[:16]
    
    def _count_total_records(self, data: Dict[str, Any]) -> int:
        """计算总记录数"""
        count = 0
        
        # 计算历史数据记录数
        if 'historical_data' in data:
            historical_data = data['historical_data']
            if isinstance(historical_data, dict):
                count += len(historical_data)
        
        # 计算财务报表字段数
        for statement_name in ['income_statement', 'balance_sheet', 'cash_flow']:
            if statement_name in data and isinstance(data[statement_name], dict):
                count += len(data[statement_name])
        
        return max(count, 1)
    
    def _count_missing_values(self, data: Dict[str, Any]) -> int:
        """计算缺失值数量"""
        missing_count = 0
        
        for statement_name, statement_data in data.items():
            if isinstance(statement_data, dict):
                for field_name, field_value in statement_data.items():
                    if field_value is None or (isinstance(field_value, str) and not field_value.strip()):
                        missing_count += 1
        
        return missing_count
    
    def _count_outliers(self, data: Dict[str, Any]) -> int:
        """计算异常值数量"""
        outlier_count = 0
        
        # 简单的异常值检测
        for statement_name, statement_data in data.items():
            if isinstance(statement_data, dict):
                for field_name, field_value in statement_data.items():
                    if isinstance(field_value, (int, float)):
                        # 检查极端值
                        if abs(field_value) > 1e12:  # 大于万亿
                            outlier_count += 1
        
        return outlier_count
    
    def _get_magnitude(self, value: float) -> int:
        """获取数值的数量级"""
        if value == 0:
            return 0
        return int(np.floor(np.log10(abs(value))))
    
    def _find_similar_field_names(self, field_names: List[str]) -> List[List[str]]:
        """查找相似的字段名"""
        similar_groups = []
        
        for i, field1 in enumerate(field_names):
            similar_fields = [field1]
            for j, field2 in enumerate(field_names[i+1:], i+1):
                # 简单的相似性检测
                if (field1.lower() in field2.lower() or 
                    field2.lower() in field1.lower() or
                    self._levenshtein_distance(field1.lower(), field2.lower()) <= 2):
                    similar_fields.append(field2)
            
            if len(similar_fields) > 1:
                similar_groups.append(similar_fields)
        
        return similar_groups
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """计算编辑距离"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _create_error_report(self, error_message: str) -> QualityReport:
        """创建错误报告"""
        metrics = QualityMetrics(overall_score=0, quality_level="unknown")
        issue = QualityIssue(
            issue_type="assessment_failure",
            severity="critical",
            description=error_message,
            recommendation="请检查数据格式和内容"
        )
        
        return QualityReport(
            data_id="error",
            assessment_time=datetime.now().isoformat(),
            metrics=metrics,
            issues=[issue],
            recommendations=["修复数据格式问题后重新评估"],
            processing_summary={'error': error_message}
        )