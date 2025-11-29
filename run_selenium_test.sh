#!/bin/bash

# Selenium Test Runner Script
# Makes it easy to run generated Selenium scripts

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
VERBOSE=false
HEADLESS=true
SCRIPT_PATH=""
RUN_ALL=false

# Help function
show_help() {
    echo "Selenium Test Runner"
    echo ""
    echo "Usage: ./run_selenium_test.sh [OPTIONS] <script_path>"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -v, --verbose       Enable verbose output"
    echo "  --no-headless       Run browser in GUI mode (not headless)"
    echo "  --all               Run all scripts in data/scripts/"
    echo ""
    echo "Examples:"
    echo "  ./run_selenium_test.sh data/scripts/TC_001_selenium.py"
    echo "  ./run_selenium_test.sh --verbose data/scripts/TC_001_selenium.py"
    echo "  ./run_selenium_test.sh --no-headless data/scripts/TC_001_selenium.py"
    echo "  ./run_selenium_test.sh --all"
    echo ""
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --no-headless)
            HEADLESS=false
            shift
            ;;
        --all)
            RUN_ALL=true
            shift
            ;;
        *)
            SCRIPT_PATH="$1"
            shift
            ;;
    esac
done

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}⚠️  Virtual environment not activated${NC}"
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install Selenium if not installed
if ! python -c "import selenium" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Selenium not installed${NC}"
    echo "Installing Selenium..."
    pip install selenium webdriver-manager
fi

# Function to run a single test
run_test() {
    local script=$1

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Running: $(basename $script)${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # Set environment variables
    export SELENIUM_HEADLESS=$HEADLESS
    export SELENIUM_VERBOSE=$VERBOSE

    # Run the test
    if python "$script"; then
        echo ""
        echo -e "${GREEN}✅ Test PASSED: $(basename $script)${NC}"
        return 0
    else
        echo ""
        echo -e "${RED}❌ Test FAILED: $(basename $script)${NC}"
        return 1
    fi
}

# Main execution
if [ "$RUN_ALL" = true ]; then
    echo -e "${BLUE}Running all tests in data/scripts/${NC}"
    echo ""

    # Check if directory exists
    if [ ! -d "data/scripts" ]; then
        echo -e "${RED}❌ data/scripts/ directory not found${NC}"
        exit 1
    fi

    # Find all Python scripts
    scripts=$(find data/scripts -name "*.py" -type f)

    if [ -z "$scripts" ]; then
        echo -e "${YELLOW}⚠️  No test scripts found in data/scripts/${NC}"
        exit 0
    fi

    # Run each script
    total=0
    passed=0
    failed=0

    for script in $scripts; do
        ((total++))
        if run_test "$script"; then
            ((passed++))
        else
            ((failed++))
        fi
        echo ""
    done

    # Summary
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Test Summary${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "Total:  $total"
    echo -e "${GREEN}Passed: $passed${NC}"
    if [ $failed -gt 0 ]; then
        echo -e "${RED}Failed: $failed${NC}"
    else
        echo -e "Failed: $failed"
    fi
    echo ""

    # Exit code based on results
    if [ $failed -eq 0 ]; then
        echo -e "${GREEN}✅ All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}❌ Some tests failed${NC}"
        exit 1
    fi

elif [ -z "$SCRIPT_PATH" ]; then
    echo -e "${RED}❌ Error: No script path provided${NC}"
    echo ""
    show_help
    exit 1

elif [ ! -f "$SCRIPT_PATH" ]; then
    echo -e "${RED}❌ Error: Script not found: $SCRIPT_PATH${NC}"
    exit 1

else
    # Run single test
    run_test "$SCRIPT_PATH"
    exit $?
fi
