SHELL := /bin/bash
.SHELLFLAGS := -e -c

.PHONY: sync
sync:
	uv sync --all-extras --all-packages --group dev

.PHONY: format
format: 
	uv run ruff format
	uv run ruff check --fix

.PHONY: format-check
format-check:
	uv run ruff format --check

.PHONY: lint
lint: 
	uv run ruff check

.PHONY: build-docs
build-docs:
	uv run mkdocs build

.PHONY: serve-docs
serve-docs:
	uv run mkdocs serve

.PHONY: deploy-docs
deploy-docs:
	uv run mkdocs gh-deploy --force --verbose

.PHONY: build-ui
build-ui:
	uv pip install build
	npm --version || echo "npm not found, please install npm"
	cd utu/ui/frontend && npm install && bash build.sh
	uv pip install --force-reinstall utu/ui/frontend/build/utu_agent_ui-0.2.0-py3-none-any.whl

.PHONY: demo
demo: build-ui
	uv run python -m demo.demo_universal

# 测试相关命令
.PHONY: test
test: test-check-env
	uv run pytest tests/ -v --cov=utu --cov-report=term-missing

.PHONY: test-check-env
test-check-env:
	python scripts/test_runner.py check

.PHONY: test-unit
test-unit: test-check-env
	python scripts/test_runner.py unit

.PHONY: test-integration
test-integration: test-check-env
	python scripts/test_runner.py integration

.PHONY: test-financial
test-financial: test-check-env
	python scripts/test_runner.py financial

.PHONY: test-performance
test-performance: test-check-env
	python scripts/test_runner.py performance

.PHONY: test-edge
test-edge: test-check-env
	python scripts/test_runner.py edge

.PHONY: test-all
test-all: test-check-env
	python scripts/test_runner.py all

.PHONY: test-quick
test-quick: test-check-env
	python scripts/test_runner.py quick

.PHONY: test-akshare
test-akshare: test-check-env
	uv run pytest tests/integration/test_akshare_real_data.py -v -s -m akshare

.PHONY: test-chart
test-chart: test-check-env
	uv run pytest tests/tools/test_tabular_data_toolkit.py -v -m chart

.PHONY: test-report
test-report: test-check-env
	uv run pytest tests/tools/test_report_saver_toolkit.py -v -m report

.PHONY: test-workflow
test-workflow: test-check-env
	uv run pytest tests/integration/test_financial_workflow.py -v -s -m integration

.PHONY: test-coverage
test-coverage: test-all
	python scripts/test_runner.py report
	@echo "📊 覆盖率报告已生成，查看 test_results/htmlcov/index.html"

# 清理测试文件
.PHONY: test-clean
test-clean:
	rm -rf test_results/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# 安装测试依赖
.PHONY: test-setup
test-setup:
	uv sync --all-extras --all-packages --group dev
	python scripts/test_runner.py check

# 代码质量检查
.PHONY: check-all
check-all: format lint test-quick
	@echo "✅ 所有检查完成"
