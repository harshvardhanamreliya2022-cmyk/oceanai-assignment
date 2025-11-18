"""
Test Case Generation API endpoints.

Provides REST API for automated test case generation using RAG + LLM.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.app.test_generation import TestCaseGenerator
from backend.app.models.schemas import GenerateTestCasesRequest, TestCaseResponse
from backend.app.utils.logger import setup_logging

logger = setup_logging()

# Initialize router
router = APIRouter(prefix="/test-cases", tags=["Test Cases"])

# Initialize test case generator (lazy loading)
_test_generator = None


def get_test_generator() -> TestCaseGenerator:
    """Get or create test case generator instance."""
    global _test_generator
    if _test_generator is None:
        logger.info("Initializing TestCaseGenerator for API")
        _test_generator = TestCaseGenerator()
    return _test_generator


# Request/Response Models
class ValidateTestCaseRequest(BaseModel):
    """Request model for test case validation."""
    test_id: str
    feature: str
    test_scenario: str
    test_steps: List[str]
    expected_result: str
    grounded_in: str
    test_type: str = "positive"


class ValidationResponse(BaseModel):
    """Response model for validation results."""
    valid: bool
    issues: List[str]
    suggestions: List[str]
    completeness_score: float


class GeneratorStatsResponse(BaseModel):
    """Response model for generator statistics."""
    knowledge_base: dict
    llm_provider: dict
    max_test_cases: int
    top_k_retrieval: int


# Endpoints

@router.post("/generate", response_model=List[TestCaseResponse])
async def generate_test_cases(request: GenerateTestCasesRequest):
    """
    Generate test cases from natural language query.

    Uses RAG to retrieve relevant documentation and LLM to generate
    grounded test cases with source citations.

    Workflow:
    1. Semantic search in knowledge base for relevant docs
    2. Build context-aware prompt with retrieved documentation
    3. Generate test cases using LLM
    4. Parse and validate JSON output
    5. Return structured test cases

    Returns test cases with source grounding to prevent hallucination.
    """
    try:
        generator = get_test_generator()

        logger.info(f"Generating test cases for query: {request.query[:50]}...")

        # Generate test cases
        test_cases = generator.generate_test_cases(
            query=request.query,
            include_negative=request.include_negative,
            max_test_cases=request.max_test_cases,
            top_k_retrieval=request.top_k_retrieval
        )

        if not test_cases:
            return JSONResponse(
                status_code=200,
                content={
                    "message": "No test cases generated. Try rephrasing your query or adding more documentation.",
                    "test_cases": []
                }
            )

        # Convert to response models
        response_data = [
            TestCaseResponse(
                test_id=tc.test_id,
                feature=tc.feature,
                test_scenario=tc.test_scenario,
                test_steps=tc.test_steps,
                expected_result=tc.expected_result,
                grounded_in=tc.grounded_in,
                test_type=tc.test_type.value
            )
            for tc in test_cases
        ]

        logger.info(f"Successfully generated {len(response_data)} test cases")

        return response_data

    except Exception as e:
        logger.error(f"Test case generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Test case generation failed: {str(e)}"
        )


@router.post("/validate", response_model=ValidationResponse)
async def validate_test_case(request: ValidateTestCaseRequest):
    """
    Validate a test case against source documentation.

    Checks:
    - Accuracy against documentation
    - Completeness of test steps
    - Clarity of expected results
    - Source citation correctness

    Returns validation results with issues and suggestions.
    """
    try:
        from backend.app.models.test_case import TestCase, TestType

        generator = get_test_generator()

        # Convert request to TestCase object
        test_type_map = {
            "positive": TestType.POSITIVE,
            "negative": TestType.NEGATIVE,
            "edge_case": TestType.EDGE_CASE
        }

        test_case = TestCase(
            test_id=request.test_id,
            feature=request.feature,
            test_scenario=request.test_scenario,
            test_steps=request.test_steps,
            expected_result=request.expected_result,
            grounded_in=request.grounded_in,
            test_type=test_type_map.get(request.test_type.lower(), TestType.POSITIVE)
        )

        # Validate
        validation = generator.validate_test_case(test_case)

        return ValidationResponse(
            valid=validation.get("valid", False),
            issues=validation.get("issues", []),
            suggestions=validation.get("suggestions", []),
            completeness_score=validation.get("completeness_score", 0.0)
        )

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )


@router.get("/stats", response_model=GeneratorStatsResponse)
async def get_generator_stats():
    """
    Get test case generator statistics.

    Returns information about:
    - Knowledge base status (document count, chunks)
    - LLM provider configuration
    - Generator settings
    """
    try:
        generator = get_test_generator()
        stats = generator.get_generator_stats()

        return GeneratorStatsResponse(
            knowledge_base=stats.get("knowledge_base", {}),
            llm_provider=stats.get("llm_provider", {}),
            max_test_cases=stats.get("max_test_cases", 10),
            top_k_retrieval=stats.get("top_k_retrieval", 5)
        )

    except Exception as e:
        logger.error(f"Failed to get generator stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for test case generation service.

    Verifies that all dependencies (RAG, LLM) are initialized.
    """
    try:
        generator = get_test_generator()
        stats = generator.get_generator_stats()

        return JSONResponse(
            content={
                "status": "healthy",
                "service": "Test Case Generation",
                "knowledge_base_docs": stats["knowledge_base"].get("unique_sources", 0),
                "llm_provider": stats["llm_provider"].get("provider", "unknown")
            }
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "Test Case Generation",
                "error": str(e)
            }
        )
