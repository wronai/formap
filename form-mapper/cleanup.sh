#!/bin/bash
# FORMAP - Cleanup Script
# This script cleans up the development environment for the FORMAP project

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

section "Cleaning up Python artifacts"

# Remove Python cache files
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.py[co]" -delete
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true

# Remove coverage files
rm -f .coverage coverage.xml htmlcov/.gitignore 2>/dev/null || true
rm -rf htmlcov/ 2>/dev/null || true

# Remove Jupyter notebook checkpoints
find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true

section "Cleaning up virtual environment"

# Remove virtual environment
if [ -d "venv" ]; then
    echo -e "${YELLOW}Removing virtual environment...${NC}"
    rm -rf venv/
    echo -e "${GREEN}✓ Virtual environment removed.${NC}"
else
    echo -e "${GREEN}✓ No virtual environment found.${NC}"
fi

section "Cleaning up Playwright browsers"

# Remove Playwright browsers if Playwright is installed
if command -v playwright >/dev/null 2>&1; then
    echo -e "${YELLOW}Removing Playwright browsers...${NC}"
    playwright uninstall
    echo -e "${GREEN}✓ Playwright browsers removed.${NC}"
else
    echo -e "${GREEN}✓ Playwright not found, skipping browser cleanup.${NC}"
fi

section "Cleaning up temporary files"

# Remove temporary files
find . -type f -name "*.log" -delete
find . -type f -name ".coverage" -delete
find . -type f -name "coverage.xml" -delete
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.pyd" -delete
find . -type f -name "*.so" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Remove macOS specific files
find . -type f -name ".DS_Store" -delete
find . -type d -name "*.dSYM" -exec rm -rf {} + 2>/dev/null || true

section "Cleanup complete!"
echo -e "${GREEN}✓ FORMAP environment has been cleaned up.${NC}"
