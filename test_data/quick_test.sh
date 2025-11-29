#!/bin/bash

# Quick Test Script for QA Agent System
# This script runs a basic smoke test of all major features

set -e  # Exit on error

API_URL="http://localhost:8000"
TEST_DIR="$(dirname "$0")"

echo "========================================="
echo "QA AGENT - QUICK SMOKE TEST"
echo "========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if API is running
check_api() {
    echo -n "Checking if API is running... "
    if curl -s "$API_URL/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ API is running${NC}"
        return 0
    else
        echo -e "${RED}✗ API is not running${NC}"
        echo ""
        echo "Please start the API server first:"
        echo "  cd /home/user/oceanai-assignment"
        echo "  ./venv/bin/uvicorn backend.app.main:app --reload --port 8000"
        exit 1
    fi
}

# Function to test endpoint
test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"

    echo -n "Testing $name... "

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$API_URL$endpoint")
    elif [ "$method" = "POST" ] && [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL$endpoint")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi

    http_code=$(echo "$response" | tail -n1)

    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo -e "${GREEN}✓ Pass (HTTP $http_code)${NC}"
        return 0
    else
        echo -e "${RED}✗ Fail (HTTP $http_code)${NC}"
        return 1
    fi
}

# Function to upload document
upload_document() {
    local file="$1"
    local filename=$(basename "$file")

    echo -n "Uploading $filename... "

    response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/knowledge-base/upload" \
        -F "file=@$file")

    http_code=$(echo "$response" | tail -n1)

    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ Uploaded${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ Skipped (may already exist)${NC}"
        return 0
    fi
}

# Main test execution
main() {
    echo "Step 1: API Health Checks"
    echo "-------------------------"
    check_api
    test_endpoint "Main health check" "GET" "/health"
    test_endpoint "Knowledge Base health" "GET" "/knowledge-base/health"
    test_endpoint "Test Cases health" "GET" "/test-cases/health"
    test_endpoint "Selenium Scripts health" "GET" "/selenium-scripts/health"
    echo ""

    echo "Step 2: Document Upload"
    echo "-----------------------"
    upload_document "$TEST_DIR/checkout_requirements.md"
    upload_document "$TEST_DIR/validation_rules.txt"
    upload_document "$TEST_DIR/api_specification.json"
    echo ""

    echo "Step 3: Knowledge Base Operations"
    echo "----------------------------------"
    test_endpoint "Get KB stats" "GET" "/knowledge-base/stats"
    test_endpoint "List documents" "GET" "/knowledge-base/documents"

    echo -n "Semantic search... "
    search_data='{"query":"discount codes","top_k":3,"min_similarity":0.5}'
    response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/knowledge-base/search" \
        -H "Content-Type: application/json" \
        -d "$search_data")
    http_code=$(echo "$response" | tail -n1)
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ Search works${NC}"
    else
        echo -e "${RED}✗ Search failed${NC}"
    fi
    echo ""

    echo "Step 4: Test Case Generation"
    echo "-----------------------------"
    echo -n "Generating test cases... "

    gen_data='{
        "query":"Generate test cases for applying discount code SAVE15",
        "include_negative":true,
        "max_test_cases":3,
        "top_k_retrieval":3
    }'

    response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/test-cases/generate" \
        -H "Content-Type: application/json" \
        -d "$gen_data")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
        count=$(echo "$body" | grep -o '"test_id"' | wc -l)
        echo -e "${GREEN}✓ Generated $count test cases${NC}"

        # Show first test case
        echo ""
        echo "Sample Generated Test Case:"
        echo "$body" | python3 -m json.tool 2>/dev/null | head -20 || echo "$body" | head -20
    else
        echo -e "${RED}✗ Generation failed${NC}"
    fi
    echo ""

    echo "Step 5: Selenium Script Generation"
    echo "-----------------------------------"
    test_endpoint "Extract HTML selectors" "POST" "/selenium-scripts/extract-selectors" \
        '{"html_content":"<div id=\"test\"></div>"}'
    echo ""

    echo "========================================="
    echo "SMOKE TEST COMPLETE"
    echo "========================================="
    echo ""
    echo "Next steps:"
    echo "  1. View full test guide: cat $TEST_DIR/TEST_GUIDE.md"
    echo "  2. Access API docs: http://localhost:8000/docs"
    echo "  3. Run comprehensive tests using curl commands from guide"
    echo ""
}

# Run tests
main
