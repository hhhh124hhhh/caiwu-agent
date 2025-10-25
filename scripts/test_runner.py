#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财务分析系统测试运行器
提供便捷的测试运行和配置功能
"""

import os
import sys
import argparse
import subprocess
import time
from pathlib import Path
from typing import List, Optional

# 设置控制台编码
if sys.platform.startswith('win'):
    import locale
    import codecs
    # 尝试设置UTF-8编码
    try:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except:
        pass

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestRunner:
    """测试运行器类"""

    def __init__(self):
        self.project_root = project_root
        self.venv_path = project_root / ".venv"
        self.test_results_dir = project_root / "test_results"
        self.test_results_dir.mkdir(exist_ok=True)

    def check_environment(self) -> bool:
        """检查测试环境是否正确设置"""
        print("检查测试环境...")

        # 检查虚拟环境
        if not self.venv_path.exists():
            print("虚拟环境不存在，请先运行: uv sync --all-extras")
            return False

        # 检查关键依赖
        try:
            import pytest
            import utu
            print(f"pytest 版本: {pytest.__version__}")
            print("utu 包已安装")
        except ImportError as e:
            print(f"依赖检查失败: {e}")
            return False

        # 检查环境变量
        required_env_vars = ["UTU_LLM_TYPE", "UTU_LLM_MODEL", "UTU_LLM_API_KEY"]
        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            print(f"缺少环境变量: {', '.join(missing_vars)}")
            print("   某些集成测试可能无法运行")
        else:
            print("环境变量设置完整")

        return True

    def run_command(self, cmd: List[str], description: str) -> int:
        """运行命令并处理输出"""
        print(f"\n[运行] {description}")
        print(f"命令: {' '.join(cmd)}")
        print("-" * 60)

        start_time = time.time()

        try:
            # 激活虚拟环境并运行命令
            if os.name == 'nt':  # Windows
                activate_cmd = str(self.venv_path / "Scripts" / "activate.bat")
                cmd = f"call {activate_cmd} && {' '.join(cmd)}"
                result = subprocess.run(cmd, shell=True, cwd=self.project_root)
            else:  # Unix-like
                activate_cmd = str(self.venv_path / "bin" / "activate")
                cmd = f"source {activate_cmd} && {' '.join(cmd)}"
                result = subprocess.run(cmd, shell=True, cwd=self.project_root, executable="/bin/bash")

            duration = time.time() - start_time

            if result.returncode == 0:
                print(f"[成功] {description} 完成 (耗时: {duration:.2f}秒)")
            else:
                print(f"[失败] {description} 失败 (返回码: {result.returncode})")

            return result.returncode

        except Exception as e:
            print(f"[错误] 运行命令时出错: {e}")
            return 1

    def run_unit_tests(self, coverage: bool = True) -> int:
        """运行单元测试"""
        cmd = ["pytest", "tests/", "-m", "unit or (not integration and not performance and not slow)", "-v"]

        if coverage:
            cmd.extend([
                "--cov=utu",
                "--cov-report=html:test_results/htmlcov_unit",
                "--cov-report=xml:test_results/coverage_unit.xml",
                "--cov-report=term-missing"
            ])

        return self.run_command(cmd, "运行单元测试")

    def run_integration_tests(self) -> int:
        """运行集成测试"""
        cmd = [
            "pytest", "tests/integration/",
            "-m", "integration",
            "--cov=utu",
            "--cov-report=html:test_results/htmlcov_integration",
            "--cov-report=xml:test_results/coverage_integration.xml",
            "-v",
            "-s"
        ]
        return self.run_command(cmd, "运行集成测试")

    def run_financial_tests(self) -> int:
        """运行财务分析专项测试"""
        cmd = [
            "pytest",
            "tests/tools/test_financial_analysis_toolkit.py",
            "tests/tools/test_tabular_data_toolkit.py",
            "tests/tools/test_report_saver_toolkit.py",
            "-m", "financial",
            "--cov=utu",
            "--cov-report=html:test_results/htmlcov_financial",
            "--cov-report=xml:test_results/coverage_financial.xml",
            "-v"
        ]
        return self.run_command(cmd, "运行财务分析测试")

    def run_performance_tests(self) -> int:
        """运行性能测试"""
        cmd = [
            "pytest", "tests/performance/",
            "-m", "performance",
            "--benchmark-only",
            "--benchmark-json=test_results/benchmark.json",
            "-v"
        ]
        return self.run_command(cmd, "运行性能测试")

    def run_edge_case_tests(self) -> int:
        """运行边界情况测试"""
        cmd = [
            "pytest", "tests/edge_cases/",
            "-m", "edge_case",
            "--cov=utu",
            "--cov-report=html:test_results/htmlcov_edge_cases",
            "--cov-report=xml:test_results/coverage_edge_cases.xml",
            "-v"
        ]
        return self.run_command(cmd, "运行边界情况测试")

    def run_all_tests(self) -> int:
        """运行所有测试"""
        print("开始运行完整测试套件...")

        tests = [
            ("单元测试", self.run_unit_tests),
            ("集成测试", self.run_integration_tests),
            ("财务分析测试", self.run_financial_tests),
            ("性能测试", self.run_performance_tests),
            ("边界情况测试", self.run_edge_case_tests),
        ]

        failed_tests = []

        for test_name, test_func in tests:
            result = test_func()
            if result != 0:
                failed_tests.append(test_name)

        # 汇总结果
        print("\n" + "="*60)
        print("测试结果汇总:")
        print("="*60)

        if failed_tests:
            print(f"[失败] 失败的测试: {', '.join(failed_tests)}")
            return 1
        else:
            print("[成功] 所有测试通过!")
            print(f"[报告] 测试报告保存在: {self.test_results_dir}")
            return 0

    def run_quick_tests(self) -> int:
        """运行快速测试（排除慢速测试）"""
        cmd = [
            "pytest", "tests/",
            "-m", "not slow",
            "--cov=utu",
            "--cov-report=term-missing",
            "-v"
        ]
        return self.run_command(cmd, "运行快速测试")

    def generate_test_report(self) -> int:
        """生成综合测试报告"""
        print("生成测试报告...")

        # 合并覆盖率报告（如果存在多个）
        coverage_files = list(self.test_results_dir.glob("coverage_*.xml"))
        if len(coverage_files) > 1:
            print("发现多个覆盖率文件，尝试合并...")
            # 这里可以添加覆盖率合并逻辑

        print(f"[报告] 测试报告已生成，保存在: {self.test_results_dir}")
        return 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="财务分析系统测试运行器")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 环境检查命令
    subparsers.add_parser("check", help="检查测试环境")

    # 各种测试命令
    subparsers.add_parser("unit", help="运行单元测试")
    subparsers.add_parser("integration", help="运行集成测试")
    subparsers.add_parser("financial", help="运行财务分析测试")
    subparsers.add_parser("performance", help="运行性能测试")
    subparsers.add_parser("edge", help="运行边界情况测试")
    subparsers.add_parser("all", help="运行所有测试")
    subparsers.add_parser("quick", help="运行快速测试")
    subparsers.add_parser("report", help="生成测试报告")

    # 选项参数
    parser.add_argument("--no-coverage", action="store_true", help="不生成覆盖率报告")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    runner = TestRunner()

    # 环境检查
    if not runner.check_environment():
        return 1

    # 执行命令
    if args.command == "check":
        return 0
    elif args.command == "unit":
        return runner.run_unit_tests(coverage=not args.no_coverage)
    elif args.command == "integration":
        return runner.run_integration_tests()
    elif args.command == "financial":
        return runner.run_financial_tests()
    elif args.command == "performance":
        return runner.run_performance_tests()
    elif args.command == "edge":
        return runner.run_edge_case_tests()
    elif args.command == "all":
        return runner.run_all_tests()
    elif args.command == "quick":
        return runner.run_quick_tests()
    elif args.command == "report":
        return runner.generate_test_report()
    else:
        print(f"未知命令: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())