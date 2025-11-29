"""
Selenium Script Generation API endpoints.

Provides REST API for automated Selenium script generation from test cases.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from pathlib import Path

from ..script_generation import SeleniumScriptGenerator
from ..models.test_case import TestCase, TestType
from ..utils.logger import setup_logging

logger = setup_logging()

# Initialize router
router = APIRouter(prefix="/selenium-scripts", tags=["Selenium Scripts"])

# Initialize generator (lazy loading)
_script_generator = None


def get_script_generator() -> SeleniumScriptGenerator:
    """Get or create Selenium script generator instance."""
    global _script_generator
    if _script_generator is None:
        logger.info("Initializing SeleniumScriptGenerator for API")
        _script_generator = SeleniumScriptGenerator()
    return _script_generator


# Request/Response Models
class GenerateScriptRequest(BaseModel):
    """Request model for script generation."""
    test_case_id: str = Field(..., description="Test case ID")
    feature: str = Field(..., description="Feature being tested")
    test_scenario: str = Field(..., description="Test scenario")
    test_steps: list[str] = Field(..., description="Test steps")
    expected_result: str = Field(..., description="Expected result")
    grounded_in: str = Field(..., description="Source document")
    test_type: str = Field(default="positive", description="Test type")
    html_content: str = Field(..., description="HTML content for selector extraction")
    include_assertions: bool = Field(default=True, description="Include assertions")
    include_logging: bool = Field(default=True, description="Include logging")


class ScriptResponse(BaseModel):
    """Response model for generated script."""
    code: str
    test_case_id: str
    validation_status: str
    validation_warnings: list[str] = []
    validation_errors: list[str] = []
    selectors_used: list[str]
    file_path: Optional[str] = None


class ValidateScriptRequest(BaseModel):
    """Request model for script validation."""
    script_code: str = Field(..., description="Python script code to validate")


class ValidationResult(BaseModel):
    """Response model for validation results."""
    valid: bool
    status: str
    issues: list[str]
    selectors_count: int
    selectors: list[str]
    file_size: int


# Endpoints

@router.post("/generate", response_model=ScriptResponse)
async def generate_selenium_script(request: GenerateScriptRequest):
    """
    Generate Selenium WebDriver script from test case and HTML.

    Workflow:
    1. Extract selectors from HTML structure
    2. Build context-aware prompt with test case
    3. Generate Python Selenium code using LLM
    4. Validate syntax with AST parser
    5. Extract selectors used in generated code
    6. Return script with validation status

    The generated script uses:
    - Page Object Model pattern
    - Explicit waits (WebDriverWait)
    - Stable selectors (ID > Name > CSS > XPath)
    - Proper error handling
    - Assertions for verification
    """
    try:
        generator = get_script_generator()

        # Convert request to TestCase object
        test_type_map = {
            "positive": TestType.POSITIVE,
            "negative": TestType.NEGATIVE,
            "edge_case": TestType.EDGE_CASE
        }

        test_case = TestCase(
            test_id=request.test_case_id,
            feature=request.feature,
            test_scenario=request.test_scenario,
            test_steps=request.test_steps,
            expected_result=request.expected_result,
            grounded_in=request.grounded_in,
            test_type=test_type_map.get(request.test_type.lower(), TestType.POSITIVE)
        )

        logger.info(f"Generating Selenium script for test case: {request.test_case_id}")

        # Generate script
        selenium_script = generator.generate_script(
            test_case=test_case,
            html_content=request.html_content,
            include_assertions=request.include_assertions,
            include_logging=request.include_logging
        )

        # Save script to file
        file_path = generator.save_script(selenium_script)

        return ScriptResponse(
            code=selenium_script.code,
            test_case_id=selenium_script.test_case_id,
            validation_status=selenium_script.validation_status.value,
            validation_warnings=selenium_script.validation_warnings,
            validation_errors=selenium_script.validation_errors,
            selectors_used=selenium_script.selectors_used,
            file_path=file_path
        )

    except Exception as e:
        logger.error(f"Script generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Script generation failed: {str(e)}"
        )


@router.post("/validate", response_model=ValidationResult)
async def validate_script(request: ValidateScriptRequest):
    """
    Validate Python Selenium script syntax and structure.

    Performs:
    - AST-based syntax validation
    - WebDriver import checks
    - Selector extraction
    - Best practices verification

    Returns validation status with detailed issues if any.
    """
    try:
        generator = get_script_generator()

        # Validate syntax
        from ..models.selenium_script import ScriptStatus
        status, issues = generator._validate_python_syntax(request.script_code)

        # Extract selectors
        selectors = generator._extract_selectors_from_script(request.script_code)

        return ValidationResult(
            valid=status != ScriptStatus.INVALID,
            status=status.value,
            issues=issues,
            selectors_count=len(selectors),
            selectors=selectors,
            file_size=len(request.script_code)
        )

    except Exception as e:
        logger.error(f"Script validation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )


@router.get("/download/{test_case_id}")
async def download_script(test_case_id: str):
    """
    Download a generated Selenium script file.

    Returns the Python script file for download.
    """
    try:
        from backend.app.config import settings

        # Sanitize and construct file path
        from backend.app.utils.filesystem import sanitize_filename
        filename = sanitize_filename(f"test_{test_case_id}.py")
        filepath = Path(settings.scripts_dir) / filename

        if not filepath.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Script file not found: {test_case_id}"
            )

        return FileResponse(
            path=filepath,
            media_type="text/x-python",
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Script download failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Download failed: {str(e)}"
        )


class ExtractSelectorsRequest(BaseModel):
    """Request model for extracting selectors from HTML."""
    html_content: str = Field(..., description="HTML content to analyze")


@router.post("/extract-selectors")
async def extract_selectors(request: ExtractSelectorsRequest):
    """
    Extract HTML selectors from HTML content.

    Analyzes HTML structure and returns prioritized selectors:
    - ID selectors (highest stability)
    - Name attribute selectors
    - Class selectors
    - Tag selectors

    Useful for understanding available selectors before script generation.
    """
    try:
        generator = get_script_generator()

        # Extract selectors
        selectors = generator._extract_selectors(request.html_content)

        return JSONResponse(
            content={
                "total_selectors": len(selectors),
                "selectors": selectors
            }
        )

    except Exception as e:
        logger.error(f"Selector extraction failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Selector extraction failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for Selenium script generation service.

    Verifies that the LLM service is initialized and ready.
    """
    try:
        generator = get_script_generator()

        return JSONResponse(
            content={
                "status": "healthy",
                "service": "Selenium Script Generation",
                "llm_provider": generator.llm_service.get_provider_info().get("provider", "unknown")
            }
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "Selenium Script Generation",
                "error": str(e)
            }
        )
