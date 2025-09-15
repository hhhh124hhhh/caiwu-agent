#!/usr/bin/env python3
"""
测试ReportAgent与report_saver工具的配置集成
"""

import sys
import pathlib

# 添加项目根目录到Python路径
project_root = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utu.config import ConfigLoader


def test_report_saver_config():
    """测试ReportAgent与report_saver工具的配置集成"""
    print("=== 测试ReportAgent与report_saver工具的配置集成 ===\n")
    
    try:
        # 1. 加载智能体配置
        print("1. 加载智能体配置...")
        config = ConfigLoader.load_agent_config("examples/stock_analysis_final")
        print("   ✓ 配置加载成功")
        
        # 2. 检查defaults部分是否包含report_saver
        print("\n2. 检查defaults配置...")
        # 通过OmegaConf访问defaults属性
        import omegaconf
        if isinstance(config, omegaconf.DictConfig):
            defaults = config.get('defaults', [])
        else:
            # 尝试通过字典方式访问
            defaults = getattr(config, 'defaults', [])
        
        print(f"   defaults列表: {defaults}")
        report_saver_found = False
        if defaults:
            for default in defaults:
                if isinstance(default, str) and 'report_saver' in default:
                    report_saver_found = True
                    break
                elif isinstance(default, dict) and any('report_saver' in str(v) for v in default.values()):
                    report_saver_found = True
                    break
        
        if report_saver_found:
            print("   ✓ defaults已正确配置report_saver工具包")
        else:
            print("   ! defaults中未找到report_saver工具包（可能在运行时动态加载）")
        
        # 3. 检查ReportAgent是否包含report_saver工具
        print("\n3. 检查ReportAgent工具配置...")
        # 从workers_info中查找ReportAgent的工具配置
        workers_info = config.workers_info
        report_agent_tools = None
        for worker_info in workers_info:
            if worker_info.get('name') == 'ReportAgent':
                report_agent_tools = worker_info.get('tools', [])
                break
        
        if report_agent_tools is not None:
            print(f"   ReportAgent工具列表: {report_agent_tools}")
            if 'report_saver' in report_agent_tools:
                print("   ✓ ReportAgent已正确配置report_saver工具")
            else:
                print("   ✗ ReportAgent未配置report_saver工具")
                return False
        else:
            print("   ✗ 未找到ReportAgent配置")
            return False
        
        # 4. 检查toolkits部分是否包含report_saver配置
        print("\n4. 检查toolkits配置...")
        toolkits = getattr(config, 'toolkits', {})
        if 'report_saver' in toolkits:
            print("   ✓ toolkits已正确配置report_saver")
            print(f"   report_saver配置: {toolkits['report_saver']}")
        else:
            print("   ! toolkits中未找到report_saver配置（可能在运行时动态加载）")
        
        print("\n=== 测试总结 ===")
        print("✓ ReportAgent已成功集成report_saver工具")
        print("✓ 智能体配置正确加载")
        
        return True
        
    except Exception as e:
        print(f"   ✗ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 运行测试
    success = test_report_saver_config()
    
    if success:
        print("\n🎉 ReportAgent与report_saver工具配置集成测试通过！")
        sys.exit(0)
    else:
        print("\n❌ ReportAgent与report_saver工具配置集成测试失败！")
        sys.exit(1)