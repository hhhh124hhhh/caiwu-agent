# A股财报分析智能体

基于 Youtu-Agent 框架的专业A股财务分析系统，集成了增强版Python执行工具，支持代码保存和完整的财报分析流程。

## 🚀 快速开始

### 1. 安装依赖

#### 方法一：使用uv（推荐）
```bash
# 运行安装脚本（自动使用uv安装）
python examples/stock_analysis/install_deps.py

# 或者手动安装（逐个添加）
uv add --group stock-analysis akshare>=1.12.0
uv add --group stock-analysis tushare>=1.2.0
uv add --group stock-analysis plotly>=5.0.0
uv add --group stock-analysis seaborn>=0.11.0

# 如果需要使用Web界面，还需要安装UI相关依赖
uv add --group stock-analysis flask>=2.0.0
uv add --group stock-analysis flask-cors>=3.0.0
```

#### 方法二：使用pip
```bash
# 运行安装脚本（会自动检测并使用pip）
python examples/stock_analysis/install_deps.py

# 或者手动安装
pip install akshare>=1.12.0 tushare>=1.2.0 plotly>=5.0.0 seaborn>=0.11.0

# 如果需要使用Web界面，还需要安装UI相关依赖
pip install flask>=2.0.0 flask-cors>=3.0.0
```

### 2. 配置环境变量

确保在 `.env` 文件中配置：
```bash
# LLM配置
UTU_LLM_TYPE=chat.completions
UTU_LLM_MODEL=deepseek-chat
UTU_LLM_BASE_URL=https://api.deepseek.com/v1
UTU_LLM_API_KEY=your-api-key

# 可选：Tushare token (用于获取更专业的A股数据)
TUSHARE_TOKEN=your-tushare-token
```

### 3. 运行分析

#### 使用uv运行（推荐）
```bash
# 直接运行AKShare数据获取工具
uv run python examples/stock_analysis/akshare_data_fetcher.py

# 运行综合示例
uv run python examples/stock_analysis/comprehensive_examples.py

# 运行功能测试
uv run python examples/stock_analysis/test_akshare_tool.py

# 基础版本
uv run python examples/stock_analysis/main.py

# 增强版本 
uv run python scripts/cli_chat.py --stream --config examples/stock_analysis_enhanced
```

#### 使用python运行
```bash
# 直接运行AKShare数据获取工具
python examples/stock_analysis/akshare_data_fetcher.py

# 运行综合示例
python examples/stock_analysis/comprehensive_examples.py

# 运行功能测试
python examples/stock_analysis/test_akshare_tool.py
```

### 4. 启动Web界面

#### 使用uv运行Web界面（推荐）
```bash
# 启动Web界面
uv run python examples/stock_analysis/main_web.py
```

#### 使用python运行Web界面
```bash
# 启动Web界面
python examples/stock_analysis/main_web.py
```

启动后，您可以在浏览器中访问 `http://127.0.0.1:8848` 来使用Web界面与财务分析智能体进行交互。

## 🎯 功能特点

### 🔧 增强版Python执行器
- **代码保存**: 所有执行的Python代码自动保存到文件
- **文件追踪**: 自动识别生成的图表和数据文件
- **安全执行**: IPython沙盒环境，支持matplotlib绘图
- **超时控制**: 可设置执行超时时间

### 📊 专业财务分析
- **多维度分析**: 盈利能力、偿债能力、运营效率、成长性
- **趋势分析**: 同比、环比、多年度趋势
- **行业对比**: 同行业公司对比分析
- **风险评估**: 财务健康度评估

### 📈 可视化能力
- **专业图表**: 财务指标趋势图、对比图、雷达图
- **交互式图表**: Plotly交互式仪表板
- **多种格式**: PNG、SVG、HTML格式输出
- **自动化生成**: 基于数据自动选择最佳图表类型

### 📋 智能报告生成
- **HTML报告**: 专业的HTML格式分析报告
- **结构化输出**: 包含执行摘要、详细分析、投资建议
- **数据附件**: Excel格式的原始数据和分析结果
- **风险提示**: 专业的投资风险分析

## 🏗️ 系统架构

### 五大智能体协作

1. **SearchAgent**: 数据收集专家
   - A股财报数据获取
   - 行业数据收集
   - 竞争对手数据获取

2. **DataAnalysisAgent**: 数据处理专家
   - 数据清洗和预处理
   - 格式转换和标准化
   - 异常值检测和处理

3. **FinancialAnalysisAgent**: 财务分析专家
   - 财务比率计算
   - 趋势分析
   - 同行业对比分析

4. **ChartGeneratorAgent**: 可视化专家
   - 财务图表制作
   - 趋势图生成
   - 交互式仪表板

5. **ReportAgent**: 报告整合专家
   - 分析结果整合
   - 投资建议生成
   - 专业报告输出

## 💡 使用示例

### 示例1: 单一公司分析
```python
question = "分析贵州茅台(600519.SH)最近3年的财务状况"
```

### 示例2: 公司对比分析
```python
question = "对比分析宁德时代和比亚迪最近2年的财务表现"
```

### 示例3: 行业分析
```python
question = "分析新能源汽车行业主要公司的财务状况和发展趋势"
```

## 📁 输出文件结构

```
stock_analysis_workspace/
├── executed_code_20250914_143052.py    # 执行的Python代码
├── stock_analysis_report.html          # HTML分析报告
├── revenue_trend.png                   # 营收趋势图
├── financial_ratios.csv               # 财务比率数据
├── peer_comparison.png                # 同行业对比图
└── analysis_data.xlsx                 # 分析数据附件
```

## 🔧 配置说明

### 主要配置文件
- `configs/agents/examples/stock_analysis.yaml`: 主配置文件
- `configs/tools/enhanced_stock_analyzer.yaml`: 工具配置
- `examples/data_analysis/stock_analysis_examples.json`: 分析示例

### 关键配置项
```yaml
# 代码保存设置
save_code: true
workspace_root: "./stock_analysis_workspace"

# 超时设置
timeout: 120

# 支持的金融包
financial_packages:
  - akshare    # A股数据
  - tushare    # 专业金融数据
  - yfinance   # 国际市场数据
  - plotly     # 交互式图表
```

## 🐛 故障排除

### 常见问题

1. **数据获取失败**
   - 检查网络连接
   - 确认API token配置正确
   - 尝试切换数据源

2. **图表生成失败**
   - 确认matplotlib后端设置为'Agg'
   - 检查工作目录权限
   - 确认依赖包安装正确

3. **代码执行超时**
   - 增加timeout设置
   - 优化代码逻辑
   - 分步骤执行复杂分析

### 日志查看
```bash
# 查看详细日志
tail -f logs/utu.log

# 查看特定时间段的日志
grep "2025-09-14" logs/utu.log
```

## 📞 技术支持

如遇到问题，请检查：
1. 依赖包是否正确安装
2. 环境变量配置是否正确
3. 网络连接是否正常
4. 工作目录权限是否足够

## 📈 性能优化

### 大数据分析建议
- 使用数据采样减少计算量
- 分步骤执行复杂分析
- 缓存中间结果
- 优化图表生成代码

### 内存优化
- 定期清理工作目录
- 使用数据分块处理
- 避免同时生成过多图表

## 🚀 增强版AKShare数据获取工具

### 核心功能

1. **多市场支持**
   - 上海主板 (6开头)
   - 深圳主板 (0开头)
   - 创业板 (300开头)
   - 科创板 (688开头)
   - 北交所 (8开头)

2. **实时行情数据**
   - 所有A股实时行情
   - 市场统计数据
   - 涨跌幅排行榜
   - 成交额排行榜

3. **财务报表数据**
   - 东方财富财报数据
   - 新浪财报数据（备用）
   - 多年度财务数据
   - 智能报告期选择

4. **财务分析功能**
   - 财务比率计算
   - 趋势分析
   - 风险评估
   - 行业对比

### 使用示例

```python
from akshare_data_fetcher import AKShareDataFetcher

# 创建数据获取器
fetcher = AKShareDataFetcher()

# 获取股票基本信息
basic_info = fetcher.get_stock_basic_info("600519")

# 获取财务报表
reports = fetcher.get_financial_report("600519")

# 获取多年数据
multi_year_data = fetcher.get_multi_year_financial_data("600519", years=3)

# 获取市场统计
stats = fetcher.get_market_statistics()

# 生成综合报告
report = fetcher.generate_comprehensive_report("600519")
```

### API接口

#### 实时行情数据
- `stock_zh_a_spot_em()` - 所有A股实时行情
- `stock_sh_a_spot_em()` - 上海主板
- `stock_sz_a_spot_em()` - 深圳主板
- `stock_cy_a_spot_em()` - 创业板
- `stock_kc_a_spot_em()` - 科创板
- `stock_bj_a_spot_em()` - 北交所

#### 财务报表数据
- `stock_lrb_em()` - 利润表
- `stock_zcfz_em()` - 资产负债表
- `stock_xjll_em()` - 现金流量表
- `stock_lrb_bj_em()` - 北交所利润表
- `stock_zcfz_bj_em()` - 北交所资产负债表

### 数据格式

#### 实时行情数据字段
- 代码、名称、最新价、涨跌幅、涨跌额
- 成交量、成交额、振幅、最高、最低
- 今开、昨收、量比、换手率
- 市盈率、市净率、总市值、流通市值

#### 财务报表字段
- 利润表：营业收入、营业成本、净利润等
- 资产负债表：总资产、总负债、股东权益等
- 现金流量表：经营现金流、投资现金流、融资现金流等