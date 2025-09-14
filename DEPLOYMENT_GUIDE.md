# Deployment Guide

This guide explains how to deploy the Financial Analysis Toolkit for Chinese A-Shares to a GitHub repository.

## Prerequisites

1. Git installed on your system
2. GitHub account
3. Python 3.7 or higher

## Step 1: Create a New Repository on GitHub

1. Go to https://github.com and log in to your account
2. Click the "+" icon in the upper right corner and select "New repository"
3. Set the repository name to `chinese-stock-analysis-toolkit`
4. Add a description: "A specialized toolkit for Chinese A-share financial data analysis with smart caching and standardized analysis capabilities"
5. Choose Public (or Private if you prefer)
6. Do NOT initialize with a README
7. Click "Create repository"

## Step 2: Configure Local Repository

1. Open a terminal/command prompt
2. Navigate to the project directory:
   ```bash
   cd d:\youtu-agent\financial_analysis_project
   ```

3. Add the remote origin (replace `your-username` with your GitHub username):
   ```bash
   git remote add origin https://github.com/your-username/chinese-stock-analysis-toolkit.git
   ```

## Step 3: Push to GitHub

1. Push the code to GitHub:
   ```bash
   git push -u origin master
   ```

2. If prompted, enter your GitHub username and personal access token (not password)

## Creating a Personal Access Token

If you don't have a personal access token:

1. Go to GitHub Settings
2. Click "Developer settings"
3. Click "Personal access tokens"
4. Click "Tokens (classic)"
5. Click "Generate new token (classic)"
6. Give it a name like "financial-analysis-toolkit"
7. Select scopes: `repo`
8. Click "Generate token"
9. Copy the token and save it securely

## Verifying the Deployment

After pushing, you should be able to see your code at:
```
https://github.com/your-username/chinese-stock-analysis-toolkit
```

## Installing Dependencies

To use the toolkit, users need to install the required dependencies:

```bash
pip install -r requirements.txt
```

Or install directly:
```bash
pip install akshare>=1.12.0 pandas>=1.3.0 numpy>=1.21.0 matplotlib>=3.5.0 seaborn>=0.11.0 plotly>=5.0.0
```

## Running Examples

1. Basic usage:
   ```bash
   python examples/basic_usage.py
   ```

2. Comprehensive analysis:
   ```bash
   python examples/comprehensive_analysis.py
   ```

## Running Tests

To run all tests:
```bash
python run_tests.py
```

Or run individual test files:
```bash
python tests/test_data_tool.py
python tests/test_analyzer.py
```

## Project Structure

```
chinese-stock-analysis-toolkit/
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
├── requirements.txt                   # Dependencies
├── run_tests.py                      # Test runner
└── DEPLOYMENT_GUIDE.md               # This file
```

## API Overview

### Financial Data Tool

The `AKShareFinancialDataTool` provides methods for fetching Chinese A-share financial data:

- `get_financial_reports(stock_code, stock_name=None, force_refresh=False)`
- `get_key_metrics(financial_data)`
- `get_historical_trend(financial_data, years=4)`
- `save_to_csv(financial_data, filepath_prefix)`
- `refresh_cache(stock_code, stock_name=None)`
- `cleanup_cache(days=30)`

### Financial Analyzer

The `StandardFinancialAnalyzer` provides methods for financial analysis:

- `calculate_financial_ratios(financial_data)`
- `analyze_trends(financial_data, years=4)`
- `assess_financial_health(ratios, trends)`
- `generate_analysis_report(financial_data, stock_name="目标公司")`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.