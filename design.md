# System Design Document
## Autonomous QA Agent for Test Case and Script Generation

**Project Code:** QA-AGENT-2024  
**Version:** 1.0  
**Last Updated:** November 18, 2025  
**Status:** Design Approved

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Component Design](#component-design)
4. [Data Models](#data-models)
5. [API Specifications](#api-specifications)
6. [Database Design](#database-design)
7. [LLM Integration](#llm-integration)
8. [Security Design](#security-design)
9. [Deployment Architecture](#deployment-architecture)

---

## System Overview

### System Context Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         External Systems                        │
│                                                                 │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐            │
│  │  Groq    │      │ Ollama   │      │ OpenAI   │            │
│  │   API    │      │  Local   │      │   API    │            │
│  └────┬─────┘      └────┬─────┘      └────┬─────┘            │
└───────┼─────────────────┼──────────────────┼──────────────────┘
        │                 │                  │
        └─────────────────┼──────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────────┐
│                    QA Agent System                            │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Streamlit Frontend                       │   │
│  │  [Upload] [Build KB] [Generate Tests] [Gen Scripts] │   │
│  └─────────────────────┬────────────────────────────────┘   │
│                        │                                     │
│  ┌─────────────────────▼────────────────────────────────┐   │
│  │              FastAPI Backend                          │   │
│  │                                                       │   │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────────┐       │   │
│  │  │Document  │  │   RAG    │  │  Selenium   │       │   │
│  │  │Processor │  │  Engine  │  │  Generator  │       │   │
│  │  └──────────┘  └──────────┘  └─────────────┘       │   │
│  └─────────────────────┬────────────────────────────────┘   │
│                        │                                     │
│  ┌─────────────────────▼────────────────────────────────┐   │
│  │            Vector Database (ChromaDB)                 │   │
│  │  [Document Chunks] [Embeddings] [Metadata]          │   │
│  └───────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                    File System                              │
│  [Uploads] [HTML Files] [Generated Scripts] [Logs]         │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit 1.29+ | User interface |
| **Backend** | FastAPI 0.104+ | REST API server |
| **Vector DB** | ChromaDB 0.4.18 | Embedding storage & retrieval |
| **Embeddings** | sentence-transformers | Text to vector conversion |
| **LLM** | Groq/Ollama/OpenAI | Test & script generation |
| **Orchestration** | LangChain 0.1+ | RAG pipeline management |
| **Parsing** | BeautifulSoup4, pymupdf | Document processing |
| **Testing** | pytest, Selenium | Script validation |

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Presentation Layer                         │
│                      (Streamlit UI)                             │
├─────────────────────────────────────────────────────────────────┤
│                      API Layer                                  │
│                      (FastAPI Endpoints)                        │
├─────────────────────────────────────────────────────────────────┤
│                      Business Logic Layer                       │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────┐      │
│  │   Document    │  │      RAG      │  │   Selenium   │      │
│  │   Service     │  │    Service    │  │   Service    │      │
│  └───────────────┘  └───────────────┘  └──────────────┘      │
├─────────────────────────────────────────────────────────────────┤
│                      Data Access Layer                          │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────┐      │
│  │  Vector Store │  │  File System  │  │  LLM Client  │      │
│  │   Repository  │  │   Repository  │  │   Adapter    │      │
│  └───────────────┘  └───────────────┘  └──────────────┘      │
├─────────────────────────────────────────────────────────────────┤
│                      Infrastructure Layer                       │
│  [ChromaDB] [File System] [LLM APIs] [Logging]                │
└─────────────────────────────────────────────────────────────────┘
```

### Architectural Patterns

#### 1. Layered Architecture
- **Separation of Concerns:** Each layer has distinct responsibilities
- **Dependency Rule:** Higher layers depend on lower layers only
- **Testability:** Each layer can be tested independently

#### 2. Repository Pattern
- Abstract data access from business logic
- Swap implementations (e.g., different vector DBs)
- Easier unit testing with mocks

#### 3. Adapter Pattern
- LLM client adapter for different providers
- Parser adapter for different document types
- Consistent interface across implementations

#### 4. Pipeline Pattern
- RAG pipeline: Query → Retrieve → Augment → Generate
- Document processing: Upload → Parse → Chunk → Embed → Store
- Script generation: Select → Retrieve → Generate → Validate → Return

---

## Component Design

### 1. Document Processor Service

**Responsibility:** Parse and prepare documents for vectorization

```python
# Detailed Design

class DocumentProcessor:
    """
    Processes uploaded documents into chunks suitable for embedding.
    
    Supports: MD, TXT, JSON, HTML, PDF
    """
    
    def __init__(self):
        self.parsers = {
            'md': MarkdownParser(),
            'txt': TextParser(),
            'json': JSONParser(),
            'html': HTMLParser(),
            'pdf': PDFParser()
        }
    
    def process_document(
        self, 
        file_path: str, 
        metadata: dict
    ) -> List[DocumentChunk]:
        """
        Process a single document.
        
        Args:
            file_path: Path to document
            metadata: Document metadata (name, type, upload_time)
            
        Returns:
            List of DocumentChunk objects
            
        Raises:
            UnsupportedFormatError: If file type not supported
            ParseError: If document cannot be parsed
        """
        file_type = self._detect_file_type(file_path)
        parser = self.parsers.get(file_type)
        
        if not parser:
            raise UnsupportedFormatError(f"Type {file_type} not supported")
        
        # Parse document
        text_content = parser.parse(file_path)
        
        # Chunk text
        chunks = self._chunk_text(
            text_content, 
            chunk_size=1000, 
            overlap=200
        )
        
        # Create DocumentChunk objects with metadata
        return [
            DocumentChunk(
                text=chunk,
                metadata={
                    **metadata,
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                }
            )
            for i, chunk in enumerate(chunks)
        ]
    
    def _chunk_text(
        self, 
        text: str, 
        chunk_size: int, 
        overlap: int
    ) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Uses RecursiveCharacterTextSplitter with:
        - Paragraph boundaries (\n\n)
        - Sentence boundaries (. )
        - Word boundaries ( )
        """
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        return splitter.split_text(text)
```

**Key Classes:**

```python
@dataclass
class DocumentChunk:
    """Represents a chunk of document text with metadata"""
    text: str
    metadata: dict
    embedding: Optional[List[float]] = None
    chunk_id: Optional[str] = None

class ParserInterface(ABC):
    """Abstract interface for document parsers"""
    
    @abstractmethod
    def parse(self, file_path: str) -> str:
        """Parse document and return text content"""
        pass
    
    @abstractmethod
    def validate(self, file_path: str) -> bool:
        """Validate document format"""
        pass
```

---

### 2. Vector Store Service

**Responsibility:** Manage vector database operations

```python
class VectorStoreService:
    """
    Manages ChromaDB vector store operations.
    
    Handles: embedding generation, storage, retrieval
    """
    
    def __init__(self, persist_directory: str = "./data/vectordb"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection = None
    
    def create_collection(self, name: str = "qa_knowledge_base"):
        """Create or get collection"""
        self.collection = self.client.get_or_create_collection(
            name=name,
            metadata={"description": "QA Agent Knowledge Base"}
        )
    
    def add_documents(self, chunks: List[DocumentChunk]):
        """
        Add document chunks to vector store.
        
        Args:
            chunks: List of DocumentChunk objects
            
        Process:
            1. Generate embeddings for each chunk
            2. Store in ChromaDB with metadata
            3. Return success status
        """
        texts = [chunk.text for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(
            texts, 
            show_progress_bar=True
        ).tolist()
        
        # Generate unique IDs
        ids = [f"chunk_{uuid.uuid4()}" for _ in chunks]
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
    
    def query(
        self, 
        query_text: str, 
        n_results: int = 5,
        filter_dict: Optional[dict] = None
    ) -> List[RetrievedChunk]:
        """
        Query vector store for relevant chunks.
        
        Args:
            query_text: User query
            n_results: Number of results to return
            filter_dict: Metadata filters (e.g., {'source': 'product_specs.md'})
            
        Returns:
            List of RetrievedChunk objects with text, metadata, similarity score
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(
            query_text
        ).tolist()
        
        # Query collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_dict
        )
        
        # Format results
        return [
            RetrievedChunk(
                text=doc,
                metadata=meta,
                distance=dist
            )
            for doc, meta, dist in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )
        ]
    
    def clear_collection(self):
        """Clear all data from collection"""
        if self.collection:
            self.client.delete_collection(self.collection.name)
            self.create_collection()
```

**Data Model:**

```python
@dataclass
class RetrievedChunk:
    """Retrieved document chunk with similarity score"""
    text: str
    metadata: dict
    distance: float  # Lower is more similar
    
    @property
    def similarity_score(self) -> float:
        """Convert distance to similarity (0-1)"""
        return 1 / (1 + self.distance)
```

---

### 3. RAG Engine Service

**Responsibility:** Orchestrate retrieval-augmented generation

```python
class RAGEngine:
    """
    Retrieval-Augmented Generation engine.
    
    Orchestrates: retrieval → context building → LLM generation
    """
    
    def __init__(
        self, 
        vector_store: VectorStoreService,
        llm_client: LLMClient
    ):
        self.vector_store = vector_store
        self.llm_client = llm_client
    
    def generate_test_cases(
        self, 
        query: str, 
        html_content: str,
        top_k: int = 5
    ) -> TestCaseResponse:
        """
        Generate test cases using RAG pipeline.
        
        Pipeline:
        1. Retrieve relevant documentation
        2. Extract HTML selectors
        3. Build context-rich prompt
        4. Generate with LLM
        5. Parse and validate response
        """
        # Step 1: Retrieve relevant chunks
        retrieved_chunks = self.vector_store.query(
            query_text=query,
            n_results=top_k
        )
        
        # Step 2: Extract HTML information
        html_elements = self._extract_html_elements(html_content)
        
        # Step 3: Build prompt
        prompt = self._build_test_case_prompt(
            query=query,
            retrieved_chunks=retrieved_chunks,
            html_elements=html_elements
        )
        
        # Step 4: Generate with LLM
        response = self.llm_client.generate(
            prompt=prompt,
            temperature=0.0,  # Deterministic output
            max_tokens=2000
        )
        
        # Step 5: Parse response
        test_cases = self._parse_test_case_response(response)
        
        # Step 6: Validate grounding
        self._validate_grounding(test_cases, retrieved_chunks)
        
        return TestCaseResponse(
            test_cases=test_cases,
            sources=retrieved_chunks,
            query=query
        )
    
    def _build_test_case_prompt(
        self, 
        query: str,
        retrieved_chunks: List[RetrievedChunk],
        html_elements: dict
    ) -> str:
        """
        Build comprehensive prompt for test case generation.
        
        Includes:
        - Strict instructions to use only provided docs
        - Retrieved documentation context
        - HTML structure information
        - User query
        - Output format requirements
        """
        context = "\n\n".join([
            f"[Source: {chunk.metadata['source_document']}]\n{chunk.text}"
            for chunk in retrieved_chunks
        ])
        
        html_info = json.dumps(html_elements, indent=2)
        
        prompt = f"""You are a QA testing expert. Generate comprehensive test cases based STRICTLY on the provided documentation.

CRITICAL RULES:
1. ONLY use information from the documentation below
2. DO NOT invent or assume any features not mentioned
3. Every test case MUST cite its source document
4. If information is not in documentation, do not create a test for it

DOCUMENTATION CONTEXT:
{context}

HTML STRUCTURE:
{html_info}

USER REQUEST:
{query}

Generate test cases in the following JSON format:
{{
  "test_cases": [
    {{
      "test_id": "TC-001",
      "feature": "Feature name from documentation",
      "test_scenario": "Specific scenario to test",
      "test_steps": [
        "Step 1: Detailed action",
        "Step 2: Detailed action"
      ],
      "test_data": {{
        "input": "Specific test data",
        "expected": "Expected result"
      }},
      "expected_result": "What should happen",
      "test_type": "positive" or "negative",
      "grounded_in": "Exact document name from [Source: ...] above"
    }}
  ]
}}

Generate comprehensive test cases covering both positive and negative scenarios."""
        
        return prompt
    
    def _validate_grounding(
        self, 
        test_cases: List[TestCase],
        retrieved_chunks: List[RetrievedChunk]
    ):
        """
        Validate that each test case is grounded in documentation.
        
        Raises warning if source not found in retrieved chunks.
        """
        available_sources = {
            chunk.metadata['source_document'] 
            for chunk in retrieved_chunks
        }
        
        for test_case in test_cases:
            if test_case.grounded_in not in available_sources:
                logger.warning(
                    f"Test case {test_case.test_id} cites unknown source: "
                    f"{test_case.grounded_in}"
                )
```

---

### 4. Selenium Generator Service

**Responsibility:** Generate executable Selenium scripts

```python
class SeleniumGeneratorService:
    """
    Generates Selenium WebDriver scripts from test cases.
    
    Handles: selector extraction, script generation, validation
    """
    
    def __init__(
        self, 
        llm_client: LLMClient,
        vector_store: VectorStoreService
    ):
        self.llm_client = llm_client
        self.vector_store = vector_store
    
    def generate_script(
        self, 
        test_case: TestCase,
        html_content: str
    ) -> SeleniumScript:
        """
        Generate Selenium script for a test case.
        
        Process:
        1. Parse HTML to extract selectors
        2. Retrieve relevant documentation
        3. Build script generation prompt
        4. Generate script with LLM
        5. Validate Python syntax
        6. Return formatted script
        """
        # Extract selectors
        selectors = self._extract_selectors(html_content)
        
        # Get documentation context
        context = self.vector_store.query(
            query_text=test_case.test_scenario,
            n_results=3
        )
        
        # Build prompt
        prompt = self._build_script_prompt(
            test_case=test_case,
            selectors=selectors,
            context=context
        )
        
        # Generate script
        script_code = self.llm_client.generate(
            prompt=prompt,
            temperature=0.0,
            max_tokens=1500
        )
        
        # Clean and validate
        script_code = self._clean_code(script_code)
        validation = self._validate_script(script_code, selectors)
        
        return SeleniumScript(
            code=script_code,
            test_case_id=test_case.test_id,
            selectors_used=validation.selectors_found,
            validation_status=validation.status,
            validation_errors=validation.errors
        )
    
    def _extract_selectors(self, html_content: str) -> dict:
        """
        Extract all useful selectors from HTML.
        
        Returns dict with:
        - ids: List of element IDs
        - names: List of element names
        - buttons: List of button texts
        - inputs: List of input fields with types
        - forms: List of form IDs/names
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        selectors = {
            'ids': [],
            'names': [],
            'buttons': [],
            'inputs': [],
            'forms': [],
            'select': [],
            'radio': [],
            'checkbox': []
        }
        
        # Extract IDs
        for elem in soup.find_all(id=True):
            selectors['ids'].append({
                'id': elem.get('id'),
                'tag': elem.name,
                'text': elem.get_text(strip=True)[:50]
            })
        
        # Extract names
        for elem in soup.find_all(attrs={'name': True}):
            selectors['names'].append({
                'name': elem.get('name'),
                'tag': elem.name,
                'type': elem.get('type', 'text')
            })
        
        # Extract buttons
        for button in soup.find_all(['button', 'input']):
            if button.name == 'input' and button.get('type') not in ['button', 'submit']:
                continue
            selectors['buttons'].append({
                'text': button.get_text(strip=True) or button.get('value', ''),
                'id': button.get('id'),
                'name': button.get('name')
            })
        
        # Extract inputs
        for inp in soup.find_all('input'):
            selectors['inputs'].append({
                'name': inp.get('name'),
                'id': inp.get('id'),
                'type': inp.get('type', 'text'),
                'placeholder': inp.get('placeholder')
            })
        
        # Extract radio buttons
        for radio in soup.find_all('input', type='radio'):
            selectors['radio'].append({
                'name': radio.get('name'),
                'value': radio.get('value'),
                'id': radio.get('id')
            })
        
        return selectors
    
    def _build_script_prompt(
        self, 
        test_case: TestCase,
        selectors: dict,
        context: List[RetrievedChunk]
    ) -> str:
        """Build comprehensive prompt for Selenium script generation"""
        
        context_text = "\n".join([chunk.text for chunk in context])
        selectors_json = json.dumps(selectors, indent=2)
        
        prompt = f"""You are a Selenium WebDriver expert. Generate a complete, executable Python test script.

TEST CASE TO AUTOMATE:
Test ID: {test_case.test_id}
Feature: {test_case.feature}
Scenario: {test_case.test_scenario}

Test Steps:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(test_case.test_steps))}

Expected Result: {test_case.expected_result}

HTML SELECTORS AVAILABLE:
{selectors_json}

DOCUMENTATION CONTEXT:
{context_text}

Generate a complete Python Selenium script that:
1. Uses ONLY the selectors provided above
2. Implements ALL test steps
3. Includes proper waits (WebDriverWait)
4. Has comprehensive error handling
5. Includes assertions for expected results
6. Has clear comments explaining each step
7. Follows Python best practices
8. Is immediately executable

IMPORTANT: 
- Prefer IDs over other selectors when available
- Use explicit waits, not time.sleep()
- Include setup and teardown
- Add meaningful assertion messages

Use this template:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pytest

class Test{test_case.test_id.replace('-', '_')}:
    \"\"\"
    Test Case: {test_case.test_id}
    Feature: {test_case.feature}
    Scenario: {test_case.test_scenario}
    \"\"\"
    
    def setup_method(self):
        \"\"\"Setup test environment\"\"\"
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)
    
    def teardown_method(self):
        \"\"\"Cleanup after test\"\"\"
        if self.driver:
            self.driver.quit()
    
    def test_{test_case.test_id.lower().replace('-', '_')}(self):
        \"\"\"Main test method\"\"\"
        # TODO: Implement test steps
        pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

Generate the complete, runnable script now."""
        
        return prompt
    
    def _validate_script(
        self, 
        script_code: str,
        available_selectors: dict
    ) -> ScriptValidation:
        """
        Validate generated script.
        
        Checks:
        1. Python syntax is valid
        2. Required imports present
        3. Selectors used exist in HTML
        4. Proper Selenium patterns used
        """
        errors = []
        warnings = []
        selectors_found = []
        
        # Check Python syntax
        try:
            compile(script_code, '<string>', 'exec')
        except SyntaxError as e:
            errors.append(f"Syntax error: {str(e)}")
        
        # Check imports
        required_imports = ['selenium', 'webdriver', 'By']
        for imp in required_imports:
            if imp not in script_code:
                warnings.append(f"Missing import: {imp}")
        
        # Check selectors usage
        all_selector_values = []
        for selector_list in available_selectors.values():
            if isinstance(selector_list, list):
                for sel in selector_list:
                    if isinstance(sel, dict):
                        all_selector_values.extend(sel.values())
        
        # Find selectors in script
        import re
        selector_patterns = [
            r'find_element\(By\.ID,\s*["\']([^"\']+)["\']',
            r'find_element\(By\.NAME,\s*["\']([^"\']+)["\']',
            r'find_element\(By\.CSS_SELECTOR,\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in selector_patterns:
            matches = re.findall(pattern, script_code)
            selectors_found.extend(matches)
        
        # Validate selectors exist
        for selector in selectors_found:
            if selector not in [str(v) for v in all_selector_values]:
                warnings.append(
                    f"Selector '{selector}' not found in HTML"
                )
        
        status = "valid" if not errors else "invalid"
        if warnings:
            status = "valid_with_warnings"
        
        return ScriptValidation(
            status=status,
            errors=errors,
            warnings=warnings,
            selectors_found=selectors_found
        )
```

---

## Data Models

### Core Data Models

```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# ==================== Enums ====================

class TestType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    EDGE_CASE = "edge_case"
    BOUNDARY = "boundary"

class ScriptStatus(str, Enum):
    VALID = "valid"
    VALID_WITH_WARNINGS = "valid_with_warnings"
    INVALID = "invalid"

class KnowledgeBaseStatus(str, Enum):
    NOT_BUILT = "not_built"
    BUILDING = "building"
    READY = "ready"
    ERROR = "error"

# ==================== Document Models ====================

@dataclass
class DocumentMetadata:
    """Metadata for uploaded documents"""
    filename: str
    file_type: str
    file_size: int  # bytes
    upload_timestamp: datetime
    num_chunks: Optional[int] = None
    processing_time: Optional[float] = None

@dataclass
class DocumentChunk:
    """A chunk of text from a document"""
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    chunk_id: Optional[str] = None

@dataclass
class RetrievedChunk:
    """A retrieved chunk with similarity score"""
    text: str
    metadata: Dict[str, Any]
    distance: float
    
    @property
    def similarity_score(self) -> float:
        return 1 / (1 + self.distance)
    
    @property
    def source_document(self) -> str:
        return self.metadata.get('source_document', 'unknown')

# ==================== Test Case Models ====================

@dataclass
class TestData:
    """Test data for a test case"""
    input: Dict[str, Any]
    expected: Any

@dataclass
class TestCase:
    """A generated test case"""
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

@dataclass
class TestCaseResponse:
    """Response containing generated test cases"""
    test_cases: List[TestCase]
    sources: List[RetrievedChunk]
    query: str
    generated_at: datetime = field(default_factory=datetime.now)
    generation_time: Optional[float] = None

# ==================== Selenium Models ====================

@dataclass
class HTMLSelector:
    """Represents an HTML selector"""
    selector_type: str  # id, name, css, xpath
    selector_value: str
    element_tag: str
    element_text: Optional[str] = None

@dataclass
class ScriptValidation:
    """Validation results for a generated script"""
    status: ScriptStatus
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    selectors_found: List[str] = field(default_factory=list)
    syntax_valid: bool = True

@dataclass
class SeleniumScript:
    """A generated Selenium script"""
    code: str
    test_case_id: str
    selectors_used: List[str]
    validation_status: ScriptStatus
    validation_errors: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    file_name: Optional[str] = None

# ==================== Knowledge Base Models ====================

@dataclass
class KnowledgeBaseInfo:
    """Information about the knowledge base"""
    status: KnowledgeBaseStatus
    num_documents: int
    num_chunks: int
    documents: List[DocumentMetadata]
    last_build: Optional[datetime] = None
    build_duration: Optional[float] = None

# ==================== API Request/Response Models ====================

from pydantic import BaseModel, Field

class UploadDocumentRequest(BaseModel):
    """Request to upload a document"""
    filename: str
    content: str  # Base64 encoded
    file_type: str

class BuildKBRequest(BaseModel):
    """Request to build knowledge base"""
    document_ids: List[str]
    html_content: str
    chunk_size: int = 1000
    chunk_overlap: int = 200

class BuildKBResponse(BaseModel):
    """Response from building knowledge base"""
    status: str
    num_documents: int
    num_chunks: int
    build_time: float
    message: str

class GenerateTestCasesRequest(BaseModel):
    """Request to generate test cases"""
    query: str
    include_negative: bool = True
    max_test_cases: int = 10
    top_k_retrieval: int = 5

class GenerateTestCasesResponse(BaseModel):
    """Response with generated test cases"""
    test_cases: List[Dict[str, Any]]
    sources: List[Dict[str, Any]]
    generation_time: float

class GenerateScriptRequest(BaseModel):
    """Request to generate Selenium script"""
    test_case_id: str
    include_assertions: bool = True
    include_logging: bool = True

class GenerateScriptResponse(BaseModel):
    """Response with generated script"""
    script_code: str
    file_name: str
    validation_status: str
    validation_warnings: List[str] = []
    generation_time: float
```

---

## API Specifications

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
No authentication required for this version.

### Endpoints

#### 1. Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-18T10:30:00Z",
  "version": "1.0.0"
}
```

---

#### 2. Upload Document

```http
POST /documents/upload
Content-Type: multipart/form-data
```

**Request:**
```
file: <binary file data>
```

**Response:**
```json
{
  "document_id": "doc_123abc",
  "filename": "product_specs.md",
  "file_type": "md",
  "file_size": 2048,
  "status": "uploaded",
  "upload_timestamp": "2025-11-18T10:30:00Z"
}
```

**Status Codes:**
- `200 OK` - File uploaded successfully
- `400 Bad Request` - Invalid file format
- `413 Payload Too Large` - File exceeds size limit
- `500 Internal Server Error` - Upload failed

---

#### 3. Upload HTML

```http
POST /html/upload
Content-Type: multipart/form-data OR application/json
```

**Request (File):**
```
file: <HTML file>
```

**Request (Paste):**
```json
{
  "html_content": "<html>...</html>",
  "filename": "checkout.html"
}
```

**Response:**
```json
{
  "html_id": "html_456def",
  "filename": "checkout.html",
  "num_elements": 45,
  "forms": 1,
  "inputs": 8,
  "buttons": 3,
  "status": "processed"
}
```

---

#### 4. Build Knowledge Base

```http
POST /knowledge-base/build
Content-Type: application/json
```

**Request:**
```json
{
  "document_ids": ["doc_123abc", "doc_789ghi"],
  "html_id": "html_456def",
  "chunk_size": 1000,
  "chunk_overlap": 200
}
```

**Response:**
```json
{
  "status": "success",
  "num_documents": 2,
  "num_chunks": 47,
  "build_time": 12.5,
  "message": "Knowledge base built successfully",
  "kb_info": {
    "status": "ready",
    "last_build": "2025-11-18T10:35:00Z"
  }
}
```

**Status Codes:**
- `200 OK` - KB built successfully
- `400 Bad Request` - Invalid request parameters
- `500 Internal Server Error` - Build failed

---

#### 5. Get Knowledge Base Status

```http
GET /knowledge-base/status
```

**Response:**
```json
{
  "status": "ready",
  "num_documents": 3,
  "num_chunks": 52,
  "documents": [
    {
      "filename": "product_specs.md",
      "file_type": "md",
      "num_chunks": 15,
      "upload_timestamp": "2025-11-18T10:30:00Z"
    }
  ],
  "last_build": "2025-11-18T10:35:00Z",
  "build_duration": 12.5
}
```

---

#### 6. Generate Test Cases

```http
POST /test-cases/generate
Content-Type: application/json
```

**Request:**
```json
{
  "query": "Generate test cases for discount code feature",
  "include_negative": true,
  "max_test_cases": 10,
  "top_k_retrieval": 5
}
```

**Response:**
```json
{
  "test_cases": [
    {
      "test_id": "TC-001",
      "feature": "Discount Code",
      "test_scenario": "Apply valid discount code SAVE15",
      "test_steps": [
        "Navigate to checkout page",
        "Add items to cart",
        "Enter discount code 'SAVE15'",
        "Click Apply button"
      ],
      "expected_result": "Total price reduced by 15%",
      "test_type": "positive",
      "grounded_in": "product_specs.md",
      "test_data": {
        "input": {"code": "SAVE15", "cart_total": 100},
        "expected": {"discounted_total": 85}
      }
    }
  ],
  "sources": [
    {
      "text": "The discount code SAVE15 applies a 15% discount...",
      "source_document": "product_specs.md",
      "similarity_score": 0.92
    }
  ],
  "generation_time": 8.3
}
```

**Status Codes:**
- `200 OK` - Test cases generated
- `400 Bad Request` - Invalid query
- `404 Not Found` - Knowledge base not built
- `500 Internal Server Error` - Generation failed

---

#### 7. Generate Selenium Script

```http
POST /selenium/generate
Content-Type: application/json
```

**Request:**
```json
{
  "test_case_id": "TC-001",
  "include_assertions": true,
  "include_logging": true
}
```

**Response:**
```json
{
  "script_code": "from selenium import webdriver\n...",
  "file_name": "test_tc_001.py",
  "validation_status": "valid",
  "validation_warnings": [],
  "selectors_used": ["discount-code-input", "apply-button"],
  "generation_time": 6.7
}
```

**Status Codes:**
- `200 OK` - Script generated
- `400 Bad Request` - Invalid test case ID
- `404 Not Found` - Test case not found
- `500 Internal Server Error` - Generation failed

---

#### 8. Download Script

```http
GET /selenium/download/{script_id}
```

**Response:**
```
Content-Type: text/x-python
Content-Disposition: attachment; filename="test_tc_001.py"

[Script content]
```

---

#### 9. List Documents

```http
GET /documents/list
```

**Response:**
```json
{
  "documents": [
    {
      "document_id": "doc_123abc",
      "filename": "product_specs.md",
      "file_type": "md",
      "file_size": 2048,
      "upload_timestamp": "2025-11-18T10:30:00Z",
      "num_chunks": 15
    }
  ],
  "total_count": 1
}
```

---

#### 10. Delete Document

```http
DELETE /documents/{document_id}
```

**Response:**
```json
{
  "status": "deleted",
  "document_id": "doc_123abc",
  "message": "Document deleted successfully"
}
```

---

## Database Design

### Vector Database Schema (ChromaDB)

**Collection:** `qa_knowledge_base`

**Document Structure:**
```python
{
    "id": "chunk_uuid",  # Unique chunk identifier
    "embedding": [0.123, -0.456, ...],  # 384-dimensional vector
    "document": "text content of chunk",
    "metadata": {
        "source_document": "product_specs.md",
        "document_id": "doc_123abc",
        "chunk_index": 0,
        "total_chunks": 15,
        "upload_timestamp": "2025-11-18T10:30:00Z",
        "file_type": "md",
        "chunk_size": 1000
    }
}
```

**Indexing:**
- HNSW index for fast similarity search
- Cosine similarity for distance metric

---

### File System Structure

```
data/
├── vectordb/               # ChromaDB persistent storage
│   └── chroma.sqlite3     # Vector database
├── uploads/               # Uploaded documents
│   ├── doc_123abc.md
│   ├── doc_456def.txt
│   └── html_789ghi.html
├── scripts/               # Generated Selenium scripts
│   └── test_tc_001.py
└── logs/                  # Application logs
    └── app.log
```

---

## LLM Integration

### Supported LLM Providers

#### 1. Groq (Recommended)

**Configuration:**
```python
LLM_PROVIDER = "groq"
GROQ_API_KEY = "gsk_..."
GROQ_MODEL = "mixtral-8x7b-32768"
```

**Pros:**
- Free tier available
- Very fast inference
- Good quality outputs
- Large context window

**Cons:**
- Requires internet
- Rate limits on free tier

---

#### 2. Ollama (Local)

**Configuration:**
```python
LLM_PROVIDER = "ollama"
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3"
```

**Pros:**
- Completely local
- No API costs
- No rate limits
- Privacy-preserving

**Cons:**
- Requires local setup
- Slower inference
- Requires good hardware

---

#### 3. OpenAI (Optional)

**Configuration:**
```python
LLM_PROVIDER = "openai"
OPENAI_API_KEY = "sk-..."
OPENAI_MODEL = "gpt-4-turbo-preview"
```

**Pros:**
- Best quality outputs
- Reliable service
- Good documentation

**Cons:**
- Costs money
- Requires API key
- Rate limits

---

### LLM Client Interface

```python
from abc import ABC, abstractmethod

class LLMClient(ABC):
    """Abstract interface for LLM providers"""
    
    @abstractmethod
    def generate(
        self, 
        prompt: str, 
        temperature: float = 0.0,
        max_tokens: int = 2000
    ) -> str:
        """Generate completion from prompt"""
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """Test if LLM service is accessible"""
        pass

class GroqClient(LLMClient):
    """Groq implementation"""
    def __init__(self, api_key: str, model: str):
        self.client = Groq(api_key=api_key)
        self.model = model
    
    def generate(self, prompt, temperature=0.0, max_tokens=2000):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content

class OllamaClient(LLMClient):
    """Ollama implementation"""
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model = model
    
    def generate(self, prompt, temperature=0.0, max_tokens=2000):
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "temperature": temperature,
                "stream": False
            }
        )
        return response.json()["response"]
```

---

## Security Design

### Input Validation

**File Uploads:**
- File type whitelist: MD, TXT, JSON, HTML, PDF
- Maximum file size: 10MB
- Scan for malicious content
- Validate file signatures (magic bytes)

**HTML Content:**
- XSS prevention: Sanitize before display
- No script execution
- Validate HTML structure

**Query Inputs:**
- Maximum length: 500 characters
- Special character escaping
- SQL injection prevention (though no SQL DB)

### Code Generation Safety

**Generated Scripts:**
- No eval() or exec() in generated code
- Sandbox execution for validation
- Read-only file system access
- No network calls in validation

### API Security

**Rate Limiting:**
- 100 requests per hour per IP
- 10 requests per minute for generation endpoints

**CORS:**
- Whitelist Streamlit frontend origin
- No wildcard origins

---

## Deployment Architecture

### Development Environment

```yaml
services:
  backend:
    image: python:3.10
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./data:/data
    environment:
      - LLM_PROVIDER=groq
      - GROQ_API_KEY=${GROQ_API_KEY}
    command: uvicorn app.main:app --reload --host 0.0.0.0
  
  frontend:
    image: python:3.10
    ports:
      - "8501:8501"
    volumes:
      - ./frontend:/app
    depends_on:
      - backend
    command: streamlit run app.py
```

### Production Considerations

**Scalability:**
- Use Redis for caching embeddings
- Implement request queuing for heavy operations
- Load balancer for multiple backend instances

**Monitoring:**
- Log aggregation (ELK stack)
- Metrics collection (Prometheus)
- Error tracking (Sentry)

**Backup:**
- Regular vector DB backups
- Document storage backups
- Generated script versioning

---

## Performance Targets

| Operation | Target Time | Max Time |
|-----------|-------------|----------|
| Document upload | < 1s | 3s |
| KB build (5 docs) | < 20s | 30s |
| Test case generation | < 15s | 20s |
| Script generation | < 10s | 15s |
| Document retrieval | < 500ms | 1s |

---

## Logging Strategy

### Log Levels

- **DEBUG:** Detailed information for debugging
- **INFO:** General informational messages
- **WARNING:** Warning messages for potential issues
- **ERROR:** Error messages for failures
- **CRITICAL:** Critical issues requiring immediate attention

### Log Format

```python
LOG_FORMAT = (
    "%(asctime)s - %(name)s - %(levelname)s - "
    "%(funcName)s:%(lineno)d - %(message)s"
)
```

### What to Log

1. **All API requests:** Method, endpoint, params
2. **Document processing:** File name, size, chunks created
3. **Vector operations:** Query, results count, latency
4. **LLM calls:** Prompt length, response time, tokens used
5. **Errors:** Full stack trace, context
6. **Performance:** Operation duration, resource usage

---

**End of Design Document**
