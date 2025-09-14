# Financial Analysis Toolkit for Chinese A-Shares

A specialized toolkit for Chinese A-share financial data analysis, built on the Youtu-Agent framework. This project provides stable, reliable financial data interfaces and standardized analysis capabilities.

## 🌟 Features

### 📊 Financial Data Acquisition
- **Multi-source support**: AKShare integration for reliable A-share financial data
- **Smart caching**: Automatic caching and incremental updates to reduce API calls
- **Data cleaning**: Automated data preprocessing and standardization
- **Error handling**: Robust error handling and fallback mechanisms

### 📈 Financial Analysis
- **Ratio calculation**: Comprehensive financial ratio analysis (profitability, solvency, efficiency, growth)
- **Trend analysis**: Multi-year trend analysis with CAGR calculations
- **Health assessment**: Financial health scoring and risk evaluation
- **Report generation**: Automated comprehensive analysis reports

### 🔧 Technical Features
- **Modular design**: Clean, extensible architecture
- **Standardized interfaces**: Consistent APIs for all financial operations
- **Performance optimized**: Efficient data processing and caching
- **Well documented**: Comprehensive documentation and examples

## 🚀 Quick Start

### Installation

```bash
pip install akshare>=1.12.0
```

### Basic Usage

```python
from financial_tools import AKShareFinancialDataTool, StandardFinancialAnalyzer

# Initialize tools
data_tool = AKShareFinancialDataTool()
analyzer = StandardFinancialAnalyzer()

# Get financial data
financial_data = data_tool.get_financial_reports("600519", "贵州茅台")

# Analyze financial data
ratios = analyzer.calculate_financial_ratios(financial_data)
trends = analyzer.analyze_trends(financial_data)
health = analyzer.assess_financial_health(ratios, trends)

# Generate report
report = analyzer.generate_analysis_report(financial_data, "贵州茅台")
```

## 📁 Project Structure

```
financial_analysis_project/
├── financial_tools/
│   ├── akshare_financial_tool.py      # Financial data acquisition
│   ├── financial_analysis_toolkit.py   # Financial analysis toolkit
│   └── __init__.py
├── examples/
│   ├── basic_usage.py                 # Basic usage examples
│   └── comprehensive_analysis.py      # Comprehensive analysis examples
├── tests/
│   ├── test_data_tool.py              # Data tool tests
│   └── test_analyzer.py               # Analyzer tests
├── README.md                          # Project documentation
└── requirements.txt                   # Dependencies
```

## 🛠️ API Overview

### Financial Data Tool

```python
class AKShareFinancialDataTool:
    def get_financial_reports(self, stock_code, stock_name=None, force_refresh=False)
    def get_key_metrics(self, financial_data)
    def get_historical_trend(self, financial_data, years=4)
    def save_to_csv(self, financial_data, filepath_prefix)
    def refresh_cache(self, stock_code, stock_name=None)
    def cleanup_cache(self, days=30)
```

### Financial Analyzer

```python
class StandardFinancialAnalyzer:
    def calculate_financial_ratios(self, financial_data)
    def analyze_trends(self, financial_data, years=4)
    def assess_financial_health(self, ratios, trends)
    def generate_analysis_report(self, financial_data, stock_name="目标公司")
```

## 📈 Analysis Capabilities

### Financial Ratios
- **Profitability**: Gross margin, Net margin, ROE, ROA
- **Solvency**: Current ratio, Debt-to-asset ratio
- **Efficiency**: Asset turnover
- **Growth**: Revenue growth, Profit growth

### Trend Analysis
- Revenue trends with CAGR
- Profit trends with CAGR
- Multi-year growth rates

### Health Assessment
- Overall financial health scoring
- Risk level evaluation
- Strengths and weaknesses identification
- Actionable recommendations

## 📚 Documentation

### Data Sources
- **AKShare**: Primary data source for A-share financial data
- **Eastmoney**: Financial statements from Eastmoney website
- **Sina Finance**: Backup data sources

### Supported Markets
- Shanghai Stock Exchange (6xxxxx)
- Shenzhen Stock Exchange (0xxxxx, 3xxxxx)
- ChiNext (300xxx)
- STAR Market (688xxx)

## 🧪 Testing

```bash
python -m pytest tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

MIT License

## 🙏 Acknowledgments

- [AKShare](https://github.com/akfamily/akshare) - For providing excellent financial data
- [Youtu-Agent](https://github.com/TencentCloudADP/youtu-agent) - For the underlying agent framework