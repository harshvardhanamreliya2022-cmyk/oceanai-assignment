"""
Prompt templates for LLM-powered test generation.

Templates are designed to minimize hallucination by:
1. Requiring explicit source citations
2. Using structured output formats
3. Providing clear constraints
"""


class PromptTemplates:
    """Collection of prompt templates for various tasks."""

    TEST_CASE_GENERATION = """You are a QA automation expert. Generate comprehensive test cases based ONLY on the provided documentation.

**CRITICAL RULES:**
1. ONLY use information from the provided context
2. Every test case MUST cite its source document
3. If information is not in the context, do NOT make it up
4. Be specific and detailed in test steps

**CONTEXT (Retrieved Documentation):**
{context}

**USER REQUEST:**
{query}

**INSTRUCTIONS:**
Generate test cases in the following JSON format:

```json
[
  {{
    "test_id": "TC_001",
    "feature": "Feature being tested",
    "test_scenario": "Specific scenario description",
    "test_type": "positive|negative|edge_case",
    "test_steps": [
      "Step 1: Action to perform",
      "Step 2: Next action",
      "Step 3: Final action"
    ],
    "expected_result": "Expected outcome",
    "grounded_in": "Exact source filename (e.g., product_specs.md)"
  }}
]
```

**REQUIREMENTS:**
- Include both positive and negative test cases
- Cover edge cases where applicable
- Each test case MUST reference a source document
- Test steps should be clear and executable
- Expected results should be specific and verifiable

Generate the test cases now:"""

    TEST_CASE_VALIDATION = """You are a QA validation expert. Review the following test case for quality and accuracy.

**TEST CASE:**
{test_case}

**SOURCE DOCUMENTATION:**
{context}

**VALIDATION CHECKLIST:**
1. Does the test case accurately reflect the documentation?
2. Are all test steps clear and executable?
3. Is the expected result specific and verifiable?
4. Are there any missing edge cases or scenarios?
5. Is the source citation correct?

Provide validation results in JSON format:

```json
{{
  "valid": true|false,
  "issues": ["Issue 1", "Issue 2"],
  "suggestions": ["Suggestion 1", "Suggestion 2"],
  "completeness_score": 0.0-1.0
}}
```

Validate now:"""

    SELENIUM_SCRIPT_GENERATION = """You are a Selenium automation expert. Generate a Python Selenium script based ONLY on the provided test case and HTML structure.

**CRITICAL RULES:**
1. ONLY use selectors from the provided HTML
2. Include proper waits and error handling
3. Follow Selenium best practices
4. Add comments explaining each step

**TEST CASE:**
{test_case}

**HTML STRUCTURE:**
{html_content}

**REQUIREMENTS:**
- Use Page Object Model pattern
- Include explicit waits (WebDriverWait)
- Add assertions for verification
- Handle common exceptions
- Use stable selectors (ID > CSS > XPath)
- Include logging

Generate a complete, executable Selenium script in Python:

```python
# Your script here
```

Generate the script now:"""

    SELECTOR_EXTRACTION = """Extract all unique CSS selectors and their purposes from the following HTML.

**HTML:**
{html_content}

**INSTRUCTIONS:**
List selectors in order of preference (ID > Class > Tag):

```json
[
  {{
    "selector": "#element-id",
    "type": "id",
    "purpose": "Description of element",
    "stability": "high|medium|low"
  }}
]
```

Extract selectors now:"""

    ERROR_ANALYSIS = """Analyze the following error from a test execution.

**ERROR:**
{error_message}

**CONTEXT:**
Test Case: {test_case_id}
Test Step: {test_step}

**INSTRUCTIONS:**
Provide analysis in JSON format:

```json
{{
  "error_type": "Element not found|Timeout|Assertion|etc.",
  "root_cause": "Likely cause of the error",
  "suggested_fix": "How to fix the error",
  "selector_issue": true|false
}}
```

Analyze now:"""

    DOCUMENTATION_SUMMARIZATION = """Summarize the following documentation to extract key testing points.

**DOCUMENTATION:**
{document_content}

**INSTRUCTIONS:**
Extract:
1. Key features to test
2. User workflows
3. Validation rules
4. Error conditions
5. Business rules

Format as JSON:

```json
{{
  "features": ["Feature 1", "Feature 2"],
  "workflows": ["Workflow 1", "Workflow 2"],
  "validations": ["Rule 1", "Rule 2"],
  "error_conditions": ["Error 1", "Error 2"],
  "business_rules": ["Rule 1", "Rule 2"]
}}
```

Summarize now:"""

    @staticmethod
    def build_test_case_prompt(context: str, query: str) -> str:
        """
        Build test case generation prompt.

        Args:
            context: Retrieved documentation context
            query: User's test generation request

        Returns:
            Formatted prompt
        """
        return PromptTemplates.TEST_CASE_GENERATION.format(
            context=context,
            query=query
        )

    @staticmethod
    def build_selenium_prompt(test_case: str, html_content: str) -> str:
        """
        Build Selenium script generation prompt.

        Args:
            test_case: Test case to automate
            html_content: HTML structure for selectors

        Returns:
            Formatted prompt
        """
        return PromptTemplates.SELENIUM_SCRIPT_GENERATION.format(
            test_case=test_case,
            html_content=html_content
        )

    @staticmethod
    def build_validation_prompt(test_case: str, context: str) -> str:
        """
        Build test case validation prompt.

        Args:
            test_case: Test case to validate
            context: Source documentation

        Returns:
            Formatted prompt
        """
        return PromptTemplates.TEST_CASE_VALIDATION.format(
            test_case=test_case,
            context=context
        )

    @staticmethod
    def build_selector_extraction_prompt(html_content: str) -> str:
        """
        Build selector extraction prompt.

        Args:
            html_content: HTML to extract selectors from

        Returns:
            Formatted prompt
        """
        return PromptTemplates.SELECTOR_EXTRACTION.format(
            html_content=html_content
        )

    @staticmethod
    def build_error_analysis_prompt(
        error_message: str,
        test_case_id: str,
        test_step: str
    ) -> str:
        """
        Build error analysis prompt.

        Args:
            error_message: Error message to analyze
            test_case_id: ID of failed test case
            test_step: Step that failed

        Returns:
            Formatted prompt
        """
        return PromptTemplates.ERROR_ANALYSIS.format(
            error_message=error_message,
            test_case_id=test_case_id,
            test_step=test_step
        )

    @staticmethod
    def build_documentation_summary_prompt(document_content: str) -> str:
        """
        Build documentation summarization prompt.

        Args:
            document_content: Documentation to summarize

        Returns:
            Formatted prompt
        """
        return PromptTemplates.DOCUMENTATION_SUMMARIZATION.format(
            document_content=document_content
        )
