"""
财务数据格式转换工具
专门用于在智能体间转换财务数据格式
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)

class FinancialDataConverter:
    """
    财务数据格式转换器
    用于将不同智能体间的财务数据转换为图表生成所需的格式
    """
    
    def __init__(self):
        self.logger = logger
        
        # 财务指标到中文的映射
        self.metric_mapping = {
            # 盈利能力指标
            'gross_profit_margin': '毛利率',
            'net_profit_margin': '净利率',
            'roe': '净资产收益率(ROE)',
            'roa': '总资产收益率(ROA)',
            'operating_margin': '营业利润率',
            
            # 偿债能力指标
            'debt_to_asset_ratio': '资产负债率',
            'current_ratio': '流动比率',
            'quick_ratio': '速动比率',
            'debt_to_equity_ratio': '产权比率',
            
            # 运营效率指标
            'asset_turnover': '总资产周转率',
            'inventory_turnover': '存货周转率',
            'receivables_turnover': '应收账款周转率',
            
            # 成长能力指标
            'revenue_growth': '营收增长率',
            'profit_growth': '利润增长率',
            'eps_growth': '每股收益增长率',
            
            # 现金流指标
            'operating_cash_flow': '经营活动现金流',
            'cash_flow_ratio': '现金流比率',
            'free_cash_flow': '自由现金流'
        }
    
    def convert_financial_ratios_to_chart_format(self, financial_data: Dict) -> Dict[str, Any]:
        """
        将财务比率数据转换为图表格式
        
        Args:
            financial_data: 财务分析结果数据
            
        Returns:
            转换后的图表数据格式
        """
        try:
            self.logger.info("开始转换财务比率数据为图表格式")
            
            # 提取盈利能力指标
            profitability_data = financial_data.get('profitability', {})
            
            # 提取偿债能力指标
            solvency_data = financial_data.get('solvency', {})
            
            # 提取运营效率指标
            efficiency_data = financial_data.get('efficiency', {})
            
            # 提取成长能力指标
            growth_data = financial_data.get('growth', {})
            
            # 提取现金流指标
            cash_flow_data = financial_data.get('cash_flow', {})
            
            # 生成多种图表格式
            chart_data = {
                'profitability_chart': self._create_profitability_chart_data(profitability_data),
                'solvency_chart': self._create_solvency_chart_data(solvency_data),
                'efficiency_chart': self._create_efficiency_chart_data(efficiency_data),
                'growth_chart': self._create_growth_chart_data(growth_data),
                'comprehensive_chart': self._create_comprehensive_chart_data(
                    profitability_data, solvency_data, efficiency_data, growth_data
                ),
                'radar_chart': self._create_radar_chart_data(
                    profitability_data, solvency_data, efficiency_data, growth_data
                )
            }
            
            # 过滤掉空数据
            valid_charts = {k: v for k, v in chart_data.items() if self._is_valid_chart_data(v)}
            
            self.logger.info(f"成功生成 {len(valid_charts)} 个图表格式")
            return valid_charts
            
        except Exception as e:
            self.logger.error(f"转换财务比率数据失败: {e}")
            return {}
    
    def _create_profitability_chart_data(self, profitability_data: Dict) -> Dict[str, Any]:
        """创建盈利能力图表数据"""
        if not profitability_data:
            return {}
            
        # 筛选有效的盈利能力指标
        profit_metrics = {
            '毛利率': profitability_data.get('gross_profit_margin', 0),
            '净利率': profitability_data.get('net_profit_margin', 0),
            'ROE': profitability_data.get('roe', 0),
            'ROA': profitability_data.get('roa', 0)
        }
        
        # 转换为百分比显示
        for key, value in profit_metrics.items():
            if isinstance(value, (int, float)):
                profit_metrics[key] = round(value * 100, 2)
        
        return {
            'title': '盈利能力指标',
            'x_axis': {
                'name': '指标',
                'data': list(profit_metrics.keys())
            },
            'series': [{
                'name': '陕西建工',
                'data': list(profit_metrics.values())
            }]
        }
    
    def _create_solvency_chart_data(self, solvency_data: Dict) -> Dict[str, Any]:
        """创建偿债能力图表数据"""
        if not solvency_data:
            return {}
            
        # 筛选有效的偿债能力指标
        solvency_metrics = {
            '资产负债率': solvency_data.get('debt_to_asset_ratio', 0),
            '流动比率': solvency_data.get('current_ratio', 0),
            '速动比率': solvency_data.get('quick_ratio', 0)
        }
        
        # 转换为百分比显示
        for key, value in solvency_metrics.items():
            if key == '资产负债率' and isinstance(value, (int, float)):
                solvency_metrics[key] = round(value * 100, 2)
            elif isinstance(value, (int, float)):
                solvency_metrics[key] = round(value, 2)
        
        return {
            'title': '偿债能力指标',
            'x_axis': {
                'name': '指标',
                'data': list(solvency_metrics.keys())
            },
            'series': [{
                'name': '陕西建工',
                'data': list(solvency_metrics.values())
            }]
        }
    
    def _create_efficiency_chart_data(self, efficiency_data: Dict) -> Dict[str, Any]:
        """创建运营效率图表数据"""
        if not efficiency_data:
            return {}
            
        # 筛选有效的运营效率指标
        efficiency_metrics = {
            '总资产周转率': efficiency_data.get('asset_turnover', 0),
            '存货周转率': efficiency_data.get('inventory_turnover', 0),
            '应收账款周转率': efficiency_data.get('receivables_turnover', 0)
        }
        
        # 保留原始数值（周转率不是百分比）
        for key, value in efficiency_metrics.items():
            if isinstance(value, (int, float)):
                efficiency_metrics[key] = round(value, 2)
        
        return {
            'title': '运营效率指标',
            'x_axis': {
                'name': '指标',
                'data': list(efficiency_metrics.keys())
            },
            'series': [{
                'name': '陕西建工',
                'data': list(efficiency_metrics.values())
            }]
        }
    
    def _create_growth_chart_data(self, growth_data: Dict) -> Dict[str, Any]:
        """创建成长能力图表数据"""
        if not growth_data:
            return {}
            
        # 筛选有效的成长能力指标
        growth_metrics = {
            '营收增长率': growth_data.get('revenue_growth', 0),
            '利润增长率': growth_data.get('profit_growth', 0),
            '每股收益增长率': growth_data.get('eps_growth', 0)
        }
        
        # 转换为百分比显示
        for key, value in growth_metrics.items():
            if isinstance(value, (int, float)):
                growth_metrics[key] = round(value * 100, 2)
        
        return {
            'title': '成长能力指标',
            'x_axis': {
                'name': '指标',
                'data': list(growth_metrics.keys())
            },
            'series': [{
                'name': '陕西建工',
                'data': list(growth_metrics.values())
            }]
        }
    
    def _create_comprehensive_chart_data(self, profitability_data: Dict, solvency_data: Dict, 
                                       efficiency_data: Dict, growth_data: Dict) -> Dict[str, Any]:
        """创建综合对比图表数据"""
        all_metrics = {}
        
        # 合并所有指标
        all_metrics.update(self._prepare_metrics_for_chart(profitability_data))
        all_metrics.update(self._prepare_metrics_for_chart(solvency_data))
        all_metrics.update(self._prepare_metrics_for_chart(efficiency_data))
        all_metrics.update(self._prepare_metrics_for_chart(growth_data))
        
        if not all_metrics:
            return {}
        
        return {
            'title': '综合财务指标对比',
            'x_axis': {
                'name': '财务指标',
                'data': list(all_metrics.keys())
            },
            'series': [{
                'name': '陕西建工',
                'data': list(all_metrics.values())
            }]
        }
    
    def _create_radar_chart_data(self, profitability_data: Dict, solvency_data: Dict, 
                               efficiency_data: Dict, growth_data: Dict) -> Dict[str, Any]:
        """创建雷达图数据"""
        # 定义四大类别的标准评分（5分制）
        categories = ['盈利能力', '偿债能力', '运营效率', '成长能力']
        
        # 计算各类别的评分（简化计算）
        scores = []
        
        # 盈利能力评分
        profit_score = self._calculate_category_score(profitability_data, 'profitability')
        scores.append(profit_score)
        
        # 偿债能力评分
        solvency_score = self._calculate_category_score(solvency_data, 'solvency')
        scores.append(solvency_score)
        
        # 运营效率评分
        efficiency_score = self._calculate_category_score(efficiency_data, 'efficiency')
        scores.append(efficiency_score)
        
        # 成长能力评分
        growth_score = self._calculate_category_score(growth_data, 'growth')
        scores.append(growth_score)
        
        return {
            'title': '财务健康雷达图',
            'categories': categories,
            'series': [{
                'name': '陕西建工',
                'data': scores
            }]
        }
    
    def _prepare_metrics_for_chart(self, data: Dict) -> Dict[str, float]:
        """准备用于图表的指标数据"""
        metrics = {}
        for key, value in data.items():
            if isinstance(value, (int, float)):
                # 大多数指标转换为百分比，但周转率类指标保持原值
                if key in ['asset_turnover', 'inventory_turnover', 'receivables_turnover']:
                    metrics[self.metric_mapping.get(key, key)] = round(value, 2)
                else:
                    metrics[self.metric_mapping.get(key, key)] = round(value * 100, 2)
        return metrics
    
    def _calculate_category_score(self, data: Dict, category: str) -> float:
        """计算类别的综合评分（5分制）"""
        if not data:
            return 2.0  # 默认中等分数
        
        # 简化的评分计算（基于指标数量和数值）
        valid_values = [v for v in data.values() if isinstance(v, (int, float)) and v > 0]
        if not valid_values:
            return 2.0
        
        # 根据类别调整评分标准
        if category == 'profitability':
            # 盈利能力：平均得分
            avg_value = sum(valid_values) / len(valid_values)
            return min(5.0, max(1.0, avg_value * 100))  # 假设小数，转换为百分比后评分
            
        elif category == 'solvency':
            # 偿债能力：资产负债率越低越好
            debt_ratio = data.get('debt_to_asset_ratio', 0)
            if debt_ratio > 0:
                return max(1.0, 5.0 - (debt_ratio * 100 / 20))  # 资产负债率超过80%开始扣分
            
        elif category == 'efficiency':
            # 运营效率：周转率越高越好
            turnover_values = [v for k, v in data.items() if 'turnover' in k and isinstance(v, (int, float))]
            if turnover_values:
                avg_turnover = sum(turnover_values) / len(turnover_values)
                return min(5.0, max(1.0, avg_turnover * 2))
                
        elif category == 'growth':
            # 成长能力：增长率越高越好
            growth_values = [v for v in valid_values if abs(v) < 10]  # 排除异常大的增长率
            if growth_values:
                avg_growth = sum(growth_values) / len(growth_values)
                return min(5.0, max(1.0, 2.0 + avg_growth * 100))
        
        return 2.0  # 默认中等分数
    
    def _is_valid_chart_data(self, chart_data: Dict) -> bool:
        """检查图表数据是否有效"""
        if not isinstance(chart_data, dict):
            return False
        
        required_fields = ['title', 'x_axis', 'series']
        return all(field in chart_data for field in required_fields)
    
    def convert_basic_financial_data_to_chart_format(self, financial_data: Dict) -> Dict[str, Any]:
        """
        将基础财务数据（收入、利润、资产等）转换为图表格式
        
        Args:
            financial_data: 基础财务数据
            
        Returns:
            转换后的图表数据格式
        """
        try:
            self.logger.info("开始转换基础财务数据为图表格式")
            
            # 收入和利润数据
            revenue_profit_data = {
                '营业收入': financial_data.get('revenue', 0),
                '净利润': financial_data.get('net_profit', 0),
                '毛利润': financial_data.get('gross_profit', 0)
            }
            
            # 资产和负债数据
            asset_liability_data = {
                '总资产': financial_data.get('total_assets', 0),
                '总负债': financial_data.get('total_liabilities', 0),
                '净资产': financial_data.get('total_equity', 0)
            }
            
            chart_data = {
                'revenue_profit_chart': {
                    'title': '收入与利润',
                    'x_axis': {
                        'name': '指标',
                        'data': list(revenue_profit_data.keys())
                    },
                    'series': [{
                        'name': '金额(亿元)',
                        'data': list(revenue_profit_data.values())
                    }]
                },
                'asset_liability_chart': {
                    'title': '资产与负债',
                    'x_axis': {
                        'name': '指标',
                        'data': list(asset_liability_data.keys())
                    },
                    'series': [{
                        'name': '金额(亿元)',
                        'data': list(asset_liability_data.values())
                    }]
                }
            }
            
            # 过滤掉空数据
            valid_charts = {k: v for k, v in chart_data.items() if self._is_valid_chart_data(v)}
            
            self.logger.info(f"成功生成 {len(valid_charts)} 个基础图表格式")
            return valid_charts
            
        except Exception as e:
            self.logger.error(f"转换基础财务数据失败: {e}")
            return {}