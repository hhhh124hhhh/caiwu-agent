#!/usr/bin/env python3
"""
图表数据构造工具
帮助图表生成智能体正确构造各种图表类型的数据
"""

import json
from typing import Dict, Any, List, Union, Optional
from chart_data_validator import ChartDataValidator

class ChartDataBuilder:
    """图表数据构造器"""
    
    def __init__(self):
        self.validator = ChartDataValidator()
        
        # 标准数据单位映射
        self.unit_standards = {
            'revenue': '亿元',
            'profit': '亿元', 
            'assets': '亿元',
            'liabilities': '亿元',
            'ratio': '%',
            'rate': '%',
            'efficiency': '次/年'
        }
    
    def build_trend_chart_data(self, title: str, years: List[str], metrics: Dict[str, List[float]], 
                              unit: str = None) -> Dict[str, Any]:
        """
        构建趋势图数据（折线图/面积图）
        
        Args:
            title: 图表标题
            years: 年份列表
            metrics: 指标数据，格式为 {指标名: [数值列表]}
            unit: 数据单位
            
        Returns:
            标准图表数据字典
        """
        chart_data = {
            "title": title,
            "x_axis": years,
            "series": []
        }
        
        for metric_name, values in metrics.items():
            # 确定单位
            if unit:
                display_unit = unit
            else:
                # 根据指标名推断单位
                display_unit = self._infer_unit(metric_name)
            
            # 构造系列名称
            series_name = f"{metric_name}({display_unit})" if display_unit else metric_name
            
            # 确保数据长度匹配
            if len(values) != len(years):
                if len(values) > len(years):
                    values = values[:len(years)]
                else:
                    values = values + [0] * (len(years) - len(values))
            
            chart_data["series"].append({
                "name": series_name,
                "data": values
            })
        
        return self._validate_and_fix(chart_data, 'line')
    
    def build_comparison_chart_data(self, title: str, categories: List[str], 
                                   metrics: Dict[str, List[float]], chart_type: str = 'bar') -> Dict[str, Any]:
        """
        构建对比图数据（柱状图/分组柱状图）
        
        Args:
            title: 图表标题
            categories: 对比类别
            metrics: 指标数据，格式为 {指标名: [数值列表]}
            chart_type: 图表类型
            
        Returns:
            标准图表数据字典
        """
        chart_data = {
            "title": title,
            "x_axis": categories,
            "series": []
        }
        
        for metric_name, values in metrics.items():
            # 确定单位
            display_unit = self._infer_unit(metric_name)
            series_name = f"{metric_name}({display_unit})" if display_unit else metric_name
            
            # 确保数据长度匹配
            if len(values) != len(categories):
                if len(values) > len(categories):
                    values = values[:len(categories)]
                else:
                    values = values + [0] * (len(categories) - len(values))
            
            chart_data["series"].append({
                "name": series_name,
                "data": values
            })
        
        return self._validate_and_fix(chart_data, chart_type)
    
    def build_radar_chart_data(self, title: str, categories: List[str], 
                              companies_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """
        构建雷达图数据
        
        Args:
            title: 图表标题
            categories: 雷达图维度
            companies_data: 公司数据，格式为 {公司名: [分数列表]}
            
        Returns:
            标准图表数据字典
        """
        chart_data = {
            "title": title,
            "categories": categories,
            "series": []
        }
        
        for company_name, scores in companies_data.items():
            # 确保数据长度匹配
            if len(scores) != len(categories):
                if len(scores) > len(categories):
                    scores = scores[:len(categories)]
                else:
                    scores = scores + [50] * (len(categories) - len(scores))
            
            # 确保分数在0-100范围内
            scores = [max(0, min(100, score)) for score in scores]
            
            chart_data["series"].append({
                "name": company_name,
                "data": scores
            })
        
        return self._validate_and_fix(chart_data, 'radar')
    
    def build_financial_health_radar(self, company_name: str, financial_metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        构建财务健康雷达图
        
        Args:
            company_name: 公司名称
            financial_metrics: 财务指标，包含各种比率数据
            
        Returns:
            标准雷达图数据字典
        """
        # 标准财务健康维度
        categories = ["盈利能力", "偿债能力", "运营效率", "成长能力", "现金流"]
        
        # 根据财务指标计算各维度得分
        scores = self._calculate_health_scores(financial_metrics)
        
        chart_data = {
            "title": f"{company_name}财务健康雷达图",
            "categories": categories,
            "series": [
                {
                    "name": company_name,
                    "data": scores
                },
                {
                    "name": "行业平均",
                    "data": [60, 60, 60, 60, 60]  # 假设行业平均为60分
                }
            ]
        }
        
        return self._validate_and_fix(chart_data, 'radar')
    
    def build_change_rate_chart(self, title: str, indicators: List[str], 
                               change_rates: List[float]) -> Dict[str, Any]:
        """
        构建变化率图表
        
        Args:
            title: 图表标题
            indicators: 指标名称列表
            change_rates: 变化率列表（百分比）
            
        Returns:
            标准图表数据字典
        """
        chart_data = {
            "title": title,
            "x_axis": indicators,
            "series": [
                {
                    "name": "变化率(%)",
                    "data": change_rates
                }
            ]
        }
        
        return self._validate_and_fix(chart_data, 'bar')
    
    def standardize_financial_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        标准化财务数据，修复单位不一致和异常值问题
        
        Args:
            raw_data: 原始财务数据
            
        Returns:
            标准化后的财务数据
        """
        standardized = {}
        
        for key, value in raw_data.items():
            if isinstance(value, (int, float)):
                # 修复异常值
                if key in ['roe', 'roa', 'net_profit_margin', 'current_ratio']:
                    # 这些比率应该在合理范围内
                    if key == 'current_ratio':
                        value = max(0.1, min(10.0, value))  # 流动比率合理范围
                    else:
                        value = max(-100, min(100, value))  # 百分比比率合理范围
                
                # 标准化单位
                if 'revenue' in key.lower() or 'profit' in key.lower() or 'assets' in key.lower():
                    # 营收、利润、资产类数据统一为亿元
                    if abs(value) > 1000:  # 可能是万元或其他单位
                        value = value / 10000
                
                standardized[key] = value
            elif isinstance(value, dict):
                standardized[key] = self.standardize_financial_data(value)
            elif isinstance(value, list):
                standardized[key] = [self.standardize_financial_data({f'item_{i}': v})[f'item_{i}'] 
                                   for i, v in enumerate(value) if isinstance(v, (int, float))]
            else:
                standardized[key] = value
        
        return standardized
    
    def _infer_unit(self, metric_name: str) -> str:
        """根据指标名推断单位"""
        metric_name_lower = metric_name.lower()
        
        if any(keyword in metric_name_lower for keyword in ['revenue', 'income', 'profit', 'asset', 'liability']):
            return '亿元'
        elif any(keyword in metric_name_lower for keyword in ['ratio', 'rate', 'margin', 'roe', 'roa']):
            return '%'
        elif any(keyword in metric_name_lower for keyword in ['turnover', '周转']):
            return '次/年'
        elif '率' in metric_name or '比' in metric_name:
            return '%'
        else:
            return ''
    
    def _calculate_health_scores(self, financial_metrics: Dict[str, float]) -> List[float]:
        """根据财务指标计算健康得分"""
        scores = []
        
        # 确保财务数据是数值类型
        def get_numeric_value(key, default=0):
            value = financial_metrics.get(key, default)
            if isinstance(value, dict):
                # 如果是字典，尝试获取数值
                return float(list(value.values())[0]) if value.values() else default
            return float(value) if value is not None else default
        
        # 盈利能力得分
        roe = get_numeric_value('roe')
        roa = get_numeric_value('roa') 
        net_margin = get_numeric_value('net_profit_margin')
        profitability_score = min(100, max(0, (roe + roa + net_margin * 10) / 3 * 10))
        scores.append(profitability_score)
        
        # 偿债能力得分
        debt_ratio = get_numeric_value('debt_to_assets', 100)
        current_ratio = get_numeric_value('current_ratio', 1)
        solvency_score = min(100, max(0, (100 - debt_ratio) * 1.2 + current_ratio * 10))
        scores.append(solvency_score)
        
        # 运营效率得分
        asset_turnover = get_numeric_value('asset_turnover', 0)
        efficiency_score = min(100, max(0, asset_turnover * 50))
        scores.append(efficiency_score)
        
        # 成长能力得分
        revenue_growth = get_numeric_value('revenue_growth', 0)
        profit_growth = get_numeric_value('profit_growth', 0)
        growth_score = min(100, max(0, (revenue_growth + profit_growth) / 2 * 5))
        scores.append(growth_score)
        
        # 现金流得分（简化处理）
        cash_score = 50  # 默认中等水平
        scores.append(cash_score)
        
        return scores
    
    def _validate_and_fix(self, chart_data: Dict[str, Any], chart_type: str) -> Dict[str, Any]:
        """验证并自动修复图表数据"""
        validation_result = self.validator.validate_chart_data(chart_data, chart_type)
        
        if not validation_result['valid']:
            chart_data = self.validator.auto_fix_chart_data(chart_data, chart_type)
        
        return chart_data
    
    def to_json_string(self, chart_data: Dict[str, Any]) -> str:
        """将图表数据转换为JSON字符串"""
        return json.dumps(chart_data, ensure_ascii=False, separators=(',', ':'))
    
    def create_safe_chart_data(self, chart_type: str, **kwargs) -> Dict[str, Any]:
        """
        创建安全的图表数据，自动处理各种边界情况
        
        Args:
            chart_type: 图表类型
            **kwargs: 图表参数
            
        Returns:
            安全的图表数据字典
        """
        try:
            if chart_type in ['line', 'area']:
                return self.build_trend_chart_data(
                    title=kwargs.get('title', f'{chart_type.upper()}图表'),
                    years=kwargs.get('years', ['2021', '2022', '2023', '2024']),
                    metrics=kwargs.get('metrics', {'指标1': [10, 20, 30, 40]})
                )
            elif chart_type in ['bar', 'column']:
                return self.build_comparison_chart_data(
                    title=kwargs.get('title', f'{chart_type.upper()}图表'),
                    categories=kwargs.get('categories', ['类别1', '类别2', '类别3']),
                    metrics=kwargs.get('metrics', {'指标1': [10, 20, 30]})
                )
            elif chart_type == 'radar':
                if 'financial_metrics' in kwargs:
                    return self.build_financial_health_radar(
                        company_name=kwargs.get('company_name', '公司'),
                        financial_metrics=kwargs['financial_metrics']
                    )
                else:
                    return self.build_radar_chart_data(
                        title=kwargs.get('title', '雷达图'),
                        categories=kwargs.get('categories', ['维度1', '维度2', '维度3', '维度4', '维度5']),
                        companies_data=kwargs.get('companies_data', {'公司A': [60, 70, 80, 65, 75]})
                    )
            else:
                # 默认返回折线图
                return self.build_trend_chart_data(
                    title=kwargs.get('title', '图表'),
                    years=kwargs.get('years', ['2021', '2022', '2023', '2024']),
                    metrics=kwargs.get('metrics', {'指标1': [10, 20, 30, 40]})
                )
        except Exception as e:
            # 如果出现任何错误，返回默认的安全数据
            return {
                "title": "默认图表",
                "x_axis": ["A", "B", "C"],
                "series": [{"name": "数据", "data": [10, 20, 30]}]
            }


def test_chart_builder():
    """测试图表数据构造器"""
    builder = ChartDataBuilder()
    
    # 测试趋势图
    trend_data = builder.build_trend_chart_data(
        title="陕西建工营业收入趋势",
        years=["2022", "2023", "2024", "2025Q"],
        metrics={"营业收入": [1350.25, 1420.18, 1511.39, 573.88]},
        unit="亿元"
    )
    print("趋势图数据:", json.dumps(trend_data, ensure_ascii=False, indent=2))
    
    # 测试对比图
    comparison_data = builder.build_comparison_chart_data(
        title="陕西建工盈利能力指标对比",
        categories=["2022", "2023", "2024", "2025Q"],
        metrics={
            "净利率": [2.11, 2.27, 2.39, 1.92],
            "ROE": [8.15, 8.92, 9.22, 2.82]
        }
    )
    print("对比图数据:", json.dumps(comparison_data, ensure_ascii=False, indent=2))
    
    # 测试雷达图
    radar_data = builder.build_financial_health_radar(
        company_name="陕西建工",
        financial_metrics={
            'roe': 2.82,
            'net_profit_margin': 1.92,
            'debt_to_assets': 88.71,
            'current_ratio': 1.11,
            'asset_turnover': 0.17
        }
    )
    print("雷达图数据:", json.dumps(radar_data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    test_chart_builder()