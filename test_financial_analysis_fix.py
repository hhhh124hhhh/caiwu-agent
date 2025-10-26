#!/usr/bin/env python3
"""
测试财务分析工具修复效果
验证数据格式识别和财务指标计算功能
"""

import sys
import json
import pathlib
from datetime import datetime

# 设置项目路径
project_root = pathlib.Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置环境变量
import os
os.environ.setdefault("PROJECT_ROOT", str(project_root))

def test_financial_analysis_fixes():
    """测试财务分析工具的修复效果"""

    print("=" * 60)
    print("财务分析工具修复验证测试")
    print("=" * 60)

    try:
        from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer

        # 创建分析器实例
        analyzer = StandardFinancialAnalyzer({"workspace_root": "./test_workspace"})

        # 测试用例1：扁平化结构数据（用户提供的数据格式）
        test_data_flat = {
            'revenue': 180.3,
            'net_profit': 4.1,
            'total_assets': 3472.98,
            'operating_cash_flow': 15.2
        }

        print("\n1. 测试扁平化数据格式识别")
        print(f"输入数据: {json.dumps(test_data_flat, ensure_ascii=False)}")

        try:
            # 测试数据转换
            converted_data = analyzer._convert_simple_metrics_to_financial_data(test_data_flat)
            print(f"✅ 数据转换成功")
            print(f"   Income DataFrame: {converted_data['income'].shape}")
            print(f"   Balance DataFrame: {converted_data['balance'].shape}")
            print(f"   Cashflow DataFrame: {converted_data['cashflow'].shape}")

            if not converted_data['income'].empty:
                print(f"   Income 列名: {list(converted_data['income'].columns)}")
            if not converted_data['balance'].empty:
                print(f"   Balance 列名: {list(converted_data['balance'].columns)}")
            if not converted_data['cashflow'].empty:
                print(f"   Cashflow 列名: {list(converted_data['cashflow'].columns)}")

        except Exception as e:
            print(f"❌ 数据转换失败: {e}")
            import traceback
            traceback.print_exc()
            return False

        # 测试用例2：财务比率计算
        print("\n2. 测试财务比率计算")
        try:
            ratios = analyzer.calculate_ratios(converted_data)
            print(f"✅ 财务比率计算成功")

            # 检查各个维度的指标
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
            print(f"❌ 财务比率计算失败: {e}")
            import traceback
            traceback.print_exc()
            return False

        # 测试用例3：趋势分析
        print("\n3. 测试趋势分析")
        try:
            trends = analyzer.analyze_trends(converted_data, years=2)
            print(f"✅ 趋势分析成功")

            for category, data in trends.items():
                if data:
                    print(f"   {category}: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                else:
                    print(f"   {category}: 无数据")

        except Exception as e:
            print(f"❌ 趋势分析失败: {e}")
            import traceback
            traceback.print_exc()
            return False

        print("\n" + "=" * 60)
        print("🎉 主要测试通过！财务分析工具修复成功！")
        return True

    except ImportError as e:
        print(f"❌ 无法导入财务分析工具: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 运行主要测试
    success = test_financial_analysis_fixes()

    # 输出最终结果
    print("\n" + "=" * 60)
    if success:
        print("🎉 测试通过！财务分析工具已修复并可正常使用！")
        sys.exit(0)
    else:
        print("❌ 测试失败，需要进一步调试")
        sys.exit(1)
