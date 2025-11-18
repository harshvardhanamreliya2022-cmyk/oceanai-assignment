"""
Selenium script generator using LLM + HTML parsing.

Generates executable Python Selenium scripts from test cases.
"""

import ast
import re
import json
from typing import List, Dict, Optional
from pathlib import Path

from bs4 import BeautifulSoup

from backend.app.llm import LLMService, PromptTemplates
from backend.app.models.test_case import TestCase
from backend.app.models.selenium_script import SeleniumScript, ScriptStatus
from backend.app.config import settings
from backend.app.utils.logger import setup_logging
from backend.app.utils.filesystem import sanitize_filename

logger = setup_logging()


class SeleniumScriptGenerator:
    """
    Generate Selenium WebDriver scripts from test cases.

    Combines:
    1. HTML parsing for selector extraction
    2. LLM-based script generation
    3. Python syntax validation
    """

    def __init__(self):
        """Initialize generator with LLM service."""
        logger.info("Initializing SeleniumScriptGenerator...")

        try:
            self.llm_service = LLMService()
            logger.info("SeleniumScriptGenerator initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize SeleniumScriptGenerator: {e}")
            raise

    def generate_script(
        self,
        test_case: TestCase,
        html_content: str,
        include_assertions: bool = True,
        include_logging: bool = True
    ) -> SeleniumScript:
        """
        Generate Selenium script from test case and HTML.

        Workflow:
        1. Extract selectors from HTML
        2. Build prompt with test case and HTML
        3. Generate script using LLM
        4. Parse and validate Python syntax
        5. Return SeleniumScript object

        Args:
            test_case: Test case to automate
            html_content: HTML structure for selectors
            include_assertions: Include assertion statements
            include_logging: Include logging statements

        Returns:
            SeleniumScript object with code and validation status
        """
        logger.info(f"Generating Selenium script for test case: {test_case.test_id}")

        try:
            # Step 1: Extract selectors from HTML
            selectors = self._extract_selectors(html_content)
            logger.info(f"Extracted {len(selectors)} selectors from HTML")

            # Step 2: Build enhanced HTML content with selector info
            enhanced_html = self._enhance_html_with_selectors(html_content, selectors)

            # Step 3: Build test case string
            test_case_str = self._format_test_case(test_case)

            # Step 4: Generate script using LLM
            prompt = PromptTemplates.build_selenium_prompt(
                test_case=test_case_str,
                html_content=enhanced_html
            )

            logger.info("Generating script with LLM...")
            llm_response = self.llm_service.generate(
                prompt=prompt,
                temperature=0.1  # Low temperature for consistent code generation
            )

            # Step 5: Parse script from response
            script_code = self._extract_python_code(llm_response)

            if not script_code:
                logger.error("Failed to extract Python code from LLM response")
                return SeleniumScript(
                    code="# Error: Failed to generate script",
                    test_case_id=test_case.test_id,
                    selectors_used=[],
                    validation_status=ScriptStatus.INVALID
                )

            # Step 6: Validate syntax
            validation_status, issues = self._validate_python_syntax(script_code)

            # Step 7: Extract selectors used in script
            selectors_used = self._extract_selectors_from_script(script_code)

            logger.info(f"Script generated: {len(script_code)} chars, status={validation_status.value}")

            return SeleniumScript(
                code=script_code,
                test_case_id=test_case.test_id,
                selectors_used=selectors_used,
                validation_status=validation_status
            )

        except Exception as e:
            logger.error(f"Script generation failed: {e}")
            return SeleniumScript(
                code=f"# Error during generation: {str(e)}",
                test_case_id=test_case.test_id,
                selectors_used=[],
                validation_status=ScriptStatus.INVALID
            )

    def _extract_selectors(self, html_content: str) -> List[Dict]:
        """
        Extract HTML selectors with metadata.

        Args:
            html_content: HTML string to parse

        Returns:
            List of selector dictionaries
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            selectors = []

            # Find all elements with IDs (highest priority)
            for element in soup.find_all(id=True):
                selectors.append({
                    "selector": f"#{element.get('id')}",
                    "type": "id",
                    "tag": element.name,
                    "text": element.get_text(strip=True)[:50],
                    "stability": "high"
                })

            # Find form elements (inputs, buttons, etc.)
            for element in soup.find_all(['input', 'button', 'select', 'textarea']):
                # By name
                if element.get('name'):
                    selectors.append({
                        "selector": f"{element.name}[name='{element.get('name')}']",
                        "type": "name",
                        "tag": element.name,
                        "text": element.get('placeholder', '') or element.get('value', ''),
                        "stability": "high"
                    })

                # By type
                if element.get('type'):
                    selectors.append({
                        "selector": f"{element.name}[type='{element.get('type')}']",
                        "type": "attribute",
                        "tag": element.name,
                        "text": element.get('placeholder', '') or element.get('value', ''),
                        "stability": "medium"
                    })

            # Find elements with specific classes
            for element in soup.find_all(class_=True):
                classes = element.get('class', [])
                if classes:
                    selectors.append({
                        "selector": f".{classes[0]}",
                        "type": "class",
                        "tag": element.name,
                        "text": element.get_text(strip=True)[:50],
                        "stability": "medium"
                    })

            # Remove duplicates
            unique_selectors = []
            seen = set()
            for sel in selectors:
                key = sel["selector"]
                if key not in seen:
                    seen.add(key)
                    unique_selectors.append(sel)

            return unique_selectors[:30]  # Limit to top 30 selectors

        except Exception as e:
            logger.error(f"Selector extraction failed: {e}")
            return []

    def _enhance_html_with_selectors(
        self,
        html_content: str,
        selectors: List[Dict]
    ) -> str:
        """
        Create a simplified HTML representation with selector metadata.

        Args:
            html_content: Original HTML
            selectors: Extracted selectors

        Returns:
            Enhanced HTML description
        """
        selector_desc = "\n\nAVAILABLE SELECTORS:\n"
        for sel in selectors:
            selector_desc += f"- {sel['selector']} ({sel['type']}, {sel['tag']}): {sel['text']}\n"

        # Also include a snippet of the original HTML (first 2000 chars)
        html_snippet = html_content[:2000] if len(html_content) > 2000 else html_content

        return f"{html_snippet}\n{selector_desc}"

    def _format_test_case(self, test_case: TestCase) -> str:
        """
        Format test case for LLM prompt.

        Args:
            test_case: Test case object

        Returns:
            Formatted string
        """
        return f"""
Test ID: {test_case.test_id}
Feature: {test_case.feature}
Scenario: {test_case.test_scenario}
Type: {test_case.test_type.value}

Test Steps:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(test_case.test_steps))}

Expected Result:
{test_case.expected_result}

Source: {test_case.grounded_in}
"""

    def _extract_python_code(self, llm_response: str) -> Optional[str]:
        """
        Extract Python code from LLM response.

        Handles markdown code blocks and raw Python.

        Args:
            llm_response: Raw LLM output

        Returns:
            Extracted Python code or None
        """
        # Try to find Python code block
        python_match = re.search(
            r'```python\s*(.*?)\s*```',
            llm_response,
            re.DOTALL
        )

        if python_match:
            return python_match.group(1).strip()

        # Try generic code block
        code_match = re.search(
            r'```\s*(.*?)\s*```',
            llm_response,
            re.DOTALL
        )

        if code_match:
            code = code_match.group(1).strip()
            # Check if it looks like Python
            if any(keyword in code for keyword in ['import', 'def ', 'class ', 'from ']):
                return code

        # If no code blocks, try to extract if response looks like Python
        if llm_response.strip().startswith(('import', 'from', 'def', 'class')):
            return llm_response.strip()

        logger.warning("Could not extract Python code from LLM response")
        return None

    def _validate_python_syntax(self, code: str) -> tuple[ScriptStatus, List[str]]:
        """
        Validate Python syntax using AST parser.

        Args:
            code: Python code to validate

        Returns:
            Tuple of (status, list of issues)
        """
        issues = []

        # Check for basic Selenium patterns
        if 'webdriver' not in code:
            issues.append("Missing webdriver import")

        if 'driver' not in code:
            issues.append("No driver variable found")

        # Try to parse with AST
        try:
            ast.parse(code)
            logger.debug("Python syntax is valid")

            if issues:
                return ScriptStatus.VALID_WITH_WARNINGS, issues
            else:
                return ScriptStatus.VALID, []

        except SyntaxError as e:
            logger.error(f"Syntax error in generated code: {e}")
            issues.append(f"Syntax error at line {e.lineno}: {e.msg}")
            return ScriptStatus.INVALID, issues

        except Exception as e:
            logger.error(f"Validation error: {e}")
            issues.append(f"Validation error: {str(e)}")
            return ScriptStatus.INVALID, issues

    def _extract_selectors_from_script(self, code: str) -> List[str]:
        """
        Extract selectors used in the generated script.

        Args:
            code: Python script code

        Returns:
            List of selector strings
        """
        selectors = []

        # Find by ID
        id_matches = re.findall(r'find_element.*By\.ID.*?["\']([^"\']+)["\']', code)
        selectors.extend([f"#{id_}" for id_ in id_matches])

        # Find by NAME
        name_matches = re.findall(r'find_element.*By\.NAME.*?["\']([^"\']+)["\']', code)
        selectors.extend([f"[name='{name}']" for name in name_matches])

        # Find by CLASS_NAME
        class_matches = re.findall(r'find_element.*By\.CLASS_NAME.*?["\']([^"\']+)["\']', code)
        selectors.extend([f".{cls}" for cls in class_matches])

        # Find by CSS_SELECTOR
        css_matches = re.findall(r'find_element.*By\.CSS_SELECTOR.*?["\']([^"\']+)["\']', code)
        selectors.extend(css_matches)

        # Find by XPATH
        xpath_matches = re.findall(r'find_element.*By\.XPATH.*?["\']([^"\']+)["\']', code)
        selectors.extend(xpath_matches)

        return list(set(selectors))  # Remove duplicates

    def save_script(self, script: SeleniumScript, filename: Optional[str] = None) -> str:
        """
        Save generated script to file.

        Args:
            script: SeleniumScript object
            filename: Optional filename (auto-generated if not provided)

        Returns:
            Path to saved file
        """
        if not filename:
            filename = f"test_{script.test_case_id}.py"

        filename = sanitize_filename(filename)
        filepath = Path(settings.scripts_dir) / filename

        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Write script
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(script.code)

        logger.info(f"Script saved to: {filepath}")

        return str(filepath)

    def validate_script_file(self, filepath: str) -> Dict:
        """
        Validate a saved script file.

        Args:
            filepath: Path to script file

        Returns:
            Validation results dictionary
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()

            status, issues = self._validate_python_syntax(code)
            selectors = self._extract_selectors_from_script(code)

            return {
                "valid": status != ScriptStatus.INVALID,
                "status": status.value,
                "issues": issues,
                "selectors_count": len(selectors),
                "selectors": selectors,
                "file_size": len(code)
            }

        except Exception as e:
            logger.error(f"Script file validation failed: {e}")
            return {
                "valid": False,
                "status": "error",
                "issues": [str(e)],
                "selectors_count": 0,
                "selectors": [],
                "file_size": 0
            }
