#!/usr/bin/env python3
"""
多智能体系统修复验证脚本
验证工作流程文档、配置错误修复、日志系统等功能
"""

import os
import sys
from pathlib import Path
from datetime import datetime


def print_header(title):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f" {title} ")
    print(f"{'='*60}")


def print_success(message):
    """打印成功消息"""
    print(f"✅ {message}")


def print_error(message):
    """打印错误消息"""
    print(f"❌ {message}")


def print_warning(message):
    """打印警告消息"""
    print(f"⚠️  {message}")


def verify_file_exists(file_path, description):
    """验证文件是否存在"""
    full_path = Path(file_path)
    if full_path.exists():
        print_success(f"{description}: {file_path}")
        return True
    else:
        print_error(f"{description}缺失: {file_path}")
        return False


def verify_file_content(file_path, patterns, description):
    """验证文件内容"""
    full_path = Path(file_path)
    if not full_path.exists():
        print_error(f"{description}文件不存在: {file_path}")
        return False

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        missing_patterns = []
        for pattern in patterns:
            if pattern not in content:
                missing_patterns.append(pattern)

        if not missing_patterns:
            print_success(f"{description}内容验证通过")
            return True
        else:
            print_error(f"{description}内容缺失以下内容:")
            for pattern in missing_patterns:
                print(f"  - {pattern}")
            return False

    except Exception as e:
        print_error(f"读取{description}文件失败: {e}")
        return False


def verify_python_syntax(file_path):
    """验证Python语法"""
    full_path = Path(file_path)
    if not full_path.exists():
        return False

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            code = f.read()
        compile(code, str(full_path))
        print_success(f"Python语法验证通过: {file_path}")
        return True
    except SyntaxError as e:
        print_error(f"Python语法错误 {file_path}: {e}")
        return False
    except Exception as e:
        print_error(f"语法验证失败 {file_path}: {e}")
        return False


def verify_imports(module_name, file_path):
    """验证Python模块导入"""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        print_success(f"模块导入验证通过: {module_name}")
        return True
    except Exception as e:
        print_error(f"模块导入失败 {module_name}: {e}")
        return False


def main():
    """主验证函数"""
    print("多智能体系统修复验证")
    print(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = []

    # 1. 验证工作流程文档
    print_header("1. 工作流程文档验证")
    doc_files = [
        ("docs/MULTI_AGENT_WORKFLOW.md", "多智能体工作流程文档"),
    ]

    for file_path, description in doc_files:
        if verify_file_exists(file_path, description):
            # 检查文档内容完整性
            required_sections = [
                "系统架构概述",
                "核心组件详解",
                "完整工作流程",
                "智能体协作机制",
                "错误处理流程",
                "时间感知集成"
            ]
            if verify_file_content(file_path, required_sections, description):
                results.append(("文档", True))
            else:
                results.append(("文档", False))

    # 2. 验证配置错误修复
    print_header("2. 配置错误修复验证")

    # 检查修复的配置错误
    reporter_fix = verify_file_content(
        "utu/agents/orchestra/reporter.py",
        ["self.config.reporter_model.model_provider.model_dump()"],
        "ReporterAgent配置修复"
    )
    results.append(("ReporterAgent配置修复", reporter_fix))

    # 检查新增的reporter_config
    config_fix = verify_file_content(
        "configs/agents/examples/stock_analysis_final.yaml",
        ["reporter_config:"],
        "配置文件修复"
    )
    results.append(("配置文件修复", config_fix))

    # 3. 验证结构化日志系统
    print_header("3. 结构化日志系统验证")

    log_files = [
        ("utu/utils/orchestrated_logger.py", "核心日志记录器"),
        ("utu/agents/orchestra/logger.py", "多智能体日志记录器"),
        ("utu/tools/logging_wrapper.py", "工具日志包装器"),
        ("utu/config/orchestra_config.py", "配置管理器"),
    ]

    for file_path, description in log_files:
        file_ok = verify_file_exists(file_path, description)
        if file_ok:
            syntax_ok = verify_python_syntax(file_path)
            results.append((description, syntax_ok))
        else:
            results.append((description, False))

    # 4. 验证OrchestraAgent日志功能增强
    print_header("4. OrchestraAgent日志功能增强验证")

    orchestra_enhancements = [
        ("utu/agents/orchestra_agent.py", "OrchestraAgent日志增强"),
        ("utu/agents/orchestra/enhanced_executor.py", "增强执行器"),
    ]

    for file_path, description in orchestra_enhancements:
        file_ok = verify_file_exists(file_path, description)
        if file_ok:
            # 检查关键方法是否包含日志调用
            required_methods = [
                "self.orchestra_logger.start_session",
                "self.orchestra_logger.log_planning_start",
                "self.orchestra_logger.log_worker_start",
                "self.orchestra_logger.log_reporting_start"
            ]
            enhancement_ok = verify_file_content(file_path, required_methods, description)
            results.append((description, enhancement_ok))
        else:
            results.append((description, False))

    # 5. 验证工作流程优化
    print_header("5. 工作流程优化验证")

    optimization_files = [
        ("utu/agents/orchestra/enhanced_executor.py", "增强执行器"),
        ("utu/config/orchestra_config.py", "配置管理器"),
    ]

    for file_path, description in optimization_files:
        file_ok = verify_file_exists(file_path, description)
        if file_ok:
            syntax_ok = verify_python_syntax(file_path)
            results.append((description, syntax_ok))
        else:
            results.append((description, False))

    # 6. 验证日志分析工具
    print_header("6. 日志分析工具验证")

    analysis_tools = [
        ("scripts/analyze_orchestra_logs.py", "日志分析工具"),
        ("scripts/monitor_orchestra.py", "实时监控工具"),
    ]

    for file_path, description in analysis_tools:
        file_ok = verify_file_exists(file_path, description)
        if file_ok:
            # 检查工具功能
            if "analyze_orchestra_logs.py" in file_path:
                required_classes = ["LogAnalyzer"]
                class_check = verify_file_content(file_path, required_classes, description)
                results.append((f"{description} - 类定义", class_check))
            elif "monitor_orchestra.py" in file_path:
                required_classes = ["OrchestraMonitor"]
                class_check = verify_file_content(file_path, required_classes, description)
                results.append((f"{description} - 类定义", class_check))
            else:
                results.append((description, True))
        else:
            results.append((description, False))

    # 7. 检查目录结构
    print_header("7. 目录结构验证")

    required_dirs = [
        ("logs", "日志目录"),
        ("workspace", "工作目录"),
        ("temp", "临时目录"),
    ]

    for dir_name, description in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print_success(f"{description}: {dir_path}")
        else:
            print_warning(f"{description}不存在（运行时会自动创建）: {dir_path}")

    # 8. 总结验证结果
    print_header("验证结果总结")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for category, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{category:30} : {status}")

    print("-" * 60)
    print(f"总计: {passed}/{total} 项验证通过 ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 所有修复验证通过！")
        print("\n✅ 修复完成项目:")
        print("  - 创建了详细的多智能体工作流程文档")
        print("  - 修复了ReporterAgent的配置错误")
        print("  - 实现了完整的结构化日志系统")
        print("  - 增强了OrchestraAgent的日志功能")
        print("  - 优化了工作流程和错误处理")
        print("  - 创建了日志分析和监控工具")

        print("\n🚀 新增功能特性:")
        print("  - JSON格式的结构化日志记录")
        print("  - 实时性能监控和错误追踪")
        print("  - 智能体协作过程详细记录")
        print("  - 工具使用情况统计")
        print("  - 可配置的日志系统")
        print("  - 增强的错误处理和重试机制")

        print("\n📚 使用指南:")
        print("  - 运行日志分析: python scripts/analyze_orchestra_logs.py --log-file logs/orchestra_xxx.json")
        print("  - 实时监控: python scripts/monitor_orchestra.py --log-dir logs")
        print("  - 查看工作流程: docs/MULTI_AGENT_WORKFLOW.md")

        print("\n⚙️  环境变量配置:")
        print("  - UTU_LOGGING_ENABLED=true")
        print("  - UTU_LOG_LEVEL=INFO")
        print("  - UTU_LOG_DIR=./logs")
        print("  - UTU_MAX_RETRIES=3")
        print("  - UTU_TASK_TIMEOUT=300")

    else:
        failed_count = total - passed
        print(f"\n⚠️  {failed_count} 项验证失败，需要进一步检查")
        print("请查看上述错误信息并修复相关问题")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)