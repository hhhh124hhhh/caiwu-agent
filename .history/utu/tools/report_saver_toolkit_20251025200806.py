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

# 添加PDF生成相关的导入
try:
    from fpdf import FPDF
    from fpdf.html import HTMLMixin
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("Warning: fpdf2 not installed. PDF report generation will not be available.")


class ReportSaverToolkit(AsyncBaseToolkit):
    """
    A standalone tool for saving AI analysis results to files
    Supports saving various formats including MD, HTML, JSON, etc.
    """

    def __init__(self, config: ToolkitConfig | dict | None = None):
        super().__init__(config)
        self.workspace_root = getattr(config, 'workspace_root', './stock_analysis_workspace') if config else './stock_analysis_workspace'

    def get_available_chinese_fonts(self):
        """跨平台中文字体检测"""
        font_candidates = []

        # Windows字体路径
        windows_fonts = [
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simkai.ttf",
            "C:/Windows/Fonts/msyhbd.ttc"
        ]

        # Linux字体路径
        linux_fonts = [
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/arphic/uming.ttc",
            "/usr/share/fonts/truetype/arphic/ukai.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ]

        # macOS字体路径
        mac_fonts = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/Library/Fonts/Arial Unicode.ttf"
        ]

        # 检查字体文件是否存在
        all_fonts = windows_fonts + linux_fonts + mac_fonts
        for font_path in all_fonts:
            if os.path.exists(font_path):
                font_candidates.append(font_path)

        return font_candidates

    def setup_pdf_font(self, pdf):
        """为PDF设置中文字体支持"""
        available_fonts = self.get_available_chinese_fonts()

        if available_fonts:
            try:
                # 尝试使用第一个可用字体
                font_path = available_fonts[0]
                font_name = "ChineseFont"

                # 添加字体到PDF
                pdf.add_font(font_name, "", font_path, uni=True)
                pdf.set_font(font_name, size=12)
                print(f"使用中文字体: {font_path}")
                return True
            except Exception as e:
                print(f"Warning: 字体加载失败 {font_path}: {e}")
                try:
                    # 尝试下一个可用字体
                    for font_path in available_fonts[1:]:
                        try:
                            pdf.add_font("ChineseFont", "", font_path, uni=True)
                            pdf.set_font("ChineseFont", size=12)
                            print(f"使用备用中文字体: {font_path}")
                            return True
                        except Exception:
                            continue
                except Exception:
                    pass

        # 降级方案：使用系统默认字体
        try:
            pdf.set_font("Arial", size=12)
            print("Warning: 未找到中文字体，使用Arial字体（可能无法显示中文）")
            return False
        except Exception as e:
            print(f"Error: 字体设置完全失败: {e}")
            return False

    def _format_financial_data_as_markdown(self, financial_data_json: str) -> str:
        """
        将财务数据格式化为Markdown报告
        
        Args:
            financial_data_json: 包含财务数据的JSON字符串
            
        Returns:
            str: 格式化后的Markdown报告内容
        """
        try:
            # 解析JSON数据
            if isinstance(financial_data_json, str):
                data = json.loads(financial_data_json)
            else:
                data = financial_data_json
            
            # 检查是否是行业分析数据结构
            if "医药行业分析" in data:
                return self._format_industry_analysis_as_markdown(data)
            
            # 获取基本信息 - 支持多种可能的键名
            company_name = (data.get("company_name") or 
                          data.get("公司名称") or 
                          data.get("stock_name") or 
                          data.get("股票名称") or 
                          "未知公司")
            
            stock_code = (data.get("stock_code") or 
                         data.get("股票代码") or 
                         "未知代码")
            
            # 生成报告标题和基本信息
            report_content = []
            report_content.append(f"# {company_name} 财务分析报告")
            report_content.append("=" * (len(company_name) + 12))
            report_content.append(f"**股票代码**: {stock_code}")
            report_content.append(f"**报告日期**: {datetime.now().strftime('%Y-%m-%d')}")
            report_content.append("")
            
            # 处理财务数据 - 支持多种数据结构
            # 检查是否有嵌套的income, balance, metrics结构
            if "income" in data or "balance" in data or "metrics" in data:
                # 处理嵌套结构
                income_data = data.get("income", {})
                balance_data = data.get("balance", {})
                metrics_data = data.get("metrics", {})
                cashflow_data = data.get("cashflow", {})
                
                # 合并所有数据到一个字典中以便处理
                financial_data = {}
                financial_data.update(income_data)
                financial_data.update(balance_data)
                financial_data.update(metrics_data)
                financial_data.update(cashflow_data)
            else:
                # 处理扁平化结构
                financial_data = data.get("financial_data") or data.get("财务数据") or data
            
            # 如果financial_data是字典，提取关键财务指标
            if isinstance(financial_data, dict):
                # 处理简化指标结构
                revenue = (financial_data.get("revenue_billion") or 
                          financial_data.get("营业收入") or 
                          financial_data.get("revenue") or 
                          0)
                
                net_profit = (financial_data.get("net_profit_billion") or 
                             financial_data.get("净利润") or 
                             financial_data.get("net_profit") or 
                             0)
                
                parent_profit = (financial_data.get("parent_profit_billion") or 
                               financial_data.get("归属于母公司净利润") or 
                               financial_data.get("parent_net_profit") or 
                               0)
                
                total_assets = (financial_data.get("total_assets_billion") or 
                               financial_data.get("总资产") or 
                               financial_data.get("total_assets") or 
                               0)
                
                total_liabilities = (financial_data.get("total_liabilities_billion") or 
                                   financial_data.get("总负债") or 
                                   financial_data.get("total_liabilities") or 
                                   0)
                
                total_equity = (financial_data.get("total_equity_billion") or 
                               financial_data.get("股东权益") or 
                               financial_data.get("total_equity") or 
                               0)
                
                debt_ratio = (financial_data.get("debt_to_asset_ratio") or 
                             financial_data.get("资产负债率") or 
                             financial_data.get("debt_ratio") or 
                             0)
                
                roe = (financial_data.get("roe") or 
                      financial_data.get("净资产收益率") or 
                      0)
                
                net_margin = (financial_data.get("net_profit_margin") or 
                             financial_data.get("净利率") or 
                             financial_data.get("net_margin") or 
                             0)
                
                # 计算额外的财务比率
                roa = 0
                current_ratio = 0
                quick_ratio = 0
                asset_turnover = 0
                
                if total_assets and isinstance(total_assets, (int, float)) and total_assets > 0:
                    if net_profit and isinstance(net_profit, (int, float)):
                        roa = (net_profit / total_assets) * 100
                    
                    # 计算总资产周转率
                    if revenue and isinstance(revenue, (int, float)):
                        asset_turnover = revenue / total_assets
                
                if total_equity and isinstance(total_equity, (int, float)) and total_equity > 0:
                    pass  # 已经有roe了，不需要重新计算
                
                if total_liabilities and isinstance(total_liabilities, (int, float)) and total_liabilities > 0:
                    pass  # 流动比率和速动比率需要更多数据，这里暂时不计算
                
                # 创建财务数据概览
                report_content.append("## 财务数据概览")
                report_content.append("")
                report_content.append(f"- **营业收入**: {revenue:,.2f} 亿元" if isinstance(revenue, (int, float)) else f"- **营业收入**: {revenue}")
                report_content.append(f"- **净利润**: {net_profit:,.2f} 亿元" if isinstance(net_profit, (int, float)) else f"- **净利润**: {net_profit}")
                report_content.append(f"- **归属于母公司净利润**: {parent_profit:,.2f} 亿元" if isinstance(parent_profit, (int, float)) else f"- **归属于母公司净利润**: {parent_profit}")
                report_content.append(f"- **总资产**: {total_assets:,.2f} 亿元" if isinstance(total_assets, (int, float)) else f"- **总资产**: {total_assets}")
                report_content.append(f"- **总负债**: {total_liabilities:,.2f} 亿元" if isinstance(total_liabilities, (int, float)) else f"- **总负债**: {total_liabilities}")
                report_content.append(f"- **股东权益**: {total_equity:,.2f} 亿元" if isinstance(total_equity, (int, float)) else f"- **股东权益**: {total_equity}")
                report_content.append(f"- **资产负债率**: {debt_ratio:.2f}%" if isinstance(debt_ratio, (int, float)) else f"- **资产负债率**: {debt_ratio}")
                report_content.append(f"- **净资产收益率**: {roe:.2f}%" if isinstance(roe, (int, float)) else f"- **净资产收益率**: {roe}")
                report_content.append(f"- **净利率**: {net_margin:.2f}%" if isinstance(net_margin, (int, float)) else f"- **净利率**: {net_margin}")
                report_content.append(f"- **总资产收益率**: {roa:.2f}%" if isinstance(roa, (int, float)) and roa != 0 else "")
                report_content.append("")
                
                # 添加财务比率分析
                report_content.append("## 财务比率分析")
                report_content.append("")
                
                # 盈利能力分析
                report_content.append("### 盈利能力分析")
                report_content.append(f"- 净利率: {net_margin:.2f}%" if isinstance(net_margin, (int, float)) else "N/A")
                report_content.append(f"- 净资产收益率(ROE): {roe:.2f}%" if isinstance(roe, (int, float)) else "N/A")
                report_content.append(f"- 总资产收益率(ROA): {roa:.2f}%" if isinstance(roa, (int, float)) and roa != 0 else "N/A")
                report_content.append("")
                
                # 偿债能力分析
                report_content.append("### 偿债能力分析")
                report_content.append(f"- 资产负债率: {debt_ratio:.2f}%" if isinstance(debt_ratio, (int, float)) else "N/A")
                # 可以添加流动比率、速动比率等
                report_content.append("")
                
                # 运营效率分析
                report_content.append("### 运营效率分析")
                report_content.append(f"- 总资产周转率: {asset_turnover:.2f}" if isinstance(asset_turnover, (int, float)) and asset_turnover != 0 else "N/A")
                report_content.append("")
                
                # 成长能力分析
                report_content.append("### 成长能力分析")
                # 这里可以添加收入增长率、利润增长率等
                report_content.append("N/A")
                report_content.append("")
            
            # 处理趋势数据
            trend_data = data.get("trend_data") or data.get("趋势数据") or []
            
            if trend_data and isinstance(trend_data, list):
                report_content.append("## 财务趋势分析")
                report_content.append("")
                report_content.append("| 年份 | 营业收入(亿元) | 净利润(亿元) |")
                report_content.append("|------|---------------|-------------|")
                
                for item in trend_data:
                    if isinstance(item, dict):
                        year = item.get("year") or item.get("年份") or ""
                        revenue = item.get("revenue") or item.get("营业收入") or 0
                        net_profit = item.get("net_profit") or item.get("净利润") or 0
                        
                        # 格式化数值
                        revenue_str = f"{revenue:,.2f}" if isinstance(revenue, (int, float)) else str(revenue)
                        net_profit_str = f"{net_profit:,.2f}" if isinstance(net_profit, (int, float)) else str(net_profit)
                        
                        report_content.append(f"| {year} | {revenue_str} | {net_profit_str} |")
                report_content.append("")
            
            # 处理关键洞察
            key_insights = (data.get("key_insights") or 
                           data.get("关键洞察") or 
                           data.get("关键发现") or 
                           data.get("insights") or
                           [])
            
            if key_insights and isinstance(key_insights, list) and len(key_insights) > 0:
                report_content.append("## 关键洞察")
                report_content.append("")
                for i, insight in enumerate(key_insights, 1):
                    report_content.append(f"{i}. {insight}")
                report_content.append("")
            
            # 添加投资建议（如果有的话）
            investment_advice = (data.get("investment_advice") or 
                               data.get("投资建议") or 
                               data.get("建议") or 
                               [])
            
            if investment_advice and isinstance(investment_advice, list) and len(investment_advice) > 0:
                report_content.append("## 投资建议")
                report_content.append("")
                for i, advice in enumerate(investment_advice, 1):
                    report_content.append(f"{i}. {advice}")
                report_content.append("")
            elif investment_advice and isinstance(investment_advice, str):
                report_content.append("## 投资建议")
                report_content.append("")
                report_content.append(investment_advice)
                report_content.append("")
            
            # 添加风险提示（如果有的话）
            risks = (data.get("risks") or 
                    data.get("风险提示") or 
                    data.get("风险") or 
                    [])
            
            if risks and isinstance(risks, list) and len(risks) > 0:
                report_content.append("## 风险提示")
                report_content.append("")
                for i, risk in enumerate(risks, 1):
                    report_content.append(f"{i}. {risk}")
                report_content.append("")
            elif risks and isinstance(risks, str):
                report_content.append("## 风险提示")
                report_content.append("")
                report_content.append(risks)
                report_content.append("")
            
            # 添加执行摘要
            executive_summary = (data.get("executive_summary") or 
                               data.get("执行摘要") or 
                               data.get("摘要") or 
                               "")
            
            if executive_summary:
                report_content.append("## 执行摘要")
                report_content.append("")
                if isinstance(executive_summary, list):
                    for item in executive_summary:
                        report_content.append(f"- {item}")
                else:
                    report_content.append(executive_summary)
                report_content.append("")
            
            return "\n".join(report_content)
        except Exception as e:
            # 如果解析失败，返回格式化的错误信息和原始数据
            error_info = f"# 财务分析报告\n\n## 原始数据\n\n```\n{financial_data_json}\n```\n\n## 错误信息\n\n{str(e)}"
            return error_info

    def _format_industry_analysis_as_markdown(self, data: dict) -> str:
        """
        将行业分析数据格式化为Markdown报告
        
        Args:
            data: 包含行业分析数据的字典
            
        Returns:
            str: 格式化后的Markdown报告内容
        """
        try:
            # 获取行业分析数据
            industry_data = data.get("医药行业分析", {})
            key_findings = data.get("关键发现", {})
            
            # 获取基本信息
            analysis_time = industry_data.get("分析时间", "未知时间")
            company_count = industry_data.get("分析公司数量", 0)
            companies = industry_data.get("公司明细", [])
            
            # 生成报告标题和基本信息
            report_content = []
            report_content.append("# 医药行业财务分析报告")
            report_content.append("=" * 18)
            report_content.append(f"**分析时间**: {analysis_time}")
            report_content.append(f"**分析公司数量**: {company_count}")
            report_content.append(f"**报告日期**: {datetime.now().strftime('%Y-%m-%d')}")
            report_content.append("")
            
            # 添加公司明细表
            if companies and isinstance(companies, list):
                report_content.append("## 公司明细")
                report_content.append("")
                report_content.append("| 公司名称 | 股票代码 | 营收(亿元) | 净利润(亿元) | 净利润率(%) | ROE(%) | 资产负债率(%) | 行业分类 |")
                report_content.append("|---------|---------|----------|------------|------------|--------|-------------|---------|")
                
                for company in companies:
                    if isinstance(company, dict):
                        name = company.get("名称", "")
                        code = company.get("股票代码", "")
                        revenue = company.get("营收(亿元)", 0)
                        net_profit = company.get("净利润(亿元)", 0)
                        net_profit_margin = company.get("净利润率", 0)
                        roe = company.get("ROE", 0)
                        debt_ratio = company.get("资产负债率", 0)
                        category = company.get("行业分类", "")
                        
                        # 格式化数值
                        revenue_str = f"{revenue:.2f}" if isinstance(revenue, (int, float)) else str(revenue)
                        net_profit_str = f"{net_profit:.2f}" if isinstance(net_profit, (int, float)) else str(net_profit)
                        net_profit_margin_str = f"{net_profit_margin:.2f}" if isinstance(net_profit_margin, (int, float)) else str(net_profit_margin)
                        roe_str = f"{roe:.2f}" if isinstance(roe, (int, float)) else str(roe)
                        debt_ratio_str = f"{debt_ratio:.2f}" if isinstance(debt_ratio, (int, float)) else str(debt_ratio)
                        
                        report_content.append(f"| {name} | {code} | {revenue_str} | {net_profit_str} | {net_profit_margin_str} | {roe_str} | {debt_ratio_str} | {category} |")
                report_content.append("")
            
            # 添加关键发现
            if key_findings and isinstance(key_findings, dict):
                report_content.append("## 关键发现")
                report_content.append("")
                for key, value in key_findings.items():
                    # 将键名转换为更易读的中文
                    readable_key = self._translate_key_findings_key(key)
                    report_content.append(f"- **{readable_key}**: {value}")
                report_content.append("")
            
            return "\n".join(report_content)
        except Exception as e:
            # 如果解析失败，返回错误信息
            return f"# 行业分析报告格式化错误\n\n{str(e)}"

    def _translate_key_findings_key(self, key: str) -> str:
        """
        将关键发现的键名翻译为更易读的中文
        """
        translations = {
            "利润率超过10%的公司数量": "利润率超过10%的公司数量",
            "平均净利润率": "平均净利润率",
            "最高利润率": "最高利润率",
            "最低利润率": "最低利润率",
            "行业特点": "行业特点"
        }
        return translations.get(key, key)

    def _format_financial_data_as_pdf_content(self, financial_data_json: str) -> str:
        """
        将财务数据格式化为PDF报告内容（纯文本格式）
        
        Args:
            financial_data_json: 包含财务数据的JSON字符串
            
        Returns:
            str: 格式化后的PDF报告内容
        """
        try:
            # 解析JSON数据
            if isinstance(financial_data_json, str):
                data = json.loads(financial_data_json)
            else:
                data = financial_data_json
            
            # 检查是否是行业分析数据结构
            if "医药行业分析" in data:
                return self._format_industry_analysis_as_pdf_content(data)
            
            # 获取基本信息 - 支持多种可能的键名
            company_name = (data.get("company_name") or 
                          data.get("公司名称") or 
                          data.get("stock_name") or 
                          data.get("股票名称") or 
                          "未知公司")
            
            stock_code = (data.get("stock_code") or 
                         data.get("股票代码") or 
                         "未知代码")
            
            # 生成报告标题和基本信息
            report_content = []
            report_content.append(f"{company_name} 财务分析报告")
            report_content.append("=" * (len(company_name) + 12))
            report_content.append(f"股票代码: {stock_code}")
            report_content.append(f"报告日期: {datetime.now().strftime('%Y-%m-%d')}")
            report_content.append("")
            
            # 处理财务数据 - 支持多种数据结构
            # 检查是否有嵌套的income, balance, metrics结构
            if "income" in data or "balance" in data or "metrics" in data:
                # 处理嵌套结构
                income_data = data.get("income", {})
                balance_data = data.get("balance", {})
                metrics_data = data.get("metrics", {})
                cashflow_data = data.get("cashflow", {})
                
                # 合并所有数据到一个字典中以便处理
                financial_data = {}
                financial_data.update(income_data)
                financial_data.update(balance_data)
                financial_data.update(metrics_data)
                financial_data.update(cashflow_data)
            else:
                # 处理扁平化结构
                financial_data = data.get("financial_data") or data.get("财务数据") or data
            
            # 如果financial_data是字典，提取关键财务指标
            if isinstance(financial_data, dict):
                # 处理简化指标结构
                revenue = (financial_data.get("revenue_billion") or 
                          financial_data.get("营业收入") or 
                          financial_data.get("revenue") or 
                          0)
                
                net_profit = (financial_data.get("net_profit_billion") or 
                             financial_data.get("净利润") or 
                             financial_data.get("net_profit") or 
                             0)
                
                parent_profit = (financial_data.get("parent_profit_billion") or 
                               financial_data.get("归属于母公司净利润") or 
                               financial_data.get("parent_net_profit") or 
                               0)
                
                total_assets = (financial_data.get("total_assets_billion") or 
                               financial_data.get("总资产") or 
                               financial_data.get("total_assets") or 
                               0)
                
                total_liabilities = (financial_data.get("total_liabilities_billion") or 
                                   financial_data.get("总负债") or 
                                   financial_data.get("total_liabilities") or 
                                   0)
                
                total_equity = (financial_data.get("total_equity_billion") or 
                               financial_data.get("股东权益") or 
                               financial_data.get("total_equity") or 
                               0)
                
                debt_ratio = (financial_data.get("debt_to_asset_ratio") or 
                             financial_data.get("资产负债率") or 
                             financial_data.get("debt_ratio") or 
                             0)
                
                roe = (financial_data.get("roe") or 
                      financial_data.get("净资产收益率") or 
                      0)
                
                net_margin = (financial_data.get("net_profit_margin") or 
                             financial_data.get("净利率") or 
                             financial_data.get("net_margin") or 
                             0)
                
                # 计算额外的财务比率
                roa = 0
                current_ratio = 0
                quick_ratio = 0
                asset_turnover = 0
                
                if total_assets and isinstance(total_assets, (int, float)) and total_assets > 0:
                    if net_profit and isinstance(net_profit, (int, float)):
                        roa = (net_profit / total_assets) * 100
                    
                    # 计算总资产周转率
                    if revenue and isinstance(revenue, (int, float)):
                        asset_turnover = revenue / total_assets
                
                if total_equity and isinstance(total_equity, (int, float)) and total_equity > 0:
                    pass  # 已经有roe了，不需要重新计算
                
                if total_liabilities and isinstance(total_liabilities, (int, float)) and total_liabilities > 0:
                    pass  # 流动比率和速动比率需要更多数据，这里暂时不计算
                
                # 创建财务数据概览
                report_content.append("财务数据概览")
                report_content.append("")
                report_content.append(f"营业收入: {revenue:,.2f} 亿元" if isinstance(revenue, (int, float)) else f"营业收入: {revenue}")
                report_content.append(f"净利润: {net_profit:,.2f} 亿元" if isinstance(net_profit, (int, float)) else f"净利润: {net_profit}")
                report_content.append(f"归属于母公司净利润: {parent_profit:,.2f} 亿元" if isinstance(parent_profit, (int, float)) else f"归属于母公司净利润: {parent_profit}")
                report_content.append(f"总资产: {total_assets:,.2f} 亿元" if isinstance(total_assets, (int, float)) else f"总资产: {total_assets}")
                report_content.append(f"总负债: {total_liabilities:,.2f} 亿元" if isinstance(total_liabilities, (int, float)) else f"总负债: {total_liabilities}")
                report_content.append(f"股东权益: {total_equity:,.2f} 亿元" if isinstance(total_equity, (int, float)) else f"股东权益: {total_equity}")
                report_content.append(f"资产负债率: {debt_ratio:.2f}%" if isinstance(debt_ratio, (int, float)) else f"资产负债率: {debt_ratio}")
                report_content.append(f"净资产收益率: {roe:.2f}%" if isinstance(roe, (int, float)) else f"净资产收益率: {roe}")
                report_content.append(f"净利率: {net_margin:.2f}%" if isinstance(net_margin, (int, float)) else f"净利率: {net_margin}")
                report_content.append(f"总资产收益率: {roa:.2f}%" if isinstance(roa, (int, float)) and roa != 0 else "")
                report_content.append("")
                
                # 添加财务比率分析
                report_content.append("财务比率分析")
                report_content.append("")
                
                # 盈利能力分析
                report_content.append("盈利能力分析")
                report_content.append(f"净利率: {net_margin:.2f}%" if isinstance(net_margin, (int, float)) else "N/A")
                report_content.append(f"净资产收益率(ROE): {roe:.2f}%" if isinstance(roe, (int, float)) else "N/A")
                report_content.append(f"总资产收益率(ROA): {roa:.2f}%" if isinstance(roa, (int, float)) and roa != 0 else "N/A")
                report_content.append("")
                
                # 偿债能力分析
                report_content.append("偿债能力分析")
                report_content.append(f"资产负债率: {debt_ratio:.2f}%" if isinstance(debt_ratio, (int, float)) else "N/A")
                # 可以添加流动比率、速动比率等
                report_content.append("")
                
                # 运营效率分析
                report_content.append("运营效率分析")
                report_content.append(f"总资产周转率: {asset_turnover:.2f}" if isinstance(asset_turnover, (int, float)) and asset_turnover != 0 else "N/A")
                report_content.append("")
                
                # 成长能力分析
                report_content.append("成长能力分析")
                # 这里可以添加收入增长率、利润增长率等
                report_content.append("N/A")
                report_content.append("")
            
            # 处理趋势数据
            trend_data = data.get("trend_data") or data.get("趋势数据") or []
            
            if trend_data and isinstance(trend_data, list):
                report_content.append("财务趋势分析")
                report_content.append("")
                report_content.append("年份    营业收入(亿元)    净利润(亿元)")
                report_content.append("----    --------------    ------------")
                
                for item in trend_data:
                    if isinstance(item, dict):
                        year = item.get("year") or item.get("年份") or ""
                        revenue = item.get("revenue") or item.get("营业收入") or 0
                        net_profit = item.get("net_profit") or item.get("净利润") or 0
                        
                        # 格式化数值
                        revenue_str = f"{revenue:,.2f}" if isinstance(revenue, (int, float)) else str(revenue)
                        net_profit_str = f"{net_profit:,.2f}" if isinstance(net_profit, (int, float)) else str(net_profit)
                        
                        report_content.append(f"{year}    {revenue_str:>14}    {net_profit_str:>12}")
                report_content.append("")
            
            # 处理关键洞察
            key_insights = (data.get("key_insights") or 
                           data.get("关键洞察") or 
                           data.get("关键发现") or 
                           data.get("insights") or
                           [])
            
            if key_insights and isinstance(key_insights, list) and len(key_insights) > 0:
                report_content.append("关键洞察")
                report_content.append("")
                for i, insight in enumerate(key_insights, 1):
                    report_content.append(f"{i}. {insight}")
                report_content.append("")
            
            # 添加投资建议（如果有的话）
            investment_advice = (data.get("investment_advice") or 
                               data.get("投资建议") or 
                               data.get("建议") or 
                               [])
            
            if investment_advice and isinstance(investment_advice, list) and len(investment_advice) > 0:
                report_content.append("投资建议")
                report_content.append("")
                for i, advice in enumerate(investment_advice, 1):
                    report_content.append(f"{i}. {advice}")
                report_content.append("")
            elif investment_advice and isinstance(investment_advice, str):
                report_content.append("投资建议")
                report_content.append("")
                report_content.append(investment_advice)
                report_content.append("")
            
            # 添加风险提示（如果有的话）
            risks = (data.get("risks") or 
                    data.get("风险提示") or 
                    data.get("风险") or 
                    [])
            
            if risks and isinstance(risks, list) and len(risks) > 0:
                report_content.append("风险提示")
                report_content.append("")
                for i, risk in enumerate(risks, 1):
                    report_content.append(f"{i}. {risk}")
                report_content.append("")
            elif risks and isinstance(risks, str):
                report_content.append("风险提示")
                report_content.append("")
                report_content.append(risks)
                report_content.append("")
            
            # 添加执行摘要
            executive_summary = (data.get("executive_summary") or 
                               data.get("执行摘要") or 
                               data.get("摘要") or 
                               "")
            
            if executive_summary:
                report_content.append("执行摘要")
                report_content.append("")
                if isinstance(executive_summary, list):
                    for item in executive_summary:
                        report_content.append(f"- {item}")
                else:
                    report_content.append(executive_summary)
                report_content.append("")
            
            return "\n".join(report_content)
        except Exception as e:
            # 如果解析失败，返回格式化的错误信息和原始数据
            error_info = f"财务分析报告\n\n原始数据\n\n{financial_data_json}\n\n错误信息\n\n{str(e)}"
            return error_info

    def _format_industry_analysis_as_pdf_content(self, data: dict) -> str:
        """
        将行业分析数据格式化为PDF报告内容（纯文本格式）
        
        Args:
            data: 包含行业分析数据的字典
            
        Returns:
            str: 格式化后的PDF报告内容
        """
        try:
            # 获取行业分析数据
            industry_data = data.get("医药行业分析", {})
            key_findings = data.get("关键发现", {})
            
            # 获取基本信息
            analysis_time = industry_data.get("分析时间", "未知时间")
            company_count = industry_data.get("分析公司数量", 0)
            companies = industry_data.get("公司明细", [])
            
            # 生成报告标题和基本信息
            report_content = []
            report_content.append("医药行业财务分析报告")
            report_content.append("=" * 18)
            report_content.append(f"分析时间: {analysis_time}")
            report_content.append(f"分析公司数量: {company_count}")
            report_content.append(f"报告日期: {datetime.now().strftime('%Y-%m-%d')}")
            report_content.append("")
            
            # 添加公司明细表
            if companies and isinstance(companies, list):
                report_content.append("公司明细")
                report_content.append("")
                report_content.append("公司名称    股票代码    营收(亿元)    净利润(亿元)    净利润率(%)    ROE(%)    资产负债率(%)    行业分类")
                report_content.append("--------  ----------  ----------    ----------    ----------    ------    ----------    --------")
                
                for company in companies:
                    if isinstance(company, dict):
                        name = company.get("名称", "")
                        code = company.get("股票代码", "")
                        revenue = company.get("营收(亿元)", 0)
                        net_profit = company.get("净利润(亿元)", 0)
                        net_profit_margin = company.get("净利润率", 0)
                        roe = company.get("ROE", 0)
                        debt_ratio = company.get("资产负债率", 0)
                        category = company.get("行业分类", "")
                        
                        # 格式化数值
                        revenue_str = f"{revenue:.2f}" if isinstance(revenue, (int, float)) else str(revenue)
                        net_profit_str = f"{net_profit:.2f}" if isinstance(net_profit, (int, float)) else str(net_profit)
                        net_profit_margin_str = f"{net_profit_margin:.2f}" if isinstance(net_profit_margin, (int, float)) else str(net_profit_margin)
                        roe_str = f"{roe:.2f}" if isinstance(roe, (int, float)) else str(roe)
                        debt_ratio_str = f"{debt_ratio:.2f}" if isinstance(debt_ratio, (int, float)) else str(debt_ratio)
                        
                        report_content.append(f"{name:<8}  {code:<10}  {revenue_str:>10}    {net_profit_str:>10}    {net_profit_margin_str:>10}    {roe_str:>6}    {debt_ratio_str:>10}    {category}")
                report_content.append("")
            
            # 添加关键发现
            if key_findings and isinstance(key_findings, dict):
                report_content.append("关键发现")
                report_content.append("")
                for key, value in key_findings.items():
                    # 将键名转换为更易读的中文
                    readable_key = self._translate_key_findings_key(key)
                    report_content.append(f"- {readable_key}: {value}")
                report_content.append("")
            
            return "\n".join(report_content)
        except Exception as e:
            # 如果解析失败，返回错误信息
            return f"行业分析报告格式化错误\n\n{str(e)}"

    @register_tool()
    async def save_text_report(self,
                             financial_data_json: str,
                             stock_name: str = "财务分析报告",
                             file_prefix: str = "./run_workdir") -> Dict[str, Any]:
        """
        生成并保存MD格式的财务分析报告
        
        Args:
            financial_data_json: 包含财务数据的JSON字符串
            stock_name: 股票名称，用于文件名
            file_prefix: 文件路径前缀
            
        Returns:
            dict: 结果信息包括成功状态和文件路径
        """
        try:
            # 格式化财务数据为Markdown报告
            report_content = self._format_financial_data_as_markdown(financial_data_json)
            
            # 生成文件名
            current_date = datetime.now().strftime("%Y%m%d")
            # 使用传入的stock_name或从JSON中提取公司名称
            try:
                if isinstance(financial_data_json, str):
                    data = json.loads(financial_data_json)
                else:
                    data = financial_data_json
                company_name = data.get("stock_name", data.get("company_name", data.get("公司名称", stock_name)))
            except:
                company_name = stock_name
                
            file_name = f"{company_name}{current_date}财务分析报告.md"
            
            # 使用workspace_root作为默认路径，如果提供了file_prefix则使用file_prefix
            if file_prefix and file_prefix != "./run_workdir":
                file_path = os.path.join(file_prefix, file_name)
            else:
                file_path = os.path.join(self.workspace_root, file_name)
            
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            # 保存到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            # 验证文件是否保存成功
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                return {
                    "success": True,
                    "message": f"财务分析报告已成功保存到: {file_path}",
                    "file_path": file_path,
                    "file_size": file_size
                }
            else:
                return {
                    "success": False,
                    "message": "保存财务分析报告时出错: 文件未成功创建",
                    "file_path": None,
                    "file_size": 0
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"保存财务分析报告时出错: {str(e)}",
                "file_path": None,
                "file_size": 0
            }

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

    @register_tool()
    async def save_pdf_report(self,
                             financial_data_json: str,
                             stock_name: str = "财务分析报告",
                             file_prefix: str = "./run_workdir",
                             chart_files: Optional[list] = None,
                             report_date: Optional[str] = None) -> Dict[str, Any]:
        """
        生成并保存PDF格式的财务分析报告
        
        Args:
            financial_data_json: 包含财务数据的JSON字符串
            stock_name: 股票名称，用于文件名
            file_prefix: 文件路径前缀
            chart_files: 图表文件路径列表，用于在PDF中插入图表
            report_date: 报告日期，如果未提供则使用当前时间
            
        Returns:
            dict: 结果信息包括成功状态和文件路径
        """
        # 检查PDF支持是否可用
        if not PDF_SUPPORT:
            return {
                "success": False,
                "message": "PDF生成功能不可用，请安装fpdf2库",
                "file_path": None,
                "file_size": 0
            }
        
        try:
            # 格式化财务数据为PDF报告内容
            report_content = self._format_financial_data_as_pdf_content(financial_data_json)
            
            # 生成文件名
            current_date = datetime.now().strftime("%Y%m%d")
            # 使用传入的stock_name或从JSON中提取公司名称
            try:
                if isinstance(financial_data_json, str):
                    data = json.loads(financial_data_json)
                else:
                    data = financial_data_json
                company_name = data.get("stock_name", data.get("company_name", data.get("公司名称", stock_name)))
            except:
                company_name = stock_name
                
            file_name = f"{company_name}{current_date}财务分析报告.pdf"
            
            # 使用workspace_root作为默认路径，如果提供了file_prefix则使用file_prefix
            if file_prefix and file_prefix != "./run_workdir":
                file_path = os.path.join(file_prefix, file_name)
            else:
                file_path = os.path.join(self.workspace_root, file_name)
            
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            # 创建PDF文档，设置页面大小和边距
            from fpdf import FPDF  # 确保FPDF已导入
            pdf = FPDF()
            pdf.add_page()

            # 使用跨平台字体检测
            font_success = self.setup_pdf_font(pdf)
            if not font_success:
                print("Warning: PDF将使用默认字体，中文字符可能无法正常显示")

            # 设置颜色和样式
            pdf.set_fill_color(240, 240, 240)  # 浅灰色背景
            pdf.set_draw_color(100, 100, 100)  # 深灰色边框

            # 设置初始位置和行高
            pdf.set_y(20)
            line_height = 8

            # 使用传入的报告日期或当前时间
            report_date_display = report_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 添加标题页
            if font_success:
                pdf.set_font("ChineseFont", size=24)
            else:
                pdf.set_font("Arial", size=24)
            pdf.set_text_color(0, 0, 0)  # 黑色文字
            pdf.cell(0, 20, f"{company_name} Financial Analysis Report", align="C", ln=True)
            pdf.ln(10)

            if font_success:
                pdf.set_font("ChineseFont", size=14)
            else:
                pdf.set_font("Arial", size=14)
            pdf.cell(0, 10, f"Report Date: {report_date_display}", align="C", ln=True)
            pdf.ln(20)

            # 添加目录
            if font_success:
                pdf.set_font("ChineseFont", size=16)
                pdf.cell(0, 10, "Table of Contents", ln=True)
            else:
                pdf.set_font("Arial", size=16)
                pdf.cell(0, 10, "Table of Contents", ln=True)
            pdf.set_draw_color(0, 0, 0)
            pdf.line(10, pdf.get_y() + 5, 200, pdf.get_y() + 5)
            pdf.ln(10)

            # 生成目录项
            sections = self._parse_report_sections(report_content)
            section_names = list(sections.keys()) if sections else ["Company Basic Info", "Financial Data Overview", "Financial Ratio Analysis", "Financial Trend Analysis", "Key Insights", "Investment Advice", "Risk Warning"]

            if font_success:
                pdf.set_font("ChineseFont", size=12)
            else:
                pdf.set_font("Arial", size=12)
            for i, section_name in enumerate(section_names, 1):
                pdf.cell(0, 8, f"{i}. {section_name}", ln=True)
            pdf.ln(20)
            
            # 分割内容并逐段添加到PDF
            if sections:
                for section_title, section_content in sections.items():
                    # 添加新页面
                    pdf.add_page()
                    pdf.set_y(20)

                    # 添加章节标题
                    if font_success:
                        pdf.set_font("ChineseFont", size=18)
                    else:
                        pdf.set_font("Arial", size=18)
                    pdf.set_text_color(0, 0, 139)  # 深蓝色标题
                    pdf.cell(0, 15, section_title, ln=True)
                    pdf.set_draw_color(0, 0, 0)
                    pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
                    pdf.ln(10)

                    # 添加章节内容
                    if font_success:
                        pdf.set_font("ChineseFont", size=12)
                    else:
                        pdf.set_font("Arial", size=12)
                    pdf.set_text_color(0, 0, 0)  # 黑色文字
                    
                    lines = section_content.split('\n')
                    for line in lines:
                        if line.strip():  # 忽略空行
                            # 检查是否是列表项
                            if line.strip().startswith(('-', '*', '•')):
                                pdf.set_x(20)  # 缩进列表项
                                pdf.cell(0, line_height, line.strip(), ln=True)
                            # 检查是否是表格行
                            elif '|' in line and line.count('|') > 2:
                                # 简单的表格处理
                                if font_success:
                                    pdf.set_font("ChineseFont", size=10)
                                else:
                                    pdf.set_font("Arial", size=10)
                                pdf.cell(0, line_height, line.strip(), ln=True)
                                if font_success:
                                    pdf.set_font("ChineseFont", size=12)
                                else:
                                    pdf.set_font("Arial", size=12)
                            else:
                                pdf.cell(0, line_height, line.strip(), ln=True)
                        else:
                            pdf.ln(line_height / 2)  # 空行间距
            else:
                # 如果没有解析出章节，直接添加完整内容
                pdf.add_page()
                pdf.set_y(20)

                # 添加默认章节标题
                if font_success:
                    pdf.set_font("ChineseFont", size=18)
                else:
                    pdf.set_font("Arial", size=18)
                pdf.set_text_color(0, 0, 139)  # 深蓝色标题
                pdf.cell(0, 15, "Report Content", ln=True)
                pdf.set_draw_color(0, 0, 0)
                pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
                pdf.ln(10)

                # 添加内容
                if font_success:
                    pdf.set_font("ChineseFont", size=12)
                else:
                    pdf.set_font("Arial", size=12)
                pdf.set_text_color(0, 0, 0)  # 黑色文字
                
                lines = report_content.split('\n')
                for line in lines:
                    if line.strip():  # 忽略空行
                        pdf.cell(0, line_height, line.strip(), ln=True)
                    else:
                        pdf.ln(line_height / 2)  # 空行间距
            
            # 如果有图表文件，添加到PDF中
            if chart_files and isinstance(chart_files, list):
                for chart_file in chart_files:
                    if os.path.exists(chart_file):
                        try:
                            # 在PDF中添加图片
                            pdf.add_page()
                            pdf.set_y(20)
                            if font_success:
                                pdf.set_font("ChineseFont", size=16)
                            else:
                                pdf.set_font("Arial", size=16)
                            pdf.set_text_color(0, 0, 139)  # 深蓝色标题
                            pdf.cell(0, 15, f"Chart: {os.path.basename(chart_file)}", align="C", ln=True)
                            pdf.ln(10)
                            pdf.set_text_color(0, 0, 0)  # 黑色文字
                            # 添加图片（最大宽度180mm，高度自适应）
                            pdf.image(chart_file, x=15, y=None, w=180)
                        except Exception as img_error:
                            print(f"Warning: 无法添加图表 {chart_file} 到PDF: {img_error}")
            
            # 保存PDF文件
            pdf.output(file_path)
            
            # 验证文件是否保存成功
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                return {
                    "success": True,
                    "message": f"财务分析报告已成功保存到: {file_path}",
                    "file_path": file_path,
                    "file_size": file_size
                }
            else:
                return {
                    "success": False,
                    "message": "保存财务分析报告时出错: 文件未成功创建",
                    "file_path": None,
                    "file_size": 0
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"保存财务分析报告时出错: {str(e)}",
                "file_path": None,
                "file_size": 0
            }

    def _parse_report_sections(self, report_content: str) -> Dict[str, str]:
        """
        解析报告内容为章节
        
        Args:
            report_content: 报告内容字符串
            
        Returns:
            dict: 章节标题到内容的映射
        """
        sections = {}
        current_section = "公司基本信息"  # 默认章节
        current_content = []
        
        # 初始化默认章节
        sections[current_section] = ""
        
        lines = report_content.split('\n')
        for line in lines:
            # 检查是否是章节标题（以冒号结尾且内容较短，或者以##开头，或者以特定关键词开头）
            if ((line.endswith(":") and len(line) < 30) or 
                (line.startswith("##") and len(line) < 50) or
                (line.strip() in ["财务数据概览", "财务比率分析", "财务趋势分析", "关键洞察", "投资建议", "风险提示", "执行摘要", "公司基本信息"])):
                # 保存前一个章节
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                    current_content = []
                
                # 设置新的章节标题
                current_section = line.rstrip(":").lstrip("#").strip()
                sections[current_section] = ""  # 初始化新章节
            else:
                # 添加内容到当前章节
                current_content.append(line)
        
        # 保存最后一个章节
        if current_section and current_content:
            sections[current_section] = "\n".join(current_content).strip()
        
        # 如果默认章节是空的，删除它
        if "公司基本信息" in sections and not sections["公司基本信息"]:
            del sections["公司基本信息"]
        
        return sections

    @register_tool()
    async def save_html_as_pdf_report(self,
                                     html_content: str,
                                     stock_name: str = "财务分析报告",
                                     file_prefix: str = "./stock_analysis_workspace",
                                     chart_files: Optional[list] = None) -> Dict[str, Any]:
        """
        将HTML内容直接转换为PDF报告

        Args:
            html_content: HTML内容字符串
            stock_name: 股票名称，用于文件名
            file_prefix: 文件路径前缀
            chart_files: 图表文件路径列表，用于在PDF中插入图表

        Returns:
            dict: 结果信息包括成功状态和文件路径
        """
        # 检查PDF支持是否可用
        if not PDF_SUPPORT:
            return {
                "success": False,
                "message": "PDF生成功能不可用，请安装fpdf2库",
                "file_path": None,
                "file_size": 0
            }

        try:
            # 创建HTML到PDF转换器
            class HTMLPDF(FPDF, HTMLMixin):
                pass

            # 生成文件名
            current_date = datetime.now().strftime("%Y%m%d")
            # 使用传入的stock_name或从HTML中提取公司名称
            try:
                import re
                company_match = re.search(r'([A-Za-z\u4e00-\u9fff]+(?:股份有限公司|集团|公司|有限|Co\.|Ltd\.|Inc\.))', html_content)
                if company_match:
                    company_name = company_match.group(1)
                else:
                    company_name = stock_name
            except:
                company_name = stock_name

            file_name = f"{company_name}{current_date}财务分析报告.pdf"

            # 使用workspace_root作为默认路径，如果提供了file_prefix则使用file_prefix
            if file_prefix and file_prefix != "./stock_analysis_workspace":
                file_path = os.path.join(file_prefix, file_name)
            else:
                file_path = os.path.join(self.workspace_root, file_name)

            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)

            # 创建PDF文档
            pdf = HTMLPDF()
            pdf.add_page()

            # 设置字体
            font_success = self.setup_pdf_font(pdf)
            if not font_success:
                print("Warning: PDF将使用默认字体，中文字符可能无法正常显示")

            # 添加HTML内容
            try:
                pdf.write_html(html_content)
            except Exception as html_error:
                print(f"HTML渲染失败，尝试文本模式: {html_error}")
                # 降级到文本模式
                pdf.add_page()
                text_content = re.sub(r'<[^>]+>', '', html_content)  # 移除HTML标签
                text_content = text_content.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')

                if font_success:
                    pdf.set_font("ChineseFont", size=12)
                else:
                    pdf.set_font("Arial", size=12)

                lines = text_content.split('\n')
                for line in lines:
                    if line.strip():
                        pdf.cell(0, 8, line.strip(), ln=True)

            # 如果有图表文件，添加到PDF中
            if chart_files and isinstance(chart_files, list):
                for chart_file in chart_files:
                    if os.path.exists(chart_file):
                        try:
                            # 在PDF中添加图片
                            pdf.add_page()
                            pdf.set_y(20)
                            if font_success:
                                pdf.set_font("ChineseFont", size=16)
                            else:
                                pdf.set_font("Arial", size=16)
                            pdf.set_text_color(0, 0, 139)  # 深蓝色标题
                            pdf.cell(0, 15, f"Chart: {os.path.basename(chart_file)}", align="C", ln=True)
                            pdf.ln(10)
                            pdf.set_text_color(0, 0, 0)  # 黑色文字
                            # 添加图片（最大宽度180mm，高度自适应）
                            pdf.image(chart_file, x=15, y=None, w=180)
                        except Exception as img_error:
                            print(f"Warning: 无法添加图表 {chart_file} 到PDF: {img_error}")

            # 保存PDF文件
            pdf.output(file_path)

            # 验证文件是否保存成功
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                return {
                    "success": True,
                    "message": f"HTML转PDF报告已成功生成: {file_path}",
                    "file_path": file_path,
                    "file_size": file_size
                }
            else:
                return {
                    "success": False,
                    "message": "HTML转PDF报告时出错: 文件未成功创建",
                    "file_path": None,
                    "file_size": 0
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"HTML转PDF报告时出错: {str(e)}",
                "file_path": None,
                "file_size": 0
            }
