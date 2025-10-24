"""
时间感知工具包
提供日期检查、财报可用性验证等功能，解决多智能体系统缺乏时间感知的问题
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
import logging
import re
from pathlib import Path

from ..config import ToolkitConfig
from .base import AsyncBaseToolkit, register_tool

logger = logging.getLogger(__name__)


class DateTimeToolkit(AsyncBaseToolkit):
    """时间感知工具包"""

    def __init__(self, config: ToolkitConfig | dict | None = None):
        super().__init__(config)
        # 默认配置
        self.timezone = "Asia/Shanghai"
        self.financial_reporting_rules = {
            "q1_deadline": "04-30",  # 一季报4月30日前
            "q2_deadline": "08-31",  # 半年报8月31日前
            "q3_deadline": "10-31",  # 三季报10月31日前
            "q4_deadline": "04-30",  # 年报次年4月30日前
        }

        # 从配置中更新设置
        if config and isinstance(config, dict):
            self.timezone = config.get("timezone", self.timezone)
            if "financial_reporting_rules" in config:
                self.financial_reporting_rules.update(config["financial_reporting_rules"])

    @register_tool()
    def get_current_date(self) -> str:
        """
        获取当前日期

        Returns:
            str: 当前日期，格式：YYYY-MM-DD
        """
        current_date = datetime.now()
        return current_date.strftime("%Y-%m-%d")

    @register_tool()
    def get_current_time(self) -> str:
        """
        获取当前时间

        Returns:
            str: 当前时间，格式：YYYY-MM-DD HH:MM:SS
        """
        current_time = datetime.now()
        return current_time.strftime("%Y-%m-%d %H:%M:%S")

    @register_tool()
    def get_financial_year(self, offset: int = 0) -> int:
        """
        获取财年

        Args:
            offset: 年份偏移量，0为当年，-1为上一年，1为下一年

        Returns:
            int: 财年年份
        """
        current_date = datetime.now()
        # 中国财年通常与自然年一致
        financial_year = current_date.year + offset
        return financial_year

    @register_tool()
    def check_financial_report_availability(self, stock_code: str, year: int, quarter: int) -> Dict:
        """
        检查财报数据可用性

        Args:
            stock_code: 股票代码，如 "600248" 或 "600248.SH"
            year: 年份，如 2024
            quarter: 季度，1-4

        Returns:
            Dict: 包含可用性信息的字典
        """
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        current_day = current_date.day

        # 验证输入参数
        if quarter < 1 or quarter > 4:
            return {
                "available": False,
                "reason": "季度参数无效，必须是1-4之间的整数",
                "stock_code": stock_code,
                "requested_period": f"{year}Q{quarter}",
                "current_date": current_date.strftime("%Y-%m-%d")
            }

        # 检查年份是否合理
        if year > current_year + 1:  # 超过明年
            return {
                "available": False,
                "reason": f"请求的年份{year}过于久远，当前年份为{current_year}",
                "stock_code": stock_code,
                "requested_period": f"{year}Q{quarter}",
                "current_date": current_date.strftime("%Y-%m-%d"),
                "suggestion": f"建议分析{current_year-1}或{current_year}年的财报数据"
            }

        # 检查当前季度的财报发布状态
        deadline_map = {
            1: self.financial_reporting_rules["q1_deadline"],
            2: self.financial_reporting_rules["q2_deadline"],
            3: self.financial_reporting_rules["q3_deadline"],
            4: self.financial_reporting_rules["q4_deadline"]
        }

        deadline_month, deadline_day = map(int, deadline_map[quarter].split("-"))

        # 对于年报（Q4），截止日期是次年
        if quarter == 4:
            deadline_year = year + 1
        else:
            deadline_year = year

        deadline_date = datetime(deadline_year, deadline_month, deadline_day)

        # 判断是否已过截止日期
        is_past_deadline = current_date > deadline_date

        # 特殊处理：如果是今年之前的年份，假设数据已发布
        if year < current_year:
            is_past_deadline = True

        result = {
            "stock_code": stock_code,
            "requested_period": f"{year}Q{quarter}",
            "current_date": current_date.strftime("%Y-%m-%d"),
            "deadline_date": deadline_date.strftime("%Y-%m-%d"),
            "available": is_past_deadline,
            "quarter": quarter,
            "year": year
        }

        if not is_past_deadline:
            if quarter == 4:
                result["reason"] = f"{year}年年报预计在{deadline_year}年{deadline_month}月{deadline_day}日前发布"
            else:
                result["reason"] = f"{year}年第{quarter}季度财报预计在{deadline_month}月{deadline_day}日前发布"

            # 提供替代建议
            if quarter > 1:
                result["suggestion"] = f"建议分析{year}年第{quarter-1}季度财报"
            else:
                result["suggestion"] = f"建议分析{year-1}年年报数据"

        return result

    @register_tool()
    def get_latest_available_financial_period(self, stock_code: str) -> Dict:
        """
        获取最新可用的财报期间

        Args:
            stock_code: 股票代码

        Returns:
            Dict: 最新可用财报期间信息
        """
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month

        # 按季度倒推检查可用性
        quarters = [
            (current_year, 4),
            (current_year, 3),
            (current_year, 2),
            (current_year, 1),
            (current_year - 1, 4),
            (current_year - 1, 3),
            (current_year - 1, 2),
            (current_year - 1, 1)
        ]

        for year, quarter in quarters:
            availability = self.check_financial_report_availability(stock_code, year, quarter)
            if availability["available"]:
                return {
                    "stock_code": stock_code,
                    "latest_available_period": f"{year}Q{quarter}",
                    "year": year,
                    "quarter": quarter,
                    "current_date": current_date.strftime("%Y-%m-%d"),
                    "description": f"最新可用财报为{year}年第{quarter}季度报告"
                }

        # 如果都不可用，返回默认值
        return {
            "stock_code": stock_code,
            "latest_available_period": f"{current_year-1}Q4",
            "year": current_year - 1,
            "quarter": 4,
            "current_date": current_date.strftime("%Y-%m-%d"),
            "description": f"暂无可用财报数据，建议使用{current_year-1}年年报",
            "note": "这是一个保守估计，实际情况可能需要根据具体公司财报发布时间调整"
        }

    @register_tool()
    def validate_reporting_period(self, year: int, quarter: int) -> Dict:
        """
        验证财报周期是否合理

        Args:
            year: 年份
            quarter: 季度

        Returns:
            Dict: 验证结果
        """
        current_date = datetime.now()
        current_year = current_date.year

        result = {
            "year": year,
            "quarter": quarter,
            "valid": True,
            "warnings": [],
            "current_date": current_date.strftime("%Y-%m-%d")
        }

        # 检查季度范围
        if quarter < 1 or quarter > 4:
            result["valid"] = False
            result["warnings"].append(f"季度{quarter}无效，必须是1-4之间的整数")
            return result

        # 检查年份范围
        if year < 1990:  # 中国股市从1990年开始
            result["valid"] = False
            result["warnings"].append(f"年份{year}过早，中国A股市场从1990年开始")
            return result

        if year > current_year + 2:  # 超过后年
            result["valid"] = False
            result["warnings"].append(f"年份{year}过于久远，当前为{current_year}年")
            return result

        # 检查是否为未来时间
        if year > current_year or (year == current_year and quarter > self._get_current_quarter()):
            result["warnings"].append(f"请求的时间{year}Q{quarter}是未来时间")

            # 检查财报是否可能已发布
            availability = self.check_financial_report_availability("TEST", year, quarter)
            if availability["available"]:
                result["warnings"].append("该期财报可能已发布")
            else:
                result["warnings"].append(availability["reason"])

        return result

    def _get_current_quarter(self) -> int:
        """获取当前季度"""
        current_date = datetime.now()
        return (current_date.month - 1) // 3 + 1

    @register_tool()
    def get_financial_reporting_calendar(self, year: int) -> Dict:
        """
        获取财年披露日历

        Args:
            year: 年份

        Returns:
            Dict: 财报披露日历
        """
        calendar = {
            "year": year,
            "reporting_schedule": [
                {
                    "quarter": 1,
                    "report_name": "第一季度报告",
                    "deadline": f"{year}-04-30",
                    "description": "第一季度财报应在4月30日前披露"
                },
                {
                    "quarter": 2,
                    "report_name": "半年度报告",
                    "deadline": f"{year}-08-31",
                    "description": "半年度财报应在8月31日前披露"
                },
                {
                    "quarter": 3,
                    "report_name": "第三季度报告",
                    "deadline": f"{year}-10-31",
                    "description": "第三季度财报应在10月31日前披露"
                },
                {
                    "quarter": 4,
                    "report_name": "年度报告",
                    "deadline": f"{year+1}-04-30",
                    "description": f"年度报告应在{year+1}年4月30日前披露"
                }
            ],
            "current_date": self.get_current_date()
        }

        return calendar

    @register_tool()
    def analyze_time_context_for_financial_request(self, request_text: str) -> Dict:
        """
        分析财务请求的时间上下文

        Args:
            request_text: 用户请求文本

        Returns:
            Dict: 时间上下文分析结果
        """
        current_date = datetime.now()
        current_year = current_date.year

        result = {
            "request_text": request_text,
            "current_date": current_date.strftime("%Y-%m-%d"),
            "detected_time_periods": [],
            "future_data_requests": [],
            "recommendations": []
        }

        # 提取年份
        year_pattern = r'(\d{4})'
        years_in_request = re.findall(year_pattern, request_text)

        for year_str in years_in_request:
            year = int(year_str)

            # 判断是否为未来年份
            if year > current_year:
                result["future_data_requests"].append({
                    "year": year,
                    "context": f"请求{year}年数据是未来时间"
                })

                # 检查该年财报是否可能已发布
                for quarter in range(1, 5):
                    availability = self.check_financial_report_availability("DEMO", year, quarter)
                    if availability["available"]:
                        result["recommendations"].append(
                            f"{year}年第{quarter}季度财报可能已发布，可以使用"
                        )
                    else:
                        result["recommendations"].append(
                            f"{year}年第{quarter}季度财报未发布：{availability['reason']}"
                        )

            result["detected_time_periods"].append({
                "year": year,
                "is_future": year > current_year,
                "years_from_now": year - current_year
            })

        # 提取季度信息
        quarter_pattern = r'([第]?[一二三四1234]季度|Q[1234])'
        quarters_in_request = re.findall(quarter_pattern, request_text)

        # 特殊关键词检测
        if any(keyword in request_text for keyword in ["最新", "近期", "当前", "最近"]):
            latest_period = self.get_latest_available_financial_period("DEMO")
            result["recommendations"].append(
                f"建议使用{latest_period['latest_available_period']}的数据进行分析"
            )

        # 生成总体建议
        if result["future_data_requests"]:
            result["recommendations"].append(
                "由于请求包含未来时间数据，建议明确分析基于最新可用数据的假设"
            )

        return result