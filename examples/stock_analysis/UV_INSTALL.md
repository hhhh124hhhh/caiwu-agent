# UV环境安装指南

## 概述

本项目使用uv作为包管理器，为A股分析工具提供了专门的依赖组。

## 快速安装

### 1. 使用uv添加依赖（推荐）

```bash
# 运行安装脚本（推荐）
python examples/stock_analysis/install_deps.py

# 或者手动安装（逐个添加）
uv add --group stock-analysis akshare>=1.12.0
uv add --group stock-analysis tushare>=1.2.0
uv add --group stock-analysis yfinance>=0.2.0
uv add --group stock-analysis plotly>=5.0.0
uv add --group stock-analysis seaborn>=0.11.0
uv add --group stock-analysis xlrd>=2.0.0
uv add --group stock-analysis requests>=2.28.0
uv add --group stock-analysis beautifulsoup4>=4.11.0
uv add --group stock-analysis lxml>=4.9.0
```

这会安装以下依赖：
- akshare>=1.12.0 - A股数据获取
- tushare>=1.2.0 - 中国金融数据
- yfinance>=0.2.0 - 雅虎财经数据
- plotly>=5.0.0 - 交互式图表
- seaborn>=0.11.0 - 统计图表美化
- xlrd>=2.0.0 - Excel读取
- requests>=2.28.0 - HTTP请求
- beautifulsoup4>=4.11.0 - 网页解析
- lxml>=4.9.0 - XML解析

### 2. 运行示例

```bash
# 使用uv运行（推荐）
uv run python examples/stock_analysis/akshare_data_fetcher.py
uv run python examples/stock_analysis/comprehensive_examples.py
uv run python examples/stock_analysis/test_akshare_tool.py
```

## 依赖组说明

### pyproject.toml配置
```toml
[dependency-groups]
stock-analysis = [
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
```

### 使用特定依赖组
```bash
# 只安装stock-analysis依赖组
uv sync --group stock-analysis

# 安装多个依赖组
uv sync --group dev --group stock-analysis

# 安装所有依赖组
uv sync --all-groups
```

注意：`uv sync`主要用于同步pyproject.toml中已定义的依赖，而不是安装新的依赖。如果要添加新的依赖，需要使用`uv add`命令。

## 替代安装方法

### 如果uv不可用

```bash
# 运行安装脚本（会自动检测并使用pip）
python examples/stock_analysis/install_deps.py

# 或者手动安装
pip install akshare>=1.12.0 tushare>=1.2.0 plotly>=5.0.0 seaborn>=0.11.0
```

### 安装uv

如果还没有安装uv：

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.sh | iex"

# 或者使用pip
pip install uv
```

## 验证安装

```bash
# 验证依赖是否正确安装
uv run python -c "import akshare; print('AKShare version:', akshare.__version__)"
uv run python -c "import pandas; print('Pandas version:', pandas.__version__)"

# 运行测试
uv run python examples/stock_analysis/test_akshare_tool.py
```

## 项目结构

```
youtu-agent/
├── pyproject.toml          # 项目配置和依赖定义
├── uv.lock                 # 锁定的依赖版本
├── examples/stock_analysis/
│   ├── akshare_data_fetcher.py      # 主要工具类
│   ├── comprehensive_examples.py    # 综合示例
│   ├── test_akshare_tool.py         # 功能测试
│   ├── install_deps.py             # 安装脚本
│   └── USER_GUIDE.md               # 使用指南
```

## 常见问题

### Q: 为什么要使用uv？
A: uv比传统的pip更快，提供了更好的依赖管理，支持依赖组，能自动管理虚拟环境。

### Q: 如何更新依赖？
```bash
# 更新特定依赖组
uv add --group stock-analysis akshare@latest

# 更新所有依赖
uv sync --upgrade
```

### Q: 如何卸载依赖组？
```bash
# uv目前不支持直接删除依赖组，需要手动编辑pyproject.toml
# 然后运行 uv sync
```

### Q: 如何查看已安装的依赖？
```bash
# 查看所有依赖
uv tree

# 查看特定依赖组
uv tree --group stock-analysis
```

## 最佳实践

1. **使用uv运行**：始终使用`uv run python`而不是直接使用`python`
2. **依赖隔离**：uv会自动创建和管理虚拟环境
3. **版本锁定**：uv.lock文件确保了依赖版本的一致性
4. **依赖分组**：使用依赖组来管理不同功能的依赖

## 故障排除

### 如果遇到网络问题
```bash
# 使用国内镜像
uv sync --index-url https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 如果依赖冲突
```bash
# 清理并重新安装
rm -rf .venv
uv sync --all-groups
```

### 如果权限问题
```bash
# 在用户目录下安装
uv sync --no-python
```

---

更多信息请参考：
- [uv官方文档](https://docs.astral.sh/uv/)
- [项目README](../README.md)
- [用户指南](USER_GUIDE.md)