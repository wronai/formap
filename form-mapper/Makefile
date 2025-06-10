.PHONY: help venv install install-browsers clean clean-pyc clean-test test

# Variables
PYTHON = python3
PIP = pip
VENV = venv

# Default target
help:
	@echo "FORMAP - Form Mapper & Auto-Filler"
	@echo "=================================="
	@echo "Available targets:"
	@echo "  venv           : Create Python virtual environment"
	@echo "  install        : Install Python dependencies"
	@echo "  install-browsers: Install Playwright browsers"
	@echo "  test           : Run tests"
	@echo "  clean          : Remove Python file artifacts and virtual environment"
	@echo "  clean-pyc      : Remove Python file artifacts"
	@echo "  clean-test     : Remove test and coverage artifacts"

# Create a Python virtual environment
venv:
	@echo "Creating Python virtual environment..."
	$(PYTHON) -m venv $(VENV) --clear
	@echo "Virtual environment created in $(VENV)"
	@echo "To activate, run: source $(VENV)/bin/activate"

# Install Python dependencies
install:
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Run 'make venv' first."; \
		exit 1; \
	fi
	@echo "Installing Python dependencies..."
	$(VENV)/bin/$(PIP) install --upgrade pip
	$(VENV)/bin/$(PIP) install -r requirements.txt
	@echo "\n✅ Dependencies installed"

# Install Playwright browsers
install-browsers:
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Run 'make venv' first."; \
		exit 1; \
	fi
	@echo "Installing Playwright browsers..."
	$(VENV)/bin/$(PYTHON) -m playwright install
	@echo "\n✅ Browsers installed"

# Run tests
test:
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Run 'make venv' first."; \
		exit 1; \
	fi
	@echo "Running tests..."
	$(VENV)/bin/$(PYTHON) -m pytest tests/ -v

# Clean up
clean: clean-pyc clean-test
	@echo "Removing virtual environment..."
	@rm -rf $(VENV)
	@echo "Removing build artifacts..."
	@rm -rf build/ dist/ .eggs/ .pytest_cache/ .mypy_cache/
	@find . -name '*.egg-info' -exec rm -rf {} +
	@find . -name '*.egg' -exec rm -f {}

# Remove Python file artifacts
clean-pyc:
	@echo "Removing Python file artifacts..."
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -rf {} +

# Remove test and coverage artifacts
clean-test:
	@echo "Cleaning test artifacts..."
	@rm -f .coverage coverage.xml
	@rm -rf htmlcov/
	@rm -rf .pytest_cache/

# Default command when running just 'make'
.DEFAULT_GOAL := help