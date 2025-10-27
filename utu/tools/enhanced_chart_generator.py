"""
增强版图表生成工具
集成数据格式转换功能，自动处理智能体间的数据格式转换
"""

import json
import logging
from typing import Dict, Any, Optional
from .base import AsyncBaseToolkit
from .financial_data_converter import FinancialDataConverter
from .tabular_data_toolkit import TabularDataToolkit

logger = logging.getLogger(__name__)

class EnhancedChartGenerator(AsyncBaseToolkit):
    """
    增强版图表生成器
    自动处理数据格式转换和图表生成
    """
    
    def __init__(self, config=None):
        super().__init__(config=config)
        self.logger = logger
        self.data_converter = FinancialDataConverter()
        
    def generate_charts_from_financial_data(self, financial_data: Dict, chart_types: list = None, 
                                           output_dir: str = "./run_workdir") -> Dict[str, Any]:
        """
        从财务分析数据生成图表
        
        Args:
            financial_data: 财务分析结果数据
            chart_types: 要生成的图表类型列表，默认为 ['bar', 'radar', 'pie']
            output_dir: 输出目录
            
        Returns:
            生成结果
        """
        try:
            self.logger.info("开始从财务数据生成图表")
            
            if chart_types is None:
                chart_types = ['bar', 'radar', 'pie']
            
            # 转换财务数据为图表格式
            chart_data_dict = self.data_converter.convert_financial_ratios_to_chart_format(financial_data)
            
            if not chart_data_dict:
                self.logger.warning("财务数据转换为图表格式失败")
                return {'success': False, 'message': '财务数据转换为图表格式失败'}
            
            # 使用TabularDataToolkit生成图表
            tabular_toolkit = TabularDataToolkit()
            results = []
            
            for chart_type in chart_types:
                for chart_name, chart_data in chart_data_dict.items():
                    try:
                        # 确定最适合的图表类型
                        optimal_type = self._determine_optimal_chart_type(chart_name, chart_type)
                        
                        # 转换为JSON字符串
                        data_json = json.dumps(chart_data, ensure_ascii=False)
                        
                        # 生成图表
                        result = tabular_toolkit.generate_charts(
                            data_json=data_json,
                            chart_type=optimal_type,
                            output_dir=output_dir
                        )
                        
                        if result.get('success', False):
                            results.append({
                                'chart_name': chart_name,
                                'chart_type': optimal_type,
                                'files': result.get('files', []),
                                'chart_data': chart_data
                            })
                            self.logger.info(f"成功生成图表: {chart_name} ({optimal_type})")
                        else:
                            self.logger.warning(f"生成图表失败: {chart_name} - {result.get('message', '未知错误')}")
                            
                    except Exception as e:
                        self.logger.error(f"生成图表异常: {chart_name} - {e}")
            
            return {
                'success': len(results) > 0,
                'message': f"成功生成 {len(results)} 个图表" if results else "没有生成任何图表",
                'charts': results,
                'chart_count': len(results)
            }
            
        except Exception as e:
            self.logger.error(f"从财务数据生成图表失败: {e}")
            return {'success': False, 'message': f"生成图表失败: {str(e)}"}
    
    def _determine_optimal_chart_type(self, chart_name: str, requested_type: str) -> str:
        """
        根据图表名称和请求类型确定最合适的图表类型
        
        Args:
            chart_name: 图表名称
            requested_type: 用户请求的图表类型
            
        Returns:
            最适合的图表类型
        """
        # 图表名称与类型的映射
        chart_type_mapping = {
            'profitability_chart': 'bar',     # 盈利能力用柱状图
            'solvency_chart': 'bar',        # 偿债能力用柱状图
            'efficiency_chart': 'bar',      # 运营效率用柱状图
            'growth_chart': 'bar',          # 成长能力用柱状图
            'comprehensive_chart': 'bar',   # 综合对比用柱状图
            'radar_chart': 'radar'          # 雷达图专用
        }
        
        # 如果请求的类型与图表名称匹配，优先使用请求的类型
        if requested_type in chart_type_mapping.values():
            return requested_type
        
        # 根据图表名称选择最佳类型
        optimal_type = chart_type_mapping.get(chart_name, 'bar')
        
        # 如果用户请求的类型支持，使用用户请求的类型
        if requested_type in ['bar', 'line', 'pie', 'radar', 'scatter', 'heatmap']:
            return requested_type
        
        return optimal_type
    
    def generate_charts_from_basic_data(self, basic_data: Dict, chart_types: list = None,
                                          output_dir: str = "./run_workdir") -> Dict[str, Any]:
        """
        从基础财务数据生成图表
        
        Args:
            basic_data: 基础财务数据（收入、利润、资产等）
            chart_types: 要生成的图表类型列表
            output_dir: 输出目录
            
        Returns:
            生成结果
        """
        try:
            self.logger.info("开始从基础财务数据生成图表")
            
            if chart_types is None:
                chart_types = ['bar', 'pie']
            
            # 转换基础数据为图表格式
            chart_data_dict = self.data_converter.convert_basic_financial_data_to_chart_format(basic_data)
            
            if not chart_data_dict:
                self.logger.warning("基础财务数据转换为图表格式失败")
                return {'success': False, 'message': '基础财务数据转换为图表格式失败'}
            
            # 使用TabularDataToolkit生成图表
            tabular_toolkit = TabularDataToolkit()
            results = []
            
            for chart_type in chart_types:
                for chart_name, chart_data in chart_data_dict.items():
                    try:
                        # 转换为JSON字符串
                        data_json = json.dumps(chart_data, ensure_ascii=False)
                        
                        # 生成图表
                        result = tabular_toolkit.generate_charts(
                            data_json=data_json,
                            chart_type=chart_type,
                            output_dir=output_dir
                        )
                        
                        if result.get('success', False):
                            results.append({
                                'chart_name': chart_name,
                                'chart_type': chart_type,
                                'files': result.get('files', []),
                                'chart_data': chart_data
                            })
                            self.logger.info(f"成功生成基础图表: {chart_name} ({chart_type})")
                        else:
                            self.logger.warning(f"生成基础图表失败: {chart_name} - {result.get('message', '未知错误')}")
                            
                    except Exception as e:
                        self.logger.error(f"生成基础图表异常: {chart_name} - {e}")
            
            return {
                'success': len(results) > 0,
                'message': f"成功生成 {len(results)} 个基础图表" if results else "没有生成任何基础图表",
                'charts': results,
                'chart_count': len(results)
            }
            
        except Exception as e:
            self.logger.error(f"从基础财务数据生成图表失败: {e}")
            return {'success': False, 'message': f"生成基础图表失败: {str(e)}"}
    
    def analyze_and_generate_charts(self, data: Dict, output_dir: str = "./run_workdir") -> Dict[str, Any]:
        """
        智能分析数据并生成合适的图表
        
        Args:
            data: 输入数据（可能是财务比率或基础数据）
            output_dir: 输出目录
            
        Returns:
            生成结果
        """
        try:
            self.logger.info("开始智能分析数据并生成图表")
            
            # 判断数据类型
            if self._is_financial_ratios_data(data):
                self.logger.info("检测到财务比率数据")
                return self.generate_charts_from_financial_data(data, output_dir=output_dir)
            elif self._is_basic_financial_data(data):
                self.logger.info("检测到基础财务数据")
                return self.generate_charts_from_basic_data(data, output_dir=output_dir)
            else:
                self.logger.warning("未识别的数据类型，尝试通用处理")
                # 尝试作为财务比率数据处理
                return self.generate_charts_from_financial_data(data, output_dir=output_dir)
                
        except Exception as e:
            self.logger.error(f"智能分析数据失败: {e}")
            return {'success': False, 'message': f"智能分析失败: {str(e)}"}
    
    def _is_financial_ratios_data(self, data: Dict) -> bool:
        """判断是否为财务比率数据"""
        if not isinstance(data, dict):
            return False
        
        # 检查是否包含典型的财务比率字段
        ratio_indicators = ['profitability', 'solvency', 'efficiency', 'growth', 'cash_flow']
        return any(indicator in data for indicator in ratio_indicators)
    
    def _is_basic_financial_data(self, data: Dict) -> bool:
        """判断是否为基础财务数据"""
        if not isinstance(data, dict):
            return False
        
        # 检查是否包含基础财务字段
        basic_fields = ['revenue', 'net_profit', 'total_assets', 'total_liabilities', 'total_equity']
        return any(field in data for field in basic_fields)