#!/usr/bin/env python3
"""
图表数据验证和修复工具
解决图表生成智能体中的JSON格式和数据格式问题
"""

import json
import re
from typing import Dict, Any, List, Optional, Union

class ChartDataValidator:
    """图表数据验证和修复器"""
    
    def __init__(self):
        self.required_fields = {
            'line': ['title', 'x_axis', 'series'],
            'bar': ['title', 'x_axis', 'series'], 
            'pie': ['title', 'series'],
            'radar': ['title', 'categories', 'series'],
            'scatter': ['title', 'x_axis', 'series']
        }
        
        # 标准数据格式模板
        self.format_templates = {
            'line': {
                "title": "折线图标题",
                "x_axis": ["X轴标签1", "X轴标签2", "X轴标签3"],
                "series": [
                    {"name": "系列1", "data": [10, 20, 30]},
                    {"name": "系列2", "data": [15, 25, 35]}
                ]
            },
            'bar': {
                "title": "柱状图标题", 
                "x_axis": ["类别1", "类别2", "类别3"],
                "series": [
                    {"name": "系列1", "data": [10, 20, 30]},
                    {"name": "系列2", "data": [15, 25, 35]}
                ]
            },
            'radar': {
                "title": "雷达图标题",
                "categories": ["维度1", "维度2", "维度3", "维度4", "维度5"],
                "series": [
                    {"name": "系列1", "data": [80, 60, 70, 90, 75]},
                    {"name": "系列2", "data": [60, 70, 65, 80, 70]}
                ]
            }
        }

    def validate_and_fix_json(self, json_str: str, chart_type: str = 'line') -> Dict[str, Any]:
        """
        验证并修复JSON字符串
        
        Args:
            json_str: 可能格式错误的JSON字符串
            chart_type: 图表类型
            
        Returns:
            修复后的数据字典，包含验证结果
        """
        result = {
            'success': False,
            'data': None,
            'error': None,
            'fixed': False,
            'original_error': None
        }
        
        # 第一步：尝试直接解析
        try:
            data = json.loads(json_str)
            validation_result = self.validate_chart_data(data, chart_type)
            if validation_result['valid']:
                result['success'] = True
                result['data'] = data
                return result
        except json.JSONDecodeError as e:
            result['original_error'] = str(e)
        
        # 第二步：尝试修复常见JSON错误
        fixed_json = self._fix_common_json_errors(json_str)
        if fixed_json != json_str:
            try:
                data = json.loads(fixed_json)
                validation_result = self.validate_chart_data(data, chart_type)
                if validation_result['valid']:
                    result['success'] = True
                    result['data'] = data
                    result['fixed'] = True
                    return result
            except json.JSONDecodeError:
                pass
        
        # 第三步：尝试从错误中提取数据并重构
        reconstructed_data = self._reconstruct_from_broken_json(json_str, chart_type)
        if reconstructed_data:
            validation_result = self.validate_chart_data(reconstructed_data, chart_type)
            if validation_result['valid']:
                result['success'] = True
                result['data'] = reconstructed_data
                result['fixed'] = True
                return result
        
        # 如果所有修复都失败，返回错误信息
        result['error'] = f"无法修复JSON格式。原始错误: {result['original_error']}"
        return result

    def _fix_common_json_errors(self, json_str: str) -> str:
        """修复常见的JSON格式错误"""
        fixed = json_str
        
        # 修复缺少逗号的问题
        fixed = re.sub(r'([}\]])\s*([{\[])', r'\1,\2', fixed)
        
        # 修复多余的逗号
        fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)
        
        # 修复引号不匹配的问题
        # 这里使用启发式方法，可能不完全准确但对大多数情况有效
        fixed = self._fix_quote_mismatches(fixed)
        
        return fixed

    def _fix_quote_mismatches(self, json_str: str) -> str:
        """修复引号不匹配的问题"""
        # 这是一个简化的实现，实际应用中可能需要更复杂的逻辑
        lines = json_str.split('\n')
        fixed_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith(('#', '//')):
                # 检查是否缺少引号
                if ':' in line and not line.strip().endswith(','):
                    key_part, value_part = line.split(':', 1)
                    key_part = key_part.strip()
                    value_part = value_part.strip()
                    
                    # 如果键没有引号，添加引号
                    if not (key_part.startswith('"') and key_part.endswith('"')) and not key_part.isdigit():
                        key_part = f'"{key_part}"'
                    
                    # 如果值是字符串且没有引号，添加引号
                    if value_part and not (
                        value_part.startswith(('"', '[', '{')) or 
                        value_part.endswith((']', '}')) or
                        value_part.replace('.', '').replace('-', '').isdigit()
                    ):
                        value_part = f'"{value_part}"'
                    
                    line = f"{key_part}: {value_part}"
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)

    def _reconstruct_from_broken_json(self, broken_json: str, chart_type: str) -> Optional[Dict[str, Any]]:
        """从损坏的JSON中重构数据"""
        try:
            # 提取数据模式
            title_match = re.search(r'"title"\s*:\s*"([^"]+)"', broken_json)
            title = title_match.group(1) if title_match else "图表标题"
            
            # 提取x_axis数据
            x_axis_match = re.search(r'"x_axis"\s*:\s*\[([^\]]+)\]', broken_json)
            x_axis = []
            if x_axis_match:
                x_axis_str = x_axis_match.group(1)
                x_axis = [item.strip().strip('"') for item in x_axis_str.split(',')]
            
            # 提取series数据
            series_match = re.search(r'"series"\s*:\s*\[([^\]]+)\]', broken_json, re.DOTALL)
            series = []
            if series_match:
                series_str = series_match.group(1)
                # 简化的series解析
                series_items = re.findall(r'\{[^}]+\}', series_str)
                for item in series_items:
                    name_match = re.search(r'"name"\s*:\s*"([^"]+)"', item)
                    data_match = re.search(r'"data"\s*:\s*\[([^\]]+)\]', item)
                    
                    if name_match and data_match:
                        name = name_match.group(1)
                        data_str = data_match.group(1)
                        data = [float(x.strip()) for x in data_str.split(',') if x.strip().replace('.', '').replace('-', '').isdigit()]
                        series.append({"name": name, "data": data})
            
            # 构造基本数据结构
            reconstructed = {"title": title}
            
            if chart_type in ['line', 'bar'] and x_axis:
                reconstructed["x_axis"] = x_axis
            elif chart_type == 'radar':
                # 为雷达图生成默认categories
                categories_match = re.search(r'"categories"\s*:\s*\[([^\]]+)\]', broken_json)
                if categories_match:
                    categories_str = categories_match.group(1)
                    reconstructed["categories"] = [cat.strip().strip('"') for cat in categories_str.split(',')]
                else:
                    reconstructed["categories"] = ["维度1", "维度2", "维度3", "维度4", "维度5"]
            
            if series:
                reconstructed["series"] = series
            else:
                # 添加默认series
                reconstructed["series"] = [{"name": "数据系列", "data": [10, 20, 30]}]
            
            return reconstructed
            
        except Exception as e:
            print(f"重构JSON失败: {e}")
            return None

    def validate_chart_data(self, data: Dict[str, Any], chart_type: str) -> Dict[str, Any]:
        """
        验证图表数据格式
        
        Args:
            data: 图表数据字典
            chart_type: 图表类型
            
        Returns:
            验证结果
        """
        result = {
            'valid': False,
            'missing_fields': [],
            'invalid_fields': [],
            'warnings': []
        }
        
        # 检查必需字段
        required = self.required_fields.get(chart_type, ['title', 'series'])
        for field in required:
            if field not in data:
                result['missing_fields'].append(field)
        
        # 验证数据结构
        if 'series' in data:
            if not isinstance(data['series'], list):
                result['invalid_fields'].append('series必须是数组')
            else:
                for i, series_item in enumerate(data['series']):
                    if not isinstance(series_item, dict):
                        result['invalid_fields'].append(f'series[{i}]必须是对象')
                    else:
                        if 'name' not in series_item:
                            result['invalid_fields'].append(f'series[{i}]缺少name字段')
                        if 'data' not in series_item:
                            result['invalid_fields'].append(f'series[{i}]缺少data字段')
                        elif not isinstance(series_item['data'], list):
                            result['invalid_fields'].append(f'series[{i}].data必须是数组')
        
        # 验证x_axis（如果存在）
        if 'x_axis' in data and chart_type in ['line', 'bar']:
            if not isinstance(data['x_axis'], list):
                result['invalid_fields'].append('x_axis必须是数组')
            elif 'series' in data:
                # 检查数据长度是否匹配
                for i, series_item in enumerate(data['series']):
                    if 'data' in series_item and len(series_item['data']) != len(data['x_axis']):
                        result['warnings'].append(f'series[{i}]的数据长度与x_axis不匹配')
        
        # 验证categories（雷达图专用）
        if chart_type == 'radar' and 'categories' in data:
            if not isinstance(data['categories'], list):
                result['invalid_fields'].append('categories必须是数组')
            elif 'series' in data:
                # 检查雷达图数据维度
                for i, series_item in enumerate(data['series']):
                    if 'data' in series_item and len(series_item['data']) != len(data['categories']):
                        result['invalid_fields'].append(f'雷达图series[{i}]的数据维度必须与categories数量相同')
        
        result['valid'] = len(result['missing_fields']) == 0 and len(result['invalid_fields']) == 0
        return result

    def get_format_example(self, chart_type: str) -> Dict[str, Any]:
        """获取图表类型的格式示例"""
        return self.format_templates.get(chart_type, self.format_templates['line'])

    def auto_fix_chart_data(self, data: Dict[str, Any], chart_type: str) -> Dict[str, Any]:
        """
        自动修复图表数据问题
        
        Args:
            data: 原始数据
            chart_type: 图表类型
            
        Returns:
            修复后的数据
        """
        fixed_data = data.copy()
        
        # 添加缺失的必需字段
        required = self.required_fields.get(chart_type, ['title', 'series'])
        for field in required:
            if field not in fixed_data:
                if field == 'title':
                    fixed_data['title'] = f"{chart_type.upper()}图表"
                elif field == 'x_axis' and chart_type in ['line', 'bar']:
                    # 根据series数据推断x_axis
                    if 'series' in fixed_data and fixed_data['series']:
                        max_length = max(len(s.get('data', [])) for s in fixed_data['series'])
                        fixed_data['x_axis'] = [f"项目{i+1}" for i in range(max_length)]
                elif field == 'categories' and chart_type == 'radar':
                    fixed_data['categories'] = ["维度1", "维度2", "维度3", "维度4", "维度5"]
                elif field == 'series':
                    fixed_data['series'] = [{"name": "数据系列", "data": [10, 20, 30]}]
        
        # 修复series数据
        if 'series' in fixed_data:
            for i, series_item in enumerate(fixed_data['series']):
                if not isinstance(series_item, dict):
                    fixed_data['series'][i] = {"name": f"系列{i+1}", "data": [10, 20, 30]}
                else:
                    if 'name' not in series_item:
                        series_item['name'] = f"系列{i+1}"
                    if 'data' not in series_item:
                        series_item['data'] = [10, 20, 30]
                    elif not isinstance(series_item['data'], list):
                        series_item['data'] = [10, 20, 30]
        
        # 确保数据长度一致性
        if chart_type in ['line', 'bar'] and 'x_axis' in fixed_data and 'series' in fixed_data:
            x_length = len(fixed_data['x_axis'])
            for series_item in fixed_data['series']:
                if len(series_item['data']) != x_length:
                    if len(series_item['data']) > x_length:
                        series_item['data'] = series_item['data'][:x_length]
                    else:
                        # 补齐数据
                        series_item['data'].extend([0] * (x_length - len(series_item['data'])))
        
        # 雷达图特殊处理
        if chart_type == 'radar' and 'categories' in fixed_data and 'series' in fixed_data:
            categories_length = len(fixed_data['categories'])
            for series_item in fixed_data['series']:
                if len(series_item['data']) != categories_length:
                    if len(series_item['data']) > categories_length:
                        series_item['data'] = series_item['data'][:categories_length]
                    else:
                        # 补齐数据
                        series_item['data'].extend([50] * (categories_length - len(series_item['data'])))
        
        return fixed_data


def test_chart_validator():
    """测试图表数据验证器"""
    validator = ChartDataValidator()
    
    # 测试JSON修复
    broken_json = '{"title": "测试图表", "x_axis": ["A", "B", "C"], "series": [{"name": "系列1", "data": [1, 2, 3]}'
    result = validator.validate_and_fix_json(broken_json, 'line')
    print(f"JSON修复测试: {'成功' if result['success'] else '失败'}")
    if result['success']:
        print(f"修复后数据: {result['data']}")
    
    # 测试数据验证
    test_data = {
        "title": "测试图表",
        "x_axis": ["A", "B"],
        "series": [
            {"name": "系列1", "data": [1, 2, 3]}  # 数据长度不匹配
        ]
    }
    validation = validator.validate_chart_data(test_data, 'line')
    print(f"数据验证: {'通过' if validation['valid'] else '失败'}")
    print(f"警告: {validation['warnings']}")
    
    # 测试自动修复
    fixed_data = validator.auto_fix_chart_data(test_data, 'line')
    print(f"自动修复后数据: {fixed_data}")


if __name__ == "__main__":
    test_chart_validator()