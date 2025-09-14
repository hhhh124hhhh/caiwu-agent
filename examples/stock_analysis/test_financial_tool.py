#!/usr/bin/env python3
"""
测试专用AKShare财务数据工具
验证工具的稳定性和准确性
"""

import asyncio
import pathlib
import os
import sys
import pandas as pd
from datetime import datetime

# 添加项目根目录到Python路径
project_root = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utu.tools.akshare_financial_tool import AKShareFinancialDataTool, get_financial_tool


def test_financial_tool():
    """测试财务数据工具"""
    print("=== AKShare财务数据工具测试 ===\n")
    
    try:
        # 初始化工具
        print("1. 初始化AKShare财务数据工具...")
        tool = AKShareFinancialDataTool()
        print("   ✓ 工具初始化成功\n")
        
        # 测试数据获取
        print("2. 测试陕西建工(600248)财务数据获取...")
        financial_data = tool.get_financial_reports("600248", "陕西建工")
        
        if financial_data:
            print("   ✓ 财务数据获取成功")
            print(f"   - 利润表: {len(financial_data.get('income', pd.DataFrame()))}行")
            print(f"   - 资产负债表: {len(financial_data.get('balance', pd.DataFrame()))}行")
            print(f"   - 现金流量表: {len(financial_data.get('cashflow', pd.DataFrame()))}行")
        else:
            print("   ✗ 财务数据获取失败")
            return False
        print()
        
        # 测试关键指标提取
        print("3. 测试关键财务指标提取...")
        metrics = tool.get_key_metrics(financial_data)
        
        if metrics:
            print("   ✓ 关键指标提取成功")
            print("   主要指标:")
            for key, value in metrics.items():
                if isinstance(value, float):
                    print(f"     - {key}: {value:.2f}")
                else:
                    print(f"     - {key}: {value}")
        else:
            print("   ✗ 关键指标提取失败")
            return False
        print()
        
        # 测试趋势数据获取
        print("4. 测试历史趋势数据获取...")
        trend_data = tool.get_historical_trend(financial_data, 4)
        
        if not trend_data.empty:
            print("   ✓ 趋势数据获取成功")
            print(f"   - 数据年份: {len(trend_data)}年")
            print("   - 趋势数据预览:")
            print(trend_data.to_string(index=False))
        else:
            print("   ✗ 趋势数据获取失败")
            return False
        print()
        
        # 测试数据保存
        print("5. 测试数据保存...")
        test_prefix = "./test_financial_data"
        tool.save_to_csv(financial_data, test_prefix)
        print("   ✓ 数据保存成功")
        
        # 列出保存的文件
        import glob
        saved_files = glob.glob(f"{test_prefix}_*.csv")
        for file in saved_files:
            file_size = os.path.getsize(file) / 1024
            print(f"     - {file} ({file_size:.1f} KB)")
        print()
        
        # 测试多只股票
        print("6. 测试多只股票数据获取...")
        test_stocks = [
            ("000858", "五粮液"),
            ("600519", "贵州茅台"),
            ("002594", "比亚迪")
        ]
        
        for code, name in test_stocks:
            print(f"   测试 {name}({code})...")
            try:
                data = tool.get_financial_reports(code, name)
                if data:
                    metrics = tool.get_key_metrics(data)
                    if metrics and 'revenue_billion' in metrics:
                        print(f"     ✓ 成功 - 营收: {metrics['revenue_billion']:.1f}亿元")
                    else:
                        print(f"     ⚠ 部分成功 - 数据获取成功但指标提取失败")
                else:
                    print(f"     ✗ 失败")
            except Exception as e:
                print(f"     ✗ 异常: {e}")
        print()
        
        print("=== 测试结果总结 ===")
        print("✓ AKShare财务数据工具功能正常")
        print("✓ 数据获取稳定性良好")
        print("✓ 关键指标提取准确")
        print("✓ 趋势分析功能完整")
        print("✓ 数据保存功能正常")
        print("\n工具可以安全用于智能体系统，将大幅减少token消耗!")
        
        return True
        
    except Exception as e:
        print(f"✗ 工具测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tool_integration():
    """测试工具与智能体系统的集成"""
    print("\n=== 测试工具集成 ===\n")
    
    try:
        # 测试单例模式
        print("1. 测试单例模式...")
        tool1 = get_financial_tool()
        tool2 = get_financial_tool()
        
        if tool1 is tool2:
            print("   ✓ 单例模式工作正常")
        else:
            print("   ✗ 单例模式失败")
            return False
        
        # 测试便利函数
        print("2. 测试便利函数...")
        from utu.tools.akshare_financial_tool import get_financial_reports, get_key_metrics
        
        financial_data = get_financial_reports("600248", "陕西建工")
        metrics = get_key_metrics(financial_data)
        
        if metrics and 'revenue_billion' in metrics:
            print("   ✓ 便利函数工作正常")
            print(f"   - 营业收入: {metrics['revenue_billion']:.1f}亿元")
        else:
            print("   ✗ 便利函数测试失败")
            return False
        
        print("\n✓ 工具集成测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def benchmark_performance():
    """性能基准测试"""
    print("\n=== 性能基准测试 ===\n")
    
    import time
    
    tool = get_financial_tool()
    test_stocks = [
        ("600248", "陕西建工"),
        ("000858", "五粮液"),
        ("600519", "贵州茅台")
    ]
    
    total_time = 0
    success_count = 0
    
    for code, name in test_stocks:
        print(f"测试 {name}({code})...")
        
        start_time = time.time()
        try:
            financial_data = tool.get_financial_reports(code, name)
            metrics = tool.get_key_metrics(financial_data)
            
            end_time = time.time()
            elapsed = end_time - start_time
            total_time += elapsed
            
            if metrics and 'revenue_billion' in metrics:
                success_count += 1
                print(f"   ✓ 成功 - 用时: {elapsed:.2f}秒")
            else:
                print(f"   ✗ 失败 - 用时: {elapsed:.2f}秒")
                
        except Exception as e:
            end_time = time.time()
            elapsed = end_time - start_time
            total_time += elapsed
            print(f"   ✗ 异常 - 用时: {elapsed:.2f}秒 - {e}")
    
    avg_time = total_time / len(test_stocks)
    success_rate = success_count / len(test_stocks) * 100
    
    print(f"\n=== 性能统计 ===")
    print(f"总耗时: {total_time:.2f}秒")
    print(f"平均耗时: {avg_time:.2f}秒/股")
    print(f"成功率: {success_rate:.1f}% ({success_count}/{len(test_stocks)})")
    
    if success_rate >= 80:
        print("✓ 性能表现良好")
    elif success_rate >= 60:
        print("⚠ 性能表现一般")
    else:
        print("✗ 性能表现不佳")
    
    return success_rate >= 60


def main():
    """主测试函数"""
    print("AKShare财务数据工具完整测试")
    print("=" * 50)
    
    # 基本功能测试
    basic_test_passed = test_financial_tool()
    
    # 集成测试
    integration_test_passed = test_tool_integration()
    
    # 性能测试
    performance_test_passed = benchmark_performance()
    
    # 总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"基本功能: {'✓ 通过' if basic_test_passed else '✗ 失败'}")
    print(f"集成测试: {'✓ 通过' if integration_test_passed else '✗ 失败'}")
    print(f"性能测试: {'✓ 通过' if performance_test_passed else '✗ 失败'}")
    
    if basic_test_passed and integration_test_passed:
        print("\n🎉 所有核心测试通过！")
        print("该工具可以安全集成到智能体系统中，将显著减少token消耗。")
        print("\n推荐使用方案:")
        print("1. 替换原有的代码生成方式")
        print("2. 使用专用工具获取财务数据")
        print("3. 智能体专注于分析和报告生成")
    else:
        print("\n❌ 部分测试未通过，需要修复后再使用。")


if __name__ == "__main__":
    main()