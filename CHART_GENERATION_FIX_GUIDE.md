# 图表生成工具修复使用指南

## 修复概述

本次修复解决了图表生成工具中的关键问题，特别是雷达图生成和HTML报告模板的变量引用错误。

## 修复内容

### 1. 增强雷达图支持

**修复前问题**：
- 雷达图只支持公司对比格式
- 无法生成单公司多维度雷达图
- 数据格式要求过于严格

**修复后改进**：
- ✅ 支持单公司多维度雷达图格式
- ✅ 支持多公司对比雷达图格式
- ✅ 支持灵活的数据结构

### 2. 修复HTML报告变量引用

**修复前问题**：
```
NameError: name 'investment_advice' is not defined
NameError: name 'basic_info' is not defined
```

**修复后改进**：
- ✅ 所有变量引用改为 `integrated_data['xxx']` 格式
- ✅ 统一数据结构引用
- ✅ 修复HTML和Markdown模板

### 3. 改进JSON错误处理

**修复前问题**：
- 错误提示不够清晰
- 缺少格式示例指导

**修复后改进**：
- ✅ 详细的错误信息
- ✅ 提供正确格式示例
- ✅ 针对不同图表类型的专门指导

## 使用方法

### 雷达图生成

#### 1. 单公司多维度雷达图

```python
from utu.tools.tabular_data_toolkit import TabularDataToolkit
import json

# 创建工具实例
toolkit = TabularDataToolkit({"workspace_root": "./output"})

# 准备数据
radar_data = {
    "title": "陕西建工财务健康雷达图",
    "categories": ["盈利能力", "偿债能力", "运营效率", "成长能力", "现金流"],
    "series": [
        {
            "name": "陕西建工",
            "data": [30, 20, 25, 15, 10]  # 各维度得分（0-100）
        }
    ]
}

# 生成雷达图
result = toolkit.generate_charts(
    data_json=json.dumps(radar_data, ensure_ascii=False),
    chart_type="radar",
    output_dir="./charts"
)

if result['success']:
    print(f"雷达图生成成功: {result['files']}")
else:
    print(f"生成失败: {result['message']}")
```

#### 2. 多公司对比雷达图

```python
# 多公司对比数据
comparison_data = {
    "title": "建筑行业财务对比雷达图",
    "categories": ["盈利能力", "偿债能力", "运营效率", "成长能力", "现金流"],
    "series": [
        {
            "name": "陕西建工",
            "data": [30, 20, 25, 15, 10]
        },
        {
            "name": "行业平均",
            "data": [60, 70, 55, 50, 65]
        },
        {
            "name": "龙头公司",
            "data": [80, 75, 70, 60, 70]
        }
    ]
}

# 生成对比雷达图
result = toolkit.generate_charts(
    data_json=json.dumps(comparison_data, ensure_ascii=False),
    chart_type="radar",
    output_dir="./charts"
)
```

### 数据格式说明

#### 必需字段
- `title`: 图表标题
- `series`: 数据系列数组

#### 可选字段
- `categories`: 维度标签数组（推荐提供）
- `series[i].name`: 系列名称
- `series[i].data`: 系列数据数组

#### 数据格式示例

**格式1：带类别的雷达图（推荐）**
```json
{
    "title": "财务健康雷达图",
    "categories": ["盈利能力", "偿债能力", "运营效率", "成长能力", "现金流"],
    "series": [
        {
            "name": "公司名称",
            "data": [30, 20, 25, 15, 10]
        }
    ]
}
```

**格式2：不带类别的雷达图**
```json
{
    "title": "财务健康雷达图",
    "series": [
        {
            "name": "公司名称",
            "data": [30, 20, 25, 15, 10]
        }
    ]
}
```

### 错误处理

当JSON格式错误时，工具会提供详细的错误信息和格式示例：

```python
# 错误示例
invalid_json = '{"title": "test", "categories": ["A", "B"], "series": [{"name": "test", "data": [1, 2]'  # 缺少括号

result = toolkit.generate_charts(invalid_json, "radar", "./output")

# 错误响应示例
{
    "success": False,
    "message": "JSON解析错误: Expecting ',' delimiter: line 1 column 80 (char 79)\n\n请使用正确的JSON格式，例如：\n{\n    \"title\": \"陕西建工财务健康雷达图\",\n    \"categories\": [\"盈利能力\", \"偿债能力\", \"运营效率\", \"成长能力\", \"现金流\"],\n    \"series\": [\n        {\"name\": \"陕西建工\", \"data\": [30, 20, 25, 15, 10]}\n    ]\n}",
    "files": [],
    "error": "Expecting ',' delimiter: line 1 column 80 (char 79)",
    "format_example": {
        "title": "陕西建工财务健康雷达图",
        "categories": ["盈利能力", "偿债能力", "运营效率", "成长能力", "现金流"],
        "series": [{"name": "陕西建工", "data": [30, 20, 25, 15, 10]}]
    }
}
```

## 财务分析报告生成

修复后的系统现在可以正常生成完整的HTML财务分析报告：

```python
# 运行完整的股票分析
cd examples/stock_analysis
python main.py --stock 600248 --name 陕西建工
```

系统将自动：
1. ✅ 获取财务数据
2. ✅ 计算财务比率
3. ✅ 生成雷达图和对比图表
4. ✅ 创建HTML报告
5. ✅ 生成PDF报告
6. ✅ 保存Markdown报告

## 支持的图表类型

除了雷达图，系统还支持：

### 1. 柱状图 (bar)
```json
{
    "title": "财务指标对比",
    "x_axis": ["2022", "2023", "2024"],
    "series": [
        {"name": "营业收入", "data": [1000, 1200, 1500]},
        {"name": "净利润", "data": [80, 100, 130]}
    ]
}
```

### 2. 趋势图 (trend)
```json
{
    "title": "营收增长趋势",
    "x_axis": ["2022", "2023", "2024"],
    "series": [
        {"name": "营收增长率", "data": [10, 20, 25]}
    ]
}
```

## 实际应用示例

### 陕西建工财务分析示例

```python
# 生成陕西建工的财务雷达图
shanxi_jiankong_radar = {
    "title": "陕西建工(600248.SH)财务健康雷达图",
    "categories": ["盈利能力", "偿债能力", "运营效率", "成长能力", "现金流"],
    "series": [
        {
            "name": "陕西建工",
            "data": [25, 30, 20, 15, 25]  # 基于实际财务数据计算
        },
        {
            "name": "建筑行业平均",
            "data": [60, 65, 55, 45, 50]
        }
    ]
}

# 生成图表
result = toolkit.generate_charts(
    data_json=json.dumps(shanxi_jiankong_radar, ensure_ascii=False),
    chart_type="radar",
    output_dir="./financial_reports"
)
```

### 多维度财务指标对比

```python
# 对比多个财务指标
financial_metrics = {
    "title": "主要财务指标雷达图",
    "categories": ["净资产收益率", "资产负债率", "流动比率", "净利润增长率", "营收增长率"],
    "series": [
        {
            "name": "陕西建工",
            "data": [8.5, 88.7, 0.97, -69.4, -62.0]
        },
        {
            "name": "行业平均",
            "data": [12.0, 75.0, 1.5, 5.0, 8.0]
        }
    ]
}
```

## 故障排除

### 常见问题

1. **JSON格式错误**
   - 确保所有字符串使用双引号
   - 检查括号和逗号是否匹配
   - 参考错误提示中的格式示例

2. **数据长度不匹配**
   - 确保 `series[i].data` 的长度与 `categories` 的长度一致
   - 或者不提供 `categories` 字段

3. **图表生成失败**
   - 检查输出目录是否存在且有写入权限
   - 查看详细的错误日志

4. **变量引用错误**
   - 确保使用最新版本的代码
   - 检查 `integrated_data` 结构是否正确

### 调试技巧

1. **启用详细日志**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **验证数据格式**
```python
import json
try:
    data = json.loads(your_json_string)
    print("JSON格式正确")
except json.JSONDecodeError as e:
    print(f"JSON错误: {e}")
```

3. **测试简单示例**
```python
# 先用最简单的数据测试
simple_data = {
    "title": "测试雷达图",
    "series": [{"name": "测试", "data": [50]}]
}
```

## 总结

本次修复彻底解决了图表生成工具的核心问题：

- ✅ **雷达图支持**：支持单公司和多公司对比格式
- ✅ **错误处理**：提供详细的错误信息和格式指导
- ✅ **变量引用**：修复HTML报告模板的所有变量引用错误
- ✅ **兼容性**：支持灵活的数据格式，向后兼容

现在系统可以稳定地为陕西建工等A股公司生成专业的财务分析报告和图表。