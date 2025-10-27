#!/usr/bin/env python3
"""
增强版图表生成工具
集成数据验证、修复和标准化功能
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union
from chart_data_validator import ChartDataValidator
from chart_data_builder import ChartDataBuilder

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedChartGenerator:
    """增强版图表生成器"""
    
    def __init__(self, workspace_root: str = "./run_workdir"):
        self.workspace_root = workspace_root
        self.validator = ChartDataValidator()
        self.builder = ChartDataBuilder()
        
        # 预定义的财务图表模板
        self.chart_templates = {
            "revenue_trend": {
                "title": "{company}营业收入趋势分析",
                "chart_type": "line",
                "required_metrics": ["revenue"],
                "unit": "亿元"
            },
            "profit_trend": {
                "title": "{company}净利润趋势分析", 
                "chart_type": "line",
                "required_metrics": ["net_profit"],
                "unit": "亿元"
            },
            "profitability_comparison": {
                "title": "{company}盈利能力指标对比",
                "chart_type": "bar",
                "required_metrics": ["net_profit_margin", "roe"],
                "unit": "%"
            },
            "financial_health_radar": {
                "title": "{company}财务健康雷达图",
                "chart_type": "radar",
                "required_metrics": ["roe", "net_profit_margin", "debt_to_assets", "current_ratio", "asset_turnover"]
            },
            "debt_ratio_trend": {
                "title": "{company}资产负债率趋势",
                "chart_type": "line", 
                "required_metrics": ["debt_to_assets"],
                "unit": "%"
            },
            "change_rate_analysis": {
                "title": "{company}关键指标变化率分析",
                "chart_type": "bar",
                "required_metrics": ["revenue_growth", "profit_growth"],
                "unit": "%"
            }
        }
    
    def generate_chart_with_validation(self, chart_data_json: str, chart_type: str = 'line', 
                                      output_dir: str = None) -> Dict[str, Any]:
        """
        生成图表，包含完整的数据验证和修复流程
        
        Args:
            chart_data_json: 图表数据的JSON字符串
            chart_type: 图表类型
            output_dir: 输出目录
            
        Returns:
            生成结果
        """
        if output_dir is None:
            output_dir = self.workspace_root
            
        logger.info(f"开始生成{chart_type}图表，输出目录: {output_dir}")
        
        # 第一步：JSON格式验证和修复
        logger.info("步骤1: 验证和修复JSON格式")
        validation_result = self.validator.validate_and_fix_json(chart_data_json, chart_type)
        
        if not validation_result['success']:
            logger.error(f"JSON格式无法修复: {validation_result['error']}")
            return {
                'success': False,
                'message': f"JSON格式错误且无法修复: {validation_result['error']}",
                'files': [],
                'error': 'JSON_FORMAT_ERROR'
            }
        
        chart_data = validation_result['data']
        if validation_result['fixed']:
            logger.info("JSON格式已自动修复")
        
        # 第二步：数据标准化和验证
        logger.info("步骤2: 数据标准化和验证")
        standardized_data = self._standardize_chart_data(chart_data, chart_type)
        
        # 第三步：生成图表
        logger.info("步骤3: 生成图表")
        try:
            # 这里应该调用实际的图表生成工具
            # 由于我们无法直接访问原始工具，这里提供一个模拟的实现
            chart_result = self._simulate_chart_generation(standardized_data, chart_type, output_dir)
            
            if chart_result['success']:
                logger.info(f"图表生成成功: {chart_result['files']}")
                return {
                    'success': True,
                    'message': '图表生成成功',
                    'files': chart_result['files'],
                    'chart_type': chart_type,
                    'data_fixed': validation_result['fixed'],
                    'standardized_data': standardized_data
                }
            else:
                logger.error(f"图表生成失败: {chart_result['message']}")
                return chart_result
                
        except Exception as e:
            logger.error(f"图表生成异常: {str(e)}")
            return {
                'success': False,
                'message': f"图表生成异常: {str(e)}",
                'files': [],
                'error': 'GENERATION_ERROR'
            }
    
    def generate_financial_charts(self, company_name: str, financial_data: Dict[str, Any], 
                                 years: List[str] = None) -> Dict[str, Any]:
        """
        为公司生成全套财务图表
        
        Args:
            company_name: 公司名称
            financial_data: 财务数据
            years: 年份列表
            
        Returns:
            所有图表的生成结果
        """
        if years is None:
            years = ["2022", "2023", "2024", "2025(Q)"]
        
        logger.info(f"为{company_name}生成全套财务图表")
        
        # 标准化财务数据
        standardized_financial_data = self.builder.standardize_financial_data(financial_data)
        
        results = {}
        
        # 生成各种类型的图表
        for chart_name, template in self.chart_templates.items():
            try:
                chart_data = self._build_chart_from_template(
                    template, company_name, standardized_financial_data, years
                )
                
                result = self.generate_chart_with_validation(
                    json.dumps(chart_data, ensure_ascii=False),
                    template['chart_type']
                )
                
                results[chart_name] = result
                
                if result['success']:
                    logger.info(f"{chart_name}图表生成成功")
                else:
                    logger.warning(f"{chart_name}图表生成失败: {result['message']}")
                    
            except Exception as e:
                logger.error(f"{chart_name}图表生成异常: {str(e)}")
                results[chart_name] = {
                    'success': False,
                    'message': f"生成异常: {str(e)}",
                    'files': []
                }
        
        # 统计结果
        success_count = sum(1 for r in results.values() if r['success'])
        total_count = len(results)
        
        summary = {
            'company': company_name,
            'total_charts': total_count,
            'successful_charts': success_count,
            'success_rate': f"{success_count/total_count*100:.1f}%",
            'results': results
        }
        
        logger.info(f"图表生成完成: {success_count}/{total_count} 成功")
        return summary
    
    def _standardize_chart_data(self, chart_data: Dict[str, Any], chart_type: str) -> Dict[str, Any]:
        """标准化图表数据"""
        standardized = chart_data.copy()
        
        # 修复数据长度不一致问题
        if 'x_axis' in standardized and 'series' in standardized:
            x_length = len(standardized['x_axis'])
            for series_item in standardized['series']:
                if len(series_item['data']) != x_length:
                    if len(series_item['data']) > x_length:
                        series_item['data'] = series_item['data'][:x_length]
                    else:
                        series_item['data'].extend([0] * (x_length - len(series_item['data'])))
        
        # 雷达图特殊处理
        if chart_type == 'radar' and 'categories' in standardized and 'series' in standardized:
            categories_length = len(standardized['categories'])
            for series_item in standardized['series']:
                if len(series_item['data']) != categories_length:
                    if len(series_item['data']) > categories_length:
                        series_item['data'] = series_item['data'][:categories_length]
                    else:
                        series_item['data'].extend([50] * (categories_length - len(series_item['data'])))
        
        return standardized
    
    def _build_chart_from_template(self, template: Dict[str, Any], company_name: str, 
                                  financial_data: Dict[str, Any], years: List[str]) -> Dict[str, Any]:
        """根据模板构建图表数据"""
        chart_type = template['chart_type']
        title = template['title'].format(company=company_name)
        
        if chart_type == 'radar':
            # 雷达图使用财务健康得分
            return self.builder.build_financial_health_radar(company_name, financial_data)
        elif chart_type in ['line', 'area']:
            # 趋势图
            required_metrics = template['required_metrics']
            metrics_data = {}
            
            for metric in required_metrics:
                # 从财务数据中提取指标
                values = self._extract_metric_values(financial_data, metric, years)
                if values:
                    metrics_data[metric] = values
            
            return self.builder.build_trend_chart_data(
                title=title,
                years=years,
                metrics=metrics_data,
                unit=template.get('unit')
            )
        else:
            # 对比图
            required_metrics = template['required_metrics']
            metrics_data = {}
            
            for metric in required_metrics:
                values = self._extract_metric_values(financial_data, metric, years)
                if values:
                    metrics_data[metric] = values
            
            return self.builder.build_comparison_chart_data(
                title=title,
                categories=years,
                metrics=metrics_data,
                chart_type=chart_type
            )
    
    def _extract_metric_values(self, financial_data: Dict[str, Any], metric: str, 
                              years: List[str]) -> Optional[List[float]]:
        """从财务数据中提取指标值"""
        values = []
        
        # 尝试多种数据提取方式
        for year in years:
            value = None
            
            # 方式1：直接查找指标名
            if metric in financial_data:
                if isinstance(financial_data[metric], dict):
                    # 多年数据格式
                    value = financial_data[metric].get(year)
                elif isinstance(financial_data[metric], (int, float)):
                    # 单一值，所有年份使用相同值
                    value = financial_data[metric]
            
            # 方式2：在嵌套结构中查找
            if value is None:
                for key, val in financial_data.items():
                    if isinstance(val, dict) and metric in val:
                        value = val[metric].get(year) if isinstance(val[metric], dict) else val[metric]
                        break
            
            # 方式3：使用默认值或推断值
            if value is None:
                value = self._infer_metric_value(metric, year, financial_data)
            
            values.append(float(value) if value is not None else 0.0)
        
        return values if any(v != 0 for v in values) else None
    
    def _infer_metric_value(self, metric: str, year: str, financial_data: Dict[str, Any]) -> Optional[float]:
        """推断指标值"""
        # 这里可以实现更复杂的推断逻辑
        # 目前返回None表示无法推断
        return None
    
    def _simulate_chart_generation(self, chart_data: Dict[str, Any], chart_type: str, 
                                  output_dir: str) -> Dict[str, Any]:
        """模拟图表生成过程（实际应用中应该调用真实的图表生成工具）"""
        try:
            # 这里应该调用实际的generate_charts工具
            # 目前返回模拟结果
            filename = f"{chart_data['title']}_{chart_type}.png"
            
            # 模拟文件保存
            import os
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, filename)
            
            # 创建一个虚拟的图片文件（实际应用中应该是真实的图表文件）
            with open(file_path, 'w') as f:
                f.write(f"模拟图表文件: {chart_data['title']}")
            
            return {
                'success': True,
                'message': f'图表生成成功，生成 1 个图表',
                'files': [file_path],
                'chart_type': chart_type,
                'chart_count': 1
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"图表生成失败: {str(e)}",
                'files': [],
                'error': str(e)
            }
    
    def get_chart_format_example(self, chart_type: str) -> Dict[str, Any]:
        """获取图表格式示例"""
        return self.validator.get_format_example(chart_type)
    
    def validate_chart_data(self, chart_data: Dict[str, Any], chart_type: str) -> Dict[str, Any]:
        """验证图表数据格式"""
        return self.validator.validate_chart_data(chart_data, chart_type)


def test_enhanced_chart_generator():
    """测试增强版图表生成器"""
    generator = EnhancedChartGenerator("./test_charts")
    
    # 测试数据
    test_financial_data = {
        "revenue": {"2022": 1350.25, "2023": 1420.18, "2024": 1511.39, "2025Q": 573.88},
        "net_profit": {"2022": 28.45, "2023": 32.18, "2024": 36.11, "2025Q": 11.04},
        "roe": {"2022": 8.15, "2023": 8.92, "2024": 9.22, "2025Q": 2.82},
        "net_profit_margin": {"2022": 2.11, "2023": 2.27, "2024": 2.39, "2025Q": 1.92},
        "debt_to_assets": {"2022": 87.25, "2023": 88.03, "2024": 88.71, "2025Q": 88.71},
        "current_ratio": {"2022": 1.15, "2023": 1.13, "2024": 1.11, "2025Q": 1.11},
        "asset_turnover": {"2022": 0.18, "2023": 0.17, "2024": 0.17, "2025Q": 0.17}
    }
    
    # 测试生成全套财务图表
    results = generator.generate_financial_charts("陕西建工", test_financial_data)
    
    print("图表生成结果:")
    print(f"总图表数: {results['total_charts']}")
    print(f"成功数: {results['successful_charts']}")
    print(f"成功率: {results['success_rate']}")
    
    for chart_name, result in results['results'].items():
        status = "成功" if result['success'] else "失败"
        print(f"- {chart_name}: {status}")


if __name__ == "__main__":
    test_enhanced_chart_generator()