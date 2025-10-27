#!/usr/bin/env python3
"""
文件名清理和标准化工具
解决PDF生成时文件名包含特殊字符的问题
"""

import re
import unicodedata
from typing import Optional

class FilenameSanitizer:
    """文件名清理器"""
    
    def __init__(self):
        # Windows文件系统不允许的字符
        self.windows_forbidden_chars = r'[<>:"/\\|?*]'
        
        # 需要移除的特殊字符（包括emoji）
        self.special_chars_pattern = r'[\x00-\x1f\x7f-\x9f]'  # 控制字符
        self.emoji_pattern = r'[\U00010000-\U0010FFFF]'     # emoji字符
        # 使用更简单的中文字符模式
        self.punctuation_pattern = r'[^\w\-_\.a-zA-Z0-9\u4e00-\u9fff]'  # 非字母数字、下划线、连字符、点、中文
        
        # 最大文件名长度
        self.max_filename_length = 200
        
    def create_safe_filename(self, company_name: str, report_type: str, date_str: str, 
                           extension: str = "pdf") -> str:
        """
        创建安全的文件名
        
        Args:
            company_name: 公司名称
            report_type: 报告类型
            date_str: 日期字符串
            extension: 文件扩展名
            
        Returns:
            清理后的安全文件名
        """
        # 清理各个组件
        clean_company = self.clean_text(company_name)
        clean_type = self.clean_text(report_type)
        clean_date = self.clean_text(date_str)
        
        # 构建文件名
        if clean_company and clean_type and clean_date:
            filename = f"{clean_company}_{clean_type}_{clean_date}.{extension}"
        elif clean_company and clean_type:
            filename = f"{clean_company}_{clean_type}.{extension}"
        elif clean_company:
            filename = f"{clean_company}_报告.{extension}"
        else:
            filename = f"财务分析报告_{clean_date}.{extension}"
        
        # 确保文件名长度不超过限制
        filename = self.truncate_filename(filename)
        
        return filename
    
    def clean_text(self, text: str) -> str:
        """
        清理文本，移除不安全字符
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        # 移除emoji字符
        text = re.sub(self.emoji_pattern, '', text)
        
        # 移除控制字符
        text = re.sub(self.special_chars_pattern, '', text)
        
        # 移除Windows不允许的字符
        text = re.sub(self.windows_forbidden_chars, '_', text)
        
        # 移除换行符、制表符等
        text = re.sub(r'[\n\r\t\s]+', '_', text)
        
        # 移除开头和结尾的特殊符号
        text = re.sub(r'^[##\s_]+', '', text)  # 移除开头的##、空格、下划线
        text = re.sub(r'[##\s_]+$', '', text)  # 移除结尾的##、空格、下划线
        
        # 标准化Unicode字符
        text = unicodedata.normalize('NFKC', text)
        
        # 移除除基本字符外的其他特殊字符
        text = re.sub(self.punctuation_pattern, '_', text)
        
        # 移除连续的下划线
        text = re.sub(r'_+', '_', text)
        
        # 移除开头和结尾的下划线
        text = text.strip('_')
        
        # 如果结果为空，返回默认值
        if not text or text.isspace():
            return "财务分析"
        
        return text
    
    def truncate_filename(self, filename: str) -> str:
        """
        截断文件名到安全长度
        
        Args:
            filename: 原始文件名
            
        Returns:
            截断后的文件名
        """
        if len(filename) <= self.max_filename_length:
            return filename
        
        # 分离文件名和扩展名
        name_part, dot, extension = filename.rpartition('.')
        
        if len(name_part) > self.max_filename_length - len(extension) - 1:
            # 截断名称部分
            max_name_length = self.max_filename_length - len(extension) - 1
            name_part = name_part[:max_name_length].rstrip('_')
            
        return f"{name_part}.{extension}"
    
    def clean_existing_filename(self, filename: str) -> str:
        """
        清理已存在的文件名
        
        Args:
            filename: 原始文件名
            
        Returns:
            清理后的文件名
        """
        # 提取扩展名
        name_part, dot, extension = filename.rpartition('.')
        
        # 清理名称部分
        clean_name = self.clean_text(name_part)
        
        # 如果清理后为空，使用默认名称
        if not clean_name:
            clean_name = "财务分析报告"
        
        # 重新组合文件名
        clean_filename = f"{clean_name}.{extension}" if extension else clean_name
        
        # 确保长度限制
        clean_filename = self.truncate_filename(clean_filename)
        
        return clean_filename
    
    def validate_filename(self, filename: str) -> dict:
        """
        验证文件名是否安全
        
        Args:
            filename: 要验证的文件名
            
        Returns:
            验证结果字典
        """
        result = {
            'is_safe': True,
            'issues': [],
            'suggested_name': None
        }
        
        issues = []
        
        # 检查长度
        if len(filename) > self.max_filename_length:
            issues.append(f"文件名过长 ({len(filename)} > {self.max_filename_length})")
            result['is_safe'] = False
        
        # 检查是否包含Windows禁止字符
        if re.search(self.windows_forbidden_chars, filename):
            issues.append("包含Windows不允许的字符")
            result['is_safe'] = False
        
        # 检查是否包含emoji
        if re.search(self.emoji_pattern, filename):
            issues.append("包含emoji字符")
            result['is_safe'] = False
        
        # 检查是否包含控制字符
        if re.search(self.special_chars_pattern, filename):
            issues.append("包含控制字符")
            result['is_safe'] = False
        
        # 检查是否以点或空格开头或结尾
        if filename.startswith('.') or filename.startswith(' ') or \
           filename.endswith('.') or filename.endswith(' '):
            issues.append("文件名以点或空格开头或结尾")
            result['is_safe'] = False
        
        # 如果有安全问题，提供建议的安全名称
        if not result['is_safe']:
            result['suggested_name'] = self.clean_existing_filename(filename)
        
        result['issues'] = issues
        return result
    
    def get_safe_filename_from_path(self, file_path: str) -> str:
        """
        从文件路径中提取并清理文件名
        
        Args:
            file_path: 文件路径
            
        Returns:
            安全的文件名
        """
        import os
        filename = os.path.basename(file_path)
        return self.clean_existing_filename(filename)


def test_filename_sanitizer():
    """测试文件名清理器"""
    sanitizer = FilenameSanitizer()
    
    # 测试用例
    test_cases = [
        # 用户遇到的具体问题
        ("## 📊 陕西建工多维度财务指标雷达图生成完成\n\n我已成功为陕西建工20251027财务分析报告.pdf", 
         "陕西建工多维度财务指标雷达图生成完成我已成功为陕西建工20251027财务分析报告.pdf"),
        
        # 其他测试用例
        ("测试公司_财务分析报告_20251027.pdf", "测试公司_财务分析报告_20251027.pdf"),
        ("公司📊报告.pdf", "公司报告.pdf"),
        ("公司<>报告.pdf", "公司_报告.pdf"),
        ("公司\n报告.pdf", "公司_报告.pdf"),
        ("", "财务分析报告.pdf"),
        ("   ", "财务分析报告.pdf"),
    ]
    
    print("文件名清理测试:")
    print("=" * 60)
    
    for i, (original, expected_pattern) in enumerate(test_cases, 1):
        print(f"\n测试案例 {i}:")
        print(f"原始: {original}")
        
        # 清理文件名
        cleaned = sanitizer.clean_existing_filename(original)
        print(f"清理后: {cleaned}")
        
        # 验证安全性
        validation = sanitizer.validate_filename(cleaned)
        print(f"安全性: {'安全' if validation['is_safe'] else '不安全'}")
        if validation['issues']:
            print(f"问题: {validation['issues']}")
        
        print("-" * 40)
    
    # 测试组件化文件名生成
    print("\n组件化文件名生成测试:")
    print("=" * 60)
    
    safe_filename = sanitizer.create_safe_filename(
        company_name="陕西建工",
        report_type="财务分析报告", 
        date_str="20251027",
        extension="pdf"
    )
    print(f"生成的安全文件名: {safe_filename}")


if __name__ == "__main__":
    test_filename_sanitizer()