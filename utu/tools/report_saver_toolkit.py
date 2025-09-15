"""
Report Saver Toolkit for saving AI analysis results to files
This is a standalone tool for saving various types of analysis reports
"""

import os
import json
import base64
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from ..config import ToolkitConfig
from .base import AsyncBaseToolkit, register_tool


class ReportSaverToolkit(AsyncBaseToolkit):
    """
    A standalone tool for saving AI analysis results to files
    Supports saving various formats including MD, HTML, JSON, etc.
    """

    def __init__(self, config: ToolkitConfig | dict | None = None):
        super().__init__(config)
        self.workspace_root = getattr(config, 'workspace_root', './run_workdir') if config else './run_workdir'

    @register_tool()
    async def save_analysis_report(self, 
                                 content: str,
                                 report_name: str = "analysis_report",
                                 file_format: str = "md",
                                 file_path: Optional[str] = None,
                                 workspace_dir: str = "./run_workdir") -> Dict[str, Any]:
        """
        Save AI analysis result to a file
        
        Args:
            content: The analysis content to save
            report_name: Name of the report (used for filename if file_path not provided)
            file_format: File format extension (md, html, txt, json, etc.)
            file_path: Complete file path (optional, if provided ignores report_name and file_format)
            workspace_dir: Workspace directory for saving files
            
        Returns:
            dict: Result information including success status and file path
        """
        try:
            # 如果没有提供完整文件路径，则根据报告名称和格式生成文件名
            if file_path is None:
                # 清理报告名称中的特殊字符，确保文件名合法
                safe_report_name = "".join(c for c in report_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                # 生成带日期的文件名
                current_date = datetime.now().strftime("%Y%m%d")
                file_name = f"{safe_report_name}{current_date}分析报告.{file_format}"
                file_path = os.path.join(workspace_dir, file_name)
            
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            # 保存到文件，确保正确处理换行符和特殊字符
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 验证文件是否保存成功
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                return {
                    "success": True,
                    "message": f"分析报告已成功保存到: {file_path}",
                    "file_path": file_path,
                    "file_size": file_size
                }
            else:
                return {
                    "success": False,
                    "message": "保存分析报告时出错: 文件未成功创建",
                    "file_path": None,
                    "file_size": 0
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"保存分析报告时出错: {str(e)}",
                "file_path": None,
                "file_size": 0
            }

    @register_tool()
    async def save_comparison_report(self,
                                   content: str,
                                   report_name: str = "comparison_report",
                                   file_format: str = "md",
                                   file_path: Optional[str] = None,
                                   workspace_dir: str = "./run_workdir") -> Dict[str, Any]:
        """
        Save comparison analysis result to a file
        
        Args:
            content: The comparison content to save
            report_name: Name of the report (used for filename if file_path not provided)
            file_format: File format extension (md, html, txt, json, etc.)
            file_path: Complete file path (optional, if provided ignores report_name and file_format)
            workspace_dir: Workspace directory for saving files
            
        Returns:
            dict: Result information including success status and file path
        """
        try:
            # 如果没有提供完整文件路径，则根据报告名称和格式生成文件名
            if file_path is None:
                # 清理报告名称中的特殊字符，确保文件名合法
                safe_report_name = "".join(c for c in report_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                # 生成带日期的文件名
                current_date = datetime.now().strftime("%Y%m%d")
                file_name = f"{safe_report_name}{current_date}对比分析报告.{file_format}"
                file_path = os.path.join(workspace_dir, file_name)
            
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            # 保存到文件，确保正确处理换行符和特殊字符
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 验证文件是否保存成功
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                return {
                    "success": True,
                    "message": f"对比分析报告已成功保存到: {file_path}",
                    "file_path": file_path,
                    "file_size": file_size
                }
            else:
                return {
                    "success": False,
                    "message": "保存对比分析报告时出错: 文件未成功创建",
                    "file_path": None,
                    "file_size": 0
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"保存对比分析报告时出错: {str(e)}",
                "file_path": None,
                "file_size": 0
            }

    @register_tool()
    async def save_json_report(self,
                             data: Dict[str, Any],
                             report_name: str = "json_report",
                             file_path: Optional[str] = None,
                             workspace_dir: str = "./run_workdir",
                             indent: int = 2) -> Dict[str, Any]:
        """
        Save structured data as JSON file
        
        Args:
            data: The data to save as JSON
            report_name: Name of the report (used for filename if file_path not provided)
            file_path: Complete file path (optional, if provided ignores report_name)
            workspace_dir: Workspace directory for saving files
            indent: JSON indentation level
            
        Returns:
            dict: Result information including success status and file path
        """
        try:
            # 如果没有提供完整文件路径，则根据报告名称生成文件名
            if file_path is None:
                # 清理报告名称中的特殊字符，确保文件名合法
                safe_report_name = "".join(c for c in report_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                # 生成带日期的文件名
                current_date = datetime.now().strftime("%Y%m%d")
                file_name = f"{safe_report_name}{current_date}数据报告.json"
                file_path = os.path.join(workspace_dir, file_name)
            
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            # 保存到JSON文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
            
            # 验证文件是否保存成功
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                return {
                    "success": True,
                    "message": f"JSON数据报告已成功保存到: {file_path}",
                    "file_path": file_path,
                    "file_size": file_size
                }
            else:
                return {
                    "success": False,
                    "message": "保存JSON数据报告时出错: 文件未成功创建",
                    "file_path": None,
                    "file_size": 0
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"保存JSON数据报告时出错: {str(e)}",
                "file_path": None,
                "file_size": 0
            }

    @register_tool()
    async def save_image_report(self,
                              image_data: str,
                              report_name: str = "image_report",
                              file_format: str = "png",
                              file_path: Optional[str] = None,
                              workspace_dir: str = "./run_workdir") -> Dict[str, Any]:
        """
        Save base64 encoded image to file
        
        Args:
            image_data: Base64 encoded image data
            report_name: Name of the report (used for filename if file_path not provided)
            file_format: Image format extension (png, jpg, svg, etc.)
            file_path: Complete file path (optional, if provided ignores report_name and file_format)
            workspace_dir: Workspace directory for saving files
            
        Returns:
            dict: Result information including success status and file path
        """
        try:
            # 如果没有提供完整文件路径，则根据报告名称和格式生成文件名
            if file_path is None:
                # 清理报告名称中的特殊字符，确保文件名合法
                safe_report_name = "".join(c for c in report_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                # 生成带日期的文件名
                current_date = datetime.now().strftime("%Y%m%d")
                file_name = f"{safe_report_name}{current_date}图表.{file_format}"
                file_path = os.path.join(workspace_dir, file_name)
            
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            # 解码base64数据并保存图像
            if image_data.startswith('data:image'):
                # 如果是data URL格式，提取base64部分
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            with open(file_path, 'wb') as f:
                f.write(image_bytes)
            
            # 验证文件是否保存成功
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                return {
                    "success": True,
                    "message": f"图像报告已成功保存到: {file_path}",
                    "file_path": file_path,
                    "file_size": file_size
                }
            else:
                return {
                    "success": False,
                    "message": "保存图像报告时出错: 文件未成功创建",
                    "file_path": None,
                    "file_size": 0
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"保存图像报告时出错: {str(e)}",
                "file_path": None,
                "file_size": 0
            }