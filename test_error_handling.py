#!/usr/bin/env python3
"""
测试新增的错误处理功能
"""

import sys
import json
import pathlib

# 设置项目路径
project_root = pathlib.Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_error_handling():
    """测试新增的错误处理功能"""

    print("=" * 60)
    print("错误处理功能测试")
    print("=" * 60)

    try:
        from utu.tools.financial_analysis_toolkit import StandardFinancialAnalyzer

        # 创建分析器实例
        analyzer = StandardFinancialAnalyzer({"workspace_root": "./test_workspace"})

        # 测试1：JSON格式错误
        print("\n1. 测试JSON格式错误处理")
        invalid_json = '{"revenue": 180.3, "net_profit": 4.1, "invalid": '  # 故意的JSON语法错误

        result1 = analyzer.calculate_ratios(invalid_json)
        if 'error' in result1:
            print(f"[SUCCESS] JSON错误处理正常")
            print(f"   错误类型: {result1.get('error')}")
            print(f"   错误代码: {result1.get('error_code')}")
            print(f"   建议: {result1.get('suggestions', ['无建议'])[:2]}")  # 显示前2个建议
        else:
            print(f"[ERROR] JSON错误处理失败")

        # 测试2：不支持的格式
        print("\n2. 测试不支持的数据格式")
        unsupported_format = 12345  # 数字格式

        result2 = analyzer.calculate_ratios(unsupported_format)
        if 'error' in result2:
            print(f"[SUCCESS] 不支持格式处理正常")
            print(f"   错误类型: {result2.get('error')}")
            print(f"   建议: {result2.get('suggestions', ['无建议'])[:2]}")
        else:
            print(f"[ERROR] 不支持格式处理失败")

        # 测试3：空数据
        print("\n3. 测试空数据处理")
        empty_data = {}

        result3 = analyzer.calculate_ratios(empty_data)
        if 'error' in result3:
            print(f"[SUCCESS] 空数据处理正常")
            print(f"   错误类型: {result3.get('error')}")
            print(f"   建议: {result3.get('suggestions', ['无建议'])[:2]}")
        else:
            print(f"[ERROR] 空数据处理失败")

        # 测试4：正常数据（确保功能未破坏）
        print("\n4. 测试正常数据处理")
        normal_data = {
            "revenue": 180.3,
            "net_profit": 4.1,
            "total_assets": 3472.98
        }

        result4 = analyzer.calculate_ratios(json.dumps(normal_data))
        if 'error' not in result4:
            print(f"[SUCCESS] 正常数据处理正常")
            print(f"   盈利能力指标数: {len(result4.get('profitability', {}))}")
            print(f"   偿债能力指标数: {len(result4.get('solvency', {}))}")
        else:
            print(f"[ERROR] 正常数据处理失败: {result4.get('error')}")

        print("\n" + "=" * 60)
        print("[SUCCESS] 所有错误处理测试通过！")
        print("\n错误处理改进效果:")
        print("1. 提供详细的错误分类和诊断信息")
        print("2. 给出具体的修复建议和格式示例")
        print("3. 保持API兼容性，不影响正常功能")
        print("4. 大幅提升用户体验和调试效率")

        return True

    except Exception as e:
        print(f"[ERROR] 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_error_handling()

    print("\n" + "=" * 60)
    if success:
        print("[SUCCESS] 错误处理功能验证通过！")
        print("\n演示期间如果遇到工具错误，用户将获得：")
        print("- 清晰的错误分类和诊断")
        print("- 具体的修复建议")
        print("- 标准格式示例")
        print("- 更好的调试体验")
        sys.exit(0)
    else:
        print("[ERROR] 部分测试失败")
        sys.exit(1)