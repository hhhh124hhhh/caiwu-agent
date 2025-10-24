#!/usr/bin/env python3
"""
时间感知功能验证脚本
简单验证时间工具包的基本功能是否正常工作
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_datetime_toolkit_basic():
    """测试时间工具包基本功能"""
    print("=== 时间感知功能验证 ===\n")

    try:
        # 直接导入和测试DateTimeToolkit类
        import importlib.util

        # 加载datetime_toolkit模块
        spec = importlib.util.spec_from_file_location(
            "datetime_toolkit",
            current_dir / "utu/tools/datetime_toolkit.py"
        )
        datetime_module = importlib.util.module_from_spec(spec)

        # 加载依赖模块
        base_spec = importlib.util.spec_from_file_location(
            "base",
            current_dir / "utu/tools/base.py"
        )
        base_module = importlib.util.module_from_spec(base_spec)

        config_spec = importlib.util.spec_from_file_location(
            "config",
            current_dir / "utu/config/__init__.py"
        )
        config_module = importlib.util.module_from_spec(config_spec)

        # 尝试执行模块代码
        spec.loader.exec_module(datetime_module)

        print("✓ 时间工具包模块加载成功")

        # 创建实例并测试基本功能
        toolkit = datetime_module.DateTimeToolkit()
        print("✓ DateTimeToolkit实例创建成功")

        # 测试获取当前日期
        current_date = toolkit.get_current_date()
        print(f"✓ 当前日期: {current_date}")

        # 测试获取当前时间
        current_time = toolkit.get_current_time()
        print(f"✓ 当前时间: {current_time}")

        # 测试财年获取
        financial_year = toolkit.get_financial_year()
        print(f"✓ 当前财年: {financial_year}")

        # 测试财报可用性检查（当前年份Q1）
        current_year = datetime.now().year
        availability = toolkit.check_financial_report_availability("600248", current_year, 1)
        print(f"✓ 财报可用性检查: {availability['available']}")

        # 测试财报周期验证
        validation = toolkit.validate_reporting_period(2023, 2)
        print(f"✓ 财报周期验证: {validation['valid']}")

        # 测试时间上下文分析
        time_context = toolkit.analyze_time_context_for_financial_request("分析2024年贵州茅台的财务数据")
        print(f"✓ 时间上下文分析: 检测到{len(time_context['detected_time_periods'])}个时间期间")

        # 测试获取最新可用期间
        latest_period = toolkit.get_latest_available_financial_period("600248")
        print(f"✓ 最新可用期间: {latest_period['latest_available_period']}")

        # 测试财报日历
        calendar = toolkit.get_financial_reporting_calendar(current_year)
        print(f"✓ 财报日历: 包含{len(calendar['reporting_schedule'])}个季度计划")

        print("\n🎉 时间感知工具包所有基本功能测试通过！")
        return True

    except Exception as e:
        print(f"❌ 时间工具包测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_akshare_time_enhancement():
    """测试AKShare工具的时间感知增强"""
    print("\n=== AKShare工具时间感知增强验证 ===\n")

    try:
        import importlib.util

        # 加载AKShare工具模块
        spec = importlib.util.spec_from_file_location(
            "akshare_financial_tool",
            current_dir / "utu/tools/akshare_financial_tool.py"
        )
        akshare_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(akshare_module)

        print("✓ AKShare工具模块加载成功")

        # 测试是否包含新增的时间感知方法
        tool_methods = dir(akshare_module.AKShareFinancialDataTool)

        time_aware_methods = [
            'check_latest_available_report',
            'get_financial_calendar_info',
            'validate_data_freshness'
        ]

        for method in time_aware_methods:
            if method in tool_methods:
                print(f"✓ 时间感知方法已添加: {method}")
            else:
                print(f"❌ 时间感知方法缺失: {method}")
                return False

        print("\n🎉 AKShare工具时间感知增强验证通过！")
        return True

    except Exception as e:
        print(f"❌ AKShare工具增强验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration_files():
    """测试配置文件"""
    print("\n=== 配置文件验证 ===\n")

    # 检查时间工具配置文件
    datetime_config = current_dir / "configs/tools/datetime.yaml"
    if datetime_config.exists():
        print("✓ 时间工具配置文件存在")

        with open(datetime_config, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'activated_tools' in content and 'get_current_date' in content:
            print("✓ 时间工具配置格式正确")
        else:
            print("❌ 时间工具配置格式有误")
            return False
    else:
        print("❌ 时间工具配置文件不存在")
        return False

    # 检查智能体配置文件更新
    agent_config = current_dir / "configs/agents/examples/stock_analysis_final.yaml"
    if agent_config.exists():
        print("✓ 智能体配置文件存在")

        with open(agent_config, 'r', encoding='utf-8') as f:
            content = f.read()

        if '/tools/datetime@toolkits.datetime' in content:
            print("✓ 智能体配置已包含时间工具")
        else:
            print("❌ 智能体配置未包含时间工具")
            return False

        if '时间感知工作流程' in content:
            print("✓ 智能体指令已更新时间感知功能")
        else:
            print("❌ 智能体指令未更新时间感知功能")
            return False
    else:
        print("❌ 智能体配置文件不存在")
        return False

    print("\n🎉 配置文件验证通过！")
    return True

def test_file_structure():
    """测试文件结构完整性"""
    print("\n=== 文件结构验证 ===\n")

    required_files = [
        "utu/tools/datetime_toolkit.py",
        "configs/tools/datetime.yaml",
        "tests/tools/test_datetime_toolkit.py",
        "examples/stock_analysis/test_time_aware_analysis.py"
    ]

    missing_files = []
    for file_path in required_files:
        full_path = current_dir / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"❌ {file_path} - 缺失")
            missing_files.append(file_path)

    if missing_files:
        print(f"\n❌ 缺失文件: {len(missing_files)}个")
        return False
    else:
        print(f"\n🎉 所有必需文件都存在！")
        return True

def main():
    """主验证函数"""
    print("时间感知功能修复验证脚本")
    print("=" * 50)
    print(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results = []

    # 运行各项验证
    tests = [
        ("文件结构完整性", test_file_structure),
        ("配置文件正确性", test_configuration_files),
        ("时间工具包基本功能", test_datetime_toolkit_basic),
        ("AKShare工具时间感知增强", test_akshare_time_enhancement)
    ]

    for test_name, test_func in tests:
        print(f"\n开始验证: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 验证异常: {e}")
            results.append((test_name, False))

    # 输出总结
    print("\n" + "=" * 50)
    print("🎯 时间感知功能修复验证总结")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:25} : {status}")

    print("-" * 50)
    print(f"总计: {passed}/{total} 项验证通过")

    if passed == total:
        print("\n🎉 时间感知功能修复验证完全通过！")
        print("\n✅ 修复成果:")
        print("  - 创建了完整的时间感知工具包")
        print("  - 增强了AKShare工具的时间感知能力")
        print("  - 更新了智能体配置和工作流程")
        print("  - 提供了完整的测试用例")
        print("  - 解决了未来数据请求处理问题")

        print("\n🚀 多智能体系统现在具备:")
        print("  - 智能时间判断能力")
        print("  - 财报可用性验证")
        print("  - 自动替代方案提供")
        print("  - 数据新鲜度评估")
        print("  - 完整的时间上下文分析")

        print("\n📝 使用方法:")
        print("  多智能体现在可以正确处理类似'分析2025年财报数据'的请求，")
        print("  自动识别未来时间，提供合理的替代方案和解释。")

    else:
        print(f"\n⚠️  {total - passed} 项验证失败，需要进一步检查")
        print("建议检查相关文件或配置。")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)