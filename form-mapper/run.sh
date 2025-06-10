#!/bin/bash
# FORMAP - Run Script
# This script provides a simple interface to run the FORMAP tools

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print section headers
section() {
    echo -e "\n${BLUE}==> $1${NC}"
}

# Function to check if virtual environment exists
check_venv() {
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}Virtual environment not found. Setting up...${NC}"
        ./setup.sh
    fi
    
    # Activate virtual environment if not already activated
    if [ -z "${VIRTUAL_ENV:-}" ]; then
        source venv/bin/activate
    fi
}

# Function to run map_fields.py
run_map() {
    check_venv
    section "Running Form Field Mapper"
    if [ $# -eq 0 ]; then
        echo -e "${YELLOW}Usage: $0 map <url> [output_file]${NC}"
        echo -e "Example: $0 map https://example.com/form form_map.json"
        exit 1
    fi
    
    URL=$1
    OUTPUT_FILE="${2:-form_map.json}"
    
    echo -e "Mapping form at: ${GREEN}$URL${NC}"
    echo -e "Output file: ${GREEN}$OUTPUT_FILE${NC}"
    
    python map_fields.py "$URL" "$OUTPUT_FILE"
}

# Function to run fill_form.py
run_fill() {
    check_venv
    section "Running Form Filler"
    INPUT_FILE="${1:-form_map.json}"
    
    if [ ! -f "$INPUT_FILE" ]; then
        echo -e "${YELLOW}Error: Mapping file '$INPUT_FILE' not found.${NC}"
        echo -e "First run: $0 map <url> [output_file]"
        exit 1
    fi
    
    echo -e "Using mapping file: ${GREEN}$INPUT_FILE${NC}"
    python fill_form.py "$INPUT_FILE"
}

# Function to show help
show_help() {
    echo -e "${BLUE}FORMAP - Form Mapper & Auto-Filler${NC}"
    echo -e "${BLUE}=================================${NC}\n"
    
    echo -e "${GREEN}Usage:${NC} $0 [command] [options]\n"
    
    echo -e "${GREEN}Commands:${NC}"
    echo -e "  ${YELLOW}map <url> [output_file]${NC}    Map form fields from a URL"
    echo -e "  ${YELLOW}fill [input_file]${NC}         Fill a form using a mapping file"
    echo -e "  ${YELLOW}setup${NC}                     Set up the development environment"
    echo -e "  ${YELLOW}clean${NC}                     Clean up the development environment"
    echo -e "  ${YELLOW}help${NC}                      Show this help message\n"
    
    echo -e "${GREEN}Examples:${NC}"
    echo -e "  ${YELLOW}$0 map https://example.com/form${NC}         # Map form fields"
    echo -e "  ${YELLOW}$0 fill form_map.json${NC}                   # Fill a form"
    echo -e "  ${YELLOW}$0 map https://example.com/form my_form.json${NC} # Map with custom output"
}

# Main script
case "${1:-help}" in
    map)
        shift
        run_map "$@"
        ;;
    fill)
        shift
        run_fill "$@"
        ;;
    setup)
        ./setup.sh
        ;;
    clean)
        ./cleanup.sh
        ;;
    help|--help|-h|*)
        show_help
        ;;
esac
