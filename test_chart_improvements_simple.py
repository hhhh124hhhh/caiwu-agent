#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试图表生成工具改进功能
"""

import sys
import os
import json
import traceback

def test_area_chart_support():
    """直接测试area图支持"""
    print("开始测试area图支持...")
    print("=" * 50)
    
    try:
        # 直接导入模块
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utu', 'tools'))
        from tabular_data_toolkit import TabularDataToolkit
        
        toolkit = TabularDataToolkit()
        
        # 测试数据
        test_data = {
            "title": "陕西建工收入与利润趋势",
            "x_axis": ["2021", "2022", "2023", "2024"],
            "series": [
                {"name": "营业收入(亿元)", "data": [450.23, 485.67, 520.15, 573.88]},
                {"name": "净利润(亿元)", "data": [7.23, 8.45, 9.87, 11.04]}
            ]
        }
        
        test_json = json.dumps(test_data, ensure_ascii=False)
        
        # 测试area图
        print("测试area图生成...")
        result = toolkit.generate_charts(test_json, "area", "./test_charts")
        
        print(f"生成结果: {result.get('success', False)}")
        print(f"消息: {result.get('message', '')}")
        
        if result.get('success', False):
            files = result.get('files', [])
            print(f"生成文件: {files}")
            print("area图支持测试: 成功")
            return True
        else:
            print("area图支持测试: 失败")
            return False
            
    except Exception as e:
        print(f"测试异常: {e}")
        traceback.print_exc()
        return False

def test_error_handling_improvement():
    """测试错误处理改进"""
    print("\n开始测试错误处理改进...")
    print("=" * 50)
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utu', 'tools'))
        from tabular_data_toolkit import TabularDataToolkit
        
        toolkit = TabularDataToolkit()
        
        # 测试数据
        test_data = {
            "title": "测试图表",
            "x_axis": ["2021", "2022"],
            "series": [{"name": "系列1", "data": [100, 150]}]
        }
        
        test_json = json.dumps(test_data)
        
        # 测试不支持的图表类型
        print("测试不支持的图表类型处理...")
        result = toolkit.generate_charts(test_json, "waterfall", "./test_charts")
        
        print(f"处理结果: {not result.get('success', True)}")
        print(f"消息: {result.get('message', '')}")
        print(f"建议类型: {result.get('suggested_chart_type', '无')}")
        print(f"替代工具: {result.get('alternative_tools', [])}")
        
        if result.get('suggested_chart_type') or result.get('alternative_tools'):
            print("错误处理改进测试: 成功")
            return True
        else:
            print("错误处理改进测试: 失败")
            return False
            
    except Exception as e:
        print(f"测试异常: {e}")
        traceback.print_exc()
        return False

def main():
    """运行测试"""
    print("图表生成工具改进功能测试")
    print("=" * 50)
    
    test_results = {}
    
    try:
        test_results['area_chart'] = test_area_chart_support()
        test_results['error_handling'] = test_error_handling_improvement()
        
        print("\n" + "=" * 50)
        print("测试总结")
        print("=" * 50)
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        print(f"测试结果: {passed_tests}/{total_tests} 通过")
        
        for test_name, passed in test_results.items():
            status = "通过" if passed else "失败"
            print(f"  {test_name}: {status}")
        
        if passed_tests == total_tests:
            print("\n图表生成工具改进成功!")
            print("主要改进:")
            print("1. 添加了area图支持")
            print("2. 改进了错误处理机制")
            print("3. 提供了智能替代建议")
            print("4. 增强了用户体验")
        else:
            print(f"\n部分改进需要进一步完善")
            
    except Exception as e:
        print(f"测试过程出错: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()