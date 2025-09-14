# AKShare增强版数据获取工具使用指南

## 概述

本工具是基于AKShare库的增强版A股数据获取工具，专门为财务分析智能体设计。支持多市场数据获取、财务报表分析、市场统计等功能。

## 主要特性

### 1. 多市场支持
- **上海主板**：股票代码以6开头（不包括688）
- **深圳主板**：股票代码以0开头（000、002、003）
- **创业板**：股票代码以300开头
- **科创板**：股票代码以688开头
- **北交所**：股票代码以8或43开头

### 2. 数据源
- **东方财富**：主要数据源，提供实时行情和财务报表
- **新浪财经**：备用数据源
- **AKShare API**：统一的Python接口

### 3. 功能模块
- 实时行情数据获取
- 财务报表数据获取
- 多年财务数据分析
- 市场统计分析
- 财务比率计算
- 综合报告生成

## 快速开始

### 1. 安装依赖

#### 使用uv（推荐）
```bash
# 添加stock-analysis依赖组
uv add --group stock-analysis

# 或者运行安装脚本（自动检测uv/pip）
python examples/stock_analysis/install_deps.py
```

#### 使用pip
```bash
# 运行安装脚本
python examples/stock_analysis/install_deps.py

# 或者手动安装
pip install akshare>=1.12.0 tushare>=1.2.0 plotly>=5.0.0 seaborn>=0.11.0
```

### 2. 基础使用
```python
from akshare_data_fetcher import AKShareDataFetcher

# 创建数据获取器
fetcher = AKShareDataFetcher(save_dir="./my_workspace")

# 获取股票基本信息
basic_info = fetcher.get_stock_basic_info("600519")
print(basic_info)
```

### 3. 运行示例

#### 使用uv运行（推荐）
```bash
# 基础功能示例
uv run python examples/stock_analysis/akshare_data_fetcher.py

# 综合示例
uv run python examples/stock_analysis/comprehensive_examples.py

# 功能测试
uv run python examples/stock_analysis/test_akshare_tool.py
```

#### 使用python运行
```bash
# 基础功能示例
python examples/stock_analysis/akshare_data_fetcher.py

# 综合示例
python examples/stock_analysis/comprehensive_examples.py

# 功能测试
python examples/stock_analysis/test_akshare_tool.py
```

## 详细功能说明

### 1. 股票基本信息获取

```python
# 获取单个股票信息
basic_info = fetcher.get_stock_basic_info("600519")

# 支持的股票类型
# 600519 - 贵州茅台 (上海主板)
# 000858 - 五粮液 (深圳主板)
# 300750 - 宁德时代 (创业板)
# 688036 - 传音控股 (科创板)
# 832175 - 东方碳素 (北交所)
```

**返回数据字段：**
- 代码、名称、最新价、涨跌幅、涨跌额
- 成交量、成交额、振幅、最高、最低
- 今开、昨收、量比、换手率
- 市盈率、市净率、总市值、流通市值

### 2. 财务报表获取

```python
# 获取最新财务报表
reports = fetcher.get_financial_report("600519")

# 获取指定日期的财务报表
reports = fetcher.get_financial_report("600519", date="20231231")

# 强制使用东方财富数据
reports = fetcher.get_financial_report("600519", use_eastmoney=True)
```

**返回数据：**
```python
{
    'income_statement': pd.DataFrame,     # 利润表
    'balance_sheet': pd.DataFrame,        # 资产负债表
    'cash_flow_statement': pd.DataFrame  # 现金流量表
}
```

### 3. 多年财务数据获取

```python
# 获取3年财务数据
multi_year_data = fetcher.get_multi_year_financial_data("600519", years=3)

# 智能报告期选择，会根据当前时间自动选择合适的报告期
# 例如：当前是10月，会优先使用三季报数据
```

### 4. 市场数据获取

```python
# 获取市场总览
market_data = fetcher.get_market_overview()

# 获取市场统计
stats = fetcher.get_market_statistics()

# 市场统计包含：
# - 总股票数、总市值、总成交额
# - 上涨/下跌/平盘家数
# - 平均市盈率、平均市净率
# - 涨幅榜、跌幅榜、成交额榜
```

### 5. 财务分析功能

```python
# 计算财务比率
ratios = fetcher.calculate_financial_ratios("600519")
# 返回：ROE、ROA、毛利率、净利率、负债率等

# 生成财务摘要
summary = fetcher.get_financial_summary("600519", years=3)
# 返回：趋势分析、风险评估、关键指标等

# 生成综合报告
report = fetcher.generate_comprehensive_report("600519", years=3)
# 返回：包含所有数据的完整报告
```

## 高级功能

### 1. 同行业分析

```python
# 获取同行业股票
peers = fetcher.get_stock_peers("600519", "白酒")
print(f"同行业股票: {peers}")

# 获取行业数据
industry_data = fetcher.get_industry_data("白酒")
```

### 2. 历史数据获取

```python
# 获取历史股价数据
from datetime import datetime, timedelta

end_date = datetime.now().strftime('%Y%m%d')
start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')

hist_data = fetcher.get_stock_daily_data("600519", start_date, end_date)
```

### 3. 自定义分析

```python
# 获取数据后进行自定义分析
reports = fetcher.get_financial_report("600519")

if reports and 'income_statement' in reports:
    income_df = reports['income_statement']
    
    # 计算同比增长率
    if 'revenue' in income_df.columns and 'revenue_yoy' in income_df.columns:
        revenue = income_df['revenue'].iloc[0]
        revenue_growth = income_df['revenue_yoy'].iloc[0]
        print(f"营业收入: {revenue:,.0f}元")
        print(f"同比增长: {revenue_growth:.2f}%")
```

## 数据格式说明

### 实时行情数据格式
```python
# 数据字段
{
    '序号': int,
    '代码': str,        # 股票代码
    '名称': str,        # 股票名称
    '最新价': float,    # 最新价格
    '涨跌幅': float,    # 涨跌幅(%)
    '涨跌额': float,    # 涨跌额
    '成交量': float,    # 成交量(手)
    '成交额': float,    # 成交额(元)
    '振幅': float,      # 振幅(%)
    '最高': float,      # 最高价
    '最低': float,      # 最低价
    '今开': float,      # 今开价
    '昨收': float,      # 昨收价
    '量比': float,      # 量比
    '换手率': float,    # 换手率(%)
    '市盈率-动态': float,  # 市盈率
    '市净率': float,    # 市净率
    '总市值': float,    # 总市值(元)
    '流通市值': float,  # 流通市值(元)
    '涨速': float,      # 涨速
    '5分钟涨跌': float, # 5分钟涨跌(%)
    '60日涨跌幅': float, # 60日涨跌幅(%)
    '年初至今涨跌幅': float # 年初至今涨跌幅(%)
}
```

### 财务报表数据格式
```python
# 利润表字段
{
    '股票代码': str,
    '股票简称': str,
    '营业收入': float,    # 营业收入
    '营业成本': float,    # 营业成本
    '营业利润': float,    # 营业利润
    '利润总额': float,    # 利润总额
    '净利润': float,      # 净利润
    '基本每股收益': float, # 基本每股收益
    '稀释每股收益': float, # 稀释每股收益
    '营业收入同比': float, # 营业收入同比增长
    '净利润同比': float    # 净利润同比增长
}

# 资产负债表字段
{
    '股票代码': str,
    '股票简称': str,
    '资产-货币资金': float,   # 货币资金
    '资产-应收账款': float,   # 应收账款
    '资产-存货': float,       # 存货
    '资产-总资产': float,     # 总资产
    '负债-应付账款': float,   # 应付账款
    '负债-总负债': float,     # 总负债
    '负债-预收账款': float,   # 预收账款
    '资产负债率': float,      # 资产负债率
    '股东权益合计': float     # 股东权益合计
}

# 现金流量表字段
{
    '股票代码': str,
    '股票简称': str,
    '经营性现金流-现金流量净额': float,  # 经营活动现金流净额
    '投资性现金流-现金流量净额': float,  # 投资活动现金流净额
    '融资性现金流-现金流量净额': float,  # 筹资活动现金流净额
    '净现金流-净现金流': float,          # 净现金流
    '经营性现金流-净现金流占比': float,   # 经营现金流占比
    '投资性现金流-净现金流占比': float,   # 投资现金流占比
    '融资性现金流-净现金流占比': float    # 融资现金流占比
}
```

## 错误处理

### 1. 常见错误及解决方案

**网络连接问题**
```python
try:
    basic_info = fetcher.get_stock_basic_info("600519")
except Exception as e:
    print(f"网络错误: {e}")
    # 可以尝试重试或使用备用数据源
```

**数据为空**
```python
basic_info = fetcher.get_stock_basic_info("600519")
if basic_info.empty:
    print("未获取到数据，请检查股票代码是否正确")
```

**API限制**
```python
# 如果遇到API调用限制，可以：
# 1. 增加调用间隔
# 2. 使用缓存数据
# 3. 切换数据源
```

### 2. 日志查看
```python
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO)

# 查看详细日志
logger = logging.getLogger(__name__)
```

## 性能优化

### 1. 数据缓存
```python
# 数据会自动保存到工作目录
# 可以重复使用已保存的数据，避免重复获取
```

### 2. 批量处理
```python
# 批量获取多只股票数据
stocks = ["600519", "000858", "300750"]
for stock in stocks:
    data = fetcher.get_stock_basic_info(stock)
    # 处理数据
```

### 3. 内存管理
```python
# 处理大量数据时，可以：
# 1. 分批处理
# 2. 及时清理不需要的数据
# 3. 使用数据采样
```

## 集成到智能体

### 1. 在Youtu-Agent中使用
```python
# 在智能体工具中调用
from akshare_data_fetcher import AKShareDataFetcher

def get_stock_data(stock_code):
    fetcher = AKShareDataFetcher()
    return fetcher.get_financial_report(stock_code)
```

### 2. 配置文件
```yaml
# 在配置文件中添加
tools:
  - enhanced_python_executor
  - akshare_data_fetcher
```

## 部署说明

### 1. 环境要求
- Python 3.12+ (项目要求)
- uv包管理器 (推荐)
- AKShare >= 1.12.0
- Pandas >= 1.5.0

### 2. 安装步骤

#### 使用uv（推荐）
```bash
# 运行安装脚本（自动使用uv安装）
python examples/stock_analysis/install_deps.py

# 或者手动安装（逐个添加）
uv add --group stock-analysis akshare>=1.12.0
uv add --group stock-analysis tushare>=1.2.0
uv add --group stock-analysis plotly>=5.0.0
uv add --group stock-analysis seaborn>=0.11.0

# 运行测试
uv run python examples/stock_analysis/test_akshare_tool.py

# 运行示例
uv run python examples/stock_analysis/comprehensive_examples.py
```

#### 使用pip
```bash
# 安装依赖
python examples/stock_analysis/install_deps.py

# 运行测试
python examples/stock_analysis/test_akshare_tool.py

# 运行示例
python examples/stock_analysis/comprehensive_examples.py
```

### 3. 配置说明
- 无需额外配置
- 自动数据源选择
- 智能缓存管理
- uv会自动管理虚拟环境

## 注意事项

1. **数据来源**：本工具使用公开的金融数据API，请遵守相关使用条款
2. **数据延迟**：实时行情数据可能有几分钟延迟
3. **数据完整性**：部分股票可能缺少某些财务数据
4. **网络依赖**：需要稳定的网络连接
5. **API限制**：请合理使用API，避免过度调用

## 技术支持

如遇到问题，请：
1. 检查网络连接
2. 确认依赖包是否正确安装
3. 查看错误日志
4. 尝试更新AKShare库到最新版本

## 更新日志

### v1.0.0
- 支持多市场股票数据获取
- 集成东方财富和新浪数据源
- 提供财务报表分析功能
- 支持多年数据对比分析
- 生成综合分析报告