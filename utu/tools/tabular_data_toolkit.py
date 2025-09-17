"""
WARNING: WIP
"""

import json
import math
import os
import pathlib
from collections.abc import Callable

import pandas as pd

from ..config import ToolkitConfig
from ..utils import SimplifiedAsyncOpenAI, async_file_cache, get_logger
from .base import AsyncBaseToolkit, register_tool

logger = get_logger(__name__)

TEMPLATE_COLUMN_QA = (
    "You are a data analysis agent that extracts and summarizes data structure information "
    "from tabular data files (CSV, Excel, etc.).\n\n"
    "<column_info>\n"
    "{column_info}\n"
    "</column_info>\n\n"
    "You should extract the file structure(e.g. the delimiter), and provide detail column information "
    "(e.g. column_name, type, column explanation and sample values) for each column.\n"
    "<output_format>\n"
    "### File Structure\n"
    "- Delimiter: <the delimiter used in the file, e.g. ',', '\\\\t', ' '>\n\n"
    "### Columns\n"
    "| Column Name | Type | Explanation | Sample Value |\n"
    "|-------------|------|-------------|--------------|\n"
    "| name_of_column1 | type_of_column1 | explanation_of_column1, i.e. what the column represents "
    "| sample_value_of_column1 |\n"
    "| name_of_column2 | type_of_column2 | explanation_of_column2, i.e. what the column represents "
    "| sample_value_of_column2 |\n"
    "| ... | ... | ... | ... |\n"
    "</output_format>"
).strip()


class TabularDataToolkit(AsyncBaseToolkit):
    def __init__(self, config: ToolkitConfig | None = None):
        super().__init__(config)
        self.llm = SimplifiedAsyncOpenAI(
            **self.config.config_llm.model_provider.model_dump() if self.config.config_llm else {}
        )

    @register_tool()
    def get_tabular_columns(self, file_path: str, return_feat: list[str] | None = None) -> str:
        """Extract raw column metadata from tabular data files.

        Directly reads file and returns basic column information:
        column names, data types, and sample values.

        Args:
            file_path (str): Path to the tabular data file.

        Returns:
            str: Formatted string with raw column information.
        """
        logger.info(f"[tool] get_tabular_columns: {file_path}")
        if not os.path.exists(file_path):
            return self._stringify_column_info([{"error": f"File '{file_path}' does not exist."}])

        try:
            # 1. Load the tabular data using the helper function
            df = self._load_tabular_data(file_path)
            # 2. Build column information
            column_info = []
            for col in df.columns:
                try:
                    # Get data type
                    dtype = str(df[col].dtype)

                    # Get a non-null sample value
                    sample_value = None
                    non_null_values = df[col].dropna()
                    if len(non_null_values) > 0:
                        # Get the first non-null value as sample
                        sample_value = non_null_values.iloc[0]
                        # Convert to string, handling different data types
                        if pd.isna(sample_value):
                            sample_str = "NaN"
                        elif isinstance(sample_value, float):
                            if math.isnan(sample_value):
                                sample_str = "NaN"
                            else:
                                sample_str = str(sample_value)
                        else:
                            sample_str = str(sample_value)
                    else:
                        sample_str = "No data"

                    column_info.append({"column_name": str(col), "type": dtype, "sample": sample_str})

                except Exception as e:  # pylint: disable=broad-except
                    logger.warning(f"Error processing column '{col}': {e}")
                    column_info.append({"column_name": str(col), "type": "unknown", "sample": "Error reading sample"})

            return self._stringify_column_info(column_info, return_feat=return_feat)

        except Exception as e:  # pylint: disable=broad-except
            error_msg = f"Error reading file '{file_path}': {str(e)}"
            logger.error(error_msg)
            return self._stringify_column_info([{"error": error_msg}], return_feat=return_feat)

    @register_tool()
    @async_file_cache(mode="file", expire_time=None)
    async def get_column_info(self, file_path: str) -> str:
        """Intelligently analyze and interpret column information.

        Builds on get_tabular_columns() to provide simple file structure analysis
        and column meaning interpretation.

        Args:
            file_path (str): Path to the tabular data file.

        Returns:
            str: Analysis with file structure and column explanations.
        """
        column_info_str = self.get_tabular_columns(file_path)
        prompt = TEMPLATE_COLUMN_QA.format(column_info=column_info_str)
        logger.info(f"[tool] get_column_info: {file_path}")

        try:
            response = await self.llm.query_one(
                messages=[{"role": "user", "content": prompt}],
                # **self.config.config_llm.model_params.model_dump()
            )
            return response
        except Exception as e:  # pylint: disable=broad-except
            error_msg = f"Error during LLM processing: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def _load_tabular_data(self, file_path: str) -> pd.DataFrame:
        """Load tabular data from a file and return as a DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing the tabular data.
        Raises:
            Exception: If the file cannot be loaded as tabular data.
        """
        # Get file extension to determine how to read the file
        file_ext = pathlib.Path(file_path).suffix.lower()

        # Read the file based on its extension
        if file_ext == ".csv":
            # Try different encodings for CSV files
            encodings = ["utf-8", "latin1", "cp1252", "iso-8859-1"]
            df = None
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            if df is None:
                raise Exception("Could not read CSV file with any supported encoding")
        elif file_ext in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path)
        elif file_ext == ".json":
            # Try to read JSON as tabular data
            df = pd.read_json(file_path)
        elif file_ext == ".parquet":
            df = pd.read_parquet(file_path)
        elif file_ext == ".tsv":
            # Tab-separated values
            encodings = ["utf-8", "latin1", "cp1252", "iso-8859-1"]
            df = None
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, sep="\t", encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            if df is None:
                raise Exception("Could not read TSV file with any supported encoding")
        else:
            # Try to read as CSV by default
            try:
                df = pd.read_csv(file_path)
            except Exception as e:  # pylint: disable=broad-except
                raise Exception(f"Unsupported file format: {file_ext}") from e

        return df

    def _stringify_column_info(self, column_info: list[dict], return_feat: list[str] | None = None) -> str:
        """Convert column information to a formatted string."""
        if "error" in column_info[0]:
            return column_info[0]["error"]

        lines = []
        return_keys = ["column_name", "type", "sample"]
        if return_feat:
            return_keys = [key for key in return_keys if key in return_feat]
        for i, col in enumerate(column_info):
            lines.append(
                f"- Column {i + 1}: {json.dumps({k: col[k] for k in return_keys if k in col}, ensure_ascii=False)}"
            )
        return "\n".join(lines)

    async def get_tools_map(self) -> dict[str, Callable]:
        """Return a mapping of tool names to their corresponding methods."""
        return {
            "get_tabular_columns": self.get_tabular_columns,
            "get_column_info": self.get_column_info,
            "generate_charts": self.generate_charts,
        }

    @register_tool()
    def generate_charts(self, data_json: str, chart_type: str = "bar", output_dir: str = "./run_workdir") -> dict:
        """Generate charts from financial data.
        
        Args:
            data_json (str): Financial data in JSON format
            chart_type (str): Type of chart to generate (bar, line, pie)
            output_dir (str): Directory to save charts
            
        Returns:
            dict: Information about generated charts
        """
        import json
        import matplotlib.pyplot as plt
        import seaborn as sns
        import os
        from datetime import datetime
        import numpy as np
        import re
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        try:
            # 解析数据
            data = json.loads(data_json)
            
            # 数据验证和时间检查
            current_year = datetime.now().year
            current_month = datetime.now().month
            current_date = datetime.now()
            
            # 检查数据中的时间是否合理
            if isinstance(data, dict) and 'trend' in data:
                filtered_trend_data = []
                for item in data['trend']:
                    if isinstance(item, dict) and ('年份' in item or 'year' in item or '日期' in item):
                        # 提取时间信息
                        time_key = None
                        time_value = None
                        for key in ['年份', 'year', '日期', 'date']:
                            if key in item:
                                time_key = key
                                time_value = item[key]
                                break
                        
                        if time_key and time_value:
                            # 解析时间字符串
                            year_match = re.search(r'(\d{4})', str(time_value))
                            if year_match:
                                year = int(year_match.group(1))
                                # 检查是否是合理的时间
                                if year < current_year or (year == current_year and current_month >= 6):
                                    # 如果是过去或当前年份且已过半年，保留该数据
                                    filtered_trend_data.append(item)
                                else:
                                    # 如果是未来时间或今年但还没到财报季，跳过该数据
                                    logger.warning(f"跳过不合理的时间数据: {time_value}")
                            else:
                                # 如果无法解析年份，保留数据但记录警告
                                logger.warning(f"无法解析时间字段: {time_value}")
                                filtered_trend_data.append(item)
                        else:
                            # 如果没有时间字段，保留数据
                            filtered_trend_data.append(item)
                    else:
                        # 如果不是趋势数据项，保留数据
                        filtered_trend_data.append(item)
                
                # 更新趋势数据
                data['trend'] = filtered_trend_data
            
            # 处理嵌套数据结构，将其扁平化
            # 确保data是字典类型，如果不是则进行转换
            if isinstance(data, list):
                # 如果是列表，尝试将其转换为字典格式
                flattened_data = self._flatten_financial_list_data(data)
            else:
                flattened_data = self._flatten_financial_data(data)
            
            # 数据验证：检查毛利率等关键指标是否合理
            for key, value in flattened_data.items():
                if '毛利率' in key and value > 95:  # 如果毛利率超过95%，可能是数据错误
                    logger.warning(f"检测到异常毛利率数据: {key} = {value}%，可能存在问题")
                elif '净利率' in key and value > 50:  # 如果净利率超过50%，可能是数据错误
                    logger.warning(f"检测到异常净利率数据: {key} = {value}%，可能存在问题")
            
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成图表
            chart_files = []
            
            # 检查是否是公司对比数据并生成分组图表
            if isinstance(data, dict) and 'companies' in data and isinstance(data.get('revenue'), list):
                companies = data['companies']
                # 生成公司对比图表
                fig, ax = plt.subplots(figsize=(12, 8))
                
                # 获取要绘制的指标
                metrics = {}
                metric_names = {
                    'revenue': '营业收入',
                    'net_profit': '净利润',
                    'total_assets': '总资产',
                    'debt_ratio': '资产负债率',
                    'roe': 'ROE'
                }
                
                for metric_key, metric_name in metric_names.items():
                    if metric_key in data and isinstance(data[metric_key], list):
                        metrics[metric_name] = data[metric_key]
                
                # 绘制分组柱状图
                if metrics:
                    x = np.arange(len(companies))
                    width = 0.8 / len(metrics)
                    
                    for i, (metric_name, values) in enumerate(metrics.items()):
                        ax.bar(x + i*width, values, width, label=metric_name)
                    
                    ax.set_xlabel('公司')
                    ax.set_ylabel('数值')
                    ax.set_title('公司财务指标对比')
                    ax.set_xticks(x + width * (len(metrics) - 1) / 2)
                    ax.set_xticklabels(companies)
                    ax.legend()
                    
                    # 保存图表
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    chart_file = os.path.join(output_dir, f"comparison_chart_{timestamp}.png")
                    plt.savefig(chart_file, dpi=300, bbox_inches='tight')
                    plt.close()
                    chart_files.append(chart_file)
            else:
                # 过滤掉异常数据后再生成图表
                filtered_data = {}
                for key, value in flattened_data.items():
                    # 过滤掉明显异常的数据
                    if isinstance(value, (int, float)) and not (np.isnan(value) or np.isinf(value)):
                        # 检查毛利率等关键指标
                        if '毛利率' in key and value <= 100 and value >= 0:
                            filtered_data[key] = value
                        elif '净利率' in key and value <= 100 and value >= -100:
                            filtered_data[key] = value
                        elif '资产负债率' in key and value <= 100 and value >= 0:
                            filtered_data[key] = value
                        elif 'ROE' in key and abs(value) <= 100:
                            filtered_data[key] = value
                        elif not any(keyword in key for keyword in ['毛利率', '净利率', '资产负债率', 'ROE']):
                            # 其他指标不做特殊限制
                            filtered_data[key] = value
                
                # 如果过滤后没有数据，使用原始数据
                if not filtered_data:
                    filtered_data = flattened_data
                
                # 原有的单公司图表生成逻辑
                if chart_type == "bar":
                    # 生成柱状图
                    fig, ax = plt.subplots(figsize=(10, 6))
                    
                    # 提取数据
                    keys = list(filtered_data.keys())
                    values = list(filtered_data.values())
                    
                    # 创建柱状图
                    bars = ax.bar(keys, values, color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D'])
                    ax.set_title("财务数据图表")
                    ax.set_ylabel("数值")
                    
                    # 添加数值标签
                    y_max = ax.get_ylim()[1]
                    for bar, value in zip(bars, values):
                        # 计算标签位置，确保不会超出图表上边界
                        label_y = bar.get_height() + (y_max * 0.02)
                        if label_y > y_max * 0.9:  # 如果标签位置过高
                            label_y = bar.get_height() - (y_max * 0.05)  # 放在柱子内部，增加偏移量
                            va = 'top'
                        else:
                            va = 'bottom'
                        ax.text(bar.get_x() + bar.get_width() / 2, label_y, f'{value:.2f}', ha='center', va=va,
                                bbox=dict(boxstyle="square,pad=0.3", fc="white", alpha=0.7))  # 添加背景框
                    
                    # 保存图表
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    chart_file = os.path.join(output_dir, f"bar_chart_{timestamp}.png")
                    plt.savefig(chart_file, dpi=300, bbox_inches='tight')
                    plt.close()
                    chart_files.append(chart_file)
                    
                elif chart_type == "line":
                    # 生成折线图
                    fig, ax = plt.subplots(figsize=(10, 6))
                    
                    # 提取数据
                    keys = list(filtered_data.keys())
                    values = list(filtered_data.values())
                    
                    # 创建折线图
                    ax.plot(keys, values, marker='o', linewidth=2, markersize=8, color='#2E86AB')
                    ax.set_title("财务数据趋势图")
                    ax.set_ylabel("数值")
                    ax.grid(True, linestyle='--', alpha=0.5)  # 调整网格线样式
                    
                    # 添加数值标签
                    y_min, y_max = ax.get_ylim()
                    y_range = y_max - y_min
                    label_positions = []  # 用于存储已添加标签的位置，避免重叠
                    
                    for i, (key, value) in enumerate(zip(keys, values)):
                        # 动态调整标签偏移量，避免重叠
                        offset = min(15, max(5, y_range * 0.02))  # 偏移量在5-15之间
                        label_y = value + offset
                        
                        # 检查标签是否重叠
                        if any(abs(label_y - pos) < offset for pos in label_positions):
                            label_y = value - offset  # 如果会重叠，则放在数据点下方
                        
                        label_positions.append(label_y)
                        
                        # 只在关键点显示标签（例如，最大值、最小值和起点）
                        if i == 0 or value == max(values) or value == min(values):
                            ax.annotate(f'{value:.2f}', (i, label_y), textcoords="offset points", 
                                       xytext=(0, 0), ha='center', va='bottom', 
                                       bbox=dict(boxstyle="square,pad=0.3", fc="white", alpha=0.7))
                    
                    # 保存图表
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    chart_file = os.path.join(output_dir, f"line_chart_{timestamp}.png")
                    plt.savefig(chart_file, dpi=300, bbox_inches='tight')
                    plt.close()
                    chart_files.append(chart_file)
                    
                elif chart_type == "pie":
                    # 生成饼图
                    fig, ax = plt.subplots(figsize=(10, 8))
                    
                    # 提取数据
                    keys = list(filtered_data.keys())
                    values = list(filtered_data.values())
                    
                    # 过滤掉负值和零值，饼图不能显示负值
                    positive_keys = []
                    positive_values = []
                    for k, v in zip(keys, values):
                        if isinstance(v, (int, float)) and v > 0:
                            positive_keys.append(k)
                            positive_values.append(v)
                    
                    if positive_keys:  # 只有当有正值时才生成饼图
                        # 创建饼图
                        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']
                        pie_result = ax.pie(positive_values, labels=None, autopct='%1.1f%%', 
                                           colors=colors[:len(positive_keys)], startangle=90,
                                           textprops={'color': 'black'})  # 统一文本颜色
                        
                        # 获取饼图的wedges
                        wedges = pie_result[0] if isinstance(pie_result, tuple) else pie_result
                        
                        # 调整标签显示
                        label_distance = 1.1  # 标签距离圆心的距离
                        for i, wedge in enumerate(wedges):
                            angle = (wedge.theta2 - wedge.theta1) / 2. + wedge.theta1
                            x = np.cos(np.deg2rad(angle))
                            y = np.sin(np.deg2rad(angle))
                            
                            # 对于占比非常小的部分，不显示标签
                            if positive_values[i] / sum(positive_values) > 0.05:  # 只显示占比大于5%的标签
                                horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
                                connectionstyle = "angle,angleA=0,angleB={}".format(angle)
                                
                                ax.annotate(
                                    positive_keys[i], 
                                    xy=(x, y),  # 标签的坐标
                                    xytext=(label_distance * x, label_distance * y),  # 文本的坐标
                                    horizontalalignment=horizontalalignment,
                                    verticalalignment="center",
                                    fontsize=10,
                                    bbox=dict(facecolor='white', edgecolor='none', pad=5),
                                    arrowprops=dict(arrowstyle="->", connectionstyle=connectionstyle)
                                )
                        
                        ax.set_title("财务数据占比图")
                        
                        # 保存图表
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        chart_file = os.path.join(output_dir, f"pie_chart_{timestamp}.png")
                        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
                        plt.close()
                        chart_files.append(chart_file)
            
            return {
                "success": True,
                "chart_files": chart_files,
                "chart_type": chart_type,
                "message": f"成功生成{len(chart_files)}个图表"
            }
            
        except Exception as e:
            logger.error(f"生成图表时出错: {str(e)}")
            return {
                "success": False,
                "chart_files": [],
                "chart_type": chart_type,
                "error": str(e)
            }

    def _flatten_financial_data(self, data: dict) -> dict:
        """将嵌套的财务数据扁平化为简单的键值对
        
        Args:
            data (dict): 原始财务数据，可能包含嵌套结构
            
        Returns:
            dict: 扁平化的键值对数据
        """
        flattened = {}
        
        # 处理趋势数据
        if 'trend_data' in data and isinstance(data['trend_data'], list):
            for item in data['trend_data']:
                if isinstance(item, dict) and 'year' in item:
                    year = item['year']
                    for key, value in item.items():
                        if key != 'year' and isinstance(value, (int, float)):
                            # 将指标名称转换为中文
                            chinese_key = self._translate_indicator(key)
                            flattened[f"{year}年{chinese_key}"] = value
        
        # 处理比率数据
        if 'ratios_data' in data and isinstance(data['ratios_data'], dict):
            for category, ratios in data['ratios_data'].items():
                if isinstance(ratios, dict):
                    # 将类别名称转换为中文
                    chinese_category = self._translate_category(category)
                    for ratio_name, ratio_value in ratios.items():
                        if isinstance(ratio_value, (int, float)):
                            # 将指标名称转换为中文
                            chinese_ratio = self._translate_indicator(ratio_name)
                            flattened[f"{chinese_category}_{chinese_ratio}"] = ratio_value
        
        # 处理公司对比数据（新增处理逻辑）
        if 'companies' in data and isinstance(data.get('revenue'), list):
            companies = data['companies']
            # 处理各种财务指标
            for key, values in data.items():
                if isinstance(values, list) and len(values) == len(companies):
                    for i, value in enumerate(values):
                        if isinstance(value, (int, float)):
                            chinese_key = self._translate_indicator(key)
                            flattened[f"{companies[i]}_{chinese_key}"] = value
        
        # 处理扁平化的公司数据（新增处理逻辑）
        if len(data) > 0 and not flattened:
            # 检查是否是公司数据的字典格式
            for company_name, company_data in data.items():
                if isinstance(company_data, dict):
                    for key, value in company_data.items():
                        if isinstance(value, (int, float)):
                            chinese_key = self._translate_indicator(key)
                            flattened[f"{company_name}_{chinese_key}"] = value
        
        # 如果没有嵌套结构，直接返回原始数据中的数值键值对
        if not flattened:
            for key, value in data.items():
                # 增加数据验证，确保数值合理
                if isinstance(value, (int, float)) and not (isinstance(value, bool)):
                    # 对于明显的异常值进行过滤
                    if '毛利率' in key and (value < 0 or value > 100):
                        logger.warning(f"跳过异常毛利率数据: {key} = {value}")
                        continue
                    elif '净利率' in key and (value < -100 or value > 100):
                        logger.warning(f"跳过异常净利率数据: {key} = {value}")
                        continue
                    elif '资产负债率' in key and (value < 0 or value > 100):
                        logger.warning(f"跳过异常资产负债率数据: {key} = {value}")
                        continue
                    flattened[key] = value
        
        return flattened

    def _flatten_financial_list_data(self, data: list) -> dict:
        """将列表形式的财务数据扁平化为简单的键值对
        
        Args:
            data (list): 原始财务数据列表
            
        Returns:
            dict: 扁平化的键值对数据
        """
        flattened = {}
        
        # 处理列表数据，通常是年度数据列表
        for i, item in enumerate(data):
            if isinstance(item, dict):
                # 提取年份信息
                year = item.get('year', item.get('年份', f'数据{i+1}'))
                
                # 处理各项财务指标
                for key, value in item.items():
                    if key not in ['year', '年份'] and isinstance(value, (int, float)) and not (isinstance(value, bool)):
                        # 数据验证
                        if '毛利率' in key and (value < 0 or value > 100):
                            logger.warning(f"跳过异常毛利率数据: {year}年{key} = {value}")
                            continue
                        elif '净利率' in key and (value < -100 or value > 100):
                            logger.warning(f"跳过异常净利率数据: {year}年{key} = {value}")
                            continue
                        elif '资产负债率' in key and (value < 0 or value > 100):
                            logger.warning(f"跳过异常资产负债率数据: {year}年{key} = {value}")
                            continue
                        
                        # 将指标名称转换为中文
                        chinese_key = self._translate_indicator(key)
                        flattened[f"{year}年{chinese_key}"] = value
        
        return flattened

    def _translate_indicator(self, indicator: str) -> str:
        """将英文指标名称翻译为中文"""
        translations = {
            'revenue': '营收',
            'net_profit': '净利润',
            'net_margin': '净利率',
            'roa': 'ROA',
            'roe': 'ROE',
            'debt_ratio': '资产负债率',
            'equity_ratio': '权益比率'
        }
        return translations.get(indicator, indicator)

    def _translate_category(self, category: str) -> str:
        """将英文类别名称翻译为中文"""
        translations = {
            'profitability': '盈利能力',
            'solvency': '偿债能力',
            'efficiency': '运营效率',
            'growth': '成长能力'
        }
        return translations.get(category, category)