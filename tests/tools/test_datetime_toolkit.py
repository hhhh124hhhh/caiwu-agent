#!/usr/bin/env python3
"""
时间感知工具包测试用例
测试日期检查、财报可用性验证等功能
"""

import pytest
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utu.tools.datetime_toolkit import DateTimeToolkit


class TestDateTimeToolkit:
    """时间感知工具包测试类"""

    def setup_method(self):
        """测试前设置"""
        self.toolkit = DateTimeToolkit()
        self.current_date = datetime.now()

    def test_get_current_date(self):
        """测试获取当前日期"""
        result = self.toolkit.get_current_date()

        # 验证返回格式
        assert isinstance(result, str)
        assert len(result) == 10  # YYYY-MM-DD格式
        assert result[4] == '-'
        assert result[7] == '-'

        # 验证日期有效性
        year, month, day = map(int, result.split('-'))
        assert 1900 <= year <= 2100
        assert 1 <= month <= 12
        assert 1 <= day <= 31

    def test_get_current_time(self):
        """测试获取当前时间"""
        result = self.toolkit.get_current_time()

        # 验证返回格式
        assert isinstance(result, str)
        assert len(result) == 19  # YYYY-MM-DD HH:MM:SS格式
        assert result[4] == '-'
        assert result[7] == '-'
        assert result[10] == ' '
        assert result[13] == ':'
        assert result[16] == ':'

    def test_get_financial_year(self):
        """测试获取财年"""
        current_year = self.current_date.year

        # 测试当年
        result = self.toolkit.get_financial_year()
        assert result == current_year

        # 测试去年
        result = self.toolkit.get_financial_year(-1)
        assert result == current_year - 1

        # 测试明年
        result = self.toolkit.get_financial_year(1)
        assert result == current_year + 1

    def test_check_financial_report_availability_current_year(self):
        """测试当前年份财报可用性检查"""
        current_year = self.current_date.year

        # 测试已发布的季度
        if self.current_date.month > 4:  # Q1已发布
            result = self.toolkit.check_financial_report_availability("600248", current_year, 1)
            assert result["available"] is True
            assert result["year"] == current_year
            assert result["quarter"] == 1
            assert result["stock_code"] == "600248"

    def test_check_financial_report_availability_future(self):
        """测试未来财报可用性检查"""
        future_year = self.current_date.year + 1
        result = self.toolkit.check_financial_report_availability("600248", future_year, 1)

        assert result["available"] is False
        assert "reason" in result
        assert "suggestion" in result
        assert "尚未发布" in result["reason"] or "过于久远" in result["reason"]

    def test_check_financial_report_availability_invalid_quarter(self):
        """测试无效季度的财报可用性检查"""
        result = self.toolkit.check_financial_report_availability("600248", 2024, 5)

        assert result["available"] is False
        assert "季度参数无效" in result["reason"]

    def test_get_latest_available_financial_period(self):
        """测试获取最新可用财报期间"""
        result = self.toolkit.get_latest_available_financial_period("600248")

        assert "stock_code" in result
        assert "latest_available_period" in result
        assert "year" in result
        assert "quarter" in result
        assert "current_date" in result
        assert result["stock_code"] == "600248"
        assert 1 <= result["quarter"] <= 4

    def test_validate_reporting_period_valid(self):
        """测试有效财报周期验证"""
        result = self.toolkit.validate_reporting_period(2023, 2)

        assert result["valid"] is True
        assert result["year"] == 2023
        assert result["quarter"] == 2

    def test_validate_reporting_period_invalid_quarter(self):
        """测试无效季度的财报周期验证"""
        result = self.toolkit.validate_reporting_period(2023, 5)

        assert result["valid"] is False
        assert "quarter" in str(result["warnings"]).lower()

    def test_validate_reporting_period_invalid_year(self):
        """测试无效年份的财报周期验证"""
        result = self.toolkit.validate_reporting_period(1980, 2)

        assert result["valid"] is False
        assert "年份" in str(result["warnings"])

    def test_validate_reporting_period_future(self):
        """测试未来财报周期验证"""
        future_year = self.current_date.year + 1
        result = self.toolkit.validate_reporting_period(future_year, 3)

        assert "warnings" in result
        assert len(result["warnings"]) > 0

    def test_get_financial_reporting_calendar(self):
        """测试获取财报披露日历"""
        current_year = self.current_date.year
        result = self.toolkit.get_financial_reporting_calendar(current_year)

        assert result["year"] == current_year
        assert "reporting_schedule" in result
        assert "current_date" in result
        assert len(result["reporting_schedule"]) == 4

        # 验证每个季度的信息
        for i, report in enumerate(result["reporting_schedule"], 1):
            assert "quarter" in report
            assert "report_name" in report
            assert "deadline" in report
            assert "description" in report
            assert report["quarter"] == i

    def test_analyze_time_context_for_financial_request_with_year(self):
        """测试分析包含年份的财务请求时间上下文"""
        request = "分析2024年贵州茅台的财务数据"
        result = self.toolkit.analyze_time_context_for_financial_request(request)

        assert result["request_text"] == request
        assert "current_date" in result
        assert "detected_time_periods" in result
        assert len(result["detected_time_periods"]) > 0

        # 验证检测到的年份
        detected_periods = result["detected_time_periods"]
        assert any(p["year"] == 2024 for p in detected_periods)

    def test_analyze_time_context_for_financial_request_with_keywords(self):
        """测试分析包含关键词的财务请求时间上下文"""
        request = "请分析最新的财务数据"
        result = self.toolkit.analyze_time_context_for_financial_request(request)

        assert result["request_text"] == request
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0
        assert any("最新可用" in rec for rec in result["recommendations"])

    def test_analyze_time_context_for_financial_request_future_data(self):
        """测试分析包含未来数据的财务请求"""
        future_year = self.current_date.year + 2
        request = f"分析{future_year}年的财务报告"
        result = self.toolkit.analyze_time_context_for_financial_request(request)

        assert result["request_text"] == request
        assert "future_data_requests" in result
        assert len(result["future_data_requests"]) > 0
        assert len(result["recommendations"]) > 0

        # 验证未来数据请求被识别
        future_requests = result["future_data_requests"]
        assert any(req["year"] == future_year for req in future_requests)

    def test_configuration_updates(self):
        """测试配置更新功能"""
        custom_config = {
            "timezone": "UTC",
            "financial_reporting_rules": {
                "q1_deadline": "05-01",
                "q2_deadline": "09-01",
                "q3_deadline": "11-01",
                "q4_deadline": "05-01"
            }
        }

        toolkit = DateTimeToolkit(custom_config)
        assert toolkit.timezone == "UTC"
        assert toolkit.financial_reporting_rules["q1_deadline"] == "05-01"

    def test_edge_cases(self):
        """测试边界情况"""
        # 测试边界年份
        result = self.toolkit.validate_reporting_period(2099, 4)
        assert result["valid"] is True

        # 测试极远的未来年份
        result = self.toolkit.validate_reporting_period(2200, 1)
        assert result["valid"] is False

        # 测试极早的年份
        result = self.toolkit.validate_reporting_period(1800, 1)
        assert result["valid"] is False

    def test_error_handling(self):
        """测试错误处理"""
        # 测试无效参数类型
        try:
            # 这些应该不会抛出异常，而是返回包含错误信息的结果
            result = self.toolkit.check_financial_report_availability("", 2024, 1)
            assert "reason" in result

            result = self.toolkit.validate_reporting_period(0, 0)
            assert "valid" in result

        except Exception as e:
            pytest.fail(f"工具应该能够处理无效参数而不抛出异常: {e}")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])