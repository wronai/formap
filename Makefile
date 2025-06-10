# Makefile for formap project

# Default target when just 'make' is run
help:
	@echo "Available commands:"
	@echo "  install     - Install the package in development mode"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linters and formatters"
	@echo "  clean      - Clean build artifacts"
	@echo "  build      - Build the package"
	@echo "  publish    - Build and publish the package to PyPI"

# Install the package in development mode
install:
	poetry install

# Run tests
test:
	poetry run pytest tests/ -v

# Run linters and formatters
lint:
	poetry run black --check .
	poetry run isort --check-only .
	poetry run mypy formap/

# Format code
format:
	poetry run black .
	poetry run isort .

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/ htmlcov/

# Build the package
build:
	poetry version patch
	poetry build

# Publish the package to PyPI
publish: clean build
	@echo "Publishing to PyPI..."
	poetry publish

# Set default target
.PHONY: help install test lint format clean build publish
