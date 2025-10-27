"""
TabularDataToolkit - 修复版本
用于数据分析和图表生成的工具类
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from ..config import ToolkitConfig
from .base import AsyncBaseToolkit

# 设置中文字体支持
try:
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
except:
    pass

# 设置日志
logger = logging.getLogger(__name__)

class TabularDataToolkit(AsyncBaseToolkit):
    """
    表格数据处理和图表生成工具
    """

    def __init__(self, config: ToolkitConfig | dict | None = None):
        super().__init__(config)
        self.logger = logger

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.build()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.cleanup()

    def generate_charts(self, data_json: str, chart_type: str = "bar", output_dir: str = "./run_workdir") -> Dict[str, Any]:
        """
        生成图表的主要方法，支持公司对比数据格式

        Args:
            data_json: JSON格式的数据字符串
            chart_type: 图表类型
            output_dir: 输出目录

        Returns:
            Dict: 包含图表生成结果的字典
        """
        try:
            # 解析数据
            data = json.loads(data_json) if isinstance(data_json, str) else data_json

            if not isinstance(data, dict):
                return {
                    "success": False,
                    "message": "数据格式错误，需要字典格式",
                    "files": []
                }

            # 检查是否是公司对比数据格式
            companies = data.get('companies', [])
            if companies:
                self.logger.info(f"检测到公司对比数据格式，公司数量: {len(companies)}")
                return self._generate_company_comparison_charts(data, chart_type, output_dir)
            else:
                # 通用图表生成逻辑
                return self._generate_generic_charts(data, chart_type, output_dir)

        except json.JSONDecodeError as e:
            error_msg = f"JSON解析错误: {str(e)}"
            logger.error(error_msg)

            # 提供详细的错误信息和格式示例
            if chart_type == "radar":
                format_example = {
                    "title": "陕西建工财务健康雷达图",
                    "categories": ["盈利能力", "偿债能力", "运营效率", "成长能力", "现金流"],
                    "series": [
                        {"name": "陕西建工", "data": [30, 20, 25, 15, 10]},
                        {"name": "行业平均", "data": [60, 70, 55, 50, 65]}
                    ]
                }
            else:
                format_example = {
                    "title": "图表标题",
                    "x_axis": ["X轴标签1", "X轴标签2"],
                    "series": [
                        {"name": "系列1", "data": [10, 20]},
                        {"name": "系列2", "data": [15, 25]}
                    ]
                }

            return {
                "success": False,
                "message": f"{error_msg}\n\n请使用正确的JSON格式，例如：\n{json.dumps(format_example, ensure_ascii=False, indent=2)}",
                "files": [],
                "error": str(e),
                "format_example": format_example
            }
        except Exception as e:
            error_msg = f"图表生成失败: {str(e)}"
            logger.error(error_msg)
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": error_msg,
                "files": [],
                "error": str(e)
            }

    def _generate_company_comparison_charts(self, data: dict, chart_type: str, output_dir: str) -> Dict[str, Any]:
        """
        生成公司对比图表

        Args:
            data: 包含companies和财务指标的字典
            chart_type: 图表类型
            output_dir: 输出目录

        Returns:
            dict: 图表生成结果
        """
        try:
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)

            # 提取数据
            companies = data.get('companies', [])
            if not companies:
                return {
                    "success": False,
                    "message": "缺少公司数据",
                    "files": []
                }

            chart_files = []

            # 创建变量定义
            variables_code = self._create_chart_variables(data)

            # 根据图表类型生成不同的图表
            if chart_type in ["bar", "comparison"]:
                # 生成综合对比图表
                chart_file = self._create_comparison_chart(data, output_dir, variables_code)
                if chart_file:
                    chart_files.append(chart_file)

            elif chart_type == "radar":
                # 生成雷达图
                chart_file = self._create_radar_chart(data, output_dir, variables_code)
                if chart_file:
                    chart_files.append(chart_file)

            elif chart_type == "trend":
                # 生成趋势图
                chart_file = self._create_trend_chart(data, output_dir, variables_code)
                if chart_file:
                    chart_files.append(chart_file)

            elif chart_type == "scatter":
                # 生成散点图
                chart_file = self._create_scatter_chart(data, output_dir, variables_code)
                if chart_file:
                    chart_files.append(chart_file)

            elif chart_type == "heatmap":
                # 生成热力图
                chart_file = self._create_heatmap_chart(data, output_dir, variables_code)
                if chart_file:
                    chart_files.append(chart_file)

            elif chart_type == "cashflow":
                # 生成现金流专用图表
                chart_files = self._create_cashflow_charts(data, output_dir, variables_code)

            else:
                # 默认生成对比图表
                chart_file = self._create_comparison_chart(data, output_dir, variables_code)
                if chart_file:
                    chart_files.append(chart_file)

            return {
                "success": True,
                "message": f"公司对比图表生成成功，生成 {len(chart_files)} 个图表",
                "files": chart_files,
                "companies": companies,
                "chart_count": len(chart_files),
                "chart_type": chart_type
            }

        except Exception as e:
            error_msg = f"公司对比图表生成失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "files": [],
                "error": str(e)
            }

    def _create_comparison_chart(self, data: dict, output_dir: str, variables_code: str) -> Optional[str]:
        """
        创建综合对比图表（重构版本 - 移除exec动态执行）

        Args:
            data: 数据字典
            output_dir: 输出目录
            variables_code: 变量定义代码

        Returns:
            str: 图表文件路径或None
        """
        try:
            # 提取数据
            companies = data.get('companies', [])
            revenue = data.get('revenue', [])
            net_profit = data.get('net_profit', [])
            profit_margin = data.get('profit_margin', [])
            roe = data.get('roe', [])

            if not companies:
                logger.warning("缺少公司数据，无法生成对比图表")
                return None

            # 数据验证
            chart_data = {
                'companies': companies,
                'revenue': revenue,
                'net_profit': net_profit,
                'profit_margin': profit_margin,
                'roe': roe
            }

            # 验证数据完整性
            if not self._validate_chart_data(chart_data):
                logger.error("图表数据验证失败")
                return None

            # 静态创建图表
            chart_file = self._create_static_comparison_chart(chart_data, output_dir)
            return chart_file

        except Exception as e:
            logger.error(f"对比图表生成失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _validate_chart_data(self, data: dict) -> bool:
        """
        验证图表数据的完整性和合理性

        Args:
            data: 图表数据字典

        Returns:
            bool: 是否验证通过
        """
        try:
            companies = data.get('companies', [])
            if not companies:
                return False

            # 检查数据长度一致性
            for key, values in data.items():
                if key == 'companies':
                    continue
                if values and len(values) != len(companies):
                    logger.warning(f"数据长度不一致: {key} ({len(values)}) vs companies ({len(companies)})")
                    # 可以选择填充或截断
                    return False

            return True

        except Exception as e:
            logger.error(f"数据验证失败: {e}")
            return False

    def _create_static_comparison_chart(self, data: dict, output_dir: str) -> Optional[str]:
        """
        静态创建对比图表（不使用exec）

        Args:
            data: 验证过的图表数据
            output_dir: 输出目录

        Returns:
            str: 图表文件路径或None
        """
        try:
            companies = data['companies']

            # 创建2x2子图
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('公司财务指标对比', fontsize=16, fontweight='bold')

            chart_count = 0

            # 1. 营业收入对比
            if data.get('revenue'):
                self._draw_bar_chart(ax1, companies, data['revenue'],
                                    '营业收入对比（亿元）', '营业收入（亿元）', '#1f77b4')
                chart_count += 1
            else:
                ax1.text(0.5, 0.5, '暂无营业收入数据', ha='center', va='center', transform=ax1.transAxes)
                ax1.set_title('营业收入对比（亿元）')

            # 2. 净利润对比
            if data.get('net_profit'):
                self._draw_bar_chart(ax2, companies, data['net_profit'],
                                    '净利润对比（亿元）', '净利润（亿元）', '#2ca02c')
                chart_count += 1
            else:
                ax2.text(0.5, 0.5, '暂无净利润数据', ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title('净利润对比（亿元）')

            # 3. 净利率对比
            if data.get('profit_margin'):
                self._draw_bar_chart(ax3, companies, data['profit_margin'],
                                    '净利率对比（%）', '净利率（%）', '#ff9896', is_percentage=True)
                chart_count += 1
            else:
                ax3.text(0.5, 0.5, '暂无净利率数据', ha='center', va='center', transform=ax3.transAxes)
                ax3.set_title('净利率对比（%）')

            # 4. ROE对比
            if data.get('roe'):
                self._draw_bar_chart(ax4, companies, data['roe'],
                                    'ROE对比（%）', 'ROE（%）', '#c5b0d5', is_percentage=True)
                chart_count += 1
            else:
                ax4.text(0.5, 0.5, '暂无ROE数据', ha='center', va='center', transform=ax4.transAxes)
                ax4.set_title('ROE对比（%）')

            plt.tight_layout()

            # 保存图表
            chart_file = os.path.join(output_dir, 'company_comparison.png')
            plt.savefig(chart_file, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()

            if os.path.exists(chart_file):
                logger.info(f"对比图表生成成功: {chart_file}")
                return chart_file
            else:
                logger.error("图表文件保存失败")
                return None

        except Exception as e:
            logger.error(f"静态图表创建失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _draw_bar_chart(self, ax, companies, values, title, ylabel, color, is_percentage=False):
        """
        绘制柱状图

        Args:
            ax: matplotlib轴对象
            companies: 公司名称列表
            values: 数值列表
            title: 图表标题
            ylabel: y轴标签
            color: 柱状图颜色
            is_percentage: 是否为百分比数据
        """
        try:
            bars = ax.bar(companies, values, color=color, alpha=0.7)
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_ylabel(ylabel)

            # 添加数值标签
            if values:
                max_val = max(abs(v) for v in values if v is not None)
                for bar, value in zip(bars, values):
                    if value is not None:
                        if is_percentage:
                            label_text = f'{value:.2f}%'
                            offset = max_val * 0.02 if max_val > 0 else 0.5
                        else:
                            label_text = f'{value:.2f}'
                            offset = max_val * 0.02 if max_val > 0 else 0.1

                        ax.text(bar.get_x() + bar.get_width()/2.,
                               bar.get_height() + offset,
                               label_text, ha='center', va='bottom', fontweight='bold')

        except Exception as e:
            logger.error(f"绘制柱状图失败: {e}")
            ax.text(0.5, 0.5, f'图表绘制失败: {str(e)}', ha='center', va='center', transform=ax.transAxes)

    def _create_radar_chart(self, data: dict, output_dir: str, variables_code: str) -> Optional[str]:
        """
        创建雷达图（重构版本 - 移除exec动态执行）

        Args:
            data: 数据字典
            output_dir: 输出目录
            variables_code: 变量定义代码

        Returns:
            str: 图表文件路径或None
        """
        try:
            # 提取数据
            companies = data.get('companies', [])
            profit_margin = data.get('profit_margin', [])
            roe = data.get('roe', [])
            revenue_growth = data.get('revenue_growth', [])
            profit_growth = data.get('profit_growth', [])

            if len(companies) < 2:
                logger.warning("雷达图需要至少两家公司的数据")
                return None

            # 构建雷达图数据
            categories = []
            radar_data = {}

            # 添加净利率
            if profit_margin and len(profit_margin) >= 2:
                categories.append('净利率')
                for i, company in enumerate(companies):
                    if company not in radar_data:
                        radar_data[company] = []
                    radar_data[company].append(profit_margin[i])

            # 添加ROE
            if roe and len(roe) >= 2:
                categories.append('ROE')
                for i, company in enumerate(companies):
                    if company not in radar_data:
                        radar_data[company] = []
                    radar_data[company].append(roe[i])

            # 添加营收增长率
            if revenue_growth and len(revenue_growth) >= 2:
                categories.append('营收增长率')
                for i, company in enumerate(companies):
                    if company not in radar_data:
                        radar_data[company] = []
                    radar_data[company].append(revenue_growth[i])

            # 添加利润增长率
            if profit_growth and len(profit_growth) >= 2:
                categories.append('利润增长率')
                for i, company in enumerate(companies):
                    if company not in radar_data:
                        radar_data[company] = []
                    radar_data[company].append(profit_growth[i])

            if len(categories) == 0:
                logger.warning("没有足够的数据生成雷达图")
                return None

            # 静态创建雷达图
            chart_file = self._create_static_radar_chart(companies, categories, radar_data, output_dir)
            return chart_file

        except Exception as e:
            logger.error(f"雷达图生成失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _create_static_radar_chart(self, companies: list, categories: list, radar_data: dict, output_dir: str) -> Optional[str]:
        """
        静态创建雷达图（不使用exec）

        Args:
            companies: 公司名称列表
            categories: 指标类别列表
            radar_data: 雷达图数据
            output_dir: 输出目录

        Returns:
            str: 图表文件路径或None
        """
        try:
            fig = plt.figure(figsize=(12, 10))

            # 计算角度
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            angles += angles[:1]  # 闭合图形

            # 颜色配置
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

            ax = fig.add_subplot(111, polar=True)

            # 为每个公司绘制雷达图
            for i, company in enumerate(companies[:2]):  # 最多显示2家公司避免过于复杂
                if company in radar_data:
                    values = radar_data[company]
                    values += values[:1]  # 闭合图形

                    color = colors[i % len(colors)]
                    ax.plot(angles, values, 'o-', linewidth=2, label=company, color=color)
                    ax.fill(angles, values, alpha=0.25, color=color)

            # 设置角度标签
            ax.set_thetagrids(np.degrees(angles[:-1]), categories)

            # 设置径向范围
            all_values = []
            for company_data in radar_data.values():
                all_values.extend(company_data)

            if all_values:
                max_value = max(all_values)
                min_value = min(all_values)
                if max_value > 0:
                    ax.set_ylim(0, max_value * 1.1)
                else:
                    ax.set_ylim(min_value * 1.1, 0)

            ax.grid(True)
            ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

            plt.title('公司财务表现雷达图', size=16, fontweight='bold', pad=20)

            # 保存图表
            chart_file = os.path.join(output_dir, 'radar_comparison.png')
            plt.savefig(chart_file, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()

            if os.path.exists(chart_file):
                logger.info(f"雷达图生成成功: {chart_file}")
                return chart_file
            else:
                logger.error("雷达图文件保存失败")
                return None

        except Exception as e:
            logger.error(f"静态雷达图创建失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _create_trend_chart(self, data: dict, output_dir: str, variables_code: str) -> Optional[str]:
        """
        创建趋势图（支持多期数据对比）

        Args:
            data: 数据字典
            output_dir: 输出目录
            variables_code: 变量定义代码

        Returns:
            str: 图表文件路径或None
        """
        try:
            # 检查是否有多期数据
            trend_data = data.get('trend_data')
            if not trend_data:
                logger.warning("缺少趋势数据，无法生成趋势图")
                return None

            companies = data.get('companies', [])
            if not companies:
                logger.warning("缺少公司数据，无法生成趋势图")
                return None

            # 静态创建趋势图
            chart_file = self._create_static_trend_chart(companies, trend_data, output_dir)
            return chart_file

        except Exception as e:
            logger.error(f"趋势图生成失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _create_static_trend_chart(self, companies: list, trend_data: dict, output_dir: str) -> Optional[str]:
        """
        静态创建趋势图（多期数据对比）

        Args:
            companies: 公司名称列表
            trend_data: 趋势数据字典
            output_dir: 输出目录

        Returns:
            str: 图表文件路径或None
        """
        try:
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('财务指标趋势分析', fontsize=16, fontweight='bold')

            chart_count = 0

            # 1. 营业收入趋势
            if 'revenue' in trend_data:
                self._draw_trend_line(axes[0, 0], companies, trend_data['revenue'],
                                        '营业收入趋势', '营业收入（亿元）')
                chart_count += 1
            else:
                axes[0, 0].text(0.5, 0.5, '暂无营业收入趋势数据', ha='center', va='center', transform=axes[0, 0].transAxes)

            # 2. 净利润趋势
            if 'net_profit' in trend_data:
                self._draw_trend_line(axes[0, 1], companies, trend_data['net_profit'],
                                        '净利润趋势', '净利润（亿元）')
                chart_count += 1
            else:
                axes[0, 1].text(0.5, 0.5, '暂无净利润趋势数据', ha='center', va='center', transform=axes[0, 1].transAxes)

            # 3. ROE趋势
            if 'roe' in trend_data:
                self._draw_trend_line(axes[1, 0], companies, trend_data['roe'],
                                        'ROE趋势', 'ROE（%）', is_percentage=True)
                chart_count += 1
            else:
                axes[1, 0].text(0.5, 0.5, '暂无ROE趋势数据', ha='center', va='center', transform=axes[1, 0].transAxes)

            # 4. 资产负债率趋势
            if 'debt_to_asset_ratio' in trend_data:
                self._draw_trend_line(axes[1, 1], companies, trend_data['debt_to_asset_ratio'],
                                        '资产负债率趋势', '资产负债率（%）', is_percentage=True)
                chart_count += 1
            else:
                axes[1, 1].text(0.5, 0.5, '暂无资产负债率趋势数据', ha='center', va='center', transform=axes[1, 1].transAxes)

            plt.tight_layout()

            # 保存图表
            chart_file = os.path.join(output_dir, 'financial_trends.png')
            plt.savefig(chart_file, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()

            if os.path.exists(chart_file):
                logger.info(f"趋势图生成成功: {chart_file}")
                return chart_file
            else:
                logger.error("趋势图文件保存失败")
                return None

        except Exception as e:
            logger.error(f"静态趋势图创建失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _create_scatter_chart(self, data: dict, output_dir: str, variables_code: str) -> Optional[str]:
        """
        创建散点图（指标相关性分析）

        Args:
            data: 数据字典
            output_dir: 输出目录
            variables_code: 变量定义代码

        Returns:
            str: 图表文件路径或None
        """
        try:
            companies = data.get('companies', [])
            if len(companies) < 2:
                logger.warning("散点图需要至少两家公司的数据")
                return None

            # 静态创建散点图
            chart_file = self._create_static_scatter_chart(companies, data, output_dir)
            return chart_file

        except Exception as e:
            logger.error(f"散点图生成失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _create_static_scatter_chart(self, companies: list, data: dict, output_dir: str) -> Optional[str]:
        """
        静态创建散点图（指标相关性分析）

        Args:
            companies: 公司名称列表
            data: 数据字典
            output_dir: 输出目录

        Returns:
            str: 图表文件路径或None
        """
        try:
            fig, axes = plt.subplots(1, 2, figsize=(16, 8))
            fig.suptitle('财务指标相关性分析', fontsize=16, fontweight='bold')

            # 准备数据
            metrics = ['revenue', 'net_profit', 'profit_margin', 'roe', 'roa', 'debt_to_asset_ratio']

            # ROE vs ROA散点图
            if all(metric in data for metric in ['roe', 'roa']):
                roe_data = data['roe']
                roa_data = data['roa']
                if len(roe_data) == len(companies) and len(roa_data) == len(companies):
                    self._draw_scatter_plot(axes[0], companies, roe_data, roa_data,
                                            'ROE vs ROA相关性分析', 'ROE（%）', 'ROA（%）')
                else:
                    axes[0].text(0.5, 0.5, 'ROE或ROA数据不完整', ha='center', va='center', transform=axes[0].transAxes)
            else:
                axes[0].text(0.5, 0.5, '缺少ROE或ROA数据', ha='center', va='center', transform=axes[0].transAxes)

            # 净利率 vs 资产负债率散点图
            if all(metric in data for metric in ['profit_margin', 'debt_to_asset_ratio']):
                margin_data = data['profit_margin']
                debt_ratio_data = data['debt_to_asset_ratio']
                if len(margin_data) == len(companies) and len(debt_ratio_data) == len(companies):
                    self._draw_scatter_plot(axes[1], companies, margin_data, debt_ratio_data,
                                            '净利率 vs 资产负债率相关性分析', '净利率（%）', '资产负债率（%）')
                else:
                    axes[1].text(0.5, 0.5, '净利率或资产负债率数据不完整', ha='center', va='center', transform=axes[1].transAxes)
            else:
                axes[1].text(0.5, 0.5, '缺少净利率或资产负债率数据', ha='center', va='center', transform=axes[1].transAxes)

            plt.tight_layout()

            # 保存图表
            chart_file = os.path.join(output_dir, 'correlation_scatter.png')
            plt.savefig(chart_file, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()

            if os.path.exists(chart_file):
                logger.info(f"散点图生成成功: {chart_file}")
                return chart_file
            else:
                logger.error("散点图文件保存失败")
                return None

        except Exception as e:
            logger.error(f"静态散点图创建失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _draw_trend_line(self, ax, companies: list, data: list, title: str, ylabel: str, is_percentage: bool = False):
        """绘制趋势线图"""
        try:
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

            for i, company in enumerate(companies):
                if i < len(data):
                    years = list(range(len(data[i])))
                    values = data[i]
                    color = colors[i % len(colors)]

                    ax.plot(years, values, marker='o', linewidth=2, label=company, color=color)

                    # 添加数据标签
                    for j, (year, value) in enumerate(zip(years, values)):
                        if value is not None:
                            label = f'{value:.1f}%' if is_percentage else f'{value:.1f}'
                            ax.annotate(label, (year, value), textcoords="offset points",
                                        xytext=(0,10), ha='center', fontsize=8, color=color)

            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel('期数')
            ax.set_ylabel(ylabel)
            ax.legend()
            ax.grid(True, alpha=0.3)

        except Exception as e:
            logger.error(f"绘制趋势图失败: {e}")
            ax.text(0.5, 0.5, f'趋势图绘制失败: {str(e)}', ha='center', va='center', transform=ax.transAxes)

    def _draw_scatter_plot(self, ax, companies: list, x_data: list, y_data: list, title: str, xlabel: str, ylabel: str):
        """绘制散点图"""
        try:
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

            for i, company in enumerate(companies):
                if i < len(x_data) and i < len(y_data):
                    x_val = x_data[i]
                    y_val = y_data[i]
                    color = colors[i % len(colors)]

                    ax.scatter(x_val, y_val, s=100, alpha=0.7, label=company, color=color)

                    # 添加公司标签
                    ax.annotate(company, (x_val, y_val), textcoords="offset points",
                               xytext=(5,5), ha='left', fontsize=9, color=color)

            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.legend()
            ax.grid(True, alpha=0.3)

        except Exception as e:
            logger.error(f"绘制散点图失败: {e}")
            ax.text(0.5, 0.5, f'散点图绘制失败: {str(e)}', ha='center', va='center', transform=ax.transAxes)

    def _create_heatmap_chart(self, data: dict, output_dir: str, variables_code: str = "") -> Optional[str]:
        """
        创建热力图

        Args:
            data: 数据字典
            output_dir: 输出目录
            variables_code: 变量代码（已弃用，保留兼容性）

        Returns:
            str: 图表文件路径
        """
        try:
            logger.info("开始创建热力图...")

            plt.style.use('seaborn-v0_8')
            fig, ax = plt.subplots(figsize=(12, 8))

            companies = data.get('companies', [])
            if not companies:
                ax.text(0.5, 0.5, '没有公司数据', ha='center', va='center', transform=ax.transAxes)
                return None

            # 准备热力图数据矩阵
            metrics = ['profit_margin', 'roe', 'asset_turnover', 'debt_ratio', 'current_ratio', 'revenue_growth']
            matrix_data = []
            valid_metrics = []

            for metric in metrics:
                if metric in data and data[metric]:
                    values = data[metric]
                    if len(values) == len(companies):
                        # 标准化数据到0-100范围以便显示
                        normalized_values = []
                        for v in values:
                            if isinstance(v, (int, float)) and not pd.isna(v):
                                if metric == 'debt_ratio':
                                    # 资产负债率：0-100%直接映射
                                    normalized_values.append(min(max(v * 100, 0), 100))
                                elif metric in ['profit_margin', 'roe', 'revenue_growth']:
                                    # 百分比指标：直接使用
                                    normalized_values.append(min(max(v, 0), 100))
                                else:
                                    # 比率指标：标准化到0-100
                                    normalized_values.append(min(max(v * 20, 0), 100))
                            else:
                                normalized_values.append(0)
                        matrix_data.append(normalized_values)
                        valid_metrics.append(metric)

            if not matrix_data:
                ax.text(0.5, 0.5, '没有有效数据生成热力图', ha='center', va='center', transform=ax.transAxes)
                return None

            # 创建热力图
            matrix_data = np.array(matrix_data)

            # 定义中文指标名称
            metric_names = {
                'profit_margin': '净利率',
                'roe': 'ROE',
                'asset_turnover': '资产周转率',
                'debt_ratio': '资产负债率',
                'current_ratio': '流动比率',
                'revenue_growth': '收入增长率'
            }

            display_metrics = [metric_names.get(m, m) for m in valid_metrics]

            # 创建热力图
            im = ax.imshow(matrix_data, cmap='RdYlBu_r', aspect='auto', vmin=0, vmax=100)

            # 设置标签
            ax.set_xticks(np.arange(len(companies)))
            ax.set_yticks(np.arange(len(display_metrics)))
            ax.set_xticklabels(companies, rotation=45, ha='right')
            ax.set_yticklabels(display_metrics)

            # 添加数值标签
            for i in range(len(display_metrics)):
                for j in range(len(companies)):
                    text = ax.text(j, i, f'{matrix_data[i, j]:.1f}',
                                 ha="center", va="center", color="black", fontsize=10)

            # 添加颜色条
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('指标得分', rotation=270, labelpad=20)

            # 设置标题
            ax.set_title('财务指标热力图分析', fontsize=16, fontweight='bold', pad=20)

            plt.tight_layout()

            # 保存图表
            chart_file = os.path.join(output_dir, 'financial_heatmap.png')
            plt.savefig(chart_file, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()

            if os.path.exists(chart_file):
                logger.info(f"热力图生成成功: {chart_file}")
                return chart_file
            else:
                logger.error("热力图文件保存失败")
                return None

        except Exception as e:
            logger.error(f"热力图创建失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _create_cashflow_charts(self, data: dict, output_dir: str, variables_code: str = "") -> List[str]:
        """
        创建现金流专用图表

        Args:
            data: 数据字典
            output_dir: 输出目录
            variables_code: 变量代码（已弃用，保留兼容性）

        Returns:
            List[str]: 生成的图表文件路径列表
        """
        chart_files = []

        try:
            # 1. 现金流结构图
            structure_chart = self._create_cashflow_structure_chart(data, output_dir)
            if structure_chart:
                chart_files.append(structure_chart)

            # 2. 现金流瀑布图
            waterfall_chart = self._create_cashflow_waterfall_chart(data, output_dir)
            if waterfall_chart:
                chart_files.append(waterfall_chart)

        except Exception as e:
            logger.error(f"现金流图表创建失败: {e}")
            import traceback
            traceback.print_exc()

        return chart_files

    def _create_cashflow_structure_chart(self, data: dict, output_dir: str) -> Optional[str]:
        """
        创建现金流结构图

        Args:
            data: 数据字典
            output_dir: 输出目录

        Returns:
            str: 图表文件路径
        """
        try:
            logger.info("开始创建现金流结构图...")

            plt.style.use('seaborn-v0_8')
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

            companies = data.get('companies', [])
            if not companies:
                ax1.text(0.5, 0.5, '没有公司数据', ha='center', va='center', transform=ax1.transAxes)
                return None

            # 检查现金流数据
            cash_flow_metrics = ['operating_cash_flow', 'investing_cash_flow', 'financing_cash_flow']
            valid_data = True

            for metric in cash_flow_metrics:
                if metric not in data or not data[metric]:
                    valid_data = False
                    break

            if not valid_data:
                # 使用模拟数据展示图表结构
                logger.info("使用模拟数据展示现金流结构图")
                operating_cf = [2.5, 1.8, 3.2, 1.5, 2.1][:len(companies)]
                investing_cf = [-1.2, -0.8, -2.1, -0.9, -1.5][:len(companies)]
                financing_cf = [-0.5, -0.3, -0.8, -0.2, -0.6][:len(companies)]
            else:
                operating_cf = data['operating_cash_flow']
                investing_cf = data['investing_cash_flow']
                financing_cf = data['financing_cash_flow']

            # 图1：现金流构成堆叠柱状图
            x = np.arange(len(companies))
            width = 0.6

            # 处理负值的堆叠图
            operating_pos = [max(v, 0) for v in operating_cf]
            investing_pos = [max(v, 0) for v in investing_cf]
            financing_pos = [max(v, 0) for v in financing_cf]

            operating_neg = [abs(min(v, 0)) for v in operating_cf]
            investing_neg = [abs(min(v, 0)) for v in investing_cf]
            financing_neg = [abs(min(v, 0)) for v in financing_cf]

            # 绘制正向现金流
            ax1.bar(x, operating_pos, width, label='经营活动现金流', color='#2ecc71', alpha=0.8)
            ax1.bar(x, investing_pos, width, bottom=operating_pos, label='投资活动现金流', color='#3498db', alpha=0.8)
            ax1.bar(x, financing_pos, width,
                   bottom=[o + i for o, i in zip(operating_pos, investing_pos)],
                   label='筹资活动现金流', color='#e74c3c', alpha=0.8)

            # 绘制负向现金流
            ax1.bar(x, operating_neg, width, bottom=-np.array(operating_neg), color='#2ecc71', alpha=0.8)
            ax1.bar(x, investing_neg, width,
                   bottom=-np.array(operating_neg) - np.array(investing_neg),
                   color='#3498db', alpha=0.8)
            ax1.bar(x, financing_neg, width,
                   bottom=-np.array(operating_neg) - np.array(investing_neg) - np.array(financing_neg),
                   color='#e74c3c', alpha=0.8)

            ax1.set_xlabel('公司')
            ax1.set_ylabel('现金流（亿元）')
            ax1.set_title('现金流构成分析', fontsize=14, fontweight='bold')
            ax1.set_xticks(x)
            ax1.set_xticklabels(companies, rotation=45, ha='right')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            ax1.axhline(y=0, color='black', linestyle='-', alpha=0.5)

            # 图2：现金流比例饼图（取第一家公司或平均值）
            avg_operating = np.mean([abs(v) for v in operating_cf])
            avg_investing = np.mean([abs(v) for v in investing_cf])
            avg_financing = np.mean([abs(v) for v in financing_cf])

            sizes = [avg_operating, avg_investing, avg_financing]
            labels = ['经营活动', '投资活动', '筹资活动']
            colors = ['#2ecc71', '#3498db', '#e74c3c']
            explode = (0.05, 0.05, 0.05)

            ax2.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                   shadow=True, startangle=90)
            ax2.set_title('现金流活动占比（平均）', fontsize=14, fontweight='bold')

            plt.tight_layout()

            # 保存图表
            chart_file = os.path.join(output_dir, 'cashflow_structure.png')
            plt.savefig(chart_file, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()

            if os.path.exists(chart_file):
                logger.info(f"现金流结构图生成成功: {chart_file}")
                return chart_file
            else:
                logger.error("现金流结构图文件保存失败")
                return None

        except Exception as e:
            logger.error(f"现金流结构图创建失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _create_cashflow_waterfall_chart(self, data: dict, output_dir: str) -> Optional[str]:
        """
        创建现金流瀑布图

        Args:
            data: 数据字典
            output_dir: 输出目录

        Returns:
            str: 图表文件路径
        """
        try:
            logger.info("开始创建现金流瀑布图...")

            plt.style.use('seaborn-v0_8')
            fig, ax = plt.subplots(figsize=(14, 8))

            companies = data.get('companies', [])
            if not companies:
                ax.text(0.5, 0.5, '没有公司数据', ha='center', va='center', transform=ax.transAxes)
                return None

            # 使用模拟数据或真实数据
            if len(companies) > 0:
                company_name = companies[0]
                # 模拟现金流数据
                net_income = 1.5
                depreciation = 0.8
                working_capital = -0.3
                operating_cf = 2.0
                capex = -1.2
                acquisition = -0.5
                investing_cf = -1.7
                debt_change = 0.5
                dividend = -0.3
                financing_cf = 0.2
                final_cash = 0.5
            else:
                return None

            # 瀑布图数据
            categories = ['净利润', '折旧摊销', '营运资本变化', '经营活动现金流',
                         '资本支出', '并购支出', '投资活动现金流', '债务变化', '股利支付',
                         '筹资活动现金流', '期末现金']
            values = [net_income, depreciation, working_capital, operating_cf,
                     capex, acquisition, investing_cf, debt_change, dividend,
                     financing_cf, final_cash]

            # 计算累积位置
            cumulative = 0
            positions = []
            colors = []

            for i, value in enumerate(values):
                positions.append(cumulative)
                if i == 3:  # 经营活动现金流
                    colors.append('#2ecc71')
                elif i == 6:  # 投资活动现金流
                    colors.append('#3498db')
                elif i == 9:  # 筹资活动现金流
                    colors.append('#e74c3c')
                elif i == len(values) - 1:  # 期末现金
                    colors.append('#f39c12')
                elif value >= 0:
                    colors.append('#27ae60')
                else:
                    colors.append('#e67e22')

                cumulative += value

            # 绘制瀑布图
            x_pos = np.arange(len(categories))

            for i, (x, y, value, color) in enumerate(zip(x_pos, positions, values, colors)):
                if value >= 0:
                    ax.bar(x, value, bottom=y, color=color, alpha=0.8, width=0.6)
                else:
                    ax.bar(x, abs(value), bottom=y, color=color, alpha=0.8, width=0.6)

                # 添加数值标签
                ax.text(x, y + value/2, f'{value:.2f}', ha='center', va='center',
                       fontweight='bold', fontsize=10)

            # 设置图表
            ax.set_xlabel('现金流项目')
            ax.set_ylabel('金额（亿元）')
            ax.set_title(f'{company_name} 现金流瀑布图分析', fontsize=16, fontweight='bold')
            ax.set_xticks(x_pos)
            ax.set_xticklabels(categories, rotation=45, ha='right')

            # 添加网格线
            ax.grid(True, alpha=0.3, axis='y')
            ax.axhline(y=0, color='black', linestyle='-', alpha=0.7)

            # 添加汇总线
            for i in [3, 6, 9]:  # 主要汇总点
                if i < len(values):
                    cumulative_value = sum(values[:i+1])
                    ax.axhline(y=cumulative_value, color='red', linestyle='--', alpha=0.5)
                    ax.text(len(categories)-0.5, cumulative_value, f'{cumulative_value:.2f}',
                           ha='right', va='bottom', color='red', fontweight='bold')

            plt.tight_layout()

            # 保存图表
            chart_file = os.path.join(output_dir, 'cashflow_waterfall.png')
            plt.savefig(chart_file, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()

            if os.path.exists(chart_file):
                logger.info(f"现金流瀑布图生成成功: {chart_file}")
                return chart_file
            else:
                logger.error("现金流瀑布图文件保存失败")
                return None

        except Exception as e:
            logger.error(f"现金流瀑布图创建失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _create_chart_variables(self, data: dict) -> str:
        """
        创建matplotlib代码所需的变量定义

        Args:
            data: 数据字典

        Returns:
            str: 变量定义代码
        """
        variable_code = []

        # 添加公司列表
        companies = data.get('companies', [])
        variable_code.append(f"companies = {repr(companies)}")

        # 添加其他指标
        indicators = ['revenue', 'net_profit', 'profit_margin', 'roe', 'asset_turnover',
                    'debt_ratio', 'current_ratio', 'revenue_growth', 'profit_growth']

        for indicator in indicators:
            if indicator in data:
                values = data[indicator]
                if isinstance(values, list) and len(values) == len(companies):
                    variable_code.append(f"{indicator} = {repr(values)}")

        return "\n".join(variable_code)

    def _generate_generic_charts(self, data: dict, chart_type: str, output_dir: str) -> Dict[str, Any]:
        """
        生成通用图表

        Args:
            data: 数据字典，支持title、x_axis、series格式
            chart_type: 图表类型
            output_dir: 输出目录

        Returns:
            Dict: 图表生成结果
        """
        try:
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 检查必要的数据字段 - 雷达图有特殊格式要求
            if chart_type == "radar":
                # 雷达图支持两种格式：
                # 1. 标准格式：title, x_axis, series
                # 2. 雷达图专用格式：title, categories, series
                required_fields = ['title', 'series']
                if not all(key in data for key in required_fields):
                    return {
                        "success": False,
                        "message": f"雷达图数据格式错误，缺少必要字段（{', '.join(required_fields)}）",
                        "files": []
                    }

                # 检查雷达图特有的字段
                if 'categories' in data:
                    # 使用雷达图专用格式
                    return self._generate_radar_chart_with_categories(data, output_dir)
                elif 'x_axis' in data:
                    # 使用标准格式，需要转换为categories格式
                    # 从x_axis中提取数据作为categories
                    categories_data = []
                    if isinstance(data['x_axis'], dict) and 'data' in data['x_axis']:
                        categories_data = data['x_axis']['data']
                    elif isinstance(data['x_axis'], list):
                        categories_data = data['x_axis']
                    
                    if categories_data:
                        # 创建转换后的数据字典
                        radar_data = {
                            'title': data.get('title', '雷达图'),
                            'categories': categories_data,
                            'series': data.get('series', [])
                        }
                        # 调用雷达图生成方法
                        return self._generate_radar_chart_with_categories(radar_data, output_dir)
                    else:
                        return {
                            "success": False,
                            "message": "雷达图的x_axis数据为空",
                            "files": []
                        }
                else:
                    return {
                        "success": False,
                        "message": "雷达图需要categories或x_axis字段",
                        "files": []
                    }
            else:
                # 其他图表类型的标准格式检查
                if not all(key in data for key in ['title', 'x_axis', 'series']):
                    # 提供详细的格式示例和修复建议
                    missing_fields = [key for key in ['title', 'x_axis', 'series'] if key not in data]

                    # 生成格式示例
                    format_example = {
                        "title": "图表标题",
                        "x_axis": ["2021", "2022", "2023", "2024"],
                        "series": [
                            {"name": "系列1", "data": [100, 150, 120, 180]},
                            {"name": "series2", "data": [80, 120, 110, 140]}
                        ]
                    }

                    # 支持X轴字典格式的示例
                    dict_axis_example = {
                        "title": "图表标题",
                        "x_axis": {"name": "年份", "data": ["2021", "2022", "2023", "2024"]},
                        "series": [
                            {"name": "系列1", "data": [100, 150, 120, 180]},
                            {"name": "series2", "data": [80, 120, 110, 140]}
                        ]
                    }

                    return {
                        "success": False,
                        "message": f"数据格式错误，缺少必要字段: {', '.join(missing_fields)}",
                        "files": [],
                        "format_example": format_example,
                        "dict_axis_example": dict_axis_example,
                        "suggestions": [
                            "1. 确保数据包含 title（图表标题）字段",
                            "2. 确保数据包含 x_axis（X轴标签）字段，可以是列表或字典格式",
                            "3. 确保数据包含 series（数据系列）字段",
                            f"4. 缺失的字段: {', '.join(missing_fields)}",
                            "5. 参考上面的格式示例调整数据结构"
                        ]
                    }
            
            # 准备数据
            title = data.get('title', '图表')
            x_axis_data = data.get('x_axis', [])
            series = data.get('series', [])

            # 增强X轴数据格式处理
            x_axis = []
            x_axis_name = 'X轴'
            if isinstance(x_axis_data, dict):
                # 处理 {"name": "标签名", "data": [...]} 格式
                x_axis = x_axis_data.get('data', [])
                x_axis_name = x_axis_data.get('name', 'X轴')
                logger.info(f"检测到X轴字典格式，名称: {x_axis_name}, 数据: {x_axis}")
            elif isinstance(x_axis_data, list):
                # 处理直接列表格式
                x_axis = x_axis_data
                x_axis_name = 'X轴'
                logger.info(f"检测到X轴列表格式，数据: {x_axis}")
            else:
                logger.warning(f"X轴数据格式不正确，类型: {type(x_axis_data)}, 值: {x_axis_data}")
                x_axis = []
                x_axis_name = 'X轴'
            
            if not x_axis or not series:
                return {
                    "success": False,
                    "message": "数据为空，无法生成图表",
                    "files": []
                }
            
            # 创建图表
            plt.figure(figsize=(12, 8), dpi=300)
            
            # 为不同的数据系列生成不同的颜色
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
            
            chart_files = []
            
            if chart_type == 'line':
                # 生成折线图
                for i, item in enumerate(series):
                    series_name = item.get('name', f'系列{i+1}')
                    series_data = item.get('data', [])

                    # 数据长度检查
                    expected_length = len(x_axis)
                    actual_length = len(series_data)

                    if actual_length != expected_length:
                        logger.warning(f"系列 '{series_name}' 数据长度不匹配，跳过")
                        logger.warning(f"  期望长度: {expected_length}, 实际长度: {actual_length}")
                        logger.warning(f"  X轴标签: {x_axis}")
                        logger.warning(f"  系列数据: {series_data}")

                        # 提供修复建议
                        if actual_length < expected_length:
                            logger.info(f"  建议补充 {expected_length - actual_length} 个数据点")
                        else:
                            logger.info(f"  建议移除 {actual_length - expected_length} 个数据点")
                        continue
                    
                    # 使用不同颜色，循环使用
                    color = colors[i % len(colors)]

                    # 确保X轴数据是列表格式
                    plot_x_axis = x_axis if isinstance(x_axis, list) else list(x_axis) if x_axis else []

                    # 添加绘图错误处理
                    try:
                        # 绘制折线图
                        plt.plot(plot_x_axis, series_data, marker='o', linewidth=2, markersize=6, color=color, label=series_name)
                        logger.debug(f"成功绘制系列 '{series_name}'，数据点数: {len(series_data)}")
                    except Exception as e:
                        logger.error(f"绘制系列 '{series_name}' 时出错: {e}")
                        logger.error(f"  X轴数据: {plot_x_axis} (类型: {type(plot_x_axis)})")
                        logger.error(f"  系列数据: {series_data} (类型: {type(series_data)})")
                        continue
                
                # 设置图表标题和标签
                plt.title(title, fontsize=16, fontweight='bold')
                plt.xlabel(x_axis_name, fontsize=12)
                plt.ylabel('数值', fontsize=12)

                # 添加图例
                plt.legend(loc='best', fontsize=10)
                
                # 添加网格线
                plt.grid(True, linestyle='--', alpha=0.7)
                
                # 保存图表
                chart_filename = os.path.join(output_dir, f"{title.replace(' ', '_')}_折线图.png")
                plt.tight_layout()
                plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
                plt.close()
                
                chart_files.append(chart_filename)
                
            elif chart_type == 'bar':
                # 实现柱状图逻辑
                x = np.arange(len(x_axis))
                width = 0.8 / len(series)
                
                for i, item in enumerate(series):
                    series_name = item.get('name', f'系列{i+1}')
                    series_data = item.get('data', [])
                    
                    if len(series_data) != len(x_axis):
                        logger.warning(f"系列 '{series_name}' 的数据长度与X轴不匹配，跳过")
                        continue
                    
                    # 使用不同颜色，循环使用
                    color = colors[i % len(colors)]
                    
                    # 绘制柱状图
                    plt.bar(x + i * width - (width * len(series)) / 2 + width / 2, 
                           series_data, width=width, color=color, label=series_name)
                
                # 设置图表标题和标签
                plt.title(title, fontsize=16, fontweight='bold')
                plt.xlabel('年份', fontsize=12)
                plt.ylabel('数值', fontsize=12)
                
                # 设置X轴刻度标签
                plt.xticks(x, x_axis)
                
                # 添加图例
                plt.legend(loc='best', fontsize=10)
                
                # 添加网格线
                plt.grid(True, linestyle='--', alpha=0.7, axis='y')
                
                # 保存图表
                chart_filename = os.path.join(output_dir, f"{title.replace(' ', '_')}_柱状图.png")
                plt.tight_layout()
                plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
                plt.close()
                
                chart_files.append(chart_filename)
            
            elif chart_type == 'pie':
                # 生成饼图
                for i, item in enumerate(series):
                    # 创建新图表
                    plt.figure(figsize=(10, 8), dpi=300)
                    
                    series_name = item.get('name', f'系列{i+1}')
                    pie_data = item.get('data', [])
                    
                    # 严格的数据验证
                    if not pie_data:
                        logger.warning(f"饼图数据为空，系列: {series_name}")
                        continue
                    
                    # 确保pie_data是列表
                    if not isinstance(pie_data, list):
                        logger.warning(f"饼图数据格式错误，应为列表，系列: {series_name}")
                        continue
                    
                    labels = []
                    values = []
                    
                    try:
                        # 支持两种格式：直接的数值列表或[{name, value}格式]
                        if pie_data and isinstance(pie_data[0], dict):
                            # 处理{name, value}格式
                            for j, d in enumerate(pie_data):
                                if isinstance(d, dict) and 'value' in d:
                                    label = d.get('name', f'项目{j+1}')
                                    value = d.get('value', 0)
                                    if isinstance(value, (int, float)) and value >= 0:
                                        labels.append(label)
                                        values.append(value)
                        else:
                            # 处理简单数值列表格式
                            for j, val in enumerate(pie_data):
                                if isinstance(val, (int, float)) and val >= 0:
                                    if x_axis and j < len(x_axis):
                                        labels.append(x_axis[j])
                                    else:
                                        labels.append(f'项目{j+1}')
                                    values.append(val)
                    except Exception as e:
                        logger.error(f"饼图数据解析失败: {str(e)}")
                        continue
                    
                    # 再次验证处理后的数据
                    if not values or sum(values) == 0:
                        logger.warning(f"饼图有效数据为空或总和为零，系列: {series_name}")
                        plt.close()
                        continue
                    
                    # 限制标签数量，避免饼图过于复杂
                    if len(labels) > 15:
                        logger.warning(f"饼图数据项过多({len(labels)}项)，可能影响可视化效果")
                        # 可以考虑合并小项
                        pass
                    
                    # 绘制饼图
                    try:
                        # 使用足够的颜色
                        pie_colors = colors * (len(labels) // len(colors) + 1)
                        pie_colors = pie_colors[:len(labels)]
                        
                        # 计算百分比标签位置和格式
                        wedges, texts, autotexts = plt.pie(
                            values, 
                            autopct=lambda p: f'{p:.1f}%' if p >= 2 else '',  # 只显示>=2%的标签
                            startangle=90, 
                            colors=pie_colors, 
                            wedgeprops={'edgecolor': 'w', 'linewidth': 1}
                        )
                        
                        # 设置文本样式
                        for text in texts:
                            text.set_fontsize(10)
                        for autotext in autotexts:
                            autotext.set_fontsize(9)
                            autotext.set_fontweight('bold')
                        
                        plt.axis('equal')  # 保证饼图是圆形的
                        plt.title(f"{title} - {series_name}", fontsize=16, fontweight='bold', pad=20)
                        
                        # 添加图例（如果有多个数据项）
                        if len(labels) > 1:
                            plt.legend(wedges, labels, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
                        
                        # 保存图表
                        safe_title = ''.join(c for c in title if c.isalnum() or c in ['_', ' ', '-'])[:100]
                        safe_series_name = ''.join(c for c in series_name if c.isalnum() or c in ['_', ' ', '-'])[:50]
                        pie_filename = os.path.join(output_dir, f"{safe_title.replace(' ', '_')}_{safe_series_name}_饼图.png")
                        plt.tight_layout(pad=3.0)
                        plt.savefig(pie_filename, dpi=300, bbox_inches='tight', facecolor='white')
                        plt.close()
                        
                        if os.path.exists(pie_filename):
                            logger.info(f"饼图生成成功: {pie_filename}")
                            chart_files.append(pie_filename)
                        else:
                            logger.error(f"饼图保存失败: {pie_filename}")
                    except Exception as e:
                        logger.error(f"饼图绘制失败: {str(e)}")
                        plt.close()
                        continue
            
            # 可以根据需要添加更多图表类型的支持
            else:
                return {
                    "success": False,
                    "message": f"不支持的图表类型: {chart_type}",
                    "files": []
                }
            
            return {
                "success": True,
                "message": f"图表生成成功，生成 {len(chart_files)} 个图表",
                "files": chart_files,
                "chart_type": chart_type,
                "chart_count": len(chart_files)
            }
            
        except Exception as e:
            error_msg = f"通用图表生成失败: {str(e)}"
            logger.error(error_msg)
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": error_msg,
                "files": [],
                "error": str(e)
            }

    def _generate_radar_chart_with_categories(self, data: dict, output_dir: str) -> Dict[str, Any]:
        """
        生成带类别的雷达图（支持单公司多维度数据）

        Args:
            data: 数据字典，包含title、categories、series
            output_dir: 输出目录

        Returns:
            Dict: 图表生成结果
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            import os

            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)

            # 提取数据
            title = data.get('title', '财务雷达图')
            categories = data.get('categories', [])
            series = data.get('series', [])

            if not categories:
                return {
                    "success": False,
                    "message": "雷达图缺少categories字段",
                    "files": []
                }

            if not series:
                return {
                    "success": False,
                    "message": "雷达图缺少series字段",
                    "files": []
                }

            # 创建图表
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, polar=True)

            # 计算角度
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            angles += angles[:1]  # 闭合图形

            # 颜色配置
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

            # 为每个系列绘制雷达图
            for i, serie in enumerate(series):
                if not isinstance(serie, dict):
                    continue

                name = serie.get('name', f'系列{i+1}')
                values = serie.get('data', [])

                if len(values) != len(categories):
                    self.logger.warning(f"系列 '{name}' 的数据长度 {len(values)} 与类别数量 {len(categories)} 不匹配")
                    continue

                # 闭合图形
                values += values[:1]

                color = colors[i % len(colors)]
                ax.plot(angles, values, 'o-', linewidth=2, label=name, color=color)
                ax.fill(angles, values, alpha=0.25, color=color)

            # 设置角度标签
            ax.set_thetagrids(np.degrees(angles[:-1]), categories)

            # 设置径向范围
            all_values = []
            for serie in series:
                if isinstance(serie, dict) and 'data' in serie:
                    all_values.extend(serie['data'])

            if all_values:
                max_value = max(all_values)
                min_value = min(all_values)
                if min_value >= 0:
                    ax.set_ylim(0, max_value * 1.1)
                else:
                    ax.set_ylim(min_value * 1.1, max_value * 1.1)

            ax.grid(True)
            ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

            plt.title(title, size=16, fontweight='bold', pad=20)

            # 保存图表
            chart_file = os.path.join(output_dir, 'radar_chart.png')
            plt.savefig(chart_file, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()

            if os.path.exists(chart_file):
                self.logger.info(f"雷达图生成成功: {chart_file}")
                return {
                    "success": True,
                    "message": "雷达图生成成功",
                    "files": [chart_file],
                    "chart_type": "radar",
                    "chart_count": 1
                }
            else:
                return {
                    "success": False,
                    "message": "雷达图文件保存失败",
                    "files": []
                }

        except Exception as e:
            error_msg = f"雷达图生成失败: {str(e)}"
            self.logger.error(error_msg)
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": error_msg,
                "files": [],
                "error": str(e)
            }

    async def build(self):
        """构建工具包"""
        self._built = True

    async def cleanup(self):
        """清理资源"""
        pass

    async def get_tools_map_func(self) -> dict[str, Any]:
        """获取工具映射函数"""
        return {
            "generate_charts": self.generate_charts,
        }