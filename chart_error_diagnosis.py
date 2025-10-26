#!/usr/bin/env python3
"""
图表生成错误诊断工具
提供详细的错误分析和解决建议
"""

import json
import traceback
import sys
from typing import Dict, Any, List
from datetime import datetime

class ChartErrorDiagnosis:
    """图表生成错误诊断工具"""

    def __init__(self):
        self.error_patterns = {
            "json_syntax": {
                "keywords": ["JSONDecodeError", "Expecting", "delimiter", "Invalid"],
                "solutions": [
                    "检查JSON字符串的括号是否匹配",
                    "确保所有字符串使用双引号",
                    "检查是否有多余的逗号",
                    "使用JSON格式验证工具验证"
                ]
            },
            "missing_fields": {
                "keywords": ["缺少必要字段", "missing required fields", "title", "x_axis", "series"],
                "solutions": [
                    "确保数据包含 title（标题）字段",
                    "确保数据包含 x_axis（X轴标签）字段",
                    "确保数据包含 series（数据系列）字段",
                    "参考正确的数据格式示例"
                ]
            },
            "data_format": {
                "keywords": ["数据格式错误", "format error", "type", "list", "dict"],
                "solutions": [
                    "检查数据类型是否正确",
                    "确保 series 是数组格式",
                    "确保 data 是数组格式",
                    "验证数据结构的完整性"
                ]
            },
            "file_path": {
                "keywords": ["OSError", "Invalid argument", "No such file", "Permission denied"],
                "solutions": [
                    "检查文件路径是否正确",
                    "确保目录存在且有写入权限",
                    "避免使用特殊字符作为文件名",
                    "使用绝对路径或相对路径"
                ]
            },
            "matplotlib": {
                "keywords": ["matplotlib", "plt", "AttributeError", "ModuleNotFoundError"],
                "solutions": [
                    "确保已安装matplotlib: pip install matplotlib",
                    "检查代码中的变量名冲突",
                    "验证数据类型是否正确",
                    "查看详细的错误堆栈信息"
                ]
            }
        }

    def diagnose_error(self, error_message: str, error_traceback: str = None) -> Dict[str, Any]:
        """
        诊断错误并提供解决建议

        Args:
            error_message: 错误消息
            error_traceback: 错误堆栈信息

        Returns:
            诊断结果字典
        """
        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "error_message": error_message,
            "error_type": "unknown",
            "solutions": [],
            "confidence": 0.0,
            "related_files": [],
            "recommended_actions": []
        }

        # 分析错误类型
        error_lower = error_message.lower()
        matched_patterns = []

        for pattern_name, pattern_info in self.error_patterns.items():
            keywords = pattern_info["keywords"]
            match_count = sum(1 for keyword in keywords if keyword.lower() in error_lower)

            if match_count > 0:
                matched_patterns.append({
                    "type": pattern_name,
                    "match_count": match_count,
                    "solutions": pattern_info["solutions"]
                })

        # 确定最可能的错误类型
        if matched_patterns:
            best_match = max(matched_patterns, key=lambda x: x["match_count"])
            diagnosis["error_type"] = best_match["type"]
            diagnosis["solutions"] = best_match["solutions"]
            diagnosis["confidence"] = min(best_match["match_count"] * 0.2, 1.0)

        # 分析堆栈信息
        if error_traceback:
            diagnosis["traceback_analysis"] = self._analyze_traceback(error_traceback)

        # 生成推荐操作
        diagnosis["recommended_actions"] = self._generate_recommendations(diagnosis)

        return diagnosis

    def _analyze_traceback(self, traceback_str: str) -> Dict[str, Any]:
        """分析错误堆栈信息"""
        analysis = {
            "files_involved": [],
            "functions_involved": [],
            "error_line": None,
            "error_context": []
        }

        lines = traceback_str.split('\n')
        for line in lines:
            if 'File "' in line:
                # 提取文件路径
                start = line.find('File "')
                end = line.find('"', start + 6)
                if start > -1 and end > -1:
                    file_path = line[start + 6:end]
                    analysis["files_involved"].append(file_path)

            if line.strip().startswith('in '):
                # 提取函数名
                func_name = line.strip()[3:]
                if func_name:
                    analysis["functions_involved"].append(func_name)

            if 'Error:' in line or 'Exception:' in line:
                analysis["error_line"] = line.strip()

        return analysis

    def _generate_recommendations(self, diagnosis: Dict[str, Any]) -> List[str]:
        """生成推荐操作"""
        recommendations = []

        error_type = diagnosis["error_type"]
        solutions = diagnosis["solutions"]

        if error_type == "json_syntax":
            recommendations.extend([
                "1. 使用JSON验证工具检查格式: https://jsonlint.com/",
                "2. 确保所有字符串使用双引号，而不是单引号",
                "3. 检查括号、大括号、方括号是否匹配",
                "4. 移除多余的逗号"
            ])

        elif error_type == "missing_fields":
            recommendations.extend([
                "1. 参考以下标准格式:",
                "   {",
                '     "title": "图表标题",',
                '     "x_axis": ["标签1", "标签2"],',
                '     "series": [{"name": "系列1", "data": [1, 2]}]',
                "   }",
                "2. 确保所有必要字段都存在"
            ])

        elif error_type == "file_path":
            recommendations.extend([
                "1. 使用正斜杠(/)而不是反斜杠(\\)作为路径分隔符",
                "2. 避免在文件名中使用特殊字符: \\ / : * ? \" < > |",
                "3. 确保目录存在且有写入权限",
                "4. 使用os.path.exists()检查路径"
            ])

        elif error_type == "matplotlib":
            recommendations.extend([
                "1. 安装matplotlib: pip install matplotlib",
                "2. 检查代码中是否有变量名冲突",
                "3. 确保数据类型正确（数字使用列表）",
                "4. 添加plt.show()或plt.savefig()来保存图表"
            ])

        # 添加通用建议
        recommendations.extend([
            "5. 查看完整的错误堆栈信息以定位问题",
            "6. 使用print()语句在关键位置添加调试信息",
            "7. 尝试用最小化的数据重现问题"
        ])

        return recommendations

    def generate_fixed_data_format(self, original_data: Any) -> Dict[str, Any]:
        """尝试修复数据格式"""
        try:
            if isinstance(original_data, str):
                # 尝试解析JSON
                try:
                    data = json.loads(original_data)
                except json.JSONDecodeError:
                    return {"success": False, "message": "无法解析JSON数据"}
            else:
                data = original_data

            # 如果已经是字典，检查格式
            if isinstance(data, dict):
                return self._fix_dict_format(data)
            else:
                return {"success": False, "message": f"不支持的数据类型: {type(data)}"}

        except Exception as e:
            return {"success": False, "message": f"修复失败: {str(e)}"}

    def _fix_dict_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """修复字典格式"""
        fixed_data = {}

        # 必需字段
        if "title" not in data:
            fixed_data["title"] = "财务分析图表"

        if "series" not in data:
            if any(key in data for key in ["营业收入", "净利润", "revenue", "profit"]):
                # 看起来像是财务数据，尝试转换为series格式
                series_data = []
                for key, value in data.items():
                    if isinstance(value, list):
                        series_data.append({
                            "name": key,
                            "data": value
                        })
                if series_data:
                    fixed_data["series"] = series_data

        if "x_axis" not in data:
            # 尝试推断X轴标签
            if any(key in data for key in ["2024Q1", "2023", "2022"]):
                # 看起来像是季度或年度数据
                time_keys = [k for k in data.keys() if any(year in k for year in ["2024", "2023", "2022"])]
                if time_keys:
                    fixed_data["x_axis"] = time_keys

        # 保留原有数据
        for key, value in data.items():
            if key not in fixed_data:
                fixed_data[key] = value

        return {"success": True, "fixed_data": fixed_data}

def diagnose_chart_errors():
    """演示错误诊断功能"""
    print("图表生成错误诊断工具")
    print("=" * 50)

    diagnosis_tool = ChartErrorDiagnosis()

    # 示例错误
    test_errors = [
        {
            "name": "JSON语法错误",
            "error": "JSON解析错误: Expecting ',' delimiter: line 1 column 80 (char 79)"
        },
        {
            "name": "缺少字段错误",
            "error": "数据格式错误，缺少必要字段（title、x_axis、series）"
        },
        {
            "name": "文件路径错误",
            "error": "OSError: [Errno 22] Invalid argument: 'path/to/file with emoji.png'"
        },
        {
            "name": "Matplotlib错误",
            "error": "AttributeError: 'float' object has no attribute 'append'"
        }
    ]

    for i, test_error in enumerate(test_errors, 1):
        print(f"\n{i}. 诊断: {test_error['name']}")
        print(f"   错误信息: {test_error['error']}")

        diagnosis = diagnosis_tool.diagnose_error(test_error['error'])

        print(f"   错误类型: {diagnosis['error_type']}")
        print(f"   置信度: {diagnosis['confidence']:.2f}")
        print(f"   解决方案:")
        for j, solution in enumerate(diagnosis['solutions'], 1):
            print(f"     {j}. {solution}")

        print(f"   推荐操作:")
        for j, action in enumerate(diagnosis['recommended_actions'][:3], 1):  # 只显示前3个
            print(f"     {action}")

def test_data_format_fixing():
    """测试数据格式修复功能"""
    print("\n" + "=" * 50)
    print("数据格式修复测试")
    print("=" * 50)

    diagnosis_tool = ChartErrorDiagnosis()

    # 测试数据
    test_cases = [
        {
            "name": "缺少字段的JSON",
            "data": '{"series": [{"name": "revenue", "data": [100, 200]}]}'
        },
        {
            "name": "财务数据转series",
            "data": '{"2024Q1": 100, "2024Q2": 200, "2024Q3": 300}'
        },
        {
            "name": "完整格式",
            "data": '{"title": "测试图表", "x_axis": ["A", "B"], "series": [{"name": "test", "data": [1, 2]}]}'
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 测试: {test_case['name']}")
        result = diagnosis_tool.generate_fixed_data_format(test_case['data'])

        if result['success']:
            print(f"   ✅ 修复成功")
            fixed_data = result['fixed_data']
            print(f"   标题: {fixed_data.get('title', 'N/A')}")
            if 'series' in fixed_data:
                print(f"   数据系列: {len(fixed_data['series'])} 个")
        else:
            print(f"   ❌ 修复失败: {result['message']}")

def main():
    """主函数"""
    # 1. 演示错误诊断
    diagnose_chart_errors()

    # 2. 测试数据格式修复
    test_data_format_fixing()

    print("\n" + "=" * 50)
    print("📋 错误诊断和修复指南")
    print("=" * 50)
    print("""
常见图表生成问题及解决方案:

1. JSON格式错误
   - 使用在线JSON验证工具
   - 确保所有字符串使用双引号
   - 检查括号匹配

2. 数据字段缺失
   - 确保包含title、x_axis、series字段
   - 参考标准格式示例
   - 使用数据格式修复工具

3. 文件保存错误
   - 避免文件名中的特殊字符
   - 确保目录存在且有权限
   - 使用正斜杠作为路径分隔符

4. 代码执行错误
   - 检查变量名冲突
   - 验证数据类型
   - 添加错误处理和日志

如需更多帮助，请查看详细的诊断报告。
""")

if __name__ == "__main__":
    main()