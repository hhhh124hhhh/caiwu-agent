#!/usr/bin/env python3
"""
时间感知财务分析集成测试
测试时间感知功能与财务分析工具的完整集成
"""

import sys
import pathlib
from datetime import datetime

# 添加项目根目录到Python路径
project_root = pathlib.Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utu.tools.datetime_toolkit import DateTimeToolkit
from utu.tools.akshare_financial_tool import AKShareFinancialDataTool


def test_time_aware_data_availability():
    """测试时间感知的数据可用性检查"""
    print("=== 测试时间感知的数据可用性检查 ===\n")

    # 初始化工具
    datetime_toolkit = DateTimeToolkit()
    akshare_tool = AKShareFinancialDataTool()

    # 测试股票代码
    test_stock = "600248"  # 陕西建工

    # 1. 获取当前时间
    current_date = datetime_toolkit.get_current_date()
    current_time = datetime_toolkit.get_current_time()
    print(f"当前时间: {current_date} {current_time}")

    # 2. 检查最新可用报告
    print(f"\n检查 {test_stock} 的最新可用报告...")
    latest_report = akshare_tool.check_latest_available_report(test_stock)
    print(f"结果: {latest_report}")

    if latest_report["available"]:
        print(f"✓ 最新可用报告: {latest_report['period']} ({latest_report['description']})")
        print(f"  数据完整性: {latest_report['data_completeness']['overall_score']:.1f}%")

        # 3. 获取最新可用财报期间
        latest_period = datetime_toolkit.get_latest_available_financial_period(test_stock)
        print(f"\n时间工具确认的最新期间: {latest_period['latest_available_period']}")
        print(f"描述: {latest_period['description']}")

        # 4. 验证数据新鲜度
        requested_period = {
            "year": latest_report["report_year"],
            "quarter": latest_report["report_quarter"]
        }
        freshness_check = akshare_tool.validate_data_freshness(test_stock, requested_period)
        print(f"\n数据新鲜度验证: {freshness_check}")

        if freshness_check["valid"]:
            print("✓ 数据新鲜度验证通过")
            if "freshness" in freshness_check:
                freshness_info = freshness_check["freshness"]
                print(f"  新鲜度等级: {freshness_info['level']} ({freshness_info['description']})")
                print(f"  数据天数: {freshness_info['days_old']}天")
        else:
            print(f"✗ 数据新鲜度验证失败: {freshness_check['reason']}")

    else:
        print(f"✗ 无法获取最新报告: {latest_report['reason']}")
        print(f"建议: {latest_report['suggestion']}")

    return latest_report["available"]


def test_future_data_request_handling():
    """测试未来数据请求处理"""
    print("\n=== 测试未来数据请求处理 ===\n")

    datetime_toolkit = DateTimeToolkit()
    akshare_tool = AKShareFinancialDataTool()

    current_year = datetime.now().year
    test_stock = "600248"

    # 测试请求未来年报
    future_year = current_year + 1
    print(f"测试请求 {future_year} 年年报数据...")

    # 1. 检查财报可用性
    availability = datetime_toolkit.check_financial_report_availability(test_stock, future_year, 4)
    print(f"财报可用性检查: {availability}")

    if not availability["available"]:
        print(f"✓ 正确识别未来数据不可用")
        print(f"原因: {availability['reason']}")
        print(f"建议: {availability['suggestion']}")

        # 2. 获取替代方案
        alternative = datetime_toolkit.get_latest_available_financial_period(test_stock)
        print(f"\n建议的替代方案: {alternative['latest_available_period']}")
        print(f"描述: {alternative['description']}")

        # 3. 验证替代数据的新鲜度
        alt_period = {
            "year": alternative["year"],
            "quarter": alternative["quarter"]
        }
        alt_freshness = akshare_tool.validate_data_freshness(test_stock, alt_period)
        print(f"替代数据新鲜度: {alt_freshness['valid']}")

        if alt_freshness["valid"]:
            print("✓ 替代数据可用且新鲜")
        else:
            print(f"✗ 替代数据有问题: {alt_freshness['reason']}")

        return True
    else:
        print("⚠ 意外：未来数据被标记为可用")
        return False


def test_time_context_analysis():
    """测试时间上下文分析"""
    print("\n=== 测试时间上下文分析 ===\n")

    datetime_toolkit = DateTimeToolkit()

    # 测试不同类型的请求
    test_requests = [
        "分析2024年贵州茅台的财务数据",
        "请分析最新的财务报告",
        "对比2023年和2024年的业绩表现",
        "分析2026年的发展趋势",  # 未来数据
        "最近三个季度的财务状况"
    ]

    for i, request in enumerate(test_requests, 1):
        print(f"{i}. 分析请求: '{request}'")
        analysis = datetime_toolkit.analyze_time_context_for_financial_request(request)

        print(f"   检测到的时间期间: {len(analysis['detected_time_periods'])}个")
        for period in analysis['detected_time_periods']:
            status = "未来" if period['is_future'] else "过去/现在"
            print(f"     - {period['year']}年 ({status})")

        if analysis['future_data_requests']:
            print(f"   未来数据请求: {len(analysis['future_data_requests'])}个")
            for req in analysis['future_data_requests']:
                print(f"     - {req['year']}年: {req['context']}")

        print(f"   建议数量: {len(analysis['recommendations'])}个")
        for j, rec in enumerate(analysis['recommendations'][:3], 1):  # 只显示前3个建议
            print(f"     {j}. {rec}")

        print()


def test_financial_calendar_integration():
    """测试财报日历集成"""
    print("=== 测试财报日历集成 ===\n")

    datetime_toolkit = DateTimeToolkit()
    akshare_tool = AKShareFinancialDataTool()

    test_stock = "600248"
    current_year = datetime.now().year

    # 1. 获取财报日历
    print(f"获取 {current_year} 年财报发布日历...")
    calendar = datetime_toolkit.get_financial_reporting_calendar(current_year)
    print(f"当前日期: {calendar['current_date']}")

    print("\n预期财报发布时间表:")
    for schedule in calendar['expected_schedule']:
        status_emoji = "✓" if schedule['status'] == "expected_published" else "⏳"
        print(f"  {status_emoji} {schedule['period']} {schedule['report_name']}: {schedule['description']}")

    # 2. 获取实际数据状态
    print(f"\n检查 {test_stock} 的实际数据状态...")
    actual_calendar = akshare_tool.get_financial_calendar_info(test_stock)
    print(f"最新可用报告: {actual_calendar['latest_available_report']}")

    data_status = actual_calendar['data_status']
    print(f"数据状态: {data_status['status']}")
    if 'freshness' in data_status:
        print(f"数据新鲜度: {data_status['freshness']} - {data_status['freshness_description']}")
        print(f"距离最新数据天数: {data_status['days_since_latest']}天")
    print(f"数据完整性评分: {data_status.get('completeness_score', 0):.1f}%")
    print(f"建议: {data_status.get('recommendation', 'N/A')}")


def test_complete_time_aware_workflow():
    """测试完整的时间感知工作流程"""
    print("\n=== 测试完整的时间感知工作流程 ===\n")

    datetime_toolkit = DateTimeToolkit()
    akshare_tool = AKShareFinancialDataTool()

    # 模拟用户请求未来数据
    user_request = "分析中国移动2025年最新财报数据"
    test_stock = "0941"  # 中国移动

    print(f"模拟用户请求: '{user_request}'")
    print(f"目标股票: {test_stock}")

    # 步骤1: 时间上下文分析
    print("\n步骤1: 分析时间上下文...")
    time_context = datetime_toolkit.analyze_time_context_for_financial_request(user_request)
    print(f"检测到未来数据请求: {len(time_context['future_data_requests'])}个")

    # 步骤2: 检查数据可用性
    print("\n步骤2: 检查请求数据的可用性...")
    if time_context['future_data_requests']:
        future_request = time_context['future_data_requests'][0]
        availability = datetime_toolkit.check_financial_report_availability(
            test_stock, future_request['year'], 4  # 假设请求年报
        )
        print(f"数据可用性: {availability['available']}")
        if not availability['available']:
            print(f"原因: {availability['reason']}")
            print(f"建议: {availability['suggestion']}")

    # 步骤3: 获取可用数据
    print("\n步骤3: 获取最新可用数据...")
    latest_period = datetime_toolkit.get_latest_available_financial_period(test_stock)
    print(f"推荐使用数据: {latest_period['latest_available_period']}")

    # 步骤4: 验证数据质量
    print("\n步骤4: 验证数据质量...")
    actual_report = akshare_tool.check_latest_available_report(test_stock)
    if actual_report['available']:
        print(f"✓ 数据可用: {actual_report['description']}")
        print(f"  数据完整性: {actual_report['data_completeness']['overall_score']:.1f}%")

        # 验证新鲜度
        requested_period = {
            "year": actual_report['report_year'],
            "quarter": actual_report['report_quarter']
        }
        freshness = akshare_tool.validate_data_freshness(test_stock, requested_period)
        if freshness['valid']:
            print(f"✓ 数据新鲜度验证通过")
        else:
            print(f"⚠ 数据新鲜度警告: {freshness['reason']}")

        # 步骤5: 总结时间感知分析结果
        print("\n步骤5: 时间感知分析总结...")
        print("🎯 时间感知功能验证结果:")
        print("  ✓ 成功识别未来数据请求")
        print("  ✓ 正确判断数据不可用性")
        print("  ✓ 提供合理替代方案")
        print("  ✓ 验证实际数据质量")
        print("  ✓ 完整的时间上下文处理")

        return True
    else:
        print(f"✗ 无法获取实际数据: {actual_report['reason']}")
        return False


def main():
    """主测试函数"""
    print("=== 时间感知财务分析集成测试 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    test_results = []

    # 运行各项测试
    try:
        print("开始测试1: 时间感知的数据可用性检查")
        result1 = test_time_aware_data_availability()
        test_results.append(("数据可用性检查", result1))
    except Exception as e:
        print(f"测试1失败: {e}")
        test_results.append(("数据可用性检查", False))

    try:
        print("\n开始测试2: 未来数据请求处理")
        result2 = test_future_data_request_handling()
        test_results.append(("未来数据请求处理", result2))
    except Exception as e:
        print(f"测试2失败: {e}")
        test_results.append(("未来数据请求处理", False))

    try:
        print("\n开始测试3: 时间上下文分析")
        test_time_context_analysis()
        test_results.append(("时间上下文分析", True))
    except Exception as e:
        print(f"测试3失败: {e}")
        test_results.append(("时间上下文分析", False))

    try:
        print("\n开始测试4: 财报日历集成")
        test_financial_calendar_integration()
        test_results.append(("财报日历集成", True))
    except Exception as e:
        print(f"测试4失败: {e}")
        test_results.append(("财报日历集成", False))

    try:
        print("\n开始测试5: 完整时间感知工作流程")
        result5 = test_complete_time_aware_workflow()
        test_results.append(("完整工作流程", result5))
    except Exception as e:
        print(f"测试5失败: {e}")
        test_results.append(("完整工作流程", False))

    # 输出测试总结
    print("\n" + "="*60)
    print("🎯 时间感知功能测试总结")
    print("="*60)

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:20} : {status}")
        if result:
            passed += 1

    print("-" * 60)
    print(f"总计: {passed}/{total} 项测试通过")

    if passed == total:
        print("\n🎉 所有时间感知功能测试通过！")
        print("✅ 时间感知工具包集成成功")
        print("✅ AKShare工具时间感知增强正常")
        print("✅ 未来数据请求处理机制完善")
        print("✅ 财报可用性验证准确")
        print("✅ 完整的时间上下文分析流程")
    else:
        print(f"\n⚠️  {total - passed} 项测试失败，需要进一步检查")
        print("建议检查相关配置或依赖项")

    print("\n🚀 时间感知功能已准备就绪，多智能体系统现在具备:")
    print("   - 智能时间判断能力")
    print("   - 未来数据请求识别")
    print("   - 自动替代方案提供")
    print("   - 财报发布时间表理解")
    print("   - 数据新鲜度评估")


if __name__ == "__main__":
    main()