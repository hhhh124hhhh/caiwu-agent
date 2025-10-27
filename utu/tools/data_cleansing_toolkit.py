"""
数据清洗工具集
遵循AsyncBaseToolkit模式，为DataCleanserAgent提供专门的工具
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from .base import AsyncBaseToolkit, register_tool
from ..config import ToolkitConfig
from ..agents.data_cleanser_agent import DataCleanserAgent

logger = logging.getLogger(__name__)


class DataCleansingToolkit(AsyncBaseToolkit):
    """数据清洗工具集"""
    
    def __init__(self, config: Optional[ToolkitConfig] = None):
        """初始化数据清洗工具集"""
        super().__init__(config)
        
        # 初始化数据清洗智能体
        agent_config = config.config if config else {}
        self.cleanser_agent = DataCleanserAgent(agent_config)
        
        # 工具配置
        self.strict_mode = agent_config.get('strict_mode', False)
        self.auto_fix_issues = agent_config.get('auto_fix_issues', True)
        self.generate_quality_report = agent_config.get('generate_quality_report', True)
        
        # 工作空间配置
        self.workspace_root = agent_config.get('workspace_root', './run_workdir')
        
        logger.info("DataCleansingToolkit初始化完成")
    
    @register_tool()
    def cleanse_financial_data(self, 
                              financial_data: Union[str, Dict[str, Any]], 
                              options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        智能清洗和标准化财务数据
        
        这是DataCleanserAgent的核心工具，执行完整的数据清洗流程：
        1. 数据验证和格式检查
        2. 智能字段名映射和标准化
        3. 数据类型转换
        4. 历史数据处理
        5. 质量评估和报告
        
        Args:
            financial_data: 原始财务数据，支持多种格式：
                          - JSON字符串：标准的JSON格式财务数据
                          - 字典：Python字典格式的财务数据
                          - 支持中英文字段名混合格式
                          - 支持历史数据嵌套格式
            options: 可选的处理选项，包括：
                    - strict_mode: 严格模式验证（默认False）
                    - auto_fix_issues: 自动修复常见问题（默认True）
                    - target_format: 目标格式（默认data_analysis_agent_compatible）
                    - generate_quality_report: 生成质量报告（默认True）
        
        Returns:
            Dict[str, Any]: 清洗结果，包含：
                - success: 是否成功
                - cleansed_data: 清洗后的标准化数据
                - quality_score: 质量分数（0-100）
                - quality_level: 质量等级（excellent/good/acceptable/poor）
                - transformation_summary: 转换统计信息
                - recommendations: 改进建议列表
                - processing_log: 详细的处理日志
                - metadata: 处理元数据
        
        Example:
            >>> data = {
            ...     "利润表": {"营业收入": 573.88, "净利润": 11.04},
            ...     "历史数据": {
            ...         "2025": {"营业收入": 573.88, "净利润": 11.04},
            ...         "2024": {"营业收入": 1511.39, "净利润": 36.11}
            ...     }
            ... }
            >>> result = toolkit.cleanse_financial_data(data)
            >>> print(f"质量分数: {result['quality_score']}")
            >>> print(f"标准化数据: {result['cleansed_data']}")
        """
        try:
            self.logger.info("开始执行财务数据清洗...")
            
            # 准备处理选项
            cleanse_options = {
                'strict_mode': self.strict_mode,
                'auto_fix_issues': self.auto_fix_issues,
                'generate_quality_report': self.generate_quality_report,
                'target_format': 'data_analysis_agent_compatible'
            }
            
            # 合并用户提供的选项
            if options:
                cleanse_options.update(options)
            
            # 执行数据清洗
            import asyncio
            result = asyncio.run(
                self.cleanser_agent.cleanse_financial_data(financial_data, cleanse_options)
            )
            
            if result['success']:
                self.logger.info(f"数据清洗成功完成，质量分数: {result['quality_score']:.2f}")
                
                # 记录关键信息
                transformation_summary = result.get('transformation_summary', {})
                self.logger.info(
                    f"转换统计 - 字段处理: {transformation_summary.get('fields_transformed', 0)}, "
                    f"新增字段: {transformation_summary.get('fields_added', 0)}, "
                    f"转换率: {transformation_summary.get('conversion_rate', 0):.1f}%"
                )
                
                # 记录问题和建议
                if result.get('issues_found', 0) > 0:
                    self.logger.warning(f"发现{result['issues_found']}个数据质量问题")
                    critical_issues = result.get('critical_issues', 0)
                    if critical_issues > 0:
                        self.logger.error(f"包含{critical_issues}个严重问题")
                
                return result
            else:
                self.logger.error(f"数据清洗失败: {result.get('error', 'Unknown error')}")
                return result
                
        except Exception as e:
            error_msg = f"财务数据清洗工具执行失败: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'tool': 'cleanse_financial_data',
                'timestamp': datetime.now().isoformat()
            }
    
    @register_tool()
    def validate_data_format(self, 
                           data: Union[str, Dict[str, Any]], 
                           validation_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        验证数据格式和完整性
        
        执行全面的数据格式验证，检查：
        - 数据结构完整性
        - 必需字段存在性
        - 数据类型正确性
        - 数值范围合理性
        - 业务逻辑一致性
        
        Args:
            data: 要验证的数据
            validation_rules: 自定义验证规则，可选
        
        Returns:
            Dict[str, Any]: 验证结果，包含：
                - success: 验证是否通过
                - data_type: 检测到的数据类型
                - quality_score: 质量分数
                - validation_summary: 验证摘要
                - recommendations: 改进建议
                - normalized_data: 标准化后的数据（如果可能）
        
        Example:
            >>> result = toolkit.validate_data_format(data)
            >>> if result['success']:
            ...     print("数据格式验证通过")
            ... else:
            ...     print(f"发现问题: {result['validation_summary']['errors']}")
        """
        try:
            self.logger.info("开始数据格式验证...")
            
            # 执行验证
            import asyncio
            result = asyncio.run(
                self.cleanser_agent.validate_data_format(data, validation_rules)
            )
            
            if result['success']:
                self.logger.info(f"数据格式验证通过，质量分数: {result['quality_score']:.2f}")
            else:
                self.logger.warning(f"数据格式验证失败，发现{len(result['validation_summary']['errors'])}个错误")
            
            return result
            
        except Exception as e:
            error_msg = f"数据格式验证失败: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'tool': 'validate_data_format',
                'timestamp': datetime.now().isoformat()
            }
    
    @register_tool()
    def transform_data_structure(self, 
                               data: Union[str, Dict[str, Any]], 
                               target_format: str = "data_analysis_agent_compatible") -> Dict[str, Any]:
        """
        转换数据结构以适配下游智能体
        
        将数据转换为特定智能体需要的格式：
        - data_analysis_agent_compatible: 适配DataAnalysisAgent
        - chart_generator_compatible: 适配ChartGeneratorAgent
        - report_agent_compatible: 适配ReportAgent
        
        Args:
            data: 原始数据
            target_format: 目标格式
        
        Returns:
            Dict[str, Any]: 转换结果
        """
        try:
            self.logger.info(f"开始数据结构转换，目标格式: {target_format}")
            
            # 执行转换
            import asyncio
            result = asyncio.run(
                self.cleanser_agent.transform_data_structure(data, target_format)
            )
            
            if result['success']:
                self.logger.info(f"数据结构转换成功，转换率: {result['transformation_stats']['conversion_rate']:.1f}%")
            else:
                self.logger.error(f"数据结构转换失败: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            error_msg = f"数据结构转换失败: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'tool': 'transform_data_structure',
                'timestamp': datetime.now().isoformat()
            }
    
    @register_tool()
    def assess_data_quality(self, 
                          data: Union[str, Dict[str, Any]], 
                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        评估数据质量并生成质量报告
        
        执行全面的数据质量评估：
        - 完整性评估
        - 准确性评估
        - 一致性评估
        - 有效性评估
        - 时效性评估
        - 唯一性评估
        
        Args:
            data: 要评估的数据
            context: 数据上下文信息，可选
        
        Returns:
            Dict[str, Any]: 质量评估结果，包含：
                - success: 评估是否成功
                - quality_metrics: 详细的质量指标
                - issues_summary: 问题摘要
                - recommendations: 改进建议
                - processing_summary: 处理摘要
        
        Example:
            >>> result = toolkit.assess_data_quality(data)
            >>> print(f"总体质量分数: {result['quality_metrics']['overall_score']}")
            >>> print(f"质量等级: {result['quality_metrics']['quality_level']}")
        """
        try:
            self.logger.info("开始数据质量评估...")
            
            # 执行质量评估
            import asyncio
            result = asyncio.run(
                self.cleanser_agent.assess_data_quality(data, context)
            )
            
            if result['success']:
                quality_score = result['quality_metrics']['overall_score']
                quality_level = result['quality_metrics']['quality_level']
                self.logger.info(f"数据质量评估完成，分数: {quality_score:.2f}, 等级: {quality_level}")
                
                # 记录关键问题
                issues_summary = result.get('issues_summary', {})
                if issues_summary.get('critical_issues', 0) > 0:
                    self.logger.error(f"发现{issues_summary['critical_issues']}个严重质量问题")
                
                total_issues = issues_summary.get('total_issues', 0)
                if total_issues > 0:
                    self.logger.warning(f"总共发现{total_issues}个质量问题")
            else:
                self.logger.error(f"数据质量评估失败: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            error_msg = f"数据质量评估失败: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'tool': 'assess_data_quality',
                'timestamp': datetime.now().isoformat()
            }
    
    @register_tool()
    def quick_cleanse_data(self, 
                          financial_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        快速数据清洗（简化版）
        
        对于常见的数据问题进行快速修复，适用于简单场景。
        执行基本的清洗操作：
        - 中英文字段名映射
        - 数据类型标准化
        - 基本格式转换
        - 简单质量检查
        
        Args:
            financial_data: 要清洗的财务数据
        
        Returns:
            Dict[str, Any]: 快速清洗结果
        """
        try:
            self.logger.info("开始快速数据清洗...")
            
            # 使用简化的选项进行清洗
            quick_options = {
                'strict_mode': False,
                'auto_fix_issues': True,
                'generate_quality_report': False,  # 快速模式不生成详细报告
                'target_format': 'data_analysis_agent_compatible'
            }
            
            # 执行清洗
            import asyncio
            result = asyncio.run(
                self.cleanser_agent.cleanse_financial_data(financial_data, quick_options)
            )
            
            # 简化返回结果
            if result['success']:
                simplified_result = {
                    'success': True,
                    'cleansed_data': result['cleansed_data'],
                    'quality_score': result['quality_score'],
                    'quality_level': result['quality_level'],
                    'fields_processed': result['transformation_summary']['fields_transformed'],
                    'warnings_count': len(result.get('processing_log', {}).get('validation', {}).get('warnings', [])),
                    'metadata': {
                        'processing_mode': 'quick_cleanse',
                        'processed_by': 'DataCleansingToolkit'
                    }
                }
                
                self.logger.info(f"快速数据清洗完成，质量分数: {result['quality_score']:.2f}")
                return simplified_result
            else:
                self.logger.error(f"快速数据清洗失败: {result.get('error', 'Unknown error')}")
                return result
                
        except Exception as e:
            error_msg = f"快速数据清洗失败: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'tool': 'quick_cleanse_data',
                'timestamp': datetime.now().isoformat()
            }
    
    @register_tool()
    def get_tool_status(self) -> Dict[str, Any]:
        """
        获取工具状态和统计信息
        
        Returns:
            Dict[str, Any]: 工具状态信息
        """
        try:
            # 获取处理统计
            stats = self.cleanser_agent.get_processing_statistics()
            
            status_info = {
                'tool_name': 'DataCleansingToolkit',
                'version': '1.0',
                'status': 'active',
                'configuration': {
                    'strict_mode': self.strict_mode,
                    'auto_fix_issues': self.auto_fix_issues,
                    'generate_quality_report': self.generate_quality_report,
                    'workspace_root': self.workspace_root
                },
                'processing_statistics': stats.get('processing_stats', {}),
                'capabilities': [
                    'cleanse_financial_data',
                    'validate_data_format', 
                    'transform_data_structure',
                    'assess_data_quality',
                    'quick_cleanse_data'
                ],
                'supported_data_formats': [
                    'chinese_financial_format',
                    'standard_financial_format',
                    'user_custom_format',
                    'historical_data_format',
                    'mixed_financial_format'
                ],
                'last_updated': datetime.now().isoformat()
            }
            
            self.logger.info("工具状态查询完成")
            return status_info
            
        except Exception as e:
            error_msg = f"获取工具状态失败: {str(e)}"
            self.logger.error(error_msg)
            return {
                'tool_name': 'DataCleansingToolkit',
                'status': 'error',
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            }