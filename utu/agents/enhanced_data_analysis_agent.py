"""
增强版DataAnalysisAgent
集成智能数据转换功能，自动处理数据格式问题
"""

import json
import logging
from typing import Dict, Any, List
from ..schemas import AgentMessage, DataType, AgentDataFormatter
from ..data_conversion import UniversalDataConverter
from ..context_compression import IntelligentContextCompressor

logger = logging.getLogger(__name__)

class EnhancedDataAnalysisAgent:
    """增强版数据分析智能体"""
    
    def __init__(self):
        self.logger = logger
        self.universal_converter = UniversalDataConverter()
        self.context_compressor = IntelligentContextCompressor()
        
        # 预定义的中文到英文财务字段映射
        self.field_mapping = {
            '利润表': {
                '营业收入': ['revenue', 'operating_revenue', 'sales_revenue'],
                '营业成本': ['cost_of_goods_sold', 'operating_cost'],
                '营业利润': ['operating_profit', 'operating_income'],
                '利润总额': ['total_profit', 'profit_before_tax'],
                '净利润': ['net_profit', 'net_income']
            },
            '资产负债表': {
                '总资产': ['total_assets', 'assets'],
                '总负债': ['total_liabilities', 'liabilities'],
                '所有者权益': ['total_equity', 'shareholders_equity'],
                '流动资产': ['current_assets'],
                '流动负债': ['current_liabilities'],
                '应收账款': ['accounts_receivable'],
                '存货': ['inventory'],
                '固定资产': ['fixed_assets'],
                '货币资金': ['cash_and_cash_equivalents', 'cash']
            },
            '现金流量表': {
                '经营活动现金流量净额': ['operating_cash_flow', 'cash_from_operations'],
                '投资活动现金流量净额': ['investing_cash_flow', 'cash_from_investing'],
                '筹资活动现金流量净额': ['financing_cash_flow', 'cash_from_financing'],
                '现金及现金等价物净增加额': ['net_change_in_cash']
            }
        }
    
    def analyze_financial_data_intelligently(self, financial_data_json: str, 
                                          company_name: str = "目标公司") -> Dict[str, Any]:
        """
        智能财务数据分析 - 自动处理各种数据格式
        
        Args:
            financial_data_json: 财务数据的JSON字符串
            company_name: 公司名称
            
        Returns:
            完整的分析结果
        """
        self.logger.info(f"开始智能财务数据分析: {company_name}")
        
        try:
            # 解析JSON数据
            if isinstance(financial_data_json, str):
                data_dict = json.loads(financial_data_json)
            else:
                data_dict = financial_data_json
            
            # 数据预处理和标准化
            standardized_data = self._preprocess_financial_data(data_dict)
            
            # 计算财务比率
            ratios = self._calculate_enhanced_ratios(standardized_data)
            
            # 分析趋势
            trends = self._analyze_enhanced_trends(standardized_data)
            
            # 健康评估
            health = self._assess_financial_health(ratios, trends)
            
            # 生成分析报告
            analysis_report = self._generate_analysis_report(
                ratios, trends, health, company_name
            )
            
            result = {
                'success': True,
                'company_name': company_name,
                'ratios': ratios,
                'trends': trends,
                'health_assessment': health,
                'analysis_report': analysis_report,
                'data_quality': self._assess_data_quality(standardized_data),
                'recommendations': self._generate_recommendations(ratios, health)
            }
            
            self.logger.info(f"智能财务分析完成: {company_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"智能财务分析失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'company_name': company_name,
                'analysis_report': f'分析失败: {str(e)}'
            }
    
    def _preprocess_financial_data(self, data_dict: Dict[str, Any]) -> Dict[str, Any]:
        """预处理和标准化财务数据"""
        try:
            self.logger.info("开始数据预处理")
            
            standardized = {
                'income_statement': {},
                'balance_sheet': {},
                'cash_flow': {},
                'historical_data': {},
                'key_metrics': {}
            }
            
            # 处理基础财务报表数据
            for statement_type in ['利润表', '资产负债表', '现金流量表']:
                if statement_type in data_dict:
                    statement_data = data_dict[statement_type]
                    if isinstance(statement_data, dict):
                        # 标准化字段名
                        standardized_data = self._standardize_statement_data(
                            statement_data, statement_type, standardized
                        )
            
            # 处理历史数据
            if '历史数据' in data_dict:
                historical_data = data_dict['历史数据']
                if isinstance(historical_data, dict):
                    standardized['historical_data'] = historical_data
                    
                    # 提取关键指标
                    key_metrics = self._extract_key_metrics_from_historical(historical_data)
                    standardized['key_metrics'].update(key_metrics)
            
            # 处理关键指标
            if '关键指标' in data_dict:
                key_metrics = data_dict['关键指标']
                if isinstance(key_metrics, dict):
                    standardized['key_metrics'].update(key_metrics)
            
            self.logger.info("数据预处理完成")
            return standardized
            
        except Exception as e:
            self.logger.error(f"数据预处理失败: {e}")
            return {'error': str(e)}
    
    def _standardize_statement_data(self, statement_data: Dict[str, Any], 
                                 statement_type: str, 
                                 standardized: Dict[str, Any]) -> Dict[str, Any]:
        """标准化报表数据"""
        try:
            mapping = self.field_mapping.get(statement_type, {})
            
            # 映射中文字段到英文字段
            for chinese_field, english_variants in mapping.items():
                if chinese_field in statement_data:
                    value = statement_data[chinese_field]
                    
                    # 根据报表类型存储到相应位置
                    if statement_type == '利润表':
                        standardized['income_statement'][chinese_field] = value
                        # 同时添加英文字段名
                        for english_field in english_variants:
                            standardized['income_statement'][english_field] = value
                    
                    elif statement_type == '资产负债表':
                        standardized['balance_sheet'][chinese_field] = value
                        for english_field in english_variants:
                            standardized['balance_sheet'][english_field] = value
                    
                    elif statement_type == '现金流量表':
                        standardized['cash_flow'][chinese_field] = value
                        for english_field in english_variants:
                            standardized['cash_flow'][english_field] = value
            
            return standardized
            
        except Exception as e:
            self.logger.error(f"报表数据标准化失败: {e}")
            return standardized
    
    def _extract_key_metrics_from_historical(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """从历史数据中提取关键指标"""
        try:
            key_metrics = {}
            
            # 按年份排序
            years = sorted([key for key in historical_data.keys() if key.isdigit()], 
                          key=int, reverse=True)
            
            if years:
                # 最新年度数据
                latest_year = years[0]
                latest_data = historical_data[latest_year]
                
                if isinstance(latest_data, dict):
                    # 提取关键指标
                    for metric in ['营业收入', '净利润', '总资产', '总负债', '所有者权益']:
                        if metric in latest_data:
                            key_metrics[f'latest_{metric}'] = latest_data[metric]
                
                # 前一年数据（用于计算增长率）
                if len(years) > 1:
                    prev_year = years[1]
                    prev_data = historical_data[prev_year]
                    
                    if isinstance(prev_data, dict):
                        for metric in ['营业收入', '净利润']:
                            if metric in prev_data:
                                key_metrics[f'previous_{metric}'] = prev_data[metric]
            
            return key_metrics
            
        except Exception as e:
            self.logger.error(f"历史数据关键指标提取失败: {e}")
            return {}
    
    def _calculate_enhanced_ratios(self, standardized_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算增强版财务比率"""
        try:
            self.logger.info("开始计算财务比率")
            
            ratios = {
                'profitability': {},
                'solvency': {},
                'efficiency': {},
                'growth': {},
                'warnings': []
            }
            
            # 利润表数据
            income = standardized_data.get('income_statement', {})
            balance = standardized_data.get('balance_sheet', {})
            key_metrics = standardized_data.get('key_metrics', {})
            
            # 盈利能力指标
            revenue = (income.get('营业收入') or income.get('revenue') or 
                      key_metrics.get('latest_营业收入') or key_metrics.get('latest_revenue') or 0)
            net_profit = (income.get('净利润') or income.get('net_profit') or 
                         key_metrics.get('latest_净利润') or key_metrics.get('latest_net_profit') or 0)
            
            if revenue > 0:
                ratios['profitability']['net_profit_margin'] = round(net_profit / revenue * 100, 2)
            else:
                ratios['warnings'].append('营业收入为0，无法计算利润率')
            
            # 偿债能力指标
            total_assets = (balance.get('总资产') or balance.get('total_assets') or
                          key_metrics.get('latest_总资产') or key_metrics.get('latest_total_assets') or 0)
            total_liabilities = (balance.get('总负债') or balance.get('total_liabilities') or
                              key_metrics.get('latest_总负债') or key_metrics.get('latest_total_liabilities') or 0)
            
            if total_assets > 0:
                ratios['solvency']['debt_to_asset_ratio'] = round(total_liabilities / total_assets * 100, 2)
                
                # 检查负债率是否过高
                if ratios['solvency']['debt_to_asset_ratio'] > 80:
                    ratios['warnings'].append('资产负债率偏高，存在财务风险')
            
            # 所有者权益
            equity = (balance.get('所有者权益') or balance.get('total_equity') or
                     key_metrics.get('latest_所有者权益') or key_metrics.get('latest_total_equity') or 0)
            
            if equity > 0:
                ratios['profitability']['roe'] = round(net_profit / equity * 100, 2)
            elif total_assets > 0:
                ratios['profitability']['roe'] = round(net_profit / total_assets * 100, 2)
            
            if total_assets > 0:
                ratios['profitability']['roa'] = round(net_profit / total_assets * 100, 2)
            
            # 运营效率指标
            if revenue > 0 and total_assets > 0:
                ratios['efficiency']['asset_turnover'] = round(revenue / total_assets, 2)
            
            # 增长能力指标
            if 'latest_营业收入' in key_metrics and 'previous_营业收入' in key_metrics:
                prev_revenue = key_metrics['previous_营业收入']
                if prev_revenue > 0:
                    current_revenue = key_metrics['latest_营业收入']
                    ratios['growth']['revenue_growth'] = round(
                        (current_revenue - prev_revenue) / prev_revenue * 100, 2
                    )
            
            if 'latest_净利润' in key_metrics and 'previous_净利润' in key_metrics:
                prev_profit = key_metrics['previous_净利润']
                if prev_profit > 0:
                    current_profit = key_metrics['latest_净利润']
                    ratios['growth']['profit_growth'] = round(
                        (current_profit - prev_profit) / prev_profit * 100, 2
                    )
            
            # 如果增长率计算失败，设置为0
            if 'revenue_growth' not in ratios['growth']:
                ratios['growth']['revenue_growth'] = 0.0
            if 'profit_growth' not in ratios['growth']:
                ratios['growth']['profit_growth'] = 0.0
            
            self.logger.info("财务比率计算完成")
            return ratios
            
        except Exception as e:
            self.logger.error(f"财务比率计算失败: {e}")
            return {'error': str(e), 'warnings': [f'计算失败: {str(e)}']}
    
    def _analyze_enhanced_trends(self, standardized_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析增强版趋势"""
        try:
            self.logger.info("开始趋势分析")
            
            trends = {
                'revenue': {'trend': 'stable', 'average_growth': 0.0, 'data_points': []},
                'profit': {'trend': 'stable', 'average_growth': 0.0, 'data_points': []},
                'summary': {}
            }
            
            historical_data = standardized_data.get('historical_data', {})
            
            if historical_data:
                years = sorted([key for key in historical_data.keys() if key.isdigit()], 
                              key=int, reverse=True)
                
                revenue_data = []
                profit_data = []
                
                for year in years:
                    year_data = historical_data[year]
                    if isinstance(year_data, dict):
                        revenue_data.append({
                            'year': int(year),
                            'value': year_data.get('营业收入', year_data.get('revenue', 0))
                        })
                        profit_data.append({
                            'year': int(year),
                            'value': year_data.get('净利润', year_data.get('net_profit', 0))
                        })
                
                # 分析收入趋势
                if len(revenue_data) >= 2:
                    latest_revenue = revenue_data[0]['value']
                    earliest_revenue = revenue_data[-1]['value']
                    
                    if earliest_revenue > 0:
                        growth_rate = (latest_revenue - earliest_revenue) / earliest_revenue * 100
                        trends['revenue']['average_growth'] = round(growth_rate, 2)
                        trends['revenue']['data_points'] = revenue_data
                        
                        if growth_rate > 10:
                            trends['revenue']['trend'] = 'increasing'
                        elif growth_rate < -10:
                            trends['revenue']['trend'] = 'decreasing'
                        else:
                            trends['revenue']['trend'] = 'stable'
                
                # 分析利润趋势
                if len(profit_data) >= 2:
                    latest_profit = profit_data[0]['value']
                    earliest_profit = profit_data[-1]['value']
                    
                    if earliest_profit > 0:
                        growth_rate = (latest_profit - earliest_profit) / earliest_profit * 100
                        trends['profit']['average_growth'] = round(growth_rate, 2)
                        trends['profit']['data_points'] = profit_data
                        
                        if growth_rate > 10:
                            trends['profit']['trend'] = 'increasing'
                        elif growth_rate < -10:
                            trends['profit']['trend'] = 'decreasing'
                        else:
                            trends['profit']['trend'] = 'stable'
            
            # 生成趋势摘要
            trends['summary'] = {
                'data_years': len(historical_data) if historical_data else 0,
                'revenue_trend': trends['revenue']['trend'],
                'profit_trend': trends['profit']['trend'],
                'overall_performance': self._assess_overall_performance(trends)
            }
            
            self.logger.info("趋势分析完成")
            return trends
            
        except Exception as e:
            self.logger.error(f"趋势分析失败: {e}")
            return {'error': str(e)}
    
    def _assess_financial_health(self, ratios: Dict[str, Any], trends: Dict[str, Any]) -> Dict[str, Any]:
        """评估财务健康状况"""
        try:
            self.logger.info("开始财务健康评估")
            
            health = {
                'overall_health': 'good',
                'health_score': 75,
                'analysis': '',
                'key_indicators': {},
                'risk_factors': [],
                'strengths': []
            }
            
            # 基于盈利能力评估
            profitability = ratios.get('profitability', {})
            net_margin = profitability.get('net_profit_margin', 0)
            roe = profitability.get('roe', 0)
            
            if net_margin > 5 and roe > 10:
                health['strengths'].append('盈利能力较强')
                health['key_indicators']['盈利能力'] = '优秀'
            elif net_margin > 0 and roe > 0:
                health['key_indicators']['盈利能力'] = '一般'
            else:
                health['risk_factors'].append('盈利能力较弱')
                health['key_indicators']['盈利能力'] = '需改善'
            
            # 基于偿债能力评估
            solvency = ratios.get('solvency', {})
            debt_ratio = solvency.get('debt_to_asset_ratio', 0)
            
            if debt_ratio < 40:
                health['strengths'].append('偿债能力良好，负债水平低')
                health['key_indicators']['偿债能力'] = '优秀'
            elif debt_ratio < 70:
                health['key_indicators']['偿债能力'] = '一般'
            else:
                health['risk_factors'].append('资产负债率过高，财务风险较大')
                health['key_indicators']['偿债能力'] = '高风险'
            
            # 基于成长能力评估
            growth = ratios.get('growth', {})
            revenue_growth = growth.get('revenue_growth', 0)
            profit_growth = growth.get('profit_growth', 0)
            
            if revenue_growth > 10 and profit_growth > 5:
                health['strengths'].append('成长性良好')
                health['key_indicators']['成长能力'] = '优秀'
            elif revenue_growth > 0 and profit_growth > 0:
                health['key_indicators']['成长能力'] = '一般'
            else:
                health['risk_factors'].append('成长性不足')
                health['key_indicators']['成长能力'] = '需改善'
            
            # 计算综合健康分数
            score = 75  # 基础分数
            
            if net_margin > 5: score += 10
            elif net_margin <= 0: score -= 20
            
            if debt_ratio < 40: score += 10
            elif debt_ratio > 80: score -= 20
            
            if revenue_growth > 10: score += 10
            elif revenue_growth < -10: score -= 15
            
            health['health_score'] = max(0, min(100, score))
            
            # 确定总体健康等级
            if health['health_score'] >= 85:
                health['overall_health'] = 'excellent'
                health['analysis'] = '财务状况优秀，各项指标表现良好'
            elif health['health_score'] >= 70:
                health['overall_health'] = 'good'
                health['analysis'] = '财务状况良好，存在一些改善空间'
            elif health['health_score'] >= 50:
                health['overall_health'] = 'fair'
                health['analysis'] = '财务状况一般，需要关注风险因素'
            else:
                health['overall_health'] = 'poor'
                health['analysis'] = '财务状况较差，存在较大风险'
            
            self.logger.info(f"财务健康评估完成: {health['overall_health']}")
            return health
            
        except Exception as e:
            self.logger.error(f"财务健康评估失败: {e}")
            return {'error': str(e)}
    
    def _generate_analysis_report(self, ratios: Dict[str, Any], trends: Dict[str, Any], 
                                health: Dict[str, Any], company_name: str) -> str:
        """生成分析报告"""
        try:
            report_lines = [
                f"# {company_name} 财务分析报告",
                "",
                "## 财务比率分析",
                ""
            ]
            
            # 盈利能力分析
            profitability = ratios.get('profitability', {})
            if profitability:
                report_lines.extend([
                    "### 盈利能力",
                    f"- 净利润率: {profitability.get('net_profit_margin', 0):.2f}%",
                    f"- 净资产收益率(ROE): {profitability.get('roe', 0):.2f}%",
                    f"- 总资产收益率(ROA): {profitability.get('roa', 0):.2f}%",
                    ""
                ])
            
            # 偿债能力分析
            solvency = ratios.get('solvency', {})
            if solvency:
                report_lines.extend([
                    "### 偿债能力",
                    f"- 资产负债率: {solvency.get('debt_to_asset_ratio', 0):.2f}%",
                    ""
                ])
            
            # 成长能力分析
            growth = ratios.get('growth', {})
            if growth:
                report_lines.extend([
                    "### 成长能力",
                    f"- 营收增长率: {growth.get('revenue_growth', 0):.2f}%",
                    f"- 净利润增长率: {growth.get('profit_growth', 0):.2f}%",
                    ""
                ])
            
            # 趋势分析
            if trends.get('summary'):
                summary = trends['summary']
                report_lines.extend([
                    "## 趋势分析",
                    f"- 数据涵盖年数: {summary.get('data_years', 0)}年",
                    f"- 收入趋势: {summary.get('revenue_trend', '未知')}",
                    f"- 利润趋势: {summary.get('profit_trend', '未知')}",
                    ""
                ])
            
            # 健康评估
            if health.get('overall_health'):
                report_lines.extend([
                    "## 财务健康评估",
                    f"- 总体健康状况: {health.get('overall_health', '未知')}",
                    f"- 健康评分: {health.get('health_score', 0)}/100",
                    f"- 综合分析: {health.get('analysis', '')}",
                    ""
                ])
                
                if health.get('strengths'):
                    report_lines.append("### 优势:")
                    for strength in health['strengths']:
                        report_lines.append(f"- {strength}")
                    report_lines.append("")
                
                if health.get('risk_factors'):
                    report_lines.append("### 风险因素:")
                    for risk in health['risk_factors']:
                        report_lines.append(f"- {risk}")
                    report_lines.append("")
            
            # 警告信息
            warnings = ratios.get('warnings', [])
            if warnings:
                report_lines.extend([
                    "## 注意事项",
                    *[f"- {warning}" for warning in warnings],
                    ""
                ])
            
            return "\\n".join(report_lines)
            
        except Exception as e:
            self.logger.error(f"分析报告生成失败: {e}")
            return f"报告生成失败: {str(e)}"
    
    def _assess_data_quality(self, standardized_data: Dict[str, Any]) -> Dict[str, Any]:
        """评估数据质量"""
        try:
            quality = {
                'completeness': 0,
                'consistency': 0,
                'reliability': 'medium',
                'issues': [],
                'missing_fields': []
            }
            
            # 检查数据完整性
            required_fields = [
                ('income_statement', ['营业收入', '净利润']),
                ('balance_sheet', ['总资产', '总负债', '所有者权益']),
                ('historical_data', ['至少两年数据'])
            ]
            
            present_fields = 0
            total_fields = 0
            
            for section, fields in required_fields:
                section_data = standardized_data.get(section, {})
                if section == 'historical_data':
                    if isinstance(section_data, dict) and len(section_data) >= 2:
                        present_fields += 1
                    total_fields += 1
                else:
                    for field in fields:
                        total_fields += 1
                        if field in section_data or any(
                            field in section_data.get(key, '') for key in section_data
                        ):
                            present_fields += 1
            
            quality['completeness'] = round(present_fields / total_fields * 100, 0) if total_fields > 0 else 0
            
            # 检查数据一致性
            quality['consistency'] = 85  # 默认一致性分数
            
            # 确定可靠性
            if quality['completeness'] >= 90:
                quality['reliability'] = 'high'
            elif quality['completeness'] >= 70:
                quality['reliability'] = 'medium'
            else:
                quality['reliability'] = 'low'
                quality['issues'].append('数据不完整，可能影响分析准确性')
            
            return quality
            
        except Exception as e:
            self.logger.error(f"数据质量评估失败: {e}")
            return {'reliability': 'unknown', 'issues': [str(e)]}
    
    def _generate_recommendations(self, ratios: Dict[str, Any], health: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        try:
            recommendations = []
            
            # 基于盈利能力的建议
            profitability = ratios.get('profitability', {})
            net_margin = profitability.get('net_profit_margin', 0)
            
            if net_margin < 2:
                recommendations.append("建议优化成本结构，提高净利润率")
            elif net_margin < 5:
                recommendations.append("建议关注产品定价和成本控制，提升盈利能力")
            
            # 基于偿债能力的建议
            solvency = ratios.get('solvency', {})
            debt_ratio = solvency.get('debt_to_asset_ratio', 0)
            
            if debt_ratio > 80:
                recommendations.append("建议优化资本结构，降低资产负债率")
                recommendations.append("考虑增加股权融资或债务重组")
            
            # 基于成长能力的建议
            growth = ratios.get('growth', {})
            revenue_growth = growth.get('revenue_growth', 0)
            
            if revenue_growth < 0:
                recommendations.append("建议加强市场开拓，提升收入增长")
            elif revenue_growth < 5:
                recommendations.append("建议寻找新的增长点，提高业务扩张速度")
            
            # 基于健康评估的建议
            if health.get('overall_health') == 'poor':
                recommendations.append("建议制定全面的财务改善计划")
                recommendations.append("考虑寻求专业的财务咨询建议")
            elif health.get('overall_health') == 'fair':
                recommendations.append("建议关注核心财务指标的持续改善")
            
            if not recommendations:
                recommendations.append("当前财务状况良好，建议保持现有策略并持续监控")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"建议生成失败: {e}")
            return ["建议生成失败，请检查数据格式"]

# 创建全局实例
enhanced_data_agent = EnhancedDataAnalysisAgent()

def analyze_financial_data_intelligently(financial_data_json: str, 
                                      company_name: str = "目标公司") -> Dict[str, Any]:
    """
    便捷函数：智能财务数据分析
    
    Args:
        financial_data_json: 财务数据的JSON字符串
        company_name: 公司名称
        
    Returns:
        完整的分析结果
    """
    return enhanced_data_agent.analyze_financial_data_intelligently(
        financial_data_json, company_name
    )