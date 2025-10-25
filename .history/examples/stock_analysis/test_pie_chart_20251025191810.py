import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utu.tools.tabular_data_toolkit import TabularDataToolkit

def test_pie_chart_generation():
    """
    测试饼图生成功能
    """
    print("开始测试饼图生成功能...")
    
    # 创建图表生成器实例
    toolkit = TabularDataToolkit()
    
    # 定义输出目录
    output_dir = os.path.join(os.path.dirname(__file__), 'run_workdir')
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 测试1: 使用{name, value}格式的数据生成资产结构饼图
        print("\n测试1: 生成资产结构饼图（使用{name, value}格式）...")
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
        
        response1 = toolkit.generate_charts(
            data_json=asset_structure_data,
            chart_type='pie',
            output_dir=output_dir
        )
        
        print(f"测试1结果: {response1['success']}")
        if response1['success']:
            print(f"生成的图表文件: {response1['files']}")
        else:
            print(f"错误信息: {response1['message']}")
        
        # 测试2: 使用简单数值列表格式生成负债结构饼图
        print("\n测试2: 生成负债结构饼图（使用数值列表格式）...")
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
        
        response2 = toolkit.generate_charts(
            data_json=liability_structure_data,
            chart_type='pie',
            output_dir=output_dir
        )
        
        print(f"测试2结果: {response2['success']}")
        if response2['success']:
            print(f"生成的图表文件: {response2['files']}")
        else:
            print(f"错误信息: {response2['message']}")
        
        # 测试3: 使用多个系列生成收入结构饼图
        print("\n测试3: 生成收入结构饼图（多个业务板块）...")
        revenue_structure_data = {
            "title": "陕西建工收入结构分析",
            "x_axis": [],
            "series": [
                {
                    "name": "2024年收入构成",
                    "data": [
                        {"name": "房屋建筑工程", "value": 350.67},
                        {"name": "基础设施工程", "value": 120.35},
                        {"name": "房地产开发", "value": 60.86},
                        {"name": "其他业务", "value": 42.00}
                    ]
                }
            ]
        }
        
        response3 = toolkit.generate_charts(
            data_json=revenue_structure_data,
            chart_type='pie',
            output_dir=output_dir
        )
        
        print(f"测试3结果: {response3['success']}")
        if response3['success']:
            print(f"生成的图表文件: {response3['files']}")
        else:
            print(f"错误信息: {response3['message']}")
        
        # 验证生成的文件是否存在
        all_success = response1['success'] and response2['success'] and response3['success']
        generated_files = []
        if all_success:
            generated_files.extend(response1['files'])
            generated_files.extend(response2['files'])
            generated_files.extend(response3['files'])
            
            print("\n验证生成的文件:")
            for file_path in generated_files:
                if os.path.exists(file_path):
                    print(f"✓ 文件存在: {file_path} (大小: {os.path.getsize(file_path)} 字节)")
                else:
                    print(f"✗ 文件不存在: {file_path}")
                    all_success = False
        
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

def update_main_script():
    """
    更新main.py脚本，添加饼图生成功能
    """
    print("\n更新main.py脚本，添加饼图生成功能...")
    main_file_path = os.path.join(os.path.dirname(__file__), 'main.py')
    
    if not os.path.exists(main_file_path):
        print(f"✗ 找不到main.py文件: {main_file_path}")
        return False
    
    try:
        # 读取main.py内容
        with open(main_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已经包含饼图生成代码
        if "chart_type='pie'" in content:
            print("✓ main.py已经包含饼图生成功能")
            return True
        
        # 在图表生成部分添加饼图代码
        if "# 生成财务指标图表" in content:
            # 找到盈利能力趋势图后面的位置
            if "trend_chart = tabular_toolkit.generate_charts" in content:
                # 定义要添加的饼图代码
                pie_chart_code = '''            # 4. 资产结构饼图
            asset_structure_data = {
                "title": "陕西建工资产结构分析",
                "x_axis": [],
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
            asset_chart = tabular_toolkit.generate_charts(
                data_json=asset_structure_data,
                chart_type='pie',
                output_dir=str(workspace_path)
            )
            
            # 5. 负债结构饼图
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
            liability_chart = tabular_toolkit.generate_charts(
                data_json=liability_structure_data,
                chart_type='pie',
                output_dir=str(workspace_path)
            )
'''
                
                # 插入饼图代码
                trend_chart_line = "trend_chart = tabular_toolkit.generate_charts"
                start_idx = content.find(trend_chart_line)
                if start_idx != -1:
                    # 找到趋势图代码块的结束位置（通常是下一个主要代码块的开始或空行）
                    end_idx = content.find("\n            ", start_idx)
                    if end_idx == -1:
                        end_idx = len(content)
                    
                    # 插入饼图代码
                    new_content = content[:end_idx] + "\n" + pie_chart_code + content[end_idx:]
                    
                    # 写回文件
                    with open(main_file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    print("✓ 成功更新main.py，添加了饼图生成功能")
                    return True
                else:
                    print("✗ 在main.py中找不到趋势图生成代码")
                    return False
            else:
                print("✗ 在main.py中找不到趋势图生成代码")
                return False
        else:
            print("✗ 在main.py中找不到图表生成部分")
            return False
            
    except Exception as e:
        print(f"✗ 更新main.py时发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    print("========== 饼图功能测试 ==========\n")
    
    # 运行饼图测试
    pie_test_result = test_pie_chart_generation()
    
    # 更新main.py脚本
    update_result = update_main_script()
    
    print("\n========== 测试总结 ==========\n")
    print(f"饼图生成测试: {'成功' if pie_test_result else '失败'}")
    print(f"main.py更新: {'成功' if update_result else '失败'}")
    
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