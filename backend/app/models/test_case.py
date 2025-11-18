"""
Internal data models for test cases and related entities.

Uses dataclasses for internal representation of business objects.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== Enums ====================

class TestType(str, Enum):
    """Test case type enumeration."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    EDGE_CASE = "edge_case"
    BOUNDARY = "boundary"


class KnowledgeBaseStatus(str, Enum):
    """Knowledge base build status."""
    NOT_BUILT = "not_built"
    BUILDING = "building"
    READY = "ready"
    ERROR = "error"


# ==================== Document Models ====================

@dataclass
class DocumentMetadata:
    """Metadata for uploaded documents."""
    filename: str
    file_type: str
    file_size: int  # bytes
    upload_timestamp: datetime
    num_chunks: Optional[int] = None
    processing_time: Optional[float] = None


@dataclass
class DocumentChunk:
    """A chunk of text from a document."""
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    chunk_id: Optional[str] = None


@dataclass
class RetrievedChunk:
    """A retrieved chunk with similarity score."""
    text: str
    metadata: Dict[str, Any]
    distance: float

    @property
    def similarity_score(self) -> float:
        """Convert distance to similarity score (0-1)."""
        return 1 / (1 + self.distance)

    @property
    def source_document(self) -> str:
        """Get source document name."""
        return self.metadata.get('source_document', 'unknown')


# ==================== Test Case Models ====================

@dataclass
class TestData:
    """Test data for a test case."""
    input: Dict[str, Any]
    expected: Any


@dataclass
class TestCase:
    """A generated test case."""
    test_id: str
    feature: str
    test_scenario: str
    test_steps: List[str]
    expected_result: str
    grounded_in: str  # Source document
    test_type: TestType = TestType.POSITIVE
    test_data: Optional[TestData] = None
    priority: str = "medium"
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "test_id": self.test_id,
            "feature": self.feature,
            "test_scenario": self.test_scenario,
            "test_steps": self.test_steps,
            "expected_result": self.expected_result,
            "grounded_in": self.grounded_in,
            "test_type": self.test_type.value if isinstance(self.test_type, TestType) else self.test_type,
            "test_data": {
                "input": self.test_data.input,
                "expected": self.test_data.expected
            } if self.test_data else None,
            "priority": self.priority,
            "tags": self.tags,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class TestCaseResponse:
    """Response containing generated test cases."""
    test_cases: List[TestCase]
    sources: List[RetrievedChunk]
    query: str
    generated_at: datetime = field(default_factory=datetime.now)
    generation_time: Optional[float] = None


# ==================== Knowledge Base Models ====================

@dataclass
class KnowledgeBaseInfo:
    """Information about the knowledge base."""
    status: KnowledgeBaseStatus
    num_documents: int
    num_chunks: int
    documents: List[DocumentMetadata]
    last_build: Optional[datetime] = None
    build_duration: Optional[float] = None
