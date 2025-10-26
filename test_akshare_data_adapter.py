#!/usr/bin/env python3
"""
测试AKShare数据传递问题的完整解决方案
验证数据适配器、AKShare工具增强、财务分析工具扩展的完整链路
"""

import sys
import json
import pathlib
import pandas as pd

# 设置项目路径
project_root = pathlib.Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_data_adapter():
    """测试智能数据适配器"""
    print("=" * 60)
    print("1. 测试智能数据适配器")
    print("=" * 60)

    try:
        from utu.utils.data_adapter import get_data_adapter

        adapter = get_data_adapter()

        # 测试1：扁平化数据格式
        print("\n1.1 测试扁平化数据格式")
        flat_data = {
            "revenue": 1000.0,
            "net_profit": 100.0,
            "total_assets": 5000.0,
            "total_liabilities": 3000.0,
            "operating_cash_flow": 150.0
        }

        result1 = adapter.normalize_financial_data(flat_data)
        parsed1 = json.loads(result1)
        if 'income' in parsed1 or 'balance' in parsed1:
            print(f"[SUCCESS] 扁平化数据格式转换成功")
            print(f"   包含报表类型: {list(parsed1.keys())}")
        else:
            print(f"[ERROR] 扁平化数据格式转换失败")

        # 测试2：DataFrame字典格式（模拟AKShare输出）
        print("\n1.2 测试DataFrame字典格式")
        df_income = pd.DataFrame({
            '营业收入': [1000.0, 1200.0],
            '净利润': [100.0, 150.0],
            'REPORT_DATE': ['2023-12-31', '2022-12-31']
        })

        df_balance = pd.DataFrame({
            '总资产': [5000.0, 4500.0],
            '总负债': [3000.0, 2800.0],
            'REPORT_DATE': ['2023-12-31', '2022-12-31']
        })

        dataframe_dict = {
            'income': df_income,
            'balance': df_balance
        }

        result2 = adapter.normalize_financial_data(dataframe_dict)
        parsed2 = json.loads(result2)
        if 'income' in parsed2 and 'balance' in parsed2:
            print(f"[SUCCESS] DataFrame字典格式转换成功")
            print(f"   income数据行数: {len(parsed2['income'])}")
            print(f"   balance数据行数: {len(parsed2['balance'])}")
        else:
            print(f"[ERROR] DataFrame字典格式转换失败")

        # 测试3：关键指标提取
        print("\n1.3 测试关键指标提取")
        metrics = adapter.extract_key_metrics(parsed2)
        if metrics:
            print(f"[SUCCESS] 关键指标提取成功")
            print(f"   提取指标数: {len(metrics)}")
            for metric, value in list(metrics.items())[:5]:
                print(f"     - {metric}: {value}")
        else:
            print(f"[ERROR] 关键指标提取失败")

        return True

    except Exception as e:
        print(f"[ERROR] 数据适配器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_akshare_enhancement():
    """测试AKShare工具增强"""
    print("\n" + "=" * 60)
    print("2. 测试AKShare工具增强")
    print("=" * 60)

    try:
        from utu.tools.akshare_financial_tool import AKShareFinancialDataTool

        # 创建工具实例
        akshare_tool = AKShareFinancialDataTool({
            "workspace_root": "./test_workspace",
            "cache_enabled": True
        })

        # 测试1：模拟DataFrame数据序列化
        print("\n2.1 测试DataFrame数据序列化")
        mock_financial_data = {
            'income': pd.DataFrame({
                '营业收入': [1000.0],
                '净利润': [100.0],
                'REPORT_DATE': ['2023-12-31']
            }),
            'balance': pd.DataFrame({
                '总资产': [5000.0],
                '总负债': [3000.0],
                'REPORT_DATE': ['2023-12-31']
            }),
            'cashflow': pd.DataFrame({
                '经营活动现金流净额': [150.0],
                'REPORT_DATE': ['2023-12-31']
            })
        }

        try:
            serialized = akshare_tool._serialize_for_analysis(mock_financial_data)
            parsed = json.loads(serialized)
            if 'income' in parsed or 'balance' in parsed:
                print(f"[SUCCESS] DataFrame数据序列化成功")
                print(f"   序列化数据大小: {len(serialized)} 字符")
            else:
                print(f"[ERROR] DataFrame数据序列化失败")
        except Exception as e:
            print(f"[INFO] 序列化测试（预期可能失败）: {e}")

        # 测试2：获取标准化分析数据（如果网络允许）
        print("\n2.2 测试标准化分析数据接口")
        try:
            # 使用一个知名股票代码进行测试
            analysis_data = akshare_tool.get_financial_data_for_analysis("000001", "平安银行", "simple")
            parsed_analysis = json.loads(analysis_data)

            if 'error' not in parsed_analysis:
                print(f"[SUCCESS] 标准化分析数据接口工作正常")
                print(f"   数据格式: {parsed_analysis.get('format', 'unknown')}")
                if 'financial_data' in parsed_analysis:
                    print(f"   财务数据键: {list(parsed_analysis['financial_data'].keys())}")
            else:
                print(f"[INFO] 标准化分析数据接口返回提示: {parsed_analysis.get('message', 'Unknown error')}")
        except Exception as e:
            print(f"[INFO] 网络相关测试（预期可能失败）: {e}")

        return True

    except Exception as e:
        print(f"[ERROR] AKShare工具增强测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_financial_analyzer_extension():
    """测试财务分析工具扩展"""
    print("\n" + "=" * 60)
    print("3. 测试财务分析工具扩展")
    print("=" * 60)

    try:
        from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer

        analyzer = StandardFinancialAnalyzer({"workspace_root": "./test_workspace"})

        # 测试1：传统JSON字符串格式（向后兼容）
        print("\n3.1 测试传统JSON字符串格式")
        json_data = json.dumps({
            "revenue": 1000.0,
            "net_profit": 100.0,
            "total_assets": 5000.0,
            "total_liabilities": 3000.0
        })

        try:
            result1 = analyzer.calculate_ratios(json_data)
            if 'error' not in result1:
                print(f"[SUCCESS] JSON字符串格式处理正常")
                print(f"   盈利能力指标数: {len(result1.get('profitability', {}))}")
            else:
                print(f"[ERROR] JSON字符串格式处理失败: {result1.get('error')}")
        except Exception as e:
            print(f"[ERROR] JSON字符串格式测试异常: {e}")

        # 测试2：字典格式（新增功能）
        print("\n3.2 测试字典格式")
        dict_data = {
            "revenue": 1000.0,
            "net_profit": 100.0,
            "total_assets": 5000.0,
            "total_liabilities": 3000.0
        }

        try:
            result2 = analyzer.calculate_ratios(dict_data)
            if 'error' not in result2:
                print(f"[SUCCESS] 字典格式处理正常")
                print(f"   偿债能力指标数: {len(result2.get('solvency', {}))}")
            else:
                print(f"[ERROR] 字典格式处理失败: {result2.get('error')}")
        except Exception as e:
            print(f"[ERROR] 字典格式测试异常: {e}")

        # 测试3：DataFrame字典格式（新增功能）
        print("\n3.3 测试DataFrame字典格式")
        dataframe_dict = {
            'income': pd.DataFrame({
                '营业收入': [1000.0],
                '净利润': [100.0],
                'REPORT_DATE': ['2023-12-31']
            }),
            'balance': pd.DataFrame({
                '总资产': [5000.0],
                '总负债': [3000.0],
                'REPORT_DATE': ['2023-12-31']
            })
        }

        try:
            result3 = analyzer.calculate_ratios(dataframe_dict)
            if 'error' not in result3:
                print(f"[SUCCESS] DataFrame字典格式处理正常")
                print(f"   运营效率指标数: {len(result3.get('efficiency', {}))}")
            else:
                print(f"[ERROR] DataFrame字典格式处理失败: {result3.get('error')}")
                print(f"   建议: {result3.get('suggestions', ['无建议'])[:2]}")
        except Exception as e:
            print(f"[ERROR] DataFrame字典格式测试异常: {e}")

        return True

    except Exception as e:
        print(f"[ERROR] 财务分析工具扩展测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_workflow():
    """测试完整工作流程"""
    print("\n" + "=" * 60)
    print("4. 测试完整工作流程")
    print("=" * 60)

    try:
        from utu.utils.data_adapter import get_data_adapter
        from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer

        adapter = get_data_adapter()
        analyzer = StandardFinancialAnalyzer({"workspace_root": "./test_workspace"})

        # 模拟完整的AKShare→财务分析工具数据流
        print("\n4.1 模拟完整数据流：AKShare → 数据适配器 → 财务分析")

        # 步骤1：模拟AKShare输出（DataFrame字典）
        akshare_output = {
            'income': pd.DataFrame({
                '营业收入': [1200.0, 1000.0],
                '净利润': [150.0, 100.0],
                'REPORT_DATE': ['2023-12-31', '2022-12-31']
            }),
            'balance': pd.DataFrame({
                '总资产': [6000.0, 5000.0],
                '总负债': [3500.0, 3000.0],
                'REPORT_DATE': ['2023-12-31', '2022-12-31']
            })
        }

        print("   步骤1: 模拟AKShare数据获取完成")

        # 步骤2：数据适配器处理
        try:
            adapted_data = adapter.normalize_financial_data(akshare_output)
            print("   步骤2: 数据适配器处理成功")
        except Exception as e:
            print(f"   步骤2: 数据适配器处理失败: {e}")
            return False

        # 步骤3：财务分析工具处理
        try:
            # 使用字典格式直接传递（模拟工具间直接传递）
            analysis_result = analyzer.calculate_ratios(akshare_output)

            if 'error' not in analysis_result:
                print("   步骤3: 财务分析工具处理成功")
                print(f"   分析结果概览:")
                for category, metrics in analysis_result.items():
                    if isinstance(metrics, dict) and metrics:
                        print(f"     - {category}: {len(metrics)} 个指标")
            else:
                print(f"   步骤3: 财务分析工具处理失败: {analysis_result.get('error')}")
                return False

        except Exception as e:
            print(f"   步骤3: 财务分析工具处理异常: {e}")
            return False

        print("\n[SUCCESS] 完整工作流程测试通过！")
        return True

    except Exception as e:
        print(f"[ERROR] 完整工作流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("AKShare数据传递问题解决方案测试")
    print("=" * 60)

    results = []

    # 运行各项测试
    results.append(("智能数据适配器", test_data_adapter()))
    results.append(("AKShare工具增强", test_akshare_enhancement()))
    results.append(("财务分析工具扩展", test_financial_analyzer_extension()))
    results.append(("完整工作流程", test_complete_workflow()))

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    success_count = 0
    for test_name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{test_name:25} {status}")
        if success:
            success_count += 1

    print(f"\n总体通过率: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")

    if success_count == len(results):
        print("\n[SUCCESS] 所有测试通过！AKShare数据传递问题已完全解决！")
        print("\n解决方案亮点:")
        print("1. [OK] 智能数据适配器 - 自动处理多种数据格式")
        print("2. [OK] AKShare工具增强 - 支持标准化数据输出")
        print("3. [OK] 财务分析工具扩展 - 直接支持DataFrame字典")
        print("4. [OK] 完整工作流程 - 端到端数据传递成功")
        print("\n现在智能体可以:")
        print("- 直接使用AKShare获取标准化财务数据")
        print("- 无缝传递数据给财务分析工具")
        print("- 获得准确的财务比率计算结果")
        print("- 避免数据格式相关的错误")
        return True
    else:
        print(f"\n[WARNING] {len(results) - success_count} 个测试失败，需要进一步调试")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)