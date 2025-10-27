#!/usr/bin/env python3
"""
内容清理工具
处理PDF生成中的emoji字符、特殊字符和字体问题
"""

import re
import unicodedata
from typing import Dict, Any, Optional

class ContentSanitizer:
    """内容清理器"""
    
    def __init__(self):
        # Emoji字符模式
        self.emoji_pattern = re.compile(r'[\U00010000-\U0010FFFF]')
        
        # 特殊符号模式
        self.special_symbols_pattern = re.compile(r'[^\w\s\u4e00-\u9fff.,!?;:()[\]{}"\'-]')
        
        # 控制字符模式
        self.control_chars_pattern = re.compile(r'[\x00-\x1f\x7f-\x9f]')
        
        # Emoji到文本的映射
        self.emoji_replacements = {
            '📊': '[图表]',
            '📈': '[上升]', 
            '📉': '[下降]',
            '⚠️': '[警告]',
            '⚙️': '[设置]',
            '⚖️': '[权衡]',
            '💰': '[资金]',
            '🏢': '[公司]',
            '🎯': '[目标]',
            '📋': '[列表]',
            '✅': '[完成]',
            '❌': '[失败]',
            '⭐': '[星级]',
            '🔍': '[搜索]',
            '💡': '[想法]',
            '🚀': '[增长]',
            '📱': '[手机]',
            '💻': '[电脑]',
            '🌐': '[网络]',
            '🏆': '[奖杯]',
            '📚': '[书籍]',
            '🛡️': '[保护]',
            '⚡': '[闪电]',
            '🔔': '[通知]',
            '📌': '[标记]',
            '🎨': '[设计]',
            '🔬': '[分析]',
            '💼': '[商务]',
            '🏗️': '[建筑]',
            '📊': '[数据]',
            '📐': '[测量]',
            '📝': '[笔记]',
            '🗂️': '[文件夹]',
            '📂': '[打开文件夹]',
            '🔄': '[循环]',
            '⚗️': '[建设]',
            '🖥️': '[显示器]'
        }
    
    def sanitize_text_for_pdf(self, text: str) -> str:
        """
        清理文本以适配PDF生成
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        # 第一步：替换emoji字符为文本
        text = self.replace_emojis_with_text(text)
        
        # 第二步：移除剩余的Unicode字符
        text = self.remove_problematic_unicode(text)
        
        # 第三步：移除控制字符
        text = self.remove_control_characters(text)
        
        # 第四步：标准化空白字符
        text = self.normalize_whitespace(text)
        
        # 第五步：修复特殊字符编码
        text = self.fix_character_encoding(text)
        
        return text
    
    def replace_emojis_with_text(self, text: str) -> str:
        """
        将emoji字符替换为文本描述
        
        Args:
            text: 包含emoji的文本
            
        Returns:
            替换后的文本
        """
        # 逐个替换已知的emoji
        for emoji_char, replacement in self.emoji_replacements.items():
            text = text.replace(emoji_char, replacement)
        
        # 移除剩余的未替换emoji
        text = self.emoji_pattern.sub('', text)
        
        return text
    
    def remove_problematic_unicode(self, text: str) -> str:
        """
        移除有问题的Unicode字符
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        # 移除特殊符号（保留基本标点）
        text = self.special_symbols_pattern.sub('', text)
        
        # 标准化Unicode字符
        text = unicodedata.normalize('NFKC', text)
        
        return text
    
    def remove_control_characters(self, text: str) -> str:
        """
        移除控制字符
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        return self.control_chars_pattern.sub('', text)
    
    def normalize_whitespace(self, text: str) -> str:
        """
        标准化空白字符
        
        Args:
            text: 原始文本
            
        Returns:
            标准化后的文本
        """
        # 将多个空格替换为单个空格
        text = re.sub(r'\s+', ' ', text)
        
        # 移除开头和结尾的空白
        text = text.strip()
        
        return text
    
    def fix_character_encoding(self, text: str) -> str:
        """
        修复字符编码问题
        
        Args:
            text: 原始文本
            
        Returns:
            修复后的文本
        """
        try:
            # 尝试编码和解码来修复编码问题
            text = text.encode('utf-8', errors='ignore').decode('utf-8')
        except:
            pass
        
        return text
    
    def clean_html_for_pdf(self, html_content: str) -> str:
        """
        清理HTML内容以适配PDF渲染
        
        Args:
            html_content: HTML内容
            
        Returns:
            清理后的HTML内容
        """
        if not html_content:
            return ""
        
        # 移除emoji字符
        html_content = self.replace_emojis_with_text(html_content)
        
        # 移除控制字符
        html_content = self.remove_control_characters(html_content)
        
        # 移除可能导致问题的CSS和JavaScript
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<link[^>]*>', '', html_content, flags=re.IGNORECASE)
        
        # 移除HTML注释
        html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
        
        # 简化HTML标签
        html_content = re.sub(r'<[^>]*>', lambda m: self.simplify_html_tag(m.group()), html_content)
        
        # 修复HTML结构
        if not html_content.strip().startswith('<!DOCTYPE') and not html_content.strip().startswith('<html'):
            html_content = f'<html><head><meta charset="UTF-8"></head><body>{html_content}</body></html>'
        
        return html_content
    
    def simplify_html_tag(self, tag: str) -> str:
        """
        简化HTML标签，移除可能导致问题的属性
        
        Args:
            tag: HTML标签
            
        Returns:
            简化后的标签
        """
        # 保留基本标签，移除复杂属性
        tag_name = re.match(r'<(\w+)', tag)
        if tag_name:
            name = tag_name.group(1)
            if name in ['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'em', 'br', 'hr']:
                return f'<{name}>'
            elif name in ['table', 'tr', 'td', 'th', 'thead', 'tbody']:
                return f'<{name}>'
        
        return ''
    
    def clean_markdown_for_pdf(self, markdown_content: str) -> str:
        """
        清理Markdown内容以适配PDF生成
        
        Args:
            markdown_content: Markdown内容
            
        Returns:
            清理后的Markdown内容
        """
        if not markdown_content:
            return ""
        
        # 移除emoji字符
        markdown_content = self.replace_emojis_with_text(markdown_content)
        
        # 移除控制字符
        markdown_content = self.remove_control_characters(markdown_content)
        
        # 简化Markdown语法
        markdown_content = re.sub(r'!\[.*?\]\(.*?\)', '[图片]', markdown_content)  # 图片
        markdown_content = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', markdown_content)  # 链接
        markdown_content = re.sub(r'```.*?```', '[代码块]', markdown_content, flags=re.DOTALL)  # 代码块
        markdown_content = re.sub(r'`([^`]+)`', r'\1', markdown_content)  # 内联代码
        
        return markdown_content
    
    def get_font_compatibility_info(self) -> Dict[str, Any]:
        """
        获取字体兼容性信息
        
        Returns:
            字体兼容性信息字典
        """
        return {
            'supported_fonts': [
                'SimHei',      # 黑体
                'SimSun',      # 宋体
                'SimKai',      # 楷体
                'Microsoft YaHei',  # 微软雅黑
                'Arial Unicode MS',
                'DejaVu Sans'
            ],
            'fallback_fonts': [
                'Arial',
                'Helvetica',
                'Times New Roman'
            ],
            'encoding_issues': [
                'Emoji characters need to be replaced',
                'Some Unicode symbols may not display correctly',
                'Control characters should be removed'
            ],
            'recommendations': [
                'Use the sanitize_text_for_pdf method for all text content',
                'Test PDF output with different fonts',
                'Check for character encoding issues'
            ]
        }
    
    def validate_content_for_pdf(self, content: str) -> Dict[str, Any]:
        """
        验证内容是否适合PDF生成
        
        Args:
            content: 要验证的内容
            
        Returns:
            验证结果字典
        """
        result = {
            'is_safe': True,
            'issues': [],
            'recommendations': [],
            'cleaned_content': None
        }
        
        issues = []
        recommendations = []
        
        # 检查emoji字符
        if self.emoji_pattern.search(content):
            issues.append("Contains emoji characters")
            recommendations.append("Replace emoji characters with text descriptions")
        
        # 检查控制字符
        if self.control_chars_pattern.search(content):
            issues.append("Contains control characters")
            recommendations.append("Remove control characters")
        
        # 检查特殊Unicode字符
        if self.special_symbols_pattern.search(content):
            issues.append("Contains problematic Unicode characters")
            recommendations.append("Use standard ASCII or Unicode characters")
        
        # 如果有问题，提供清理后的内容
        if issues:
            result['is_safe'] = False
            result['cleaned_content'] = self.sanitize_text_for_pdf(content)
        
        result['issues'] = issues
        result['recommendations'] = recommendations
        
        return result


def test_content_sanitizer():
    """测试内容清理器"""
    sanitizer = ContentSanitizer()
    
    # 测试用例
    test_cases = [
        # Emoji字符测试
        ("📊 财务分析报告 ⚠️ 风险提示", "[图表] 财务分析报告 [警告] 风险提示"),
        
        # 控制字符测试
        ("测试文本\n\r\t包含控制字符", "测试文本 包含控制字符"),
        
        # 特殊Unicode字符测试
        ("测试◆特殊★符号※内容", "测试特殊符号内容"),
        
        # 混合测试
        ("📈 收入增长📊 \n\t⚠️ 风险提示⚖️", "[上升] 收入增长[图表]  [警告] 风险提示[权衡]"),
    ]
    
    print("内容清理测试:")
    print("=" * 60)
    
    for i, (original, expected) in enumerate(test_cases, 1):
        print(f"\n测试案例 {i}:")
        print(f"原始: {repr(original)}")
        
        cleaned = sanitizer.sanitize_text_for_pdf(original)
        print(f"清理后: {repr(cleaned)}")
        
        # 验证清理效果
        validation = sanitizer.validate_content_for_pdf(original)
        print(f"安全性: {'安全' if validation['is_safe'] else '不安全'}")
        if validation['issues']:
            print(f"问题: {validation['issues']}")
        
        print("-" * 40)
    
    # 显示字体兼容性信息
    print("\n字体兼容性信息:")
    print("=" * 60)
    font_info = sanitizer.get_font_compatibility_info()
    print(f"支持的字体: {font_info['supported_fonts']}")
    print(f"后备字体: {font_info['fallback_fonts']}")
    print(f"编码问题: {font_info['encoding_issues']}")


if __name__ == "__main__":
    test_content_sanitizer()