"""
Test case generator using RAG + LLM.

Retrieves relevant documentation and generates grounded test cases.
"""

import json
import re
from typing import List, Dict, Optional

from backend.app.knowledge_base import RAGService
from backend.app.llm import LLMService, PromptTemplates
from backend.app.models.test_case import TestCase, TestType
from backend.app.config import settings
from backend.app.utils.logger import setup_logging

logger = setup_logging()


class TestCaseGenerator:
    """
    Generate test cases using RAG-enhanced LLM.

    Combines:
    1. Semantic search for relevant documentation
    2. LLM-based test case generation
    3. Source grounding to prevent hallucination
    """

    def __init__(self):
        """Initialize generator with RAG and LLM services."""
        logger.info("Initializing TestCaseGenerator...")

        try:
            self.rag_service = RAGService()
            self.llm_service = LLMService()

            logger.info("TestCaseGenerator initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize TestCaseGenerator: {e}")
            raise

    def generate_test_cases(
        self,
        query: str,
        include_negative: bool = True,
        max_test_cases: int = 10,
        top_k_retrieval: int = 5
    ) -> List[TestCase]:
        """
        Generate test cases based on query.

        Workflow:
        1. Retrieve relevant documentation using RAG
        2. Generate test cases using LLM with retrieved context
        3. Parse and validate generated test cases
        4. Return structured TestCase objects

        Args:
            query: Natural language query describing what to test
            include_negative: Whether to include negative test cases
            max_test_cases: Maximum number of test cases to generate
            top_k_retrieval: Number of document chunks to retrieve

        Returns:
            List of TestCase objects with source grounding
        """
        logger.info(f"Generating test cases for query: '{query[:50]}...'")

        try:
            # Step 1: Retrieve relevant documentation
            logger.info(f"Retrieving top {top_k_retrieval} relevant documents...")
            context_chunks = self.rag_service.search(
                query=query,
                top_k=top_k_retrieval,
                min_similarity=settings.min_similarity_score
            )

            if not context_chunks:
                logger.warning("No relevant documentation found")
                return []

            logger.info(f"Retrieved {len(context_chunks)} relevant chunks")

            # Step 2: Build prompt with context
            enhanced_query = self._build_generation_query(
                query,
                include_negative,
                max_test_cases
            )

            prompt = PromptTemplates.build_test_case_prompt(
                context=self._format_context(context_chunks),
                query=enhanced_query
            )

            # Step 3: Generate test cases using LLM
            logger.info("Generating test cases with LLM...")
            llm_response = self.llm_service.generate(prompt)

            # Step 4: Parse and validate
            test_cases = self._parse_test_cases(llm_response)

            logger.info(f"Generated {len(test_cases)} test cases")

            return test_cases

        except Exception as e:
            logger.error(f"Test case generation failed: {e}")
            raise

    def _build_generation_query(
        self,
        base_query: str,
        include_negative: bool,
        max_count: int
    ) -> str:
        """
        Enhance query with generation requirements.

        Args:
            base_query: Original user query
            include_negative: Include negative test cases
            max_count: Maximum test cases

        Returns:
            Enhanced query with requirements
        """
        requirements = [
            f"Generate up to {max_count} test cases",
            "Include positive test cases for happy path scenarios"
        ]

        if include_negative:
            requirements.extend([
                "Include negative test cases for error conditions",
                "Include edge cases for boundary conditions"
            ])

        requirements.append(
            "CRITICAL: Every test case MUST cite its source document"
        )

        enhanced = f"{base_query}\n\nRequirements:\n" + "\n".join(
            f"- {req}" for req in requirements
        )

        return enhanced

    def _format_context(self, chunks: List[Dict]) -> str:
        """
        Format retrieved chunks for LLM context.

        Args:
            chunks: Retrieved context chunks

        Returns:
            Formatted context string
        """
        if not chunks:
            return "No relevant context available."

        formatted_parts = []

        for idx, chunk in enumerate(chunks, 1):
            source = chunk.get("source_filename", "Unknown")
            text = chunk.get("text", "")
            score = chunk.get("similarity_score", 0.0)

            formatted_parts.append(
                f"=== Document {idx}: {source} (Relevance: {score:.2f}) ===\n"
                f"{text}\n"
            )

        return "\n\n".join(formatted_parts)

    def _parse_test_cases(self, llm_response: str) -> List[TestCase]:
        """
        Parse LLM response into TestCase objects.

        Extracts JSON from markdown code blocks and validates structure.

        Args:
            llm_response: Raw LLM output

        Returns:
            List of parsed TestCase objects
        """
        try:
            # Extract JSON from markdown code blocks
            json_match = re.search(
                r'```json\s*(.*?)\s*```',
                llm_response,
                re.DOTALL
            )

            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find raw JSON array
                json_match = re.search(
                    r'\[\s*\{.*?\}\s*\]',
                    llm_response,
                    re.DOTALL
                )
                if json_match:
                    json_str = json_match.group(0)
                else:
                    logger.error("No JSON found in LLM response")
                    return []

            # Parse JSON
            test_cases_data = json.loads(json_str)

            if not isinstance(test_cases_data, list):
                logger.error("Expected JSON array of test cases")
                return []

            # Convert to TestCase objects
            test_cases = []

            for data in test_cases_data:
                try:
                    test_case = self._dict_to_test_case(data)
                    test_cases.append(test_case)
                except Exception as e:
                    logger.warning(f"Failed to parse test case: {e}")
                    continue

            return test_cases

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.debug(f"LLM response: {llm_response[:500]}...")
            return []
        except Exception as e:
            logger.error(f"Test case parsing failed: {e}")
            return []

    def _dict_to_test_case(self, data: Dict) -> TestCase:
        """
        Convert dictionary to TestCase object.

        Args:
            data: Test case dictionary from LLM

        Returns:
            TestCase object

        Raises:
            ValueError: If required fields are missing
        """
        required_fields = [
            "test_id", "feature", "test_scenario",
            "test_steps", "expected_result", "grounded_in"
        ]

        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Parse test type
        test_type_str = data.get("test_type", "positive").lower()
        test_type_map = {
            "positive": TestType.POSITIVE,
            "negative": TestType.NEGATIVE,
            "edge_case": TestType.EDGE_CASE
        }
        test_type = test_type_map.get(test_type_str, TestType.POSITIVE)

        return TestCase(
            test_id=data["test_id"],
            feature=data["feature"],
            test_scenario=data["test_scenario"],
            test_steps=data["test_steps"],
            expected_result=data["expected_result"],
            grounded_in=data["grounded_in"],
            test_type=test_type
        )

    def validate_test_case(
        self,
        test_case: TestCase,
        source_filter: Optional[str] = None
    ) -> Dict:
        """
        Validate a test case against source documentation.

        Args:
            test_case: Test case to validate
            source_filter: Optional source document filter

        Returns:
            Validation results dictionary
        """
        try:
            # Retrieve source documentation
            context_chunks = self.rag_service.search(
                query=test_case.test_scenario,
                top_k=3,
                source_filter=source_filter or test_case.grounded_in
            )

            if not context_chunks:
                return {
                    "valid": False,
                    "issues": ["Source document not found"],
                    "suggestions": ["Verify source document exists"],
                    "completeness_score": 0.0
                }

            # Build validation prompt
            test_case_str = json.dumps({
                "test_id": test_case.test_id,
                "feature": test_case.feature,
                "test_scenario": test_case.test_scenario,
                "test_steps": test_case.test_steps,
                "expected_result": test_case.expected_result,
                "grounded_in": test_case.grounded_in
            }, indent=2)

            prompt = PromptTemplates.build_validation_prompt(
                test_case=test_case_str,
                context=self._format_context(context_chunks)
            )

            # Get validation from LLM
            llm_response = self.llm_service.generate(prompt)

            # Parse validation results
            validation = self._parse_validation(llm_response)

            return validation

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return {
                "valid": False,
                "issues": [f"Validation error: {str(e)}"],
                "suggestions": [],
                "completeness_score": 0.0
            }

    def _parse_validation(self, llm_response: str) -> Dict:
        """
        Parse validation response from LLM.

        Args:
            llm_response: Raw LLM output

        Returns:
            Validation dictionary
        """
        try:
            # Extract JSON from response
            json_match = re.search(
                r'```json\s*(.*?)\s*```',
                llm_response,
                re.DOTALL
            )

            if json_match:
                json_str = json_match.group(1)
            else:
                json_match = re.search(
                    r'\{.*?\}',
                    llm_response,
                    re.DOTALL
                )
                if json_match:
                    json_str = json_match.group(0)
                else:
                    return {
                        "valid": False,
                        "issues": ["Could not parse validation response"],
                        "suggestions": [],
                        "completeness_score": 0.0
                    }

            validation = json.loads(json_str)
            return validation

        except Exception as e:
            logger.error(f"Validation parsing failed: {e}")
            return {
                "valid": False,
                "issues": [f"Parsing error: {str(e)}"],
                "suggestions": [],
                "completeness_score": 0.0
            }

    def get_generator_stats(self) -> Dict:
        """
        Get statistics about the generator.

        Returns:
            Dictionary with generator info
        """
        kb_stats = self.rag_service.get_knowledge_base_stats()
        llm_info = self.llm_service.get_provider_info()

        return {
            "knowledge_base": kb_stats,
            "llm_provider": llm_info,
            "max_test_cases": settings.max_test_cases_per_request,
            "top_k_retrieval": settings.top_k_retrieval
        }
