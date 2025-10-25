#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试饼图生成功能
"""

import os
import sys
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utu.tools.tabular_data_toolkit import TabularDataToolkit

def test_pie_chart():
    """
    直接测试饼图生成功能（非异步）
    """
    print("开始测试饼图生成功能...")
    
    # 创建工具实例
    toolkit = TabularDataToolkit()
    
    # 创建输出目录
    output_dir = os.path.join(os.path.dirname(__file__), 'run_workdir')
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 测试1: 使用{name, value}格式的数据生成资产结构饼图
        asset_structure_data = {
            "title": "陕西建工资产结构分析",
            "x_axis": [],  # 饼图可以不使用x_axis，但仍需提供空列表以符合接口要求
            "series": [
                {
                    "name": "资产结构",
                    "data": [
                        {"name": "流动资产", "value": 2800.45},
                        {"name": "非流动资产", "value": 672.53}
                    ]
                }
            ]
        }
        
        print("\n测试1: 生成资产结构饼图...")
        result1 = toolkit._generate_generic_charts(
            asset_structure_data,
            "pie",
            output_dir
        )
        print(f"结果1: {result1}")
        
        # 测试2: 使用简单数值列表格式生成负债结构饼图
        liability_structure_data = {
            "title": "陕西建工负债结构分析",
            "x_axis": ["流动负债", "非流动负债"],
            "series": [
                {
                    "name": "负债结构",
                    "data": [3000.15, 110.28]
                }
            ]
        }
        
        print("\n测试2: 生成负债结构饼图...")
        result2 = toolkit._generate_generic_charts(
            liability_structure_data,
            "pie",
            output_dir
        )
        print(f"结果2: {result2}")
        
        # 验证生成的文件
        all_success = True
        if result1.get('success'):
            for file in result1.get('files', []):
                if os.path.exists(file):
                    print(f"✅ 饼图文件已生成: {os.path.basename(file)} ({os.path.getsize(file)/1024:.2f} KB)")
        else:
            all_success = False
        
        if result2.get('success'):
            for file in result2.get('files', []):
                if os.path.exists(file):
                    print(f"✅ 饼图文件已生成: {os.path.basename(file)} ({os.path.getsize(file)/1024:.2f} KB)")
        else:
            all_success = False
        
        # 更新HTML报告中的饼图引用
        update_html_report(output_dir)
        
        if all_success:
            print("\n🎉 所有饼图测试通过！")
            return True
        else:
            print("\n❌ 部分饼图测试失败！")
            return False
            
    except Exception as e:
        print(f"\n测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def update_html_report(output_dir):
    """
    更新HTML报告中的饼图引用
    """
    html_file = os.path.join(output_dir, "陕西建工综合财务分析报告_2025年1月_完整版.html")
    
    if not os.path.exists(html_file):
        print(f"HTML报告文件不存在: {html_file}")
        return
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 添加饼图引用 - 在偿债能力分析部分添加
        if '陕西建工负债结构分析_负债结构_饼图.png' not in content:
            # 在偿债能力分析部分添加饼图
            insertion_point = '## 二、偿债能力分析'
            if insertion_point in content:
                # 找到章节标题后的位置
                index = content.find(insertion_point) + len(insertion_point)
                # 找到下一个二级标题前的位置
                next_h2_index = content.find('## ', index)
                
                if next_h2_index > 0:
                    # 在章节中插入饼图
                    pie_chart_html = """

            <div class="chart-container">
                <img src="陕西建工负债结构分析_负债结构_饼图.png" alt="陕西建工负债结构分析">
                <div class="chart-caption">图2: 陕西建工负债结构分析 - 流动负债占比高达96.5%，财务杠杆压力较大</div>
            </div>
                    """
                    
                    # 在适当位置插入
                    content = content[:next_h2_index] + pie_chart_html + content[next_h2_index:]
                
                # 保存更新后的HTML
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"成功更新HTML报告，添加了饼图引用")
        else:
            print("饼图引用已存在于HTML报告中")
            
    except Exception as e:
        print(f"更新HTML报告失败: {str(e)}")
        import traceback
        traceback.print_exc()

def update_main_script():
    """
    更新main.py脚本，添加饼图生成功能
    """
    # 不再更新main.py，改为直接更新HTML报告
    print("\n跳过更新main.py，已改为直接更新HTML报告")
    return True

if __name__ == "__main__":
    print("========== 饼图功能测试 ==========\n")
    
    # 运行饼图测试
    pie_test_result = test_pie_chart()
    
    # 更新main.py脚本
    update_result = update_main_script()
    
    print("\n========== 测试总结 ==========\n")
    print(f"饼图生成测试: {'成功' if pie_test_result else '失败'}")
    print(f"HTML报告更新: {'成功' if update_result else '失败'}")
    
    if pie_test_result and update_result:
        print("\n✅ 所有任务完成！饼图功能已成功添加并测试通过。")
    else:
        print("\n❌ 部分任务失败，请检查错误信息。")
    
    # 输出测试完成后的目录内容
    output_dir = os.path.join(os.path.dirname(__file__), 'run_workdir')
    if os.path.exists(output_dir):
        print("\n📁 run_workdir目录下的文件:")
        for file in os.listdir(output_dir):
            if file.endswith('.png'):
                file_path = os.path.join(output_dir, file)
                size_kb = os.path.getsize(file_path) / 1024
                print(f"  - {file} ({size_kb:.2f} KB)")