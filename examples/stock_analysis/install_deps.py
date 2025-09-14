#!/usr/bin/env python3
"""
安装A股财报分析所需的额外依赖包
支持uv和pip两种安装方式
"""

import subprocess
import sys
import os
import shutil

def check_uv_available():
    """检查uv是否可用"""
    return shutil.which("uv") is not None

def install_with_uv():
    """使用uv安装依赖包"""
    try:
        print("正在使用uv安装A股分析依赖包...")
        
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # A股数据分析专用包
        packages = [
            "akshare>=1.12.0",
            "tushare>=1.2.0", 
            "yfinance>=0.2.0",
            "plotly>=5.0.0",
            "seaborn>=0.11.0",
            "xlrd>=2.0.0",
            "requests>=2.28.0",
            "beautifulsoup4>=4.11.0",
            "lxml>=4.9.0",
        ]
        
        # 使用uv添加所有包到stock-analysis组
        for package in packages:
            result = subprocess.run([
                "uv", "add", "--group", "stock-analysis", package
            ], cwd=project_root, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ 安装 {package} 失败: {result.stderr}")
                return False
            else:
                print(f"✅ {package} 安装成功")
        
        print("✅ 所有依赖包安装成功")
        return True
            
    except Exception as e:
        print(f"❌ uv安装时发生错误: {e}")
        return False

def install_with_pip():
    """使用pip安装单个包"""
    # A股数据分析专用包
    financial_packages = [
        "akshare>=1.12.0",          # A股数据获取
        "tushare>=1.2.0",         # 中国金融数据
        "yfinance>=0.2.0",         # 雅虎财经数据
        "plotly>=5.0.0",          # 交互式图表
        "seaborn>=0.11.0",        # 统计图表美化
        "xlrd>=2.0.0",            # Excel读取
        "requests>=2.28.0",       # HTTP请求
        "beautifulsoup4>=4.11.0",  # 网页解析
        "lxml>=4.9.0",            # XML解析
    ]
    
    print("将安装以下包:")
    for pkg in financial_packages:
        print(f"  - {pkg}")
    
    print("\n开始使用pip安装...")
    
    success_count = 0
    for package in financial_packages:
        try:
            print(f"正在安装 {package}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {package} 安装成功")
                success_count += 1
            else:
                print(f"❌ {package} 安装失败: {result.stderr}")
                
        except Exception as e:
            print(f"❌ 安装 {package} 时发生错误: {e}")
    
    return success_count, len(financial_packages)

def main():
    """主函数"""
    print("=== A股财报分析工具依赖安装 ===")
    
    # 检查uv是否可用
    if check_uv_available():
        print("✅ 检测到uv包管理器，推荐使用uv安装")
        
        choice = input("是否使用uv安装？(推荐) [Y/n]: ").strip().lower()
        if choice != 'n':
            success = install_with_uv()
            if success:
                print("\n🎉 所有依赖包安装成功！")
                print("\n现在可以运行A股财报分析工具了:")
                print("  uv run python examples/stock_analysis/akshare_data_fetcher.py")
                print("  uv run python examples/stock_analysis/comprehensive_examples.py")
                return
            else:
                print("⚠️  uv安装失败，尝试使用pip安装...")
    
    # 使用pip安装
    print("\n使用pip安装依赖包...")
    success_count, total_count = install_with_pip()
    
    print(f"\n=== 安装完成 ===")
    print(f"成功安装: {success_count}/{total_count} 个包")
    
    if success_count == total_count:
        print("🎉 所有依赖包安装成功！")
        print("\n现在可以运行A股财报分析工具了:")
        print("  python examples/stock_analysis/akshare_data_fetcher.py")
        print("  python examples/stock_analysis/comprehensive_examples.py")
    else:
        print("⚠️  部分包安装失败，可能影响某些功能")
        print("\n可以手动安装失败的包:")
        print("  uv add --group stock-analysis akshare>=1.12.0")
        print("  uv add --group stock-analysis tushare>=1.2.0")
        print("  uv add --group stock-analysis plotly>=5.0.0")
        print("  或者")
        print("  pip install akshare>=1.12.0 tushare>=1.2.0 plotly>=5.0.0")
    
    # 提示uv安装建议
    if not check_uv_available():
        print("\n💡 建议安装uv包管理器以获得更好的依赖管理:")
        print("  curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("  然后运行: python examples/stock_analysis/install_deps.py")

if __name__ == "__main__":
    main()