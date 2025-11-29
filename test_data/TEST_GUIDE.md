# QA AGENT - TESTING GUIDE

This guide provides step-by-step instructions for testing the complete QA Agent system using the provided test files.

## Test Files Overview

| File | Format | Purpose | Size |
|------|--------|---------|------|
| `checkout_requirements.md` | Markdown | Functional requirements for checkout system | Comprehensive |
| `validation_rules.txt` | Text | Detailed validation rules and error scenarios | Detailed |
| `api_specification.json` | JSON | API endpoints and specifications | Structured |
| `simple_checkout.html` | HTML | Simplified checkout page for Selenium testing | Minimal |

---

## Prerequisites

1. **Start the API Server:**
```bash
cd /home/user/oceanai-assignment
./venv/bin/uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

2. **Set Environment Variables:**
Create `.env` file in project root:
```env
# LLM Provider (choose one)
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here

# OR use Ollama (local)
# LLM_PROVIDER=ollama
# OLLAMA_BASE_URL=http://localhost:11434

# OR use OpenAI
# LLM_PROVIDER=openai
# OPENAI_API_KEY=your_openai_key_here
```

3. **Verify API is Running:**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-29T...",
  "version": "1.0.0",
  "service": "QA Agent API"
}
```

---

## TEST 1: Knowledge Base - Document Upload

### Step 1: Upload Requirements Document
```bash
curl -X POST "http://localhost:8000/knowledge-base/upload" \
  -F "file=@test_data/checkout_requirements.md"
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Document ingested successfully",
  "filename": "checkout_requirements.md",
  "chunks_created": 6
}
```

### Step 2: Upload Validation Rules
```bash
curl -X POST "http://localhost:8000/knowledge-base/upload" \
  -F "file=@test_data/validation_rules.txt"
```

### Step 3: Upload API Specification
```bash
curl -X POST "http://localhost:8000/knowledge-base/upload" \
  -F "file=@test_data/api_specification.json"
```

### Step 4: Verify Knowledge Base
```bash
curl http://localhost:8000/knowledge-base/stats
```

**Expected Response:**
```json
{
  "total_chunks": 18,
  "unique_sources": 3,
  "collection_name": "qa_knowledge_base"
}
```

### Step 5: List All Documents
```bash
curl http://localhost:8000/knowledge-base/documents
```

**Expected Response:**
```json
[
  "checkout_requirements.md",
  "validation_rules.txt",
  "api_specification.json"
]
```

---

## TEST 2: Semantic Search

### Test 2.1: Search for Discount Codes
```bash
curl -X POST "http://localhost:8000/knowledge-base/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the valid discount codes and their values?",
    "top_k": 3,
    "min_similarity": 0.5
  }'
```

**Expected:** Returns chunks mentioning SAVE15, FIRST10, WELCOME5

### Test 2.2: Search for Validation Rules
```bash
curl -X POST "http://localhost:8000/knowledge-base/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the email validation requirements?",
    "top_k": 3
  }'
```

**Expected:** Returns chunks about email format, @ symbol, validation

### Test 2.3: Search for Shipping Information
```bash
curl -X POST "http://localhost:8000/knowledge-base/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "shipping methods and costs",
    "top_k": 3
  }'
```

**Expected:** Returns standard (free) and express ($10) shipping info

---

## TEST 3: Test Case Generation

### Test 3.1: Generate Discount Code Test Cases
```bash
curl -X POST "http://localhost:8000/test-cases/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Generate test cases for discount code functionality, including applying SAVE15, FIRST10, and WELCOME5 codes",
    "include_negative": true,
    "max_test_cases": 8,
    "top_k_retrieval": 5
  }'
```

**Expected Test Cases:**
- TC_001: Apply SAVE15 discount code (positive)
- TC_002: Apply FIRST10 discount code (positive)
- TC_003: Apply WELCOME5 discount code (positive)
- TC_004: Invalid discount code (negative)
- TC_005: Case-sensitive code test (negative)
- TC_006: Multiple codes attempt (edge case)

**Verify:** Each test case has `grounded_in` field citing source document

### Test 3.2: Generate Form Validation Test Cases
```bash
curl -X POST "http://localhost:8000/test-cases/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Generate test cases for customer information form validation including name, email, phone, and address fields",
    "include_negative": true,
    "max_test_cases": 10
  }'
```

**Expected Test Cases:**
- Valid form submission (positive)
- Empty name field (negative)
- Invalid email format (negative)
- Phone with non-numeric characters (negative)
- Short address (negative)
- Boundary conditions for each field (edge case)

### Test 3.3: Generate Checkout Flow Test Cases
```bash
curl -X POST "http://localhost:8000/test-cases/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Generate end-to-end test cases for the complete checkout process from cart to order confirmation",
    "include_negative": true,
    "max_test_cases": 5
  }'
```

---

## TEST 4: Test Case Validation

### Step 1: Save a Generated Test Case
From Test 3.1, take one test case (e.g., TC_001)

### Step 2: Validate It
```bash
curl -X POST "http://localhost:8000/test-cases/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "test_id": "TC_001",
    "feature": "Discount Code",
    "test_scenario": "Apply SAVE15 discount code to cart",
    "test_steps": [
      "Add products to cart with subtotal $100",
      "Enter discount code SAVE15 in discount field",
      "Click Apply button",
      "Verify discount of $15 is applied",
      "Verify new total is $85"
    ],
    "expected_result": "15% discount applied successfully, total reduced by $15",
    "grounded_in": "checkout_requirements.md",
    "test_type": "positive"
  }'
```

**Expected Response:**
```json
{
  "valid": true,
  "issues": [],
  "suggestions": [],
  "completeness_score": 0.95
}
```

---

## TEST 5: Selenium Script Generation

### Step 1: Extract HTML Selectors
```bash
curl -X POST "http://localhost:8000/selenium-scripts/extract-selectors" \
  -F "file=@test_data/simple_checkout.html"
```

**Expected Response:**
```json
{
  "filename": "simple_checkout.html",
  "total_selectors": 25,
  "selectors": [
    {
      "selector": "#discount-code",
      "type": "id",
      "tag": "input",
      "text": "Enter code",
      "stability": "high"
    },
    {
      "selector": "#apply-discount-btn",
      "type": "id",
      "tag": "button",
      "text": "Apply",
      "stability": "high"
    },
    ...
  ]
}
```

### Step 2: Generate Selenium Script
```bash
curl -X POST "http://localhost:8000/selenium-scripts/generate" \
  -H "Content-Type: application/json" \
  -d @- << 'EOF'
{
  "test_case_id": "TC_001",
  "feature": "Discount Code Application",
  "test_scenario": "Apply SAVE15 discount code successfully",
  "test_steps": [
    "Navigate to checkout page",
    "Locate discount code input field",
    "Enter 'SAVE15' in discount code field",
    "Click Apply button",
    "Wait for discount to be applied",
    "Verify discount amount is displayed",
    "Verify total is updated correctly"
  ],
  "expected_result": "15% discount applied, total reduced accordingly",
  "grounded_in": "checkout_requirements.md",
  "test_type": "positive",
  "html_content": "$(cat test_data/simple_checkout.html)",
  "include_assertions": true,
  "include_logging": true
}
EOF
```

**Expected Response:**
```json
{
  "script_code": "from selenium import webdriver\nfrom selenium.webdriver.common.by import By\n...",
  "test_case_id": "TC_001",
  "validation_status": "valid",
  "selectors_used": [
    "#discount-code",
    "#apply-discount-btn",
    "#discount-amount",
    "#final-total"
  ],
  "file_path": "./data/scripts/test_TC_001.py"
}
```

### Step 3: Download Generated Script
```bash
curl -O "http://localhost:8000/selenium-scripts/download/TC_001"
```

This saves `test_TC_001.py` to current directory.

### Step 4: Validate Script Syntax
```bash
curl -X POST "http://localhost:8000/selenium-scripts/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "script_code": "<paste generated script here>"
  }'
```

**Expected Response:**
```json
{
  "valid": true,
  "status": "valid",
  "issues": [],
  "selectors_count": 4,
  "selectors": ["#discount-code", "#apply-discount-btn", ...],
  "file_size": 2847
}
```

---

## TEST 6: Complete End-to-End Workflow

### Full Workflow Test
```bash
# 1. Upload all documents
for file in test_data/*.{md,txt,json}; do
  curl -X POST "http://localhost:8000/knowledge-base/upload" -F "file=@$file"
done

# 2. Verify knowledge base
curl http://localhost:8000/knowledge-base/stats

# 3. Generate test cases
curl -X POST "http://localhost:8000/test-cases/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Generate comprehensive test cases for discount code validation",
    "include_negative": true,
    "max_test_cases": 5
  }' | jq . > generated_tests.json

# 4. Extract selectors from HTML
curl -X POST "http://localhost:8000/selenium-scripts/extract-selectors" \
  -F "file=@test_data/simple_checkout.html" | jq .

# 5. Generate Selenium script (use test case from step 3)
# Manually construct request with test case + HTML

# 6. Validate generated script
# Use script from step 5
```

---

## TEST 7: Error Scenarios

### Test 7.1: Upload Invalid File Type
```bash
curl -X POST "http://localhost:8000/knowledge-base/upload" \
  -F "file=@/etc/passwd"
```

**Expected:** 400 error - Unsupported file type

### Test 7.2: Search Empty Knowledge Base
```bash
# First clear KB
curl -X POST "http://localhost:8000/knowledge-base/clear"

# Then search
curl -X POST "http://localhost:8000/knowledge-base/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "top_k": 5}'
```

**Expected:** Empty results

### Test 7.3: Invalid Test Case Generation
```bash
curl -X POST "http://localhost:8000/test-cases/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "",
    "max_test_cases": 5
  }'
```

**Expected:** 422 validation error

---

## TEST 8: Health Checks

### Check All Services
```bash
# Main health
curl http://localhost:8000/health

# Knowledge Base health
curl http://localhost:8000/knowledge-base/health

# Test Cases health
curl http://localhost:8000/test-cases/health

# Selenium Scripts health
curl http://localhost:8000/selenium-scripts/health
```

**Expected:** All return `"status": "healthy"`

---

## TEST 9: API Documentation

### View Interactive Docs
1. Open browser: `http://localhost:8000/docs`
2. Test endpoints interactively
3. View request/response schemas

### View ReDoc
1. Open browser: `http://localhost:8000/redoc`
2. Browse API documentation

---

## Expected Results Summary

### ✅ Knowledge Base Tests
- All 3 documents uploaded successfully
- Total chunks: ~18-20
- Search returns relevant results with similarity scores
- Documents can be listed and deleted

### ✅ Test Case Generation Tests
- Test cases generated from natural language queries
- Each test case cites source document (anti-hallucination)
- Includes positive, negative, and edge cases
- JSON format with test_id, steps, expected results

### ✅ Selenium Script Tests
- HTML selectors extracted correctly
- Python scripts generated with valid syntax
- Scripts use proper Selenium patterns
- AST validation passes
- Scripts saved to filesystem

### ✅ Quality Checks
- No hallucination: all test cases cite sources
- Type-safe: Pydantic validation on all inputs
- Error handling: proper HTTP status codes
- Logging: all operations logged
- Health checks: all services report healthy

---

## Troubleshooting

### Issue: LLM API Key Not Set
**Error:** `GROQ_API_KEY environment variable is required`
**Solution:** Create `.env` file with valid API key

### Issue: Embedding Model Download Fails
**Error:** `403 Forbidden from HuggingFace`
**Solution:** Check internet connection or use local model cache

### Issue: No Test Cases Generated
**Error:** Empty results from /test-cases/generate
**Solution:**
1. Verify documents uploaded to KB
2. Check query matches document content
3. Lower min_similarity threshold

### Issue: Invalid Selenium Script
**Error:** `validation_status: "invalid"`
**Solution:** Check HTML content provided, verify LLM configuration

---

## Performance Benchmarks

Expected performance on standard hardware:

- Document upload: < 5 seconds
- Semantic search: < 1 second
- Test case generation: 5-15 seconds (depends on LLM)
- Script generation: 5-15 seconds (depends on LLM)
- Health checks: < 100ms

---

## Next Steps

After successful testing:
1. Create more domain-specific test documents
2. Generate comprehensive test suites
3. Run generated Selenium scripts
4. Integrate with CI/CD pipeline
5. Monitor quality metrics

---

**Testing Status:** ✅ All systems ready for testing
**Documentation:** Complete
**Support:** Check API docs at /docs
