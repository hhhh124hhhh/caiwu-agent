# 测试指南

本文档介绍财务分析系统的测试框架、测试策略和最佳实践。

## 测试架构概览

### 测试类型

我们采用多层次测试策略，确保系统的可靠性和稳定性：

1. **单元测试** - 测试单个函数和类
2. **集成测试** - 测试组件间的交互
3. **性能测试** - 测试系统性能和资源使用
4. **边界情况测试** - 测试异常和边界条件
5. **端到端测试** - 测试完整的工作流程

### 测试覆盖范围

#### 财务指标计算测试
- **文件**: `tests/tools/test_financial_analysis_toolkit.py`
- **覆盖**: 17个核心财务指标
- **维度**:
  - 盈利能力指标 (ROE, ROA, 净利润率等)
  - 偿债能力指标 (资产负债率, 流动比率等)
  - 运营效率指标 (总资产周转率, 存货周转率等)
  - 成长性指标 (收入增长率, 利润增长率等)
  - 现金流指标 (现金比率, 经营现金流比率等)

#### 图表生成测试
- **文件**: `tests/tools/test_tabular_data_toolkit.py`
- **覆盖**: 8种图表类型
  - 财务指标对比图
  - 雷达图
  - 趋势图
  - 散点图
  - 热力图
  - 现金流结构图
  - 现金流瀑布图
  - 通用图表

#### 报告生成测试
- **文件**: `tests/tools/test_report_saver_toolkit.py`
- **覆盖**: 4种报告格式
  - Markdown文档
  - HTML网页
  - JSON数据
  - PDF报告

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/hhhh124hhhh/caiwu-agent.git
cd caiwu-agent

# 安装依赖
make sync
# 或
uv sync --all-extras --all-packages --group dev

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或
.\.venv\Scripts\activate   # Windows
```

### 2. 设置环境变量

创建 `.env` 文件并设置必要的API密钥：

```bash
# LLM配置
export UTU_LLM_TYPE="chat.completions"
export UTU_LLM_MODEL="deepseek-chat"
export UTU_LLM_API_KEY="your_api_key"
export UTU_LLM_BASE_URL="https://api.deepseek.com/v1"

# 可选配置
export UTU_LOG_LEVEL="INFO"
export SERPER_API_KEY="your_serper_key"  # 搜索功能
```

### 3. 运行测试

```bash
# 运行所有测试
make test-all

# 运行快速测试
make test-quick

# 运行特定类型的测试
make test-financial    # 财务分析测试
make test-chart        # 图表生成测试
make test-report       # 报告生成测试
make test-akshare      # AKShare数据测试
```

## 测试命令详解

### 使用Makefile命令

```bash
# 基础测试命令
make test              # 运行基础测试
make test-unit         # 单元测试
make test-integration  # 集成测试
make test-performance  # 性能测试
make test-edge         # 边界情况测试

# 专项测试
make test-financial    # 财务分析专项测试
make test-akshare      # AKShare数据测试
make test-workflow     # 工作流测试

# 测试工具
make test-setup        # 安装测试依赖
make test-check-env    # 检查测试环境
make test-coverage     # 生成覆盖率报告
make test-clean        # 清理测试文件
```

### 使用pytest直接运行

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/tools/test_financial_analysis_toolkit.py -v

# 运行带标记的测试
pytest tests/ -m "financial" -v          # 财务相关测试
pytest tests/ -m "unit" -v               # 单元测试
pytest tests/ -m "integration" -v        # 集成测试
pytest tests/ -m "performance" -v        # 性能测试
pytest tests/ -m "not slow" -v           # 排除慢速测试

# 生成覆盖率报告
pytest tests/ --cov=utu --cov-report=html --cov-report=term-missing

# 并行运行测试（需要pytest-xdist）
pytest tests/ -n auto

# 运行特定测试函数
pytest tests/tools/test_financial_analysis_toolkit.py::TestFinancialMetricsCalculation::test_roe_calculation -v
```

### 使用测试运行器脚本

```bash
# 使用专门的测试运行器
python scripts/test_runner.py check        # 检查环境
python scripts/test_runner.py unit         # 单元测试
python scripts/test_runner.py all          # 所有测试
python scripts/test_runner.py quick        # 快速测试
python scripts/test_runner.py report       # 生成报告
```

## 测试数据管理

### AKShare真实数据

系统使用真实的AKShare财务数据进行测试，确保测试的真实性和可靠性：

```python
# 获取真实财务数据
from utu.tools.akshare_financial_tool import AKShareFinancialDataTool

akshare_tool = AKShareFinancialDataTool()
financial_data = akshare_tool.get_financial_reports("600248", "陕西建工")
```

### 模拟数据

对于不需要真实数据的测试场景，使用高质量的模拟数据：

```python
# 使用测试fixtures
from tests.fixtures.financial_data_fixtures import FinancialDataFixtures

fixtures = FinancialDataFixtures()
mock_data = fixtures.create_perfect_financial_data("测试公司")
```

## 测试标记说明

### 测试类型标记

- `@pytest.mark.unit` - 单元测试
- `@pytest.mark.integration` - 集成测试
- `@pytest.mark.performance` - 性能测试
- `@pytest.mark.edge_case` - 边界情况测试

### 功能域标记

- `@pytest.mark.financial` - 财务分析相关
- `@pytest.mark.akshare` - AKShare数据相关
- `@pytest.mark.chart` - 图表生成测试
- `@pytest.mark.report` - 报告生成测试

### 执行特性标记

- `@pytest.mark.slow` - 耗时较长的测试
- `@pytest.mark.network` - 需要网络连接
- `@pytest.mark.database` - 需要数据库连接
- `@pytest.mark.mock_data` - 使用模拟数据
- `@pytest.mark.real_data` - 使用真实数据

## 性能测试

### 基准测试

性能测试包括以下指标：

1. **财务指标计算性能**
   - 17个指标的计算时间
   - 内存使用情况
   - 大数据集处理能力

2. **图表生成性能**
   - 8种图表的生成时间
   - 图表文件大小
   - 复杂数据的渲染性能

3. **报告生成性能**
   - 4种格式的生成时间
   - 大型报告的处理能力
   - 内存和CPU使用

### 运行性能测试

```bash
# 运行性能测试
make test-performance

# 或使用pytest
pytest tests/performance/ -m "performance" --benchmark-only

# 生成性能基准报告
pytest tests/performance/ --benchmark-only --benchmark-json=benchmark.json
```

## 覆盖率报告

### 生成覆盖率报告

```bash
# 生成HTML覆盖率报告
make test-coverage

# 或手动生成
pytest tests/ --cov=utu --cov-report=html --cov-report=xml

# 查看报告
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### 覆盖率目标

- **总体覆盖率**: ≥ 70%
- **核心模块覆盖率**: ≥ 85%
- **财务分析模块**: ≥ 80%

## CI/CD集成

### GitHub Actions

项目配置了完整的CI/CD流水线：

1. **代码质量检查** - 代码格式、静态分析
2. **单元测试** - 基础功能验证
3. **集成测试** - 组件交互验证
4. **性能测试** - 性能基准验证
5. **文档构建** - 自动构建和部署文档

### 触发条件

- **Push到main/develop分支** - 运行完整测试套件
- **Pull Request** - 运行单元测试和代码质量检查
- **标记为integration-test的PR** - 额外运行集成测试

## 故障排除

### 常见问题

#### 1. AKShare数据获取失败

```bash
# 检查网络连接
ping api.akshare.xyz

# 检查akshare版本
pip show akshare

# 重新安装akshare
pip install --upgrade akshare
```

#### 2. 测试环境问题

```bash
# 重新设置环境
make test-clean
make test-setup

# 检查虚拟环境
python scripts/test_runner.py check
```

#### 3. 内存不足

```bash
# 减少并行测试数量
pytest tests/ -n 1

# 分批运行测试
pytest tests/unit/
pytest tests/integration/
```

#### 4. 字体问题（图表生成）

```bash
# 确保系统中文字体可用
# Ubuntu/Debian
sudo apt-get install fonts-wqy-zenhei fonts-wqy-microhei

# CentOS/RHEL
sudo yum install wqy-zenhei-fonts wqy-microhei-fonts
```

### 调试测试

```bash
# 启用详细日志
pytest tests/ -v -s --log-cli-level=DEBUG

# 停在第一个失败的测试
pytest tests/ -x

# 只运行上次失败的测试
pytest tests/ --lf

# 显示本地变量
pytest tests/ -v -s --tb=long
```

## 最佳实践

### 1. 编写测试

- **测试命名**: 使用描述性的测试名称
- **测试隔离**: 确保测试之间相互独立
- **数据准备**: 使用fixtures准备测试数据
- **断言清晰**: 使用有意义的断言消息

### 2. 性能考虑

- **缓存利用**: 合理使用AKShare数据缓存
- **资源清理**: 测试后清理临时文件
- **内存监控**: 监控测试的内存使用

### 3. 维护测试

- **定期更新**: 随功能更新及时更新测试
- **覆盖率监控**: 定期检查覆盖率报告
- **性能基准**: 监控性能变化趋势

## 贡献指南

### 添加新测试

1. **选择测试类型**: 确定测试的分类和标记
2. **使用fixtures**: 利用现有测试数据fixtures
3. **遵循约定**: 使用项目的测试命名约定
4. **添加文档**: 为复杂测试添加文档字符串

### 测试审查要点

- **测试覆盖**: 新功能是否有对应测试
- **边界条件**: 是否覆盖异常情况
- **性能影响**: 是否需要性能测试
- **集成测试**: 是否需要与其它组件集成测试

---

通过这套完整的测试框架，我们确保财务分析系统的质量、性能和可靠性。所有测试都经过精心设计，覆盖了从基础功能到复杂场景的各个方面。