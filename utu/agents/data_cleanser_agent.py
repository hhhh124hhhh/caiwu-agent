"""
数据清洗智能体
专门负责财务数据的清洗、标准化和质量控制
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from ..base_agent import BaseAgent
from ..data_engineering.validation_pipeline import DataValidationPipeline, EnhancedValidationResult
from ..data_engineering.transform_pipeline import DataTransformPipeline, TransformResult
from ..data_engineering.quality_monitor import DataQualityMonitor, QualityReport

logger = logging.getLogger(__name__)


class DataCleanserAgent(BaseAgent):
    """数据清洗智能体"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化数据清洗智能体"""
        super().__init__(config)
        
        # 初始化数据工程组件
        self.validation_pipeline = DataValidationPipeline(config)
        self.transform_pipeline = DataTransformPipeline(config)
        self.quality_monitor = DataQualityMonitor(config)
        
        # 智能体配置
        self.agent_config = config or {}
        self.strict_mode = self.agent_config.get('strict_mode', False)
        self.auto_fix_issues = self.agent_config.get('auto_fix_issues', True)
        self.generate_quality_report = self.agent_config.get('generate_quality_report', True)
        
        # 处理统计
        self.processing_stats = {
            'total_processed': 0,
            'successful_processed': 0,
            'failed_processed': 0,
            'average_quality_score': 0.0,
            'common_issues': {}
        }
        
        logger.info("DataCleanserAgent初始化完成")
    
    async def cleanse_financial_data(self, 
                                   financial_data: Union[str, Dict[str, Any]], 
                                   options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        清洗和标准化财务数据
        
        Args:
            financial_data: 原始财务数据
            options: 清洗选项
            
        Returns:
            Dict[str, Any]: 清洗结果
        """
        start_time = datetime.now()
        processing_id = f"cleansing_{start_time.strftime('%Y%m%d_%H%M%S')}"
        
        try:
            logger.info(f"开始数据清洗处理: {processing_id}")
            
            # 合并选项
            cleanse_options = {
                'strict_mode': self.strict_mode,
                'auto_fix_issues': self.auto_fix_issues,
                'generate_quality_report': self.generate_quality_report,
                'target_format': 'data_analysis_agent_compatible'
            }
            if options:
                cleanse_options.update(options)
            
            # 解析输入数据
            if isinstance(financial_data, str):
                try:
                    data = json.loads(financial_data)
                except json.JSONDecodeError as e:
                    error_msg = f"数据解析失败: {str(e)}"
                    logger.error(error_msg)
                    return self._create_error_response(error_msg, processing_id)
            else:
                data = financial_data
            
            # 记录原始数据
            original_data = json.loads(json.dumps(data, ensure_ascii=False))
            
            # 步骤1: 数据验证
            logger.info("执行数据验证...")
            validation_result = self.validation_pipeline.validate_financial_data_comprehensive(
                data, strict_mode=cleanse_options['strict_mode']
            )
            
            if not validation_result.is_valid and cleanse_options['strict_mode']:
                error_msg = f"数据验证失败: {'; '.join(validation_result.errors[:3])}"
                logger.error(error_msg)
                return self._create_error_response(error_msg, processing_id, validation_result)
            
            # 步骤2: 数据转换
            logger.info("执行数据转换...")
            transform_result = self.transform_pipeline.transform_financial_data(
                data, target_format=cleanse_options['target_format']
            )
            
            if not transform_result.success:
                error_msg = f"数据转换失败: {'; '.join(transform_result.errors[:3])}"
                logger.error(error_msg)
                return self._create_error_response(error_msg, processing_id, validation_result, transform_result)
            
            # 步骤3: 自动修复问题（如果启用）
            if cleanse_options['auto_fix_issues']:
                logger.info("执行自动问题修复...")
                fix_result = self._auto_fix_data_issues(
                    transform_result.transformed_data, 
                    validation_result
                )
                transform_result.transformed_data = fix_result['data']
                transform_result.transformation_log.extend(fix_result['log'])
            
            # 步骤4: 质量评估
            logger.info("执行质量评估...")
            quality_report = self.quality_monitor.assess_data_quality(
                transform_result.transformed_data,
                {
                    'processing_id': processing_id,
                    'original_format': validation_result.data_type,
                    'processing_time': start_time.isoformat()
                }
            )
            
            # 步骤5: 生成清洗结果
            end_time = datetime.now()
            processing_duration = (end_time - start_time).total_seconds()
            
            # 更新处理统计
            self._update_processing_stats(quality_report, True)
            
            # 构建响应
            result = {
                'success': True,
                'processing_id': processing_id,
                'processing_time': processing_duration,
                'original_data_format': validation_result.data_type,
                'target_format': cleanse_options['target_format'],
                
                # 清洗后的数据
                'cleansed_data': transform_result.transformed_data,
                
                # 质量信息
                'quality_score': quality_report.metrics.overall_score,
                'quality_level': quality_report.metrics.quality_level,
                'quality_metrics': {
                    'completeness': quality_report.metrics.completeness_score,
                    'accuracy': quality_report.metrics.accuracy_score,
                    'consistency': quality_report.metrics.consistency_score,
                    'validity': quality_report.metrics.validity_score,
                    'timeliness': quality_report.metrics.timeliness_score,
                    'uniqueness': quality_report.metrics.uniqueness_score
                },
                
                # 处理信息
                'transformation_summary': {
                    'fields_transformed': transform_result.fields_transformed,
                    'fields_added': transform_result.fields_added,
                    'values_converted': transform_result.values_converted,
                    'conversion_rate': transform_result.conversion_rate
                },
                
                # 问题和建议
                'issues_found': len(quality_report.issues),
                'critical_issues': len(quality_report.get_critical_issues()),
                'recommendations': quality_report.recommendations,
                
                # 详细日志（可选）
                'processing_log': {
                    'validation': {
                        'errors': validation_result.errors,
                        'warnings': validation_result.warnings,
                        'processing_suggestions': validation_result.processing_suggestions
                    },
                    'transformation': {
                        'errors': transform_result.errors,
                        'warnings': transform_result.warnings,
                        'steps': transform_result.transformation_log
                    },
                    'quality': {
                        'issues': [
                            {
                                'type': issue.issue_type,
                                'severity': issue.severity,
                                'description': issue.description,
                                'recommendation': issue.recommendation
                            } for issue in quality_report.issues
                        ]
                    }
                },
                
                # 元数据
                'metadata': {
                    'processed_by': 'DataCleanserAgent',
                    'processing_version': '1.0',
                    'data_id': quality_report.data_id,
                    'assessment_time': quality_report.assessment_time,
                    'agent_config': {
                        'strict_mode': cleanse_options['strict_mode'],
                        'auto_fix_issues': cleanse_options['auto_fix_issues']
                    }
                }
            }
            
            logger.info(f"数据清洗完成: {processing_id}, 质量分数: {quality_report.metrics.overall_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"数据清洗处理失败: {str(e)}")
            self._update_processing_stats(None, False)
            
            return self._create_error_response(
                f"数据清洗过程中发生错误: {str(e)}", 
                processing_id
            )
    
    async def validate_data_format(self, 
                                  data: Union[str, Dict[str, Any]], 
                                  validation_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        验证数据格式
        
        Args:
            data: 要验证的数据
            validation_rules: 验证规则
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        try:
            logger.info("执行数据格式验证...")
            
            # 使用验证管道
            validation_result = self.validation_pipeline.validate_financial_data_comprehensive(
                data, strict_mode=self.strict_mode
            )
            
            # 构建响应
            result = {
                'success': validation_result.is_valid,
                'data_type': validation_result.data_type,
                'quality_score': validation_result.calculate_overall_score(),
                
                # 验证结果
                'validation_summary': {
                    'errors': validation_result.errors,
                    'warnings': validation_result.warnings,
                    'processing_suggestions': validation_result.processing_suggestions,
                    'detected_issues': validation_result.detected_issues
                },
                
                # 质量指标
                'quality_metrics': {
                    'completeness_score': validation_result.completeness_score,
                    'consistency_score': validation_result.consistency_score,
                    'validity_score': validation_result.validity_score,
                    'overall_score': validation_result.calculate_overall_score()
                },
                
                # 标准化数据
                'normalized_data': validation_result.normalized_data,
                
                # 建议
                'recommendations': validation_result.processing_suggestions,
                
                'metadata': {
                    'validated_by': 'DataCleanserAgent',
                    'validation_time': datetime.now().isoformat()
                }
            }
            
            logger.info(f"数据格式验证完成，结果: {'有效' if validation_result.is_valid else '无效'}")
            return result
            
        except Exception as e:
            logger.error(f"数据格式验证失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'metadata': {
                    'validated_by': 'DataCleanserAgent',
                    'validation_time': datetime.now().isoformat()
                }
            }
    
    async def transform_data_structure(self, 
                                     data: Union[str, Dict[str, Any]], 
                                     target_format: str = "data_analysis_agent_compatible") -> Dict[str, Any]:
        """
        转换数据结构
        
        Args:
            data: 原始数据
            target_format: 目标格式
            
        Returns:
            Dict[str, Any]: 转换结果
        """
        try:
            logger.info(f"执行数据结构转换，目标格式: {target_format}")
            
            # 使用转换管道
            transform_result = self.transform_pipeline.transform_financial_data(data, target_format)
            
            # 构建响应
            result = {
                'success': transform_result.success,
                'original_format': transform_result.metadata.get('original_format', 'unknown'),
                'target_format': target_format,
                
                # 转换后的数据
                'transformed_data': transform_result.transformed_data,
                
                # 转换统计
                'transformation_stats': {
                    'fields_transformed': transform_result.fields_transformed,
                    'fields_added': transform_result.fields_added,
                    'values_converted': transform_result.values_converted,
                    'conversion_rate': transform_result.conversion_rate
                },
                
                # 处理日志
                'transformation_log': transform_result.transformation_log,
                
                # 错误和警告
                'errors': transform_result.errors,
                'warnings': transform_result.warnings,
                
                'metadata': {
                    'transformed_by': 'DataCleanserAgent',
                    'transformation_time': datetime.now().isoformat(),
                    'pipeline_version': '1.0'
                }
            }
            
            logger.info(f"数据结构转换完成，成功率: {transform_result.conversion_rate:.2f}%")
            return result
            
        except Exception as e:
            logger.error(f"数据结构转换失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'metadata': {
                    'transformed_by': 'DataCleanserAgent',
                    'transformation_time': datetime.now().isoformat()
                }
            }
    
    async def assess_data_quality(self, 
                                data: Union[str, Dict[str, Any]], 
                                context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        评估数据质量
        
        Args:
            data: 要评估的数据
            context: 数据上下文
            
        Returns:
            Dict[str, Any]: 质量评估结果
        """
        try:
            logger.info("执行数据质量评估...")
            
            # 使用质量监控器
            quality_report = self.quality_monitor.assess_data_quality(data, context)
            
            # 构建响应
            result = {
                'success': True,
                'data_id': quality_report.data_id,
                'assessment_time': quality_report.assessment_time,
                
                # 质量指标
                'quality_metrics': {
                    'overall_score': quality_report.metrics.overall_score,
                    'quality_level': quality_report.metrics.quality_level,
                    'completeness_score': quality_report.metrics.completeness_score,
                    'accuracy_score': quality_report.metrics.accuracy_score,
                    'consistency_score': quality_report.metrics.consistency_score,
                    'validity_score': quality_report.metrics.validity_score,
                    'timeliness_score': quality_report.metrics.timeliness_score,
                    'uniqueness_score': quality_report.metrics.uniqueness_score
                },
                
                # 问题统计
                'issues_summary': {
                    'total_issues': len(quality_report.issues),
                    'critical_issues': len(quality_report.get_critical_issues()),
                    'high_priority_issues': len(quality_report.get_high_priority_issues()),
                    'issues_by_type': self._group_issues_by_type(quality_report.issues)
                },
                
                # 详细问题
                'issues': [
                    {
                        'type': issue.issue_type,
                        'severity': issue.severity,
                        'description': issue.description,
                        'affected_fields': issue.affected_fields,
                        'recommendation': issue.recommendation,
                        'detected_at': issue.detected_at
                    } for issue in quality_report.issues
                ],
                
                # 建议
                'recommendations': quality_report.recommendations,
                
                # 处理摘要
                'processing_summary': quality_report.processing_summary,
                
                'metadata': {
                    'assessed_by': 'DataCleanserAgent',
                    'assessment_version': '1.0'
                }
            }
            
            logger.info(f"数据质量评估完成，质量分数: {quality_report.metrics.overall_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"数据质量评估失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'metadata': {
                    'assessed_by': 'DataCleanserAgent',
                    'assessment_time': datetime.now().isoformat()
                }
            }
    
    def _auto_fix_data_issues(self, 
                             data: Dict[str, Any], 
                             validation_result: EnhancedValidationResult) -> Dict[str, Any]:
        """自动修复数据问题"""
        log = []
        fixed_data = data.copy()
        fixes_applied = 0
        
        try:
            # 修复常见的数据问题
            fixes = 0
            
            # 修复1: 标准化财务报表结构
            if '利润表' in fixed_data and 'income_statement' not in fixed_data:
                fixed_data['income_statement'] = fixed_data['利润表']
                log.append("映射报表名称: 利润表 -> income_statement")
                fixes += 1
            
            if '资产负债表' in fixed_data and 'balance_sheet' not in fixed_data:
                fixed_data['balance_sheet'] = fixed_data['资产负债表']
                log.append("映射报表名称: 资产负债表 -> balance_sheet")
                fixes += 1
            
            if '现金流量表' in fixed_data and 'cash_flow' not in fixed_data:
                fixed_data['cash_flow'] = fixed_data['现金流量表']
                log.append("映射报表名称: 现金流量表 -> cash_flow")
                fixes += 1
            
            if '历史数据' in fixed_data and 'historical_data' not in fixed_data:
                fixed_data['historical_data'] = fixed_data['历史数据']
                log.append("映射字段名称: 历史数据 -> historical_data")
                fixes += 1
            
            # 修复2: 处理数值类型转换
            for statement_name, statement_data in fixed_data.items():
                if isinstance(statement_data, dict) and statement_name in ['income_statement', 'balance_sheet', 'cash_flow', 'historical_data']:
                    for field_name, field_value in statement_data.items():
                        if isinstance(field_value, str):
                            # 尝试转换为数值
                            try:
                                # 移除常见的非数字字符
                                cleaned_value = field_value.replace(',', '').replace(' ', '')
                                if cleaned_value and not any(c.isalpha() for c in cleaned_value):
                                    numeric_value = float(cleaned_value)
                                    fixed_data[statement_name][field_name] = numeric_value
                                    log.append(f"数值类型转换: {statement_name}.{field_name} = {numeric_value}")
                                    fixes += 1
                            except ValueError:
                                pass
            
            # 修复3: 处理年份键名格式
            if 'historical_data' in fixed_data:
                historical_data = fixed_data['historical_data']
                if isinstance(historical_data, dict):
                    # 确保所有年份键都是字符串格式
                    new_historical_data = {}
                    for year_key, year_data in historical_data.items():
                        str_year_key = str(year_key)
                        new_historical_data[str_year_key] = year_data
                        if str_year_key != str(year_key):
                            log.append(f"标准化年份键名: {year_key} -> {str_year_key}")
                            fixes += 1
                    
                    fixed_data['historical_data'] = new_historical_data
            
            fixes_applied = fixes
            log.append(f"自动修复完成，共应用{fixes}个修复")
            
        except Exception as e:
            logger.error(f"自动修复失败: {str(e)}")
            log.append(f"自动修复过程中发生错误: {str(e)}")
        
        return {
            'data': fixed_data,
            'log': log,
            'fixes_applied': fixes_applied
        }
    
    def _group_issues_by_type(self, issues: List) -> Dict[str, int]:
        """按类型分组问题"""
        grouped = {}
        for issue in issues:
            issue_type = getattr(issue, 'issue_type', 'unknown')
            grouped[issue_type] = grouped.get(issue_type, 0) + 1
        return grouped
    
    def _update_processing_stats(self, quality_report: Optional[QualityReport], success: bool):
        """更新处理统计"""
        self.processing_stats['total_processed'] += 1
        
        if success:
            self.processing_stats['successful_processed'] += 1
            if quality_report:
                # 更新平均质量分数
                current_avg = self.processing_stats['average_quality_score']
                successful_count = self.processing_stats['successful_processed']
                new_avg = ((current_avg * (successful_count - 1)) + quality_report.metrics.overall_score) / successful_count
                self.processing_stats['average_quality_score'] = round(new_avg, 2)
                
                # 统计常见问题
                for issue in quality_report.issues:
                    issue_type = issue.issue_type
                    self.processing_stats['common_issues'][issue_type] = \
                        self.processing_stats['common_issues'].get(issue_type, 0) + 1
        else:
            self.processing_stats['failed_processed'] += 1
    
    def _create_error_response(self, 
                             error_message: str, 
                             processing_id: str,
                             validation_result: Optional[EnhancedValidationResult] = None,
                             transform_result: Optional[TransformResult] = None) -> Dict[str, Any]:
        """创建错误响应"""
        response = {
            'success': False,
            'error': error_message,
            'processing_id': processing_id,
            'metadata': {
                'processed_by': 'DataCleanserAgent',
                'processing_time': datetime.now().isoformat(),
                'error_occurred': True
            }
        }
        
        # 添加可用的部分结果
        if validation_result:
            response['validation_result'] = {
                'is_valid': validation_result.is_valid,
                'errors': validation_result.errors,
                'warnings': validation_result.warnings,
                'data_type': validation_result.data_type
            }
        
        if transform_result:
            response['transformation_result'] = {
                'success': transform_result.success,
                'errors': transform_result.errors,
                'warnings': transform_result.warnings
            }
        
        return response
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        return {
            'processing_stats': self.processing_stats.copy(),
            'agent_info': {
                'agent_name': 'DataCleanserAgent',
                'version': '1.0',
                'capabilities': [
                    '数据验证',
                    '数据转换',
                    '质量评估',
                    '自动修复'
                ],
                'last_updated': datetime.now().isoformat()
            }
        }