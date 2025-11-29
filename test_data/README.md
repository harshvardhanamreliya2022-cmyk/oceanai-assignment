# QA Agent - Test Data Files

This directory contains comprehensive test files for validating the QA Agent system.

## Quick Start

### 1. Run Automated Smoke Test
```bash
cd /home/user/oceanai-assignment
./test_data/quick_test.sh
```

This script automatically tests:
- ✅ API health checks
- ✅ Document upload
- ✅ Semantic search
- ✅ Test case generation
- ✅ Script generation

### 2. Read Comprehensive Guide
```bash
cat test_data/TEST_GUIDE.md
```

Or view in your browser/editor for better formatting.

---

## Test Files Description

### 📄 checkout_requirements.md (2.8 KB)
**Format:** Markdown
**Content:** Comprehensive functional requirements for e-commerce checkout

**Covers:**
- Shopping cart management
- Discount code system (SAVE15, FIRST10, WELCOME5)
- Customer information requirements
- Shipping options (Standard free, Express $10)
- Payment methods
- Order calculation formulas
- Error scenarios

**Use For:**
- RAG knowledge base testing
- Test case generation for checkout flows
- Discount code validation tests
- Form validation tests

---

### 📝 validation_rules.txt (3.8 KB)
**Format:** Plain Text
**Content:** Detailed validation rules and business logic

**Covers:**
- Form field validation (name, email, phone, address)
- Discount code validation rules
- Payment method requirements
- Shipping method validation
- Cart validation logic
- Order calculation examples
- Error handling specifications

**Use For:**
- Generating validation test cases
- Edge case identification
- Negative test scenarios
- Boundary condition tests

---

### 📊 api_specification.json (6.2 KB)
**Format:** JSON
**Content:** REST API specifications for checkout system

**Covers:**
- Cart management endpoints
- Discount code API
- Checkout submission API
- Shipping calculation API
- Request/response schemas
- Error codes and messages
- Rate limiting rules

**Use For:**
- API test case generation
- Integration testing scenarios
- Error handling tests
- Testing JSON document parsing

---

### 🌐 simple_checkout.html (5.6 KB)
**Format:** HTML
**Content:** Simplified checkout page with proper HTML structure

**Contains:**
- Shopping cart section with products
- Discount code input (#discount-code)
- Customer information form
- Shipping method radio buttons
- Payment method dropdown
- Submit button
- Proper IDs and classes for selectors

**Use For:**
- Selenium script generation
- HTML selector extraction testing
- Web automation test creation
- E2E test scenarios

---

## File Format Coverage

| Format | Files | Purpose |
|--------|-------|---------|
| Markdown | 1 | Requirements documentation |
| Text | 1 | Validation rules |
| JSON | 1 | API specifications |
| HTML | 1 | Selenium testing |

**Total:** 4 files, 4 formats (demonstrates multi-format support)

---

## Test Scenarios Covered

### 1. Knowledge Base Testing ✅
- Multi-format document upload
- Text chunking and embedding
- Vector storage and retrieval
- Semantic search
- Source citation tracking

### 2. Test Case Generation ✅
**Positive Tests:**
- Apply valid discount codes
- Submit valid forms
- Select shipping/payment methods
- Complete checkout flow

**Negative Tests:**
- Invalid discount codes
- Empty form fields
- Invalid email/phone formats
- Case-sensitive code tests

**Edge Cases:**
- Boundary value testing
- Multiple code attempts
- Empty cart scenarios
- Maximum/minimum values

### 3. Selenium Script Generation ✅
- Element location by ID
- Form field interaction
- Button click actions
- Assertions and validations
- Wait conditions
- Error handling

---

## Expected Test Results

### Document Upload
```
✓ checkout_requirements.md → 6 chunks
✓ validation_rules.txt → 8 chunks
✓ api_specification.json → 4 chunks
✓ Total: ~18 chunks in knowledge base
```

### Test Case Generation
```
Query: "discount code tests"
Results: 5-8 test cases
- Each with test_id, steps, expected results
- All citing source documents
- Mix of positive/negative/edge cases
```

### Selenium Scripts
```
HTML Parsing: 25+ selectors extracted
Script Generation: Valid Python + Selenium
Validation: AST parsing passes
Selectors Used: IDs prioritized over CSS/XPath
```

---

## Usage Examples

### Example 1: Upload All Documents
```bash
for file in test_data/*.{md,txt,json}; do
  curl -X POST "http://localhost:8000/knowledge-base/upload" \
    -F "file=@$file"
done
```

### Example 2: Generate Discount Code Tests
```bash
curl -X POST "http://localhost:8000/test-cases/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Generate test cases for SAVE15, FIRST10, and WELCOME5 discount codes",
    "include_negative": true,
    "max_test_cases": 8
  }'
```

### Example 3: Extract HTML Selectors
```bash
curl -X POST "http://localhost:8000/selenium-scripts/extract-selectors" \
  -F "file=@test_data/simple_checkout.html"
```

---

## Validation Checklist

After running tests, verify:

- [ ] All 3 documents uploaded successfully
- [ ] Knowledge base shows ~18 total chunks
- [ ] Search returns relevant results
- [ ] Test cases cite source documents (anti-hallucination)
- [ ] Test cases include positive, negative, edge cases
- [ ] Selenium scripts have valid Python syntax
- [ ] Scripts use stable selectors (IDs preferred)
- [ ] All health checks return "healthy"
- [ ] No errors in application logs

---

## Troubleshooting

### Issue: No Test Cases Generated
**Cause:** Knowledge base empty or query doesn't match content
**Solution:**
```bash
# Check KB status
curl http://localhost:8000/knowledge-base/stats

# Upload documents if needed
./test_data/quick_test.sh
```

### Issue: LLM Provider Error
**Cause:** Missing API key
**Solution:**
```bash
# Create .env file
cat > .env << EOF
LLM_PROVIDER=groq
GROQ_API_KEY=your_key_here
EOF
```

### Issue: Script Generation Fails
**Cause:** Invalid HTML or missing selectors
**Solution:** Use `simple_checkout.html` which has proper IDs

---

## Performance Expectations

| Operation | Expected Time |
|-----------|---------------|
| Upload MD file | < 3 seconds |
| Upload TXT file | < 3 seconds |
| Upload JSON file | < 2 seconds |
| Semantic search | < 1 second |
| Generate 5 test cases | 5-15 seconds |
| Generate Selenium script | 5-15 seconds |
| Extract selectors | < 1 second |

*Times vary based on LLM provider and model*

---

## Extending Test Data

To add your own test files:

1. **Create documentation files** in supported formats:
   - `.md` for requirements
   - `.txt` for specifications
   - `.json` for API docs
   - `.html` for web pages
   - `.pdf` for reports

2. **Place in test_data/ directory**

3. **Upload via API:**
```bash
curl -X POST "http://localhost:8000/knowledge-base/upload" \
  -F "file=@test_data/your_file.md"
```

4. **Generate tests:**
```bash
curl -X POST "http://localhost:8000/test-cases/generate" \
  -H "Content-Type: application/json" \
  -d '{"query": "your test scenario"}'
```

---

## Best Practices

1. **Use specific queries:** "Generate test cases for discount code SAVE15" works better than "test discount"

2. **Include context:** "Generate test cases for email validation with requirements from validation_rules.txt"

3. **Set appropriate limits:** Use `max_test_cases` to control output size

4. **Verify source grounding:** Check that each test case has `grounded_in` field

5. **Review generated tests:** Validate test cases make sense before creating scripts

---

## Support

- **Full Guide:** `test_data/TEST_GUIDE.md`
- **Quick Test:** `./test_data/quick_test.sh`
- **API Docs:** `http://localhost:8000/docs`
- **Logs:** `data/logs/app.log`

---

**Test Data Status:** ✅ Ready for testing
**Last Updated:** 2025-11-29
**Files:** 6 (4 test files + 2 guides)
