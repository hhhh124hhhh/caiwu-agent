#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pytest全局配置文件
定义所有测试共享的fixtures和配置
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Generator
import pytest
import pandas as pd

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """提供测试配置"""
    return {
        "test_data_dir": project_root / "tests" / "fixtures",
        "temp_dir": Path(tempfile.mkdtemp(prefix="utu_test_")),
        "sample_stocks": [
            ("600248", "陕西建工"),
            ("601668", "中国建筑"),
            ("000858", "五粮液")
        ],
        "performance_thresholds": {
            "calculation_time": 5.0,  # 秒
            "chart_generation_time": 10.0,  # 秒
            "report_generation_time": 15.0,  # 秒
            "memory_usage_mb": 100,  # MB
        },
        "coverage_thresholds": {
            "financial_metrics": 0.95,
            "chart_generation": 0.90,
            "report_generation": 0.85,
            "overall": 0.70
        }
    }


@pytest.fixture(scope="session")
def temp_workspace(test_config: Dict[str, Any]) -> Generator[Path, None, None]:
    """创建临时工作空间"""
    temp_dir = test_config["temp_dir"]

    # 创建必要的子目录
    (temp_dir / "charts").mkdir(exist_ok=True)
    (temp_dir / "reports").mkdir(exist_ok=True)
    (temp_dir / "data").mkdir(exist_ok=True)

    yield temp_dir

    # 清理临时文件
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture(scope="session")
def mock_llm_config() -> Dict[str, Any]:
    """提供模拟的LLM配置"""
    return {
        "UTU_LLM_TYPE": "chat.completions",
        "UTU_LLM_MODEL": "gpt-3.5-turbo",
        "UTU_LLM_API_KEY": "test-key-for-testing",
        "UTU_LLM_BASE_URL": "https://api.openai.com/v1",
        "UTU_LOG_LEVEL": "INFO"
    }


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch, mock_llm_config: Dict[str, Any]) -> None:
    """自动设置测试环境变量"""
    # 设置测试环境变量
    for key, value in mock_llm_config.items():
        monkeypatch.setenv(key, value)


@pytest.fixture(scope="session")
def check_akshare_availability() -> bool:
    """检查AKShare是否可用"""
    try:
        import akshare as ak
        # 尝试简单的API调用
        ak.tool_trade_date_hist_sina()
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def akshare_available(check_akshare_availability: bool) -> bool:
    """AKShare可用性标记"""
    return check_akshare_availability


def pytest_configure(config):
    """pytest配置钩子"""
    # 添加自定义标记
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "edge_case: mark test as edge case test"
    )
    config.addinivalue_line(
        "markers", "financial: mark test as financial analysis related"
    )
    config.addinivalue_line(
        "markers", "akshare: mark test as requiring AKShare data"
    )
    config.addinivalue_line(
        "markers", "chart: mark test as chart generation related"
    )
    config.addinivalue_line(
        "markers", "report: mark test as report generation related"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试收集，根据条件跳过某些测试"""
    # 如果AKShare不可用，跳过需要AKShare的测试
    try:
        import akshare as ak
        akshare_available = True
    except ImportError:
        akshare_available = False

    if not akshare_available:
        skip_akshare = pytest.mark.skip(reason="AKShare not available")
        for item in items:
            if "akshare" in item.keywords:
                item.add_marker(skip_akshare)


@pytest.fixture(scope="function")
def sample_financial_data() -> Dict[str, Any]:
    """提供标准化的示例财务数据"""
    return {
        "company_info": {
            "name": "测试公司股份有限公司",
            "stock_code": "600001",
            "industry": "建筑工程",
            "analysis_date": "2024-12-31"
        },
        "financial_data": {
            "income": [
                {
                    "营业收入": 50000000000,  # 500亿
                    "营业成本": 41000000000,  # 410亿
                    "净利润": 6000000000,    # 6亿
                    "归属于母公司所有者的净利润": 5000000000  # 5亿
                }
            ],
            "balance": [
                {
                    "资产总计": 125000000000,    # 1250亿
                    "负债合计": 80000000000,     # 800亿
                    "所有者权益合计": 45000000000,  # 450亿
                    "流动资产合计": 60000000000,   # 600亿
                    "流动负债合计": 40000000000,   # 400亿
                    "存货": 15000000000,           # 150亿
                    "应收账款": 10000000000,       # 100亿
                    "固定资产": 100000000000,      # 1000亿
                    "长期投资": 20000000000        # 200亿
                }
            ],
            "cashflow": [
                {
                    "经营活动产生的现金流量净额": 7500000000,  # 75亿
                    "投资活动现金流出小计": 6000000000,      # 60亿
                    "分配股利、利润或偿付利息支付的现金": 1500000000  # 15亿
                }
            ]
        }
    }


@pytest.fixture(scope="function")
def empty_financial_data() -> Dict[str, Any]:
    """提供空的财务数据用于边界测试"""
    return {
        "company_info": {
            "name": "",
            "stock_code": "",
            "industry": "",
            "analysis_date": ""
        },
        "financial_data": {
            "income": [],
            "balance": [],
            "cashflow": []
        }
    }


@pytest.fixture(scope="function")
def performance_monitor():
    """性能监控器"""
    import time
    import psutil
    import os

    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.start_memory = None
            self.end_memory = None

        def start(self):
            self.start_time = time.time()
            process = psutil.Process(os.getpid())
            self.start_memory = process.memory_info().rss / 1024 / 1024  # MB

        def stop(self):
            self.end_time = time.time()
            process = psutil.Process(os.getpid())
            self.end_memory = process.memory_info().rss / 1024 / 1024  # MB

        def get_duration(self) -> float:
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return 0.0

        def get_memory_usage(self) -> float:
            if self.start_memory and self.end_memory:
                return max(0, self.end_memory - self.start_memory)
            return 0.0

    return PerformanceMonitor()


# 测试数据清理钩子
@pytest.fixture(autouse=True)
def cleanup_test_files(request):
    """自动清理测试生成的文件"""
    yield

    # 清理测试生成的临时文件
    test_temp_patterns = [
        "test_chart_*.png",
        "test_report_*.*",
        "temp_*.json",
        "test_*.html"
    ]

    for pattern in test_temp_patterns:
        for file_path in Path(".").glob(pattern):
            try:
                file_path.unlink()
            except OSError:
                pass


# 慢速测试标记
def pytest_addoption(parser):
    """添加自定义命令行选项"""
    parser.addoption(
        "--include-slow",
        action="store_true",
        default=False,
        help="include slow tests"
    )


def pytest_collection_modifyitems(config, items):
    """根据命令行选项修改测试收集"""
    if not config.getoption("--include-slow"):
        skip_slow = pytest.mark.skip(reason="need --include-slow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)