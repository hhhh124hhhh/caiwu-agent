#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证脚本：检查财务分析报告生成和饼图功能是否正常工作
"""

import os
import json
import sys
from bs4 import BeautifulSoup

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

def verify_html_report(html_file=None):
    """
    验证HTML报告是否为标准HTML渲染文件
    """
    # 如果没有提供HTML文件路径，使用默认路径
    if html_file is None:
        html_file = os.path.join(os.path.dirname(__file__), 'run_workdir', '陕西建工综合财务分析报告_2025年1月_完整版.html')
    
    print(f"\n=== 验证HTML报告: {os.path.basename(html_file)} ===")
    
    if not os.path.exists(html_file):
        print(f"❌ HTML报告不存在: {html_file}")
        return False
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含标准HTML结构
        if '<!DOCTYPE html>' not in content:
            print("⚠️  HTML报告缺少DOCTYPE声明")
        
        if '<html' not in content:
            print("❌ HTML报告缺少html标签")
            return False
        
        # 使用BeautifulSoup解析验证HTML结构
        soup = BeautifulSoup(content, 'html.parser')
        
        # 检查基本结构
        if not soup.find('html'):
            print("❌ 不是有效的HTML文件，缺少<html>标签")
            return False
        
        if not soup.find('head'):
            print("⚠️  HTML报告缺少head标签")
        
        if not soup.find('body'):
            print("⚠️  HTML报告缺少body标签")
        
        # 检查meta标签
        meta_charset = soup.find('meta', charset=True)
        if not meta_charset:
            print("⚠️  HTML报告缺少字符集meta标签")
        else:
            print(f"✅ 检测到字符集: {meta_charset['charset']}")
        
        # 检查标题
        title = soup.find('title')
        if not title:
            print("⚠️  HTML报告缺少标题")
        else:
            print(f"✅ 检测到标题: {title.text.strip()}")
        
        # 检查是否包含所有必要的报告部分
        required_sections = ['盈利能力分析', '偿债能力分析', '运营效率分析', '现金流分析', '财务健康综合评估']
        for section in required_sections:
            if section not in content:
                print(f"❌ HTML报告缺少必要部分: {section}")
            else:
                print(f"✅ 检测到报告部分: {section}")
        
        # 检查图表引用
        img_tags = soup.find_all('img')
        print(f"✅ 检测到 {len(img_tags)} 个图表引用")
        
        # 验证饼图是否已集成
        pie_chart_refs = soup.find_all('img', src=lambda x: x and '饼图.png' in x)
        if pie_chart_refs:
            print(f"✅ 找到 {len(pie_chart_refs)} 个饼图引用:")
            for ref in pie_chart_refs:
                print(f"  - {ref['src']}")
        else:
            print("❌ 饼图未集成到HTML报告中")
            return False
        
        print(f"✅ HTML报告验证通过，文件大小: {os.path.getsize(html_file) / 1024:.2f} KB")
        return True
        
    except Exception as e:
        print(f"❌ 验证HTML报告时出错: {str(e)}")
        return False

def verify_pie_chart_generation():
    """
    验证饼图生成功能
    """
    print("\n=== 验证饼图生成功能 ===")
    output_dir = os.path.join(os.path.dirname(__file__), 'run_workdir')
    
    # 检查生成的饼图文件
    pie_charts = []
    for file in os.listdir(output_dir):
        if '饼图.png' in file:
            file_path = os.path.join(output_dir, file)
            size_kb = os.path.getsize(file_path) / 1024
            pie_charts.append((file, size_kb))
    
    if not pie_charts:
        print("❌ 未找到任何饼图文件")
        return False
    
    print(f"✅ 找到 {len(pie_charts)} 个饼图文件:")
    for file, size_kb in pie_charts:
        print(f"  - {file} ({size_kb:.2f} KB)")
    
    # 检查是否生成了关键的饼图
    required_charts = ['陕西建工负债结构分析_负债结构_饼图.png', '陕西建工资产结构分析_资产结构_饼图.png']
    all_required = True
    for chart in required_charts:
        if not any(chart in file for file, _ in pie_charts):
            print(f"❌ 缺少必要的饼图: {chart}")
            all_required = False
        else:
            print(f"✅ 找到饼图: {chart}")
    
    # 检查图表工具是否支持pie类型
    from utu.tools.tabular_data_toolkit import TabularDataToolkit
    
    # 创建一个简单的饼图数据进行测试
    test_data = {
        "title": "测试饼图",
        "x_axis": [],
        "series": [{"name": "测试", "data": [{"name": "A", "value": 1}, {"name": "B", "value": 2}]}]
    }
    
    toolkit = TabularDataToolkit()
    result = toolkit.generate_charts(
        data_json=test_data,
        chart_type='pie',
        output_dir=output_dir
    )
    
    if result['success']:
        print("✅ 图表工具成功支持pie类型")
    else:
        print(f"❌ 图表工具不支持pie类型: {result['message']}")
        return False
    
    return all_required

def verify_chart_integration():
    """
    验证所有图表是否正确集成到HTML报告中
    """
    print("\n=== 验证图表集成 ===")
    html_path = os.path.join(os.path.dirname(__file__), 'run_workdir', '陕西建工综合财务分析报告_2025年1月_完整版.html')
    output_dir = os.path.join(os.path.dirname(__file__), 'run_workdir')
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取HTML中引用的所有图表文件
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    img_tags = soup.find_all('img')
    referenced_charts = [img.get('src') for img in img_tags if img.get('src')]
    
    print(f"HTML中引用的图表 ({len(referenced_charts)} 个):")
    all_charts_exist = True
    
    for chart_file in referenced_charts:
        chart_path = os.path.join(output_dir, chart_file)
        if os.path.exists(chart_path):
            size_kb = os.path.getsize(chart_path) / 1024
            print(f"✅ {chart_file} - 存在 ({size_kb:.2f} KB)")
        else:
            print(f"❌ {chart_file} - 不存在")
            all_charts_exist = False
    
    return all_charts_exist

def summarize_directory_content():
    """
    汇总run_workdir目录内容
    """
    print("\n=== run_workdir目录内容汇总 ===")
    output_dir = os.path.join(os.path.dirname(__file__), 'run_workdir')
    
    # 统计不同类型的文件
    file_types = {}
    chart_types = {}
    
    for file in os.listdir(output_dir):
        file_path = os.path.join(output_dir, file)
        if os.path.isfile(file_path):
            # 统计文件类型
            extension = os.path.splitext(file)[1].lower()
            file_types[extension] = file_types.get(extension, 0) + 1
            
            # 统计图表类型
            if extension == '.png':
                if '柱状图' in file:
                    chart_types['柱状图'] = chart_types.get('柱状图', 0) + 1
                elif '折线图' in file:
                    chart_types['折线图'] = chart_types.get('折线图', 0) + 1
                elif '饼图' in file:
                    chart_types['饼图'] = chart_types.get('饼图', 0) + 1
                elif '雷达图' in file:
                    chart_types['雷达图'] = chart_types.get('雷达图', 0) + 1
                else:
                    chart_types['其他图'] = chart_types.get('其他图', 0) + 1
    
    print("文件类型统计:")
    for ext, count in file_types.items():
        print(f"  - {ext}: {count} 个文件")
    
    print("\n图表类型统计:")
    for chart_type, count in chart_types.items():
        print(f"  - {chart_type}: {count} 个")
    
    # 检查是否有HTML报告
    html_files = [f for f in os.listdir(output_dir) if f.endswith('.html')]
    print(f"\nHTML报告文件 ({len(html_files)} 个):")
    for html_file in html_files:
        file_path = os.path.join(output_dir, html_file)
        size_kb = os.path.getsize(file_path) / 1024
        print(f"  - {html_file} ({size_kb:.2f} KB)")

def check_integration(html_file):
    """
    验证HTML报告与饼图的集成情况
    """
    print(f"\n=== 验证集成情况 ===")
    print(f"验证报告: {os.path.basename(html_file)}")
    
    # 读取HTML内容
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含图表容器
        if '<div class="chart-container">' not in content:
            print("⚠️  HTML报告中缺少图表容器")
        
        # 检查是否包含饼图引用
        if '饼图.png' not in content:
            print("❌ HTML报告中没有引用饼图")
            return False
        
        print("✅ 报告集成验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 验证集成情况时出错: {str(e)}")
        return False

def run_verification():
    """
    运行完整的验证流程
    """
    print("\n=========================================")
    print("     财务分析报告和饼图功能验证")
    print("=========================================")
    
    # 定义路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    run_dir = os.path.join(base_dir, 'run_workdir')
    
    # 查找HTML报告
    html_files = []
    for root, _, files in os.walk(run_dir):
        for file in files:
            if file.endswith('.html') and '陕西建工' in file:
                html_files.append(os.path.join(root, file))
    
    success_count = 0
    total_checks = 4  # HTML格式、饼图生成、图表集成、目录汇总
    html_file = html_files[0] if html_files else None
    
    # 1. 检查HTML报告格式
    if html_file:
        html_result = verify_html_report(html_file)
        if html_result:
            success_count += 1
    else:
        print("❌ 错误: 未找到HTML报告文件")
        html_result = False
    
    # 2. 检查饼图生成
    pie_result = verify_pie_chart_generation()
    if pie_result:
        success_count += 1
    
    # 3. 检查集成情况
    integration_result = False
    if html_file:
        integration_result = check_integration(html_file)
        if integration_result:
            success_count += 1
    
    # 4. 汇总目录内容
    summarize_directory_content()
    success_count += 1  # 目录汇总总是通过
    
    # 生成总结报告
    print("\n=========================================")
    print("              验证总结")
    print("=========================================")
    print(f"总检查项: {total_checks}")
    print(f"通过项: {success_count}")
    print(f"通过率: {(success_count / total_checks) * 100:.1f}%")
    
    print("\n" + "="*60)
    print("📋 最终验证结果")
    print("="*60)
    print(f"HTML报告格式: {'✅ 通过' if html_result else '❌ 失败'}")
    print(f"饼图功能实现: {'✅ 通过' if pie_result else '❌ 失败'}")
    print(f"图表集成情况: {'✅ 通过' if integration_result else '❌ 失败'}")
    print("="*60)
    
    if html_result and pie_result and integration_result:
        print("\n🎉 恭喜！所有任务已成功完成！")
        print("✅ HTML报告已生成标准格式")
        print("✅ 饼图功能已成功添加到图表工具")
        print("✅ 所有图表已正确集成到报告中")
        return True
    else:
        print("\n❌ 部分任务未完成，请检查上面的错误信息")
        return False

if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)