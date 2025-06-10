#!/bin/bash
# FORMAP - Environment Setup Script
# This script sets up the development environment for the FORMAP project

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print section headers
section() {
    echo -e "\n${YELLOW}==> $1${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if running as root
if [ "$(id -u)" -eq 0 ]; then
    echo -e "${RED}Error: Do not run this script as root.${NC}" >&2
    exit 1
fi

section "Checking system requirements"

# Check Python version
if ! command_exists python3; then
    echo -e "${RED}Error: Python 3.8+ is required but not installed.${NC}" >&2
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if [[ "$(printf '%s\n' "3.8" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.8" ]]; then
    echo -e "${RED}Error: Python 3.8 or higher is required. Found Python $PYTHON_VERSION.${NC}" >&2
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION is installed.${NC}"

# Check for pip
if ! command_exists pip3; then
    echo -e "${RED}Error: pip3 is required but not installed.${NC}" >&2
    exit 1
fi

section "Setting up Python virtual environment"

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created.${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists.${NC}"
fi

# Activate virtual environment
source venv/bin/activate

section "Installing Python dependencies"

# Upgrade pip
pip install --upgrade pip

# Install dependencies
if [ -f "requirements-dev.txt" ]; then
    pip install -r requirements-dev.txt
    echo -e "${GREEN}✓ Development dependencies installed.${NC}"
else
    echo -e "${RED}Error: requirements-dev.txt not found.${NC}" >&2
    exit 1
fi

section "Installing Playwright browsers"

# Install Playwright browsers
python -m playwright install
python -m playwright install-deps

echo -e "${GREEN}✓ Playwright browsers installed.${NC}"

section "Setting up pre-commit hooks"

# Install pre-commit hooks
if command_exists pre-commit; then
    pre-commit install
    echo -e "${GREEN}✓ Pre-commit hooks installed.${NC}"
else
    echo -e "${YELLOW}Warning: pre-commit not found. Skipping pre-commit setup.${NC}"
fi

section "Environment setup complete!"
echo -e "${GREEN}✓ FORMAP development environment is ready!${NC}"
echo -e "\nTo activate the virtual environment, run:\n  ${YELLOW}source venv/bin/activate${NC}"
echo -e "\nTo deactivate the virtual environment, run:\n  ${YELLOW}deactivate${NC}"
