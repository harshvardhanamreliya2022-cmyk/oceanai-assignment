"""
Pydantic models for API request/response schemas.

These models define the structure of data exchanged via the API endpoints.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ==================== Document Upload ====================

class UploadDocumentResponse(BaseModel):
    """Response after uploading a document."""
    document_id: str
    filename: str
    file_type: str
    file_size: int
    status: str
    upload_timestamp: datetime


class UploadHTMLResponse(BaseModel):
    """Response after uploading HTML file."""
    html_id: str
    filename: str
    num_elements: int
    forms: int
    inputs: int
    buttons: int
    status: str


# ==================== Knowledge Base ====================

class BuildKBRequest(BaseModel):
    """Request to build knowledge base."""
    document_ids: List[str] = Field(description="List of document IDs to include")
    html_id: str = Field(description="ID of uploaded HTML file")
    chunk_size: int = Field(default=1000, description="Size of text chunks")
    chunk_overlap: int = Field(default=200, description="Overlap between chunks")


class BuildKBResponse(BaseModel):
    """Response from building knowledge base."""
    status: str
    num_documents: int
    num_chunks: int
    build_time: float
    message: str


class KBStatusResponse(BaseModel):
    """Response for knowledge base status."""
    status: str
    num_documents: int
    num_chunks: int
    documents: List[Dict[str, Any]]
    last_build: Optional[datetime] = None
    build_duration: Optional[float] = None


# ==================== Test Case Generation ====================

class GenerateTestCasesRequest(BaseModel):
    """Request to generate test cases."""
    query: str = Field(description="Natural language query for test generation")
    include_negative: bool = Field(default=True, description="Include negative test cases")
    max_test_cases: int = Field(default=10, description="Maximum number of test cases")
    top_k_retrieval: int = Field(default=5, description="Number of docs to retrieve")


class TestCaseSchema(BaseModel):
    """Schema for a single test case."""
    test_id: str
    feature: str
    test_scenario: str
    test_steps: List[str]
    expected_result: str
    grounded_in: str  # Source document
    test_type: str  # positive, negative, edge_case
    test_data: Optional[Dict[str, Any]] = None
    priority: str = "medium"
    tags: List[str] = []
    created_at: datetime


class TestCaseResponse(BaseModel):
    """Response model for generated test cases."""
    test_id: str
    feature: str
    test_scenario: str
    test_steps: List[str]
    expected_result: str
    grounded_in: str  # Source document - CRITICAL for anti-hallucination
    test_type: str  # positive, negative, edge_case


class SourceDocumentSchema(BaseModel):
    """Schema for source document reference."""
    text: str
    source_document: str
    similarity_score: float


class GenerateTestCasesResponse(BaseModel):
    """Response with generated test cases."""
    test_cases: List[TestCaseSchema]
    sources: List[SourceDocumentSchema]
    generation_time: float
    query: str


# ==================== Selenium Script Generation ====================

class GenerateScriptRequest(BaseModel):
    """Request to generate Selenium script."""
    test_case_id: str = Field(description="ID of test case to convert to script")
    include_assertions: bool = Field(default=True, description="Include assertions")
    include_logging: bool = Field(default=True, description="Include logging statements")


class GenerateScriptResponse(BaseModel):
    """Response with generated Selenium script."""
    script_code: str
    file_name: str
    validation_status: str
    validation_warnings: List[str] = []
    selectors_used: List[str] = []
    generation_time: float


class ScriptValidationSchema(BaseModel):
    """Validation results for generated script."""
    status: str  # valid, valid_with_warnings, invalid
    errors: List[str] = []
    warnings: List[str] = []
    selectors_found: List[str] = []
    syntax_valid: bool = True


# ==================== Document List ====================

class DocumentListResponse(BaseModel):
    """Response with list of uploaded documents."""
    documents: List[Dict[str, Any]]
    total_count: int


# ==================== Error Responses ====================

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# ==================== Health Check ====================

class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    version: str
    service: str
