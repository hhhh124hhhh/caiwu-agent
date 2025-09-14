# How to Contribute

First off, thank you for considering contributing to Youtu-Agent 财务分析智能体! It's people like you that make our community and software better. We welcome any and all contributions.

We use GitHub [pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) to accept contributions.

## Guidelines

To ensure a smooth and effective contribution process, please adhere to the following guidelines:

1.  **Link to an Existing Issue**: All pull requests should be linked to an existing issue. If you're proposing a new feature or a bug fix, please create an issue first to discuss it with the maintainers.
2.  **Keep It Small and Focused**: Avoid bundling multiple features or fixes in a single pull request. Smaller, focused PRs are easier to review and merge.
3.  **Use Draft PRs for Work in Progress**: If your work is not yet ready for review, open it as a [draft pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests#draft-pull-requests). This signals that you're still working on it and prevents premature reviews.
4.  **Ensure All Checks Pass**: Before submitting your PR for review, make sure that all automated checks (like linting and testing) are passing.
5.  **Update Documentation**: If you're adding a new feature or changing an existing one, please update the relevant documentation to reflect your changes.
6.  **Write Clear Commit Messages and a Good PR Description**: A clear description of your changes is crucial. Explain the "what" and the "why" of your contribution, not just the "how".

## Development Workflow

### Environment Setup

For a complete guide on setting up your development environment, please refer to our [Quick Start](https://tencentcloudadp.github.io/youtu-agent/quickstart/) documentation. Here are the essential steps for the financial analysis project:

```sh
# 克隆项目
git clone <repository-url>
cd youtu-agent

# 安装依赖
uv sync --all-extras --all-packages --group dev

# 激活虚拟环境
source ./.venv/bin/activate

# Install pre-commit hooks to automatically check your code before committing
pre-commit install

# You can test the hooks at any time by running:
pre-commit run
```

### Formatting & Linting

We use `pre-commit` to automatically format code and run linters on every commit. This helps maintain a consistent code style across the project.

While the hooks run automatically, we also recommend running the formatting and linting checks manually before you commit your changes. This can help you catch and fix issues earlier.

```sh
# Format code and run linters
make format
```

### Testing

Ensure your changes are covered by tests. If you've modified a specific component, like the financial analysis toolkit, you can run its specific tests:

```sh
# 运行财务分析工具的特定测试
cd examples/stock_analysis
python test_standardized_analysis.py

# 或者运行单元测试
pytest tests/tools/test_financial_tools.py
```

To run the entire test suite:

```sh
pytest
```

### Financial Analysis Specific Guidelines

When contributing to the financial analysis components, please follow these additional guidelines:

1. **Data Accuracy**: Ensure all financial calculations are accurate and follow standard financial formulas.
2. **Cache Handling**: Be mindful of the smart caching mechanism when adding new data sources.
3. **Error Handling**: Implement proper error handling for financial data retrieval and processing.
4. **Performance**: Consider the performance impact of new features on financial data processing.
5. **Documentation**: Update the [STANDARDIZED_ANALYSIS_GUIDE.md](examples/stock_analysis/STANDARDIZED_ANALYSIS_GUIDE.md) when adding new features or modifying existing ones.

### Submitting Your Pull Request

Once your changes are ready, tested, and linted, commit your code and open a pull request on GitHub. The maintainers will review it as soon as possible.

If you have any questions or need assistance during the contribution process, please contact us via the following methods:
- 📧 **Email**: hhhh124hhhh@qq.com
- 🐛 **Bug反馈**: 请提供详细的错误日志和复现步骤
- 💡 **功能建议**: 欢迎提出新的分析需求或改进建议

Thank you for your contribution!