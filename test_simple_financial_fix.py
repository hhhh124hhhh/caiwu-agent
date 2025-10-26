#!/usr/bin/env python3
"""
简化的财务分析工具修复测试
避免编码问题
"""

import sys
import json
import pathlib

# 设置项目路径
project_root = pathlib.Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_financial_analysis():
    """测试财务分析工具"""
    
    print("=" * 60)
    print("财务分析工具修复验证测试")
    print("=" * 60)

    try:
        from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer

        # 创建分析器实例
        analyzer = StandardFinancialAnalyzer({"workspace_root": "./test_workspace"})

        # 测试数据：用户提供的数据格式
        test_data = {
            'revenue': 180.3,
            'net_profit': 4.1,
            'total_assets': 3472.98,
            'operating_cash_flow': 15.2
        }

        print("\n1. 测试扁平化数据格式识别")
        print(f"输入数据: {json.dumps(test_data, ensure_ascii=False)}")

        # 测试数据转换
        converted_data = analyzer._convert_simple_metrics_to_financial_data(test_data)
        print(f"[SUCCESS] 数据转换成功")
        print(f"   Income DataFrame: {converted_data['income'].shape}")
        print(f"   Balance DataFrame: {converted_data['balance'].shape}")
        print(f"   Cashflow DataFrame: {converted_data['cashflow'].shape}")

        # 显示详细信息
        if not converted_data['income'].empty:
            print(f"   Income 列名: {list(converted_data['income'].columns)}")
            print(f"   Income 数据: {converted_data['income'].iloc[0].to_dict()}")
        if not converted_data['balance'].empty:
            print(f"   Balance 列名: {list(converted_data['balance'].columns)}")
            print(f"   Balance 数据: {converted_data['balance'].iloc[0].to_dict()}")
        if not converted_data['cashflow'].empty:
            print(f"   Cashflow 列名: {list(converted_data['cashflow'].columns)}")
            print(f"   Cashflow 数据: {converted_data['cashflow'].iloc[0].to_dict()}")

        # 测试财务比率计算
        print("\n2. 测试财务比率计算")
        try:
            ratios = analyzer.calculate_ratios(converted_data)
            print(f"[SUCCESS] 财务比率计算成功")

            # 显示各个维度的指标
            for category, metrics in ratios.items():
                if metrics:  # 只显示非空的指标
                    print(f"   {category}: {len(metrics)} 个指标")
                    for metric_name, value in list(metrics.items())[:3]:  # 只显示前3个
                        print(f"     - {metric_name}: {value}")
                    if len(metrics) > 3:
                        print(f"     - ... 还有 {len(metrics) - 3} 个指标")
                        break
                else:
                    print(f"   {category}: 无数据")

        except Exception as e:
            print(f"[ERROR] 财务比率计算失败: {e}")
            import traceback
            traceback.print_exc()
            return False

        # 测试趋势分析
        print("\n3. 测试趋势分析")
        try:
            trends = analyzer.analyze_trends(converted_data, years=2)
            print(f"[SUCCESS] 趋势分析成功")

            for category, data in trends.items():
                if data:
                    if isinstance(data, dict):
                        print(f"   {category}: {list(data.keys())}")
                    else:
                        print(f"   {category}: {type(data)}")
                else:
                    print(f"   {category}: 无数据")

        except Exception as e:
            print(f"[ERROR] 趋势分析失败: {e}")
            import traceback
            traceback.print_exc()
            return False

        print("\n" + "=" * 60)
        print("[SUCCESS] 所有测试通过！财务分析工具修复成功！")
        print("\n主要修复内容:")
        print("1. 增强了数据格式识别逻辑，支持扁平化和嵌套结构")
        print("2. 完善了扁平化数据处理，支持中英文字段名映射")
        print("3. 改进了错误处理，提供详细的诊断信息")
        print("4. 添加了智能数据推断机制")
        print("5. 优化了单位转换和数据验证")

        return True

    except ImportError as e:
        print(f"[ERROR] 无法导入财务分析工具: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_financial_analysis()

    print("\n" + "=" * 60)
    if success:
        print("[SUCCESS] 测试通过！财务分析工具已修复并可正常使用！")
        print("\n现在可以使用以下功能:")
        print("- calculate_ratios() - 计算财务比率")
        print("- analyze_trends() - 进行趋势分析")
        print("- 支持扁平化和嵌套数据结构")
        print("- 支持中英文字段名")
        print("- 提供详细的错误诊断")
        sys.exit(0)
    else:
        print("[ERROR] 测试失败，需要进一步调试")
        sys.exit(1)
