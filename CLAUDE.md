# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Youtu-Agent is a flexible, high-performance framework for building, running, and evaluating autonomous agents. Built on openai-agents SDK, it supports various model APIs (including DeepSeek and gpt-oss), tool integrations, and benchmark evaluations.

## Common Commands

### Development Setup
```bash
# Install dependencies
make sync
# or
uv sync --all-extras --all-packages --group dev

# Activate virtual environment
source ./.venv/bin/activate
```

### Code Quality
```bash
# Format code
make format
# or
uv run ruff format
uv run ruff check --fix

# Lint code
make lint
# or
uv run ruff check

# Check formatting
make format-check
# or
uv run ruff format --check
```

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/agents/test_simple_agent.py

# Run with verbose output
uv run pytest -v -s
```

### Running Agents
```bash
# Interactive CLI chat with default agent
python scripts/cli_chat.py --stream --config default

# Run with base agent (no search tools)
python scripts/cli_chat.py --stream --config base

# Generate agent configuration interactively
python scripts/gen_simple_agent.py
```

### Running Evaluations
```bash
# Process WebWalkerQA dataset
python scripts/data/process_web_walker_qa.py

# Run evaluation on WebWalkerQA
python scripts/run_eval.py --config_name ww --exp_id <exp_id> --dataset WebWalkerQA_15 --concurrency 5
```

### Documentation
```bash
# Build docs
make build-docs
# or
uv run mkdocs build

# Serve docs locally
make serve-docs
# or
uv run mkdocs serve
```

## Architecture

### Core Components

1. **Agents** (`utu/agents/`):
   - `BaseAgent`: Abstract base class for all agents
   - `SimpleAgent`: Basic agent implementation
   - `OrchestraAgent`: Multi-agent orchestration
   - `WorkforceAgent`: Collaborative agent workforce

2. **Configuration** (`utu/config/`):
   - YAML-based configuration system using Hydra
   - `ConfigLoader`: Loads agent, model, and evaluation configs
   - Config files in `configs/` directory

3. **Tools** (`utu/tools/`):
   - `AsyncBaseToolkit`: Base class for all toolkits
   - Various toolkits: search, bash, python_executor, document, image, etc.
   - MCP (Model Context Protocol) support

4. **Evaluation** (`utu/eval/`):
   - Benchmark evaluation system
   - Support for WebWalkerQA, GAIA, and custom datasets
   - Processor pipeline for different evaluation types

5. **Tracing** (`utu/tracing/`):
   - OTEL integration for observability
   - Custom `DBTracingProcessor` for tool call analysis
   - Phoenix integration for advanced tracing

### Configuration System

The framework uses a hierarchical YAML configuration system:
- Base configs in `configs/model/base.yaml`, `configs/tools/*.yaml`
- Agent configs in `configs/agents/`
- Evaluation configs in `configs/eval/`
- Hydra handles config composition and overrides

### Environment Setup

Required environment variables (see `.env.example`):
- `UTU_LLM_TYPE`, `UTU_LLM_MODEL`, `UTU_LLM_BASE_URL`, `UTU_LLM_API_KEY`: LLM configuration
- `SERPER_API_KEY`, `JINA_API_KEY`: Search and web extraction tools
- `DB_URL`: Database for tracing and evaluation data
- `PHOENIX_ENDPOINT`: Optional Phoenix tracing endpoint

### Key Design Patterns

1. **Async/Await**: Fully asynchronous architecture for high performance
2. **Modular Toolkits**: Encapsulated tool sets with consistent interfaces
3. **Config-Driven**: Behavior defined through YAML configurations
4. **Extensible**: Easy to add new agents, tools, and evaluation benchmarks

### Testing Strategy

Tests are organized by component:
- `tests/agents/`: Agent implementations
- `tests/tools/`: Toolkit functionality
- `tests/eval/`: Evaluation system
- `tests/tracing/`: Tracing and observability

Use `uv run pytest` with appropriate flags for different testing scenarios.