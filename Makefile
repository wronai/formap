# Makefile for formap project

# Default target when just 'make' is run
.DEFAULT_GOAL := help
.PHONY: help install test lint format check clean build publish docs bump-version pre-commit coverage install-hooks clean-all

# Get version from pyproject.toml
VERSION := $(shell poetry version -s)

# Help target
help:  ## Display this help message
	@echo "\n\033[1mAvailable commands:\033[0m"
	@echo "\n\033[1mProject Setup:\033[0m"
	@echo "  \033[32mhelp\033[0m          - Show this help message"
	@echo "  \033[32minstall\033[0m       - Install the package in development mode"
	@echo "  \033[32minstall-hooks\033[0m - Install git hooks"
	@echo "\n\033[1mDevelopment:\033[0m"
	@echo "  \033[32mtest\033[0m          - Run tests"
	@echo "  \033[32mlint\033[0m          - Run linters and type checking"
	@echo "  \033[32mformat\033[0m        - Format code"
	@echo "  \033[32mcheck\033[0m         - Run lint and test (CI)"
	@echo "  \033[32mcoverage\033[0m      - Generate test coverage report"
	@echo "  \033[32mpre-commit\033[0m     - Run pre-commit hooks"
	@echo "\n\033[1mBuild & Release:\033[0m"
	@echo "  \033[32mbuild\033[0m         - Build the package (bumps patch version)"
	@echo "  \033[32mpublish\033[0m       - Build and publish the package to PyPI"
	@echo "  \033[32mbump-version\033[0m   - Bump version (patch/minor/major)"
	@echo "\n\033[1mDocumentation:\033[0m"
	@echo "  \033[32mdocs\033[0m          - Build documentation"
	@echo "\n\033[1mCleanup:\033[0m"
	@echo "  \033[32mclean\033[0m         - Clean build artifacts"
	@echo "  \033[32mclean-all\033[0m     - Clean everything (including caches and venv)"

# Project Setup
install:  ## Install the package in development mode
	@echo "Installing dependencies..."
	poetry install --with dev,docs

install-hooks:  ## Install git hooks
	@echo "Installing pre-commit hooks..."
	poetry run pre-commit install

# Development
test:  ## Run tests
	@echo "Running tests..."
	poetry run pytest tests/ -v --cov=formap --cov-report=term-missing

lint:  ## Run linters and type checking
	@echo "Running linters..."
	poetry run black --check .
	poetry run isort --check-only .
	poetry run mypy formap/

format:  ## Format code
	@echo "Formatting code..."
	poetry run black .
	poetry run isort .

check: lint test  ## Run lint and test (CI)


pre-commit:  ## Run pre-commit hooks
	@echo "Running pre-commit hooks..."
	poetry run pre-commit run --all-files

coverage: test  ## Generate test coverage report
	@echo "Generating coverage report..."
	poetry run coverage html
	@echo "Open htmlcov/index.html in your browser to view the coverage report."

# Build & Release
build:  ## Build the package (bumps patch version)
	@echo "Building package v$(VERSION)..."
	poetry version patch > /dev/null
	@echo "Bumped version to $(shell poetry version -s)"
	poetry build

publish: clean build  ## Build and publish the package to PyPI
	@echo "Publishing v$(shell poetry version -s) to PyPI..."
	poetry publish

bump-version:  ## Bump version (patch/minor/major)
	@if [ -z "$(bump)" ]; then \
		echo "Usage: make bump-version bump=<patch|minor|major>"; \
		exit 1; \
	fi
	@echo "Bumping $(bump) version..."
	poetry version $(bump) > /dev/null
	@echo "New version: $(shell poetry version -s)"

# Documentation
docs:  ## Build documentation
	@echo "Building documentation..."
	poetry run mkdocs build --clean
	@echo "Documentation built in site/ directory"

# Cleanup
clean:  ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/ htmlcov/ .coverage

clean-all: clean  ## Clean everything (including caches and venv)
	@echo "Cleaning everything..."
	rm -rf .venv/ .tox/ .cache/ .pytest_cache/ .mypy_cache/ .coverage htmlcov/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
