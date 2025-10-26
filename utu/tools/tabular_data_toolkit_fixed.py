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

# 设置中文字体支持
try:
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
except:
    pass

# 设置日志
logger = logging.getLogger(__name__)

class TabularDataToolkit:
    """
    表格数据处理和图表生成工具
    """

    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = config or {}
        self.logger = logger

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
            return {
                "success": False,
                "message": error_msg,
                "files": [],
                "error": str(e)
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
        创建综合对比图表

        Args:
            data: 数据字典
            output_dir: 输出目录
            variables_code: 变量定义代码

        Returns:
            str: 图表文件路径或None
        """
        try:
            # 构建matplotlib代码
            matplotlib_code = f'''
{variables_code}

# 生成公司对比综合图表
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('公司财务指标对比', fontsize=16, fontweight='bold')

# 1. 营业收入对比
if 'revenue' in locals():
    bars1 = ax1.bar(companies, revenue, color=['#1f77b4', '#ff7f0e'], alpha=0.7)
    ax1.set_title('营业收入对比（亿元）', fontsize=14, fontweight='bold')
    ax1.set_ylabel('营业收入（亿元）')
    for i, (bar, value) in enumerate(zip(bars1, revenue)):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(revenue)*0.02,
                f'{{value:.2f}}', ha='center', va='bottom', fontweight='bold')

# 2. 净利润对比
if 'net_profit' in locals():
    bars2 = ax2.bar(companies, net_profit, color=['#2ca02c', '#d62728'], alpha=0.7)
    ax2.set_title('净利润对比（亿元）', fontsize=14, fontweight='bold')
    ax2.set_ylabel('净利润（亿元）')
    for i, (bar, value) in enumerate(zip(bars2, net_profit)):
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(net_profit)*0.02,
                f'{{value:.2f}}', ha='center', va='bottom', fontweight='bold')

# 3. 净利率对比
if 'profit_margin' in locals():
    bars3 = ax3.bar(companies, profit_margin, color=['#ff9896', '#9467bd'], alpha=0.7)
    ax3.set_title('净利率对比（%）', fontsize=14, fontweight='bold')
    ax3.set_ylabel('净利率（%）')
    for i, (bar, value) in enumerate(zip(bars3, profit_margin)):
        ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                f'{{value:.2f}}%', ha='center', va='bottom', fontweight='bold')

# 4. ROE对比
if 'roe' in locals():
    bars4 = ax4.bar(companies, roe, color=['#c5b0d5', '#8c564b'], alpha=0.7)
    ax4.set_title('ROE对比（%）', fontsize=14, fontweight='bold')
    ax4.set_ylabel('ROE（%）')
    for i, (bar, value) in enumerate(zip(bars4, roe)):
        ax4.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(roe)*0.02,
                f'{{value:.2f}}%', ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('company_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
'''

            # 执行matplotlib代码
            exec(matplotlib_code)

            # 返回生成的文件路径
            chart_file = os.path.join(output_dir, 'company_comparison.png')
            if os.path.exists(chart_file):
                return chart_file

            return None

        except Exception as e:
            logger.error(f"对比图表生成失败: {e}")
            return None

    def _create_radar_chart(self, data: dict, output_dir: str, variables_code: str) -> Optional[str]:
        """
        创建雷达图

        Args:
            data: 数据字典
            output_dir: 输出目录
            variables_code: 变量定义代码

        Returns:
            str: 图表文件路径或None
        """
        try:
            # 构建雷达图代码
            radar_code = f'''
{variables_code}

# 生成雷达图
fig = plt.figure(figsize=(12, 10))

# 简化版雷达图：使用主要财务指标
categories = []
catl_values = []
byd_values = []

# 添加净利率
if 'profit_margin' in locals():
    categories.append('净利率')
    catl_values.append(profit_margin[0])
    byd_values.append(profit_margin[1])

# 添加ROE
if 'roe' in locals():
    categories.append('ROE')
    catl_values.append(roe[0])
    byd_values.append(roe[1])

# 添加营收增长率
if 'revenue_growth' in locals():
    categories.append('营收增长率')
    catl_values.append(revenue_growth[0])
    byd_values.append(revenue_growth[1])

# 添加利润增长率
if 'profit_growth' in locals():
    categories.append('利润增长率')
    catl_values.append(profit_growth[0])
    byd_values.append(profit_growth[1])

if len(categories) == 0:
    plt.close()
    raise ValueError("没有足够的数据生成雷达图")

angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
catl_values += catl_values[:1]
byd_values += byd_values[:1]
angles += angles[:1]

ax = fig.add_subplot(111, polar=True)
ax.plot(angles, catl_values, 'o-', linewidth=2, label=companies[0], color='#1f77b4')
ax.fill(angles, catl_values, alpha=0.25, color='#1f77b4')
ax.plot(angles, byd_values, 'o-', linewidth=2, label=companies[1], color='#ff7f0e')
ax.fill(angles, byd_values, alpha=0.25, color='#ff7f0e')

ax.set_thetagrids(np.degrees(angles[:-1]), categories)
ax.set_ylim(0, max(max(catl_values, byd_values)) * 1.1)
ax.grid(True)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
plt.title('公司财务表现雷达图', size=16, fontweight='bold', pad=20)

plt.savefig('radar_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
'''

            # 执行雷达图代码
            exec(radar_code)

            # 返回生成的文件路径
            chart_file = os.path.join(output_dir, 'radar_comparison.png')
            if os.path.exists(chart_file):
                return chart_file

            return None

        except Exception as e:
            logger.error(f"雷达图生成失败: {e}")
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
            data: 数据字典，支持title、x_axis、series格式，以及years、revenue、net_profit格式
            chart_type: 图表类型
            output_dir: 输出目录

        Returns:
            Dict: 图表生成结果
        """
        try:
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 检查是否是财务数据格式（years, revenue, net_profit）
            if 'years' in data and ('revenue' in data or 'net_profit' in data):
                # 转换为标准格式
                standard_data = {
                    'title': '财务指标趋势图',
                    'x_axis': [str(year) for year in data['years']],
                    'series': []
                }
                
                # 添加收入数据（如果存在）
                if 'revenue' in data:
                    standard_data['series'].append({
                        'name': '营业收入(亿元)',
                        'data': data['revenue']
                    })
                
                # 添加净利润数据（如果存在）
                if 'net_profit' in data:
                    standard_data['series'].append({
                        'name': '净利润(亿元)',
                        'data': data['net_profit']
                    })
                
                # 使用转换后的数据
                data = standard_data
            
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
                    # 使用标准格式
                    pass  # 继续执行通用逻辑
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
            elif isinstance(x_axis_data, list):
                # 处理直接列表格式
                x_axis = x_axis_data
                x_axis_name = 'X轴'
            
            # 验证数据
            if not x_axis or not series:
                return {
                    "success": False,
                    "message": "X轴数据或系列数据为空",
                    "files": []
                }
            
            # 验证系列数据长度
            for s in series:
                if 'data' not in s or len(s['data']) != len(x_axis):
                    return {
                        "success": False,
                        "message": "系列数据长度与X轴数据不匹配",
                        "files": []
                    }
            
            # 创建图表
            import matplotlib.pyplot as plt
            import os
            
            # 设置中文字体支持
            plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
            plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
            
            plt.figure(figsize=(10, 6))
            
            if chart_type == 'line':
                # 生成折线图
                for s in series:
                    plt.plot(x_axis, s['data'], marker='o', label=s['name'])
            elif chart_type == 'bar':
                # 生成柱状图
                width = 0.8 / len(series)
                for i, s in enumerate(series):
                    plt.bar([j + i * width - (len(series) - 1) * width / 2 for j in range(len(x_axis))], 
                            s['data'], width=width, label=s['name'])
            else:
                # 默认生成折线图
                for s in series:
                    plt.plot(x_axis, s['data'], marker='o', label=s['name'])
            
            plt.title(title, fontsize=15)
            plt.xlabel(x_axis_name, fontsize=12)
            plt.ylabel('数值', fontsize=12)
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.7)
            
            # 保存图表
            chart_file = os.path.join(output_dir, f"{title}_{chart_type}.png")
            plt.tight_layout()
            plt.savefig(chart_file)
            plt.close()
            
            return {
                "success": True,
                "message": f"图表生成成功",
                "files": [chart_file],
                "chart_type": chart_type
            }
            
        except Exception as e:
            error_msg = f"图表生成失败: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "files": [],
                "error": str(e)
            }