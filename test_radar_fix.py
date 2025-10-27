import os
import sys
import json

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入图表生成工具
from utu.tools.tabular_data_toolkit import TabularDataToolkit

# 用户原始雷达图数据
test_data = {
    "title": "陕西建工财务健康雷达图",
    "x_axis": {
        "name": "财务指标",
        "data": ["净利率", "ROE", "资产负债率", "流动比率", "总资产周转率", "应收账款周转率"]
    },
    "series": [
        {
            "name": "2025年当前",
            "data": [1.92, 2.82, 88.71, 1.11, 0.17, 0.72]
        }
    ]
}

# 测试多系列雷达图
test_data_multi_series = {
    "title": "公司财务指标对比雷达图",
    "x_axis": {
        "name": "财务指标",
        "data": ["净利率", "ROE", "资产负债率", "流动比率", "总资产周转率"]
    },
    "series": [
        {
            "name": "公司A",
            "data": [2.5, 3.2, 85.4, 1.2, 0.2]
        },
        {
            "name": "公司B",
            "data": [1.8, 2.7, 88.1, 1.0, 0.18]
        }
    ]
}

# 测试列表格式的x_axis
test_data_list_xaxis = {
    "title": "简化格式雷达图",
    "x_axis": ["指标1", "指标2", "指标3", "指标4"],
    "series": [
        {
            "name": "数据",
            "data": [10, 20, 30, 40]
        }
    ]
}

async def test_radar_chart_generation():
    # 创建工具实例
    toolkit = TabularDataToolkit()
    await toolkit.build()
    
    # 创建输出目录
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_workdir")
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 测试场景1: 用户原始数据格式
        print("测试场景1: 用户原始数据格式 (标准dict x_axis)")
        result1 = await toolkit.generate_charts(test_data, "radar", output_dir)
        print(f"结果: {result1}")
        
        # 测试场景2: 多系列数据
        print("\n测试场景2: 多系列数据")
        result2 = await toolkit.generate_charts(test_data_multi_series, "radar", output_dir)
        print(f"结果: {result2}")
        
        # 测试场景3: 列表格式的x_axis
        print("\n测试场景3: 列表格式的x_axis")
        result3 = await toolkit.generate_charts(test_data_list_xaxis, "radar", output_dir)
        print(f"结果: {result3}")
        
        # 验证输出文件
        if result1["success"] and result1["files"]:
            print(f"\n雷达图生成成功！输出文件: {result1['files'][0]}")
        
        # 汇总测试结果
        all_success = result1["success"] and result2["success"] and result3["success"]
        if all_success:
            print("\n所有测试场景通过！修复成功！")
        else:
            print("\n部分测试场景失败，请检查。")
            
    except Exception as e:
        print(f"测试过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await toolkit.cleanup()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_radar_chart_generation())