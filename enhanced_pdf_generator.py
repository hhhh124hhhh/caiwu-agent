#!/usr/bin/env python3
"""
增强版PDF生成工具
集成所有PDF生成修复功能
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# 导入清理工具
from filename_sanitizer import FilenameSanitizer
from content_sanitizer import ContentSanitizer

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedPDFGenerator:
    """增强版PDF生成器"""
    
    def __init__(self, workspace_root: str = "./run_workdir"):
        self.workspace_root = workspace_root
        self.filename_sanitizer = FilenameSanitizer()
        self.content_sanitizer = ContentSanitizer()
        
        # 检查PDF支持
        self.pdf_support = self._check_pdf_support()
        
        if self.pdf_support:
            self._setup_pdf_fonts()
    
    def _check_pdf_support(self) -> bool:
        """检查PDF生成支持"""
        try:
            from fpdf import FPDF
            from fpdf.html import HTMLMixin
            return True
        except ImportError:
            logger.warning("PDF生成库未安装，PDF功能将不可用")
            return False
    
    def _setup_pdf_fonts(self):
        """设置PDF字体"""
        try:
            from fpdf import FPDF
            
            # 创建临时PDF对象来测试字体
            test_pdf = FPDF()
            test_pdf.add_page()
            test_pdf.set_font("Arial", size=12)
            test_pdf.cell(0, 10, "Font test")
            
            logger.info("PDF字体设置成功")
            return True
        except Exception as e:
            logger.warning(f"PDF字体设置失败: {e}")
            return False
    
    def generate_safe_pdf_report(self, 
                                content: str,
                                company_name: str = "财务分析报告",
                                report_type: str = "财务分析报告",
                                date_str: str = None,
                                output_dir: str = None,
                                chart_files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        生成安全的PDF报告
        
        Args:
            content: 报告内容
            company_name: 公司名称
            report_type: 报告类型
            date_str: 日期字符串
            output_dir: 输出目录
            chart_files: 图表文件列表
            
        Returns:
            生成结果字典
        """
        if not self.pdf_support:
            return {
                'success': False,
                'message': 'PDF生成功能不可用，请安装fpdf2库',
                'files': [],
                'error': 'PDF_NOT_SUPPORTED'
            }
        
        if output_dir is None:
            output_dir = self.workspace_root
        
        logger.info(f"开始生成PDF报告: {company_name}")
        
        try:
            # 第一步：清理内容
            logger.info("步骤1: 清理报告内容")
            clean_content = self.content_sanitizer.sanitize_text_for_pdf(content)
            
            # 第二步：生成安全文件名
            logger.info("步骤2: 生成安全文件名")
            if date_str is None:
                date_str = datetime.now().strftime("%Y%m%d")
            
            safe_filename = self.filename_sanitizer.create_safe_filename(
                company_name=company_name,
                report_type=report_type,
                date_str=date_str,
                extension="pdf"
            )
            
            file_path = os.path.join(output_dir, safe_filename)
            
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 第三步：生成PDF
            logger.info("步骤3: 生成PDF文件")
            result = self._create_pdf_file(clean_content, file_path, company_name, chart_files)
            
            if result['success']:
                logger.info(f"PDF生成成功: {file_path}")
                return {
                    'success': True,
                    'message': f'PDF报告已成功生成: {safe_filename}',
                    'file_path': file_path,
                    'filename': safe_filename,
                    'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                    'content_cleaned': True
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"PDF生成异常: {str(e)}")
            return {
                'success': False,
                'message': f'PDF生成异常: {str(e)}',
                'files': [],
                'error': 'GENERATION_ERROR'
            }
    
    def _create_pdf_file(self, content: str, file_path: str, 
                        company_name: str, chart_files: Optional[List[str]] = None) -> Dict[str, Any]:
        """创建PDF文件"""
        try:
            from fpdf import FPDF
            
            # 创建PDF对象
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # 设置字体
            try:
                pdf.set_font("Arial", size=12)
            except:
                # 如果Arial不可用，尝试其他字体
                pdf.set_font("Helvetica", size=12)
            
            # 添加标题
            pdf.set_font_size(16)
            pdf.set_text_color(0, 0, 139)  # 深蓝色
            pdf.cell(0, 15, f"{company_name} {company_name} Report", ln=True, align='C')
            pdf.ln(10)
            
            # 添加内容
            pdf.set_font_size(12)
            pdf.set_text_color(0, 0, 0)  # 黑色
            
            # 分段处理内容
            lines = content.split('\n')
            for line in lines:
                if line.strip():
                    # 处理长行，自动换行
                    if len(line) > 80:
                        words = line.split(' ')
                        current_line = ""
                        for word in words:
                            if len(current_line + word) < 80:
                                current_line += word + " "
                            else:
                                if current_line:
                                    pdf.cell(0, 8, current_line.strip(), ln=True)
                                current_line = word + " "
                        if current_line:
                            pdf.cell(0, 8, current_line.strip(), ln=True)
                    else:
                        pdf.cell(0, 8, line.strip(), ln=True)
                else:
                    pdf.ln(4)  # 空行
            
            # 添加图表（如果提供）
            if chart_files and isinstance(chart_files, list):
                for chart_file in chart_files:
                    if os.path.exists(chart_file):
                        try:
                            pdf.add_page()
                            pdf.set_y(20)
                            pdf.set_font_size(14)
                            pdf.set_text_color(0, 0, 139)
                            
                            # 清理图表文件名
                            chart_title = os.path.basename(chart_file)
                            chart_title = self.content_sanitizer.replace_emojis_with_text(chart_title)
                            pdf.cell(0, 15, f"Chart: {chart_title}", ln=True, align='C')
                            pdf.ln(10)
                            
                            pdf.set_font_size(12)
                            pdf.set_text_color(0, 0, 0)
                            
                            # 添加图片（如果存在且是图片文件）
                            if chart_file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                                try:
                                    pdf.image(chart_file, x=15, y=None, w=180)
                                except Exception as img_error:
                                    logger.warning(f"无法添加图片 {chart_file}: {img_error}")
                                    pdf.cell(0, 10, f"[Image: {chart_title}]", ln=True)
                            else:
                                pdf.cell(0, 10, f"[File: {chart_title}]", ln=True)
                                
                        except Exception as e:
                            logger.warning(f"处理图表文件 {chart_file} 时出错: {e}")
            
            # 保存PDF
            pdf.output(file_path)
            
            # 验证文件是否创建成功
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                return {
                    'success': True,
                    'message': 'PDF文件创建成功'
                }
            else:
                return {
                    'success': False,
                    'message': 'PDF文件创建失败'
                }
                
        except Exception as e:
            logger.error(f"创建PDF文件时出错: {str(e)}")
            return {
                'success': False,
                'message': f'创建PDF文件失败: {str(e)}'
            }
    
    def validate_pdf_generation_requirements(self, content: str, 
                                          company_name: str) -> Dict[str, Any]:
        """
        验证PDF生成要求
        
        Args:
            content: 报告内容
            company_name: 公司名称
            
        Returns:
            验证结果
        """
        result = {
            'can_generate': True,
            'issues': [],
            'recommendations': []
        }
        
        issues = []
        recommendations = []
        
        # 检查PDF支持
        if not self.pdf_support:
            result['can_generate'] = False
            issues.append("PDF生成库未安装")
            recommendations.append("安装fpdf2库: pip install fpdf2")
        
        # 检查内容
        if not content or len(content.strip()) < 10:
            issues.append("内容为空或过短")
            recommendations.append("提供有效的报告内容")
        
        # 检查内容中的问题字符
        content_validation = self.content_sanitizer.validate_content_for_pdf(content)
        if not content_validation['is_safe']:
            issues.extend(content_validation['issues'])
            recommendations.extend(content_validation['recommendations'])
        
        # 检查公司名称
        if not company_name or len(company_name.strip()) < 2:
            issues.append("公司名称为空或过短")
            recommendations.append("提供有效的公司名称")
        
        # 检查文件名安全性
        filename_validation = self.filename_sanitizer.validate_filename(company_name)
        if not filename_validation['is_safe']:
            issues.extend(filename_validation['issues'])
            if filename_validation['suggested_name']:
                recommendations.append(f"建议使用安全文件名: {filename_validation['suggested_name']}")
        
        result['issues'] = issues
        result['recommendations'] = recommendations
        
        return result
    
    def get_pdf_generation_status(self) -> Dict[str, Any]:
        """获取PDF生成状态信息"""
        return {
            'pdf_support': self.pdf_support,
            'workspace_root': self.workspace_root,
            'available_fonts': self.content_sanitizer.get_font_compatibility_info(),
            'features': {
                'filename_sanitization': True,
                'content_sanitization': True,
                'emoji_replacement': True,
                'character_encoding_fix': True,
                'chart_integration': True
            }
        }


def test_enhanced_pdf_generator():
    """测试增强版PDF生成器"""
    generator = EnhancedPDFGenerator("./test_pdfs")
    
    # 测试内容
    test_content = """
    # 财务分析报告 📊
    
    ## 公司基本信息
    公司名称：测试公司
    股票代码：600000.SH
    分析日期：2025年10月27日
    
    ## 财务指标 ⚠️
    - 营业收入：1000万元
    - 净利润：100万元
    - ROE：10%
    
    ## 投资建议 🎯
    基于财务分析，建议谨慎投资。
    
    ## 风险提示 ⚖️
    请注意市场风险。
    """
    
    print("PDF生成器测试:")
    print("=" * 60)
    
    # 检查PDF生成状态
    status = generator.get_pdf_generation_status()
    print(f"PDF支持: {status['pdf_support']}")
    print(f"工作目录: {status['workspace_root']}")
    print(f"功能特性: {list(status['features'].keys())}")
    
    # 验证生成要求
    validation = generator.validate_pdf_generation_requirements(test_content, "测试公司")
    print(f"可以生成: {validation['can_generate']}")
    if validation['issues']:
        print(f"问题: {validation['issues']}")
    if validation['recommendations']:
        print(f"建议: {validation['recommendations']}")
    
    # 尝试生成PDF
    if validation['can_generate']:
        print("\n开始生成PDF...")
        result = generator.generate_safe_pdf_report(
            content=test_content,
            company_name="测试公司",
            report_type="财务分析报告",
            date_str="20251027"
        )
        
        if result['success']:
            print(f"✅ PDF生成成功!")
            print(f"文件路径: {result['file_path']}")
            print(f"文件大小: {result['file_size']} bytes")
        else:
            print(f"❌ PDF生成失败: {result['message']}")
    else:
        print("❌ 无法生成PDF，存在未解决的问题")


if __name__ == "__main__":
    test_enhanced_pdf_generator()