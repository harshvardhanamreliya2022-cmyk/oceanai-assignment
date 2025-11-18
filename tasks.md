# Project Tasks
## Autonomous QA Agent for Test Case and Script Generation

**Project Code:** QA-AGENT-2024  
**Duration:** 12 days  
**Last Updated:** November 18, 2025

---

## Table of Contents
1. [Task Overview](#task-overview)
2. [Phase 1: Project Setup](#phase-1-project-setup)
3. [Phase 2: Knowledge Base](#phase-2-knowledge-base)
4. [Phase 3: Test Case Generation](#phase-3-test-case-generation)
5. [Phase 4: Selenium Script Generation](#phase-4-selenium-script-generation)
6. [Phase 5: Testing & Validation](#phase-5-testing--validation)
7. [Phase 6: Documentation & Demo](#phase-6-documentation--demo)
8. [Task Dependencies](#task-dependencies)
9. [Daily Schedule](#daily-schedule)

---

## Task Overview

### Summary Statistics

| Phase | Tasks | Estimated Time | Priority |
|-------|-------|---------------|----------|
| Phase 1: Setup | 12 | 16 hours | P0 |
| Phase 2: Knowledge Base | 15 | 16 hours | P0 |
| Phase 3: Test Generation | 13 | 16 hours | P0 |
| Phase 4: Script Generation | 14 | 16 hours | P0 |
| Phase 5: Testing | 10 | 12 hours | P0 |
| Phase 6: Documentation | 8 | 8 hours | P0 |
| **Total** | **72** | **84 hours** | - |

### Task Status Legend
- 🔴 Not Started
- 🟡 In Progress
- 🟢 Completed
- 🔵 Blocked
- ⚪ Skipped

### Priority Levels
- **P0:** Critical - Must have
- **P1:** High - Should have
- **P2:** Medium - Nice to have
- **P3:** Low - Future enhancement

---

## Phase 1: Project Setup
**Duration:** Days 1-2 (16 hours)  
**Goal:** Establish project structure and core infrastructure

### Task 1.1: Initialize Project Structure
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1 hour  
**Dependencies:** None

**Description:**
Create complete project directory structure with all necessary folders.

**Acceptance Criteria:**
- [ ] Root directory created with proper naming
- [ ] Backend folder structure in place
- [ ] Frontend folder structure in place
- [ ] Data folders created (uploads, vectordb, scripts)
- [ ] Assets folder with samples directory
- [ ] .gitignore file created
- [ ] README.md placeholder created

**Steps:**
1. Create root project directory: `qa-agent/`
2. Create backend structure:
   ```
   backend/
   ├── app/
   │   ├── __init__.py
   │   ├── main.py
   │   ├── config.py
   │   ├── models/
   │   ├── services/
   │   ├── prompts/
   │   └── utils/
   ├── tests/
   └── requirements.txt
   ```
3. Create frontend structure:
   ```
   frontend/
   ├── app.py
   ├── components/
   └── requirements.txt
   ```
4. Create data directories
5. Add .gitignore with Python, IDE, and data exclusions

**Deliverables:**
- Complete folder structure
- Initial .gitignore file

---

### Task 1.2: Setup Python Virtual Environment
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 0.5 hours  
**Dependencies:** Task 1.1

**Acceptance Criteria:**
- [ ] Virtual environment created
- [ ] Python 3.10+ verified
- [ ] venv activated successfully
- [ ] pip upgraded to latest

**Steps:**
1. `python3.10 -m venv venv`
2. Activate: `source venv/bin/activate`
3. Upgrade pip: `pip install --upgrade pip`
4. Verify: `python --version`

---

### Task 1.3: Create Backend Requirements File
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 0.5 hours  
**Dependencies:** Task 1.2

**Acceptance Criteria:**
- [ ] requirements.txt created with all dependencies
- [ ] Versions pinned for stability
- [ ] Dependencies organized by category
- [ ] Comments added for clarity

**Steps:**
1. Create `backend/requirements.txt`
2. Add core dependencies:
   - FastAPI, uvicorn
   - Pydantic, python-multipart
3. Add ML/AI dependencies:
   - chromadb, sentence-transformers
   - langchain, langchain-community
4. Add document processing:
   - unstructured, pymupdf, beautifulsoup4
5. Add LLM clients:
   - groq, openai (for compatibility)
6. Add utilities:
   - python-dotenv, aiofiles

**Deliverables:**
- `backend/requirements.txt` with pinned versions

---

### Task 1.4: Install Backend Dependencies
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 0.5 hours  
**Dependencies:** Task 1.3

**Acceptance Criteria:**
- [ ] All packages installed successfully
- [ ] No dependency conflicts
- [ ] Import tests pass
- [ ] requirements.txt verified

**Steps:**
1. `pip install -r backend/requirements.txt`
2. Test imports: `python -c "import fastapi, chromadb, langchain"`
3. Document any installation issues
4. Update requirements.txt if needed

---

### Task 1.5: Setup FastAPI Application
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 2 hours  
**Dependencies:** Task 1.4

**Acceptance Criteria:**
- [ ] main.py created with FastAPI app
- [ ] CORS middleware configured
- [ ] Health check endpoint working
- [ ] API documentation accessible at /docs
- [ ] Application starts without errors

**Steps:**
1. Create `backend/app/main.py`
2. Initialize FastAPI app:
   ```python
   from fastapi import FastAPI
   from fastapi.middleware.cors import CORSMiddleware
   
   app = FastAPI(
       title="QA Agent API",
       version="1.0.0",
       description="Autonomous QA test generation system"
   )
   ```
3. Configure CORS for Streamlit
4. Add health check endpoint:
   ```python
   @app.get("/health")
   async def health_check():
       return {"status": "healthy", "timestamp": datetime.now()}
   ```
5. Test server: `uvicorn app.main:app --reload`
6. Verify /docs endpoint

**Deliverables:**
- Working FastAPI application
- Health check endpoint
- Auto-generated API docs

---

### Task 1.6: Create Configuration Management
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1 hour  
**Dependencies:** Task 1.5

**Acceptance Criteria:**
- [ ] config.py created with Settings class
- [ ] Environment variables loaded from .env
- [ ] Default values set for all settings
- [ ] Configuration validation working

**Steps:**
1. Create `backend/app/config.py`
2. Use Pydantic BaseSettings:
   ```python
   from pydantic_settings import BaseSettings
   
   class Settings(BaseSettings):
       # LLM Settings
       llm_provider: str = "groq"
       groq_api_key: str = ""
       ollama_base_url: str = "http://localhost:11434"
       
       # Vector DB Settings
       vectordb_path: str = "./data/vectordb"
       embedding_model: str = "all-MiniLM-L6-v2"
       
       # App Settings
       upload_dir: str = "./data/uploads"
       scripts_dir: str = "./data/scripts"
       
       class Config:
           env_file = ".env"
   
   settings = Settings()
   ```
3. Create `.env.example`
4. Add to .gitignore: `.env`

**Deliverables:**
- config.py with Settings class
- .env.example file

---

### Task 1.7: Setup Data Models
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 2 hours  
**Dependencies:** Task 1.6

**Acceptance Criteria:**
- [ ] All Pydantic models created
- [ ] Dataclasses for internal use created
- [ ] Type hints on all fields
- [ ] Validation rules implemented
- [ ] Example instances work

**Steps:**
1. Create `backend/app/models/schemas.py`
2. Define Pydantic models for API:
   - UploadDocumentRequest
   - BuildKBRequest, BuildKBResponse
   - GenerateTestCasesRequest, GenerateTestCasesResponse
   - GenerateScriptRequest, GenerateScriptResponse
3. Create `backend/app/models/test_case.py`
4. Define dataclasses:
   - TestCase, TestData
   - DocumentChunk, RetrievedChunk
   - SeleniumScript, ScriptValidation
5. Add validators and properties
6. Write simple tests for models

**Deliverables:**
- Complete data models
- Model validation working

---

### Task 1.8: Create Directory Structure Service
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1 hour  
**Dependencies:** Task 1.6

**Acceptance Criteria:**
- [ ] Utility function to create directories
- [ ] All data directories created on startup
- [ ] Permissions set correctly
- [ ] Error handling for directory creation

**Steps:**
1. Create `backend/app/utils/filesystem.py`
2. Implement directory creation:
   ```python
   def ensure_directories():
       dirs = [
           settings.upload_dir,
           settings.scripts_dir,
           settings.vectordb_path,
           "./data/logs"
       ]
       for dir_path in dirs:
           Path(dir_path).mkdir(parents=True, exist_ok=True)
   ```
3. Call in main.py on startup
4. Add logging for directory creation

**Deliverables:**
- Directory management utility
- Auto-creation on app startup

---

### Task 1.9: Setup Logging
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1 hour  
**Dependencies:** Task 1.8

**Acceptance Criteria:**
- [ ] Logging configured with proper format
- [ ] File and console handlers
- [ ] Log levels configurable
- [ ] Logs written to file
- [ ] Log rotation configured

**Steps:**
1. Create `backend/app/utils/logger.py`
2. Configure logging:
   ```python
   import logging
   from logging.handlers import RotatingFileHandler
   
   def setup_logging():
       logger = logging.getLogger("qa_agent")
       logger.setLevel(logging.INFO)
       
       # File handler
       file_handler = RotatingFileHandler(
           "./data/logs/app.log",
           maxBytes=10485760,  # 10MB
           backupCount=5
       )
       
       # Console handler
       console_handler = logging.StreamHandler()
       
       # Format
       formatter = logging.Formatter(
           '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
       )
       file_handler.setFormatter(formatter)
       console_handler.setFormatter(formatter)
       
       logger.addHandler(file_handler)
       logger.addHandler(console_handler)
       
       return logger
   ```
3. Initialize in main.py
4. Add logging to all major functions

**Deliverables:**
- Logging configuration
- Log file creation

---

### Task 1.10: Create Frontend Requirements
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 0.5 hours  
**Dependencies:** Task 1.2

**Acceptance Criteria:**
- [ ] frontend/requirements.txt created
- [ ] All frontend dependencies listed
- [ ] Versions compatible with backend

**Steps:**
1. Create `frontend/requirements.txt`
2. Add dependencies:
   ```
   streamlit==1.29.0
   requests==2.31.0
   pandas==2.1.4
   ```
3. Install: `pip install -r frontend/requirements.txt`

**Deliverables:**
- frontend/requirements.txt

---

### Task 1.11: Create Basic Streamlit App
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 2 hours  
**Dependencies:** Task 1.10

**Acceptance Criteria:**
- [ ] app.py created
- [ ] Basic UI layout implemented
- [ ] Can connect to backend
- [ ] Streamlit app runs without errors

**Steps:**
1. Create `frontend/app.py`
2. Basic structure:
   ```python
   import streamlit as st
   import requests
   
   st.set_page_config(
       page_title="QA Agent",
       page_icon="🤖",
       layout="wide"
   )
   
   st.title("🤖 Autonomous QA Agent")
   st.markdown("Generate test cases and Selenium scripts from documentation")
   
   # Sidebar
   with st.sidebar:
       st.header("Configuration")
       api_url = st.text_input("Backend URL", "http://localhost:8000")
   
   # Main sections
   tab1, tab2, tab3 = st.tabs([
       "📄 Documents", 
       "🧪 Test Cases", 
       "⚙️ Scripts"
   ])
   ```
3. Test connection to backend
4. Add basic styling

**Deliverables:**
- Basic Streamlit application
- Tab structure

---

### Task 1.12: Create Sample Project Assets
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 3 hours  
**Dependencies:** Task 1.1

**Acceptance Criteria:**
- [ ] checkout.html created with all features
- [ ] product_specs.md created
- [ ] ui_ux_guide.txt created
- [ ] api_endpoints.json created
- [ ] All documents contain relevant info
- [ ] HTML is valid and functional

**Steps:**
1. Create `assets/checkout.html` with:
   - Product list (2-3 items)
   - Add to Cart buttons
   - Cart summary section
   - Discount code input
   - User details form (Name, Email, Address)
   - Form validation
   - Shipping method radio buttons
   - Payment method radio buttons
   - Pay Now button
   
2. Create `assets/support_docs/product_specs.md`:
   ```markdown
   # E-Shop Product Specifications
   
   ## Discount Codes
   - SAVE15: Applies 15% discount to total
   - FIRST10: Applies 10% discount for first-time users
   - WELCOME5: Applies 5% discount (always valid)
   
   ## Shipping Options
   - Standard: Free shipping (5-7 business days)
   - Express: $10 shipping (1-2 business days)
   
   ## Products
   ...
   ```

3. Create `assets/support_docs/ui_ux_guide.txt`
4. Create `assets/support_docs/api_endpoints.json`
5. Validate HTML in browser
6. Test all interactive elements

**Deliverables:**
- Complete checkout.html
- 3-5 support documents
- All assets in proper location

---

## Phase 2: Knowledge Base
**Duration:** Days 3-4 (16 hours)  
**Goal:** Build document processing and vector storage system

### Task 2.1: Create Document Parser Interface
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1 hour  
**Dependencies:** Task 1.7

**Acceptance Criteria:**
- [ ] Abstract ParserInterface created
- [ ] Common parsing utilities
- [ ] Error handling base class
- [ ] File type detection utility

**Steps:**
1. Create `backend/app/services/parsers.py`
2. Define abstract interface:
   ```python
   from abc import ABC, abstractmethod
   
   class ParserInterface(ABC):
       @abstractmethod
       def parse(self, file_path: str) -> str:
           pass
       
       @abstractmethod
       def validate(self, file_path: str) -> bool:
           pass
   ```
3. Add file type detection
4. Create ParserError exception class

**Deliverables:**
- Parser interface
- File type detection

---

### Task 2.2: Implement Markdown Parser
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 0.5 hours  
**Dependencies:** Task 2.1

**Acceptance Criteria:**
- [ ] Can parse .md files
- [ ] Preserves structure
- [ ] Handles code blocks
- [ ] Returns plain text

**Steps:**
1. Implement MarkdownParser class
2. Use markdown library
3. Test with product_specs.md
4. Handle edge cases

**Deliverables:**
- Working Markdown parser

---

### Task 2.3: Implement Text Parser
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 0.5 hours  
**Dependencies:** Task 2.1

**Acceptance Criteria:**
- [ ] Can parse .txt files
- [ ] Handles different encodings
- [ ] Returns clean text

**Steps:**
1. Implement TextParser class
2. Handle UTF-8, ASCII encodings
3. Test with ui_ux_guide.txt

**Deliverables:**
- Working text parser

---

### Task 2.4: Implement JSON Parser
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 0.5 hours  
**Dependencies:** Task 2.1

**Acceptance Criteria:**
- [ ] Can parse .json files
- [ ] Converts to readable text
- [ ] Preserves structure in text

**Steps:**
1. Implement JSONParser class
2. Convert JSON to formatted text
3. Test with api_endpoints.json

**Deliverables:**
- Working JSON parser

---

### Task 2.5: Implement HTML Parser
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1 hour  
**Dependencies:** Task 2.1

**Acceptance Criteria:**
- [ ] Can parse HTML files
- [ ] Extracts text content
- [ ] Preserves structural info
- [ ] Extracts element details

**Steps:**
1. Implement HTMLParser class
2. Use BeautifulSoup
3. Extract text and structure
4. Create element inventory

**Deliverables:**
- Working HTML parser
- Element extraction

---

### Task 2.6: Implement PDF Parser
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1 hour  
**Dependencies:** Task 2.1

**Acceptance Criteria:**
- [ ] Can parse PDF files
- [ ] Extracts all text
- [ ] Handles multi-page PDFs

**Steps:**
1. Implement PDFParser class
2. Use pymupdf (fitz)
3. Test with sample PDF
4. Handle images gracefully

**Deliverables:**
- Working PDF parser

---

### Task 2.7: Implement Text Chunking
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1.5 hours  
**Dependencies:** Task 2.6

**Acceptance Criteria:**
- [ ] Text split into semantic chunks
- [ ] Overlap between chunks
- [ ] Metadata preserved
- [ ] Configurable chunk size

**Steps:**
1. Create `backend/app/utils/text_chunker.py`
2. Use RecursiveCharacterTextSplitter
3. Configure separators: ["\n\n", "\n", ". ", " "]
4. Set chunk_size=1000, overlap=200
5. Test with various documents
6. Ensure metadata carried forward

**Deliverables:**
- Text chunking utility
- Chunk quality tests

---

### Task 2.8: Create Document Processor Service
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 2 hours  
**Dependencies:** Task 2.7

**Acceptance Criteria:**
- [ ] DocumentProcessor class created
- [ ] Handles all file types
- [ ] Creates DocumentChunk objects
- [ ] Preserves metadata
- [ ] Error handling robust

**Steps:**
1. Create `backend/app/services/document_processor.py`
2. Implement DocumentProcessor class
3. Integrate all parsers
4. Add chunking logic
5. Create metadata structure
6. Test with all document types

**Deliverables:**
- Complete DocumentProcessor service

---

### Task 2.9: Setup ChromaDB
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1 hour  
**Dependencies:** Task 1.4

**Acceptance Criteria:**
- [ ] ChromaDB initialized
- [ ] Persistent storage configured
- [ ] Collection created
- [ ] Basic operations working

**Steps:**
1. Initialize ChromaDB client
2. Configure persistence path
3. Create collection
4. Test add/query operations

**Deliverables:**
- ChromaDB setup
- Test operations passing

---

### Task 2.10: Initialize Embedding Model
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 0.5 hours  
**Dependencies:** Task 2.9

**Acceptance Criteria:**
- [ ] Sentence transformer model loaded
- [ ] Can generate embeddings
- [ ] Embedding dimensions correct (384)
- [ ] Batch processing works

**Steps:**
1. Load 'all-MiniLM-L6-v2'
2. Test embedding generation
3. Verify dimensions
4. Test batch processing

**Deliverables:**
- Working embedding model

---

### Task 2.11: Create Vector Store Service
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 2 hours  
**Dependencies:** Task 2.10

**Acceptance Criteria:**
- [ ] VectorStoreService class created
- [ ] Can add documents
- [ ] Can query documents
- [ ] Can clear collection
- [ ] Metadata filtering works

**Steps:**
1. Create `backend/app/services/vector_store.py`
2. Implement VectorStoreService
3. Methods:
   - create_collection()
   - add_documents()
   - query()
   - clear_collection()
   - get_collection_info()
4. Add error handling
5. Write unit tests

**Deliverables:**
- Complete VectorStoreService

---

### Task 2.12: Create Document Upload API Endpoint
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1.5 hours  
**Dependencies:** Task 2.8

**Acceptance Criteria:**
- [ ] POST /documents/upload endpoint
- [ ] Accepts multipart/form-data
- [ ] Validates file type
- [ ] Saves file to disk
- [ ] Returns document metadata

**Steps:**
1. Add endpoint to main.py
2. Implement file upload handler
3. Validate file type
4. Save to uploads directory
5. Generate document ID
6. Return response

**Deliverables:**
- Document upload endpoint
- File validation

---

### Task 2.13: Create HTML Upload API Endpoint
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1 hour  
**Dependencies:** Task 2.5

**Acceptance Criteria:**
- [ ] POST /html/upload endpoint
- [ ] Accepts file or text
- [ ] Validates HTML
- [ ] Extracts element info
- [ ] Returns HTML metadata

**Steps:**
1. Add endpoint to main.py
2. Support file upload and paste
3. Validate HTML syntax
4. Extract elements (forms, inputs, buttons)
5. Save HTML
6. Return metadata

**Deliverables:**
- HTML upload endpoint

---

### Task 2.14: Create Build Knowledge Base API Endpoint
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 2 hours  
**Dependencies:** Task 2.11, 2.12, 2.13

**Acceptance Criteria:**
- [ ] POST /knowledge-base/build endpoint
- [ ] Processes all documents
- [ ] Creates chunks
- [ ] Generates embeddings
- [ ] Stores in vector DB
- [ ] Returns build summary

**Steps:**
1. Add endpoint to main.py
2. Orchestrate:
   - Load documents
   - Process each document
   - Chunk text
   - Generate embeddings
   - Store in ChromaDB
3. Track progress
4. Return summary
5. Handle errors

**Deliverables:**
- KB build endpoint
- End-to-end document processing

---

### Task 2.15: Create KB Status API Endpoint
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 0.5 hours  
**Dependencies:** Task 2.14

**Acceptance Criteria:**
- [ ] GET /knowledge-base/status endpoint
- [ ] Returns KB statistics
- [ ] Shows document list
- [ ] Indicates build status

**Steps:**
1. Add endpoint
2. Query vector store for stats
3. Return formatted response

**Deliverables:**
- KB status endpoint

---

## Phase 3: Test Case Generation
**Duration:** Days 5-6 (16 hours)  
**Goal:** Implement RAG pipeline and test case generation

### Task 3.1: Setup LLM Client Interface
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1 hour  
**Dependencies:** Task 1.6

**Acceptance Criteria:**
- [ ] Abstract LLMClient created
- [ ] Interface defined
- [ ] Connection validation method

**Steps:**
1. Create `backend/app/services/llm_client.py`
2. Define abstract interface
3. Add connection validation
4. Add error handling

**Deliverables:**
- LLM client interface

---

### Task 3.2: Implement Groq Client
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1 hour  
**Dependencies:** Task 3.1

**Acceptance Criteria:**
- [ ] GroqClient implemented
- [ ] Can generate completions
- [ ] Handles API errors
- [ ] Supports streaming (optional)

**Steps:**
1. Implement GroqClient class
2. Initialize with API key
3. Implement generate() method
4. Add retry logic
5. Test with sample prompts

**Deliverables:**
- Working Groq client

---

### Task 3.3: Implement Ollama Client
**Status:** 🔴 Not Started  
**Priority:** P1  
**Estimate:** 1 hour  
**Dependencies:** Task 3.1

**Acceptance Criteria:**
- [ ] OllamaClient implemented
- [ ] Can generate completions
- [ ] Works with local Ollama

**Steps:**
1. Implement OllamaClient class
2. Use requests library
3. Implement generate() method
4. Test with local Ollama instance

**Deliverables:**
- Working Ollama client

---

### Task 3.4: Create LLM Client Factory
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 0.5 hours  
**Dependencies:** Task 3.2, 3.3

**Acceptance Criteria:**
- [ ] Factory function created
- [ ] Returns correct client based on config
- [ ] Validates configuration
- [ ] Falls back gracefully

**Steps:**
1. Create factory function
2. Check LLM_PROVIDER setting
3. Initialize appropriate client
4. Validate connection
5. Return client

**Deliverables:**
- LLM client factory

---

### Task 3.5: Create Test Case Generation Prompts
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 2 hours  
**Dependencies:** None

**Acceptance Criteria:**
- [ ] Comprehensive prompt template
- [ ] Includes strict grounding rules
- [ ] Specifies output format
- [ ] Provides examples
- [ ] Handles edge cases

**Steps:**
1. Create `backend/app/prompts/test_case_prompts.py`
2. Write detailed prompt template
3. Include:
   - System instructions
   - Grounding rules
   - Context placeholder
   - HTML structure placeholder
   - Output format (JSON)
   - Examples
4. Test prompt with LLM
5. Refine based on outputs

**Deliverables:**
- Test case generation prompt

---

### Task 3.6: Create HTML Element Extractor
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1.5 hours  
**Dependencies:** Task 2.5

**Acceptance Criteria:**
- [ ] Extracts all relevant HTML elements
- [ ] Returns structured data
- [ ] Identifies selectors
- [ ] Groups by element type

**Steps:**
1. Create utility function
2. Parse HTML with BeautifulSoup
3. Extract:
   - IDs
   - Names
   - Buttons
   - Inputs
   - Forms
   - Radio/checkbox groups
4. Return structured dict
5. Test with checkout.html

**Deliverables:**
- HTML element extractor

---

### Task 3.7: Implement RAG Engine Service
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 3 hours  
**Dependencies:** Task 3.4, 3.5, 3.6, 2.11

**Acceptance Criteria:**
- [ ] RAGEngine class created
- [ ] Orchestrates retrieval + generation
- [ ] Builds context-rich prompts
- [ ] Validates grounding
- [ ] Returns structured response

**Steps:**
1. Create `backend/app/services/rag_engine.py`
2. Implement RAGEngine class
3. Methods:
   - generate_test_cases()
   - _build_test_case_prompt()
   - _parse_test_case_response()
   - _validate_grounding()
4. Integrate:
   - Vector store for retrieval
   - LLM client for generation
   - HTML extractor
5. Add error handling
6. Write unit tests

**Deliverables:**
- Complete RAG engine

---

### Task 3.8: Implement JSON Response Parser
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1.5 hours  
**Dependencies:** Task 3.7

**Acceptance Criteria:**
- [ ] Can parse LLM JSON output
- [ ] Handles markdown code blocks
- [ ] Validates JSON structure
- [ ] Creates TestCase objects
- [ ] Error handling for malformed JSON

**Steps:**
1. Create parser function
2. Strip markdown code fences
3. Parse JSON
4. Validate against schema
5. Create TestCase objects
6. Handle parse errors
7. Test with various outputs

**Deliverables:**
- JSON response parser

---

### Task 3.9: Implement Test Case Validation
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1 hour  
**Dependencies:** Task 3.8

**Acceptance Criteria:**
- [ ] Validates test case structure
- [ ] Verifies source documents exist
- [ ] Checks for required fields
- [ ] Warns on low confidence

**Steps:**
1. Create validation function
2. Check all required fields present
3. Verify grounded_in document exists
4. Check test steps are actionable
5. Validate expected results
6. Log warnings

**Deliverables:**
- Test case validator

---

### Task 3.10: Create Test Case Generation API Endpoint
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 2 hours  
**Dependencies:** Task 3.7, 3.8, 3.9

**Acceptance Criteria:**
- [ ] POST /test-cases/generate endpoint
- [ ] Accepts query and parameters
- [ ] Returns test cases with sources
- [ ] Handles errors gracefully
- [ ] Includes generation time

**Steps:**
1. Add endpoint to main.py
2. Accept GenerateTestCasesRequest
3. Call RAG engine
4. Format response
5. Add error handling
6. Log request/response
7. Test with sample queries

**Deliverables:**
- Test case generation endpoint

---

### Task 3.11: Create Streamlit Document Upload UI
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 2 hours  
**Dependencies:** Task 2.12, 2.13, 1.11

**Acceptance Criteria:**
- [ ] File uploader for documents
- [ ] HTML upload/paste area
- [ ] Upload button
- [ ] Shows uploaded files
- [ ] Error messages for failures

**Steps:**
1. Create document upload section
2. Add file_uploader widget
3. Add text_area for HTML paste
4. Implement upload handler
5. Call backend API
6. Display upload status
7. List uploaded documents

**Deliverables:**
- Document upload UI

---

### Task 3.12: Create Streamlit KB Build UI
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1.5 hours  
**Dependencies:** Task 3.11, 2.14

**Acceptance Criteria:**
- [ ] "Build Knowledge Base" button
- [ ] Progress indicator
- [ ] Success/failure message
- [ ] Shows KB statistics
- [ ] Displays document list

**Steps:**
1. Create KB build section
2. Add build button
3. Show spinner during build
4. Call backend API
5. Display results
6. Show KB status
7. Add rebuild option

**Deliverables:**
- KB build UI

---

### Task 3.13: Create Streamlit Test Generation UI
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 2 hours  
**Dependencies:** Task 3.10, 3.12

**Acceptance Criteria:**
- [ ] Query input field
- [ ] Generate button
- [ ] Test case display
- [ ] Source citations visible
- [ ] Expandable test details

**Steps:**
1. Create test generation section
2. Add text_input for query
3. Add example queries
4. Implement generation handler
5. Display test cases in cards
6. Show source documents
7. Make test cases selectable
8. Add filters (positive/negative)

**Deliverables:**
- Test generation UI

---

## Phase 4: Selenium Script Generation
**Duration:** Days 7-8 (16 hours)  
**Goal:** Implement Selenium script generation from test cases

### Task 4.1: Create Selenium Generation Prompts
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 2 hours  
**Dependencies:** None

**Acceptance Criteria:**
- [ ] Comprehensive Selenium prompt
- [ ] Includes best practices
- [ ] Specifies code template
- [ ] Provides selector usage examples
- [ ] Includes error handling patterns

**Steps:**
1. Create `backend/app/prompts/selenium_prompts.py`
2. Write detailed prompt template
3. Include:
   - Selenium expert role
   - Available selectors
   - Test case details
   - Code template
   - Best practices
4. Test with various test cases
5. Refine prompt

**Deliverables:**
- Selenium generation prompt

---

### Task 4.2: Implement Selector Extraction
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 2 hours  
**Dependencies:** Task 2.5

**Acceptance Criteria:**
- [ ] Extracts all HTML selectors
- [ ] Groups by selector type
- [ ] Includes element context
- [ ] Returns structured data
- [ ] Prioritizes ID selectors

**Steps:**
1. Create selector extraction function
2. Parse HTML thoroughly
3. Extract:
   - Element IDs with tags
   - Names with types
   - Button texts
   - Input fields with types
   - Form elements
   - Radio/checkbox groups
4. Create selector priority order
5. Test with checkout.html

**Deliverables:**
- Selector extraction utility

---

### Task 4.3: Create Selenium Generator Service
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 3 hours  
**Dependencies:** Task 4.1, 4.2, 3.4

**Acceptance Criteria:**
- [ ] SeleniumGeneratorService created
- [ ] Generates complete scripts
- [ ] Uses extracted selectors
- [ ] Includes proper structure
- [ ] Adds error handling

**Steps:**
1. Create `backend/app/services/selenium_generator.py`
2. Implement SeleniumGeneratorService
3. Methods:
   - generate_script()
   - _extract_selectors()
   - _build_script_prompt()
   - _clean_code()
4. Integrate LLM client
5. Build context-rich prompts
6. Parse and clean output

**Deliverables:**
- Selenium generator service

---

### Task 4.4: Implement Code Cleaning
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1 hour  
**Dependencies:** Task 4.3

**Acceptance Criteria:**
- [ ] Removes markdown fences
- [ ] Fixes indentation
- [ ] Removes extra whitespace
- [ ] Ensures proper formatting

**Steps:**
1. Create code cleaning function
2. Strip ```python``` markers
3. Normalize indentation
4. Remove trailing spaces
5. Ensure proper line endings
6. Test with various outputs

**Deliverables:**
- Code cleaning utility

---

### Task 4.5: Implement Syntax Validation
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1.5 hours  
**Dependencies:** Task 4.4

**Acceptance Criteria:**
- [ ] Validates Python syntax
- [ ] Checks for required imports
- [ ] Identifies syntax errors
- [ ] Returns validation status

**Steps:**
1. Create validation function
2. Use compile() to check syntax
3. Verify imports present
4. Check for common issues
5. Return detailed report
6. Test with valid/invalid code

**Deliverables:**
- Syntax validator

---

### Task 4.6: Implement Selector Validation
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1 hour  
**Dependencies:** Task 4.5

**Acceptance Criteria:**
- [ ] Finds selectors used in script
- [ ] Validates against available selectors
- [ ] Warns about missing selectors
- [ ] Returns validation report

**Steps:**
1. Create selector validator
2. Parse script for selector usage
3. Extract used selectors
4. Compare with available selectors
5. Generate warnings
6. Return report

**Deliverables:**
- Selector validator

---

### Task 4.7: Create Script Validation Service
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1 hour  
**Dependencies:** Task 4.5, 4.6

**Acceptance Criteria:**
- [ ] Combines all validations
- [ ] Returns comprehensive report
- [ ] Categorizes issues (error/warning)
- [ ] Provides fix suggestions

**Steps:**
1. Create validation orchestrator
2. Run syntax validation
3. Run selector validation
4. Combine results
5. Generate report
6. Add fix suggestions

**Deliverables:**
- Complete validation service

---

### Task 4.8: Create Script Generation API Endpoint
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 2 hours  
**Dependencies:** Task 4.3, 4.7

**Acceptance Criteria:**
- [ ] POST /selenium/generate endpoint
- [ ] Accepts test case ID
- [ ] Returns generated script
- [ ] Includes validation results
- [ ] Provides download filename

**Steps:**
1. Add endpoint to main.py
2. Accept GenerateScriptRequest
3. Retrieve test case
4. Load HTML content
5. Call generator service
6. Validate script
7. Return response
8. Log generation

**Deliverables:**
- Script generation endpoint

---

### Task 4.9: Create Script Download Endpoint
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1 hour  
**Dependencies:** Task 4.8

**Acceptance Criteria:**
- [ ] GET /selenium/download/{script_id}
- [ ] Returns .py file
- [ ] Proper content-type header
- [ ] Filename set correctly

**Steps:**
1. Add download endpoint
2. Retrieve script by ID
3. Set headers
4. Return FileResponse
5. Test download

**Deliverables:**
- Script download endpoint

---

### Task 4.10: Create Streamlit Test Case Selection UI
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1.5 hours  
**Dependencies:** Task 3.13

**Acceptance Criteria:**
- [ ] Can select test case from list
- [ ] Shows selected test details
- [ ] "Generate Script" button
- [ ] Clear selection option

**Steps:**
1. Add test case selection logic
2. Store selected test in session state
3. Highlight selected test
4. Show full test details
5. Add generate button
6. Clear selection option

**Deliverables:**
- Test case selection UI

---

### Task 4.11: Create Streamlit Script Generation UI
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 2 hours  
**Dependencies:** Task 4.10, 4.8

**Acceptance Criteria:**
- [ ] Generate script button
- [ ] Script display with syntax highlighting
- [ ] Validation status shown
- [ ] Download button
- [ ] Copy to clipboard option

**Steps:**
1. Create script generation section
2. Implement generation handler
3. Display script in code block
4. Show validation results
5. Add download button
6. Add copy button
7. Handle errors

**Deliverables:**
- Script generation UI

---

### Task 4.12: Add Script Syntax Highlighting
**Status:** 🔴 Not Started  
**Priority:** P1  
**Estimate:** 1 hour  
**Dependencies:** Task 4.11

**Acceptance Criteria:**
- [ ] Python syntax highlighted
- [ ] Uses appropriate colors
- [ ] Line numbers shown
- [ ] Readable font

**Steps:**
1. Use st.code() with language='python'
2. Configure theme
3. Test display
4. Adjust styling

**Deliverables:**
- Syntax highlighted code display

---

### Task 4.13: Implement Script Storage
**Status:** 🔴 Not Started  
**Priority:** P1  
**Estimate:** 1 hour  
**Dependencies:** Task 4.8

**Acceptance Criteria:**
- [ ] Scripts saved to disk
- [ ] Unique filenames
- [ ] Metadata tracked
- [ ] Can list generated scripts

**Steps:**
1. Save scripts to scripts_dir
2. Generate unique IDs
3. Store metadata
4. Create list endpoint
5. Test storage

**Deliverables:**
- Script storage system

---

### Task 4.14: Add Script Regeneration
**Status:** 🔴 Not Started  
**Priority:** P2  
**Estimate:** 1.5 hours  
**Dependencies:** Task 4.11

**Acceptance Criteria:**
- [ ] Regenerate button available
- [ ] Can provide feedback
- [ ] Previous versions saved
- [ ] Can compare versions

**Steps:**
1. Add regenerate button
2. Optional feedback input
3. Save previous version
4. Generate new version
5. Show comparison
6. Allow version selection

**Deliverables:**
- Script regeneration feature

---

## Phase 5: Testing & Validation
**Duration:** Days 9-10 (12 hours)  
**Goal:** Comprehensive testing and quality assurance

### Task 5.1: Write Unit Tests for Document Processors
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 2 hours  
**Dependencies:** Task 2.8

**Acceptance Criteria:**
- [ ] Tests for all parser types
- [ ] Edge cases covered
- [ ] Error handling tested
- [ ] Coverage > 80%

**Steps:**
1. Create test files
2. Test each parser:
   - Valid inputs
   - Invalid inputs
   - Edge cases
   - Error conditions
3. Test chunking
4. Run coverage report

**Deliverables:**
- Parser unit tests

---

### Task 5.2: Write Unit Tests for Vector Store
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1.5 hours  
**Dependencies:** Task 2.11

**Acceptance Criteria:**
- [ ] Tests for all operations
- [ ] Query accuracy tested
- [ ] Metadata filtering tested
- [ ] Coverage > 80%

**Steps:**
1. Create test file
2. Test operations:
   - Add documents
   - Query
   - Delete
   - Clear
3. Test metadata filters
4. Test edge cases

**Deliverables:**
- Vector store unit tests

---

### Task 5.3: Write Unit Tests for RAG Engine
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 2 hours  
**Dependencies:** Task 3.7

**Acceptance Criteria:**
- [ ] Tests for test generation
- [ ] Mocked LLM responses
- [ ] Grounding validation tested
- [ ] Coverage > 80%

**Steps:**
1. Create test file
2. Mock LLM client
3. Test generation pipeline
4. Test response parsing
5. Test validation

**Deliverables:**
- RAG engine unit tests

---

### Task 5.4: Write Unit Tests for Selenium Generator
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 2 hours  
**Dependencies:** Task 4.3

**Acceptance Criteria:**
- [ ] Tests for script generation
- [ ] Selector extraction tested
- [ ] Validation tested
- [ ] Coverage > 80%

**Steps:**
1. Create test file
2. Mock LLM responses
3. Test selector extraction
4. Test script generation
5. Test validation

**Deliverables:**
- Selenium generator unit tests

---

### Task 5.5: Integration Test: Full Pipeline
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 2 hours  
**Dependencies:** Task 5.1-5.4

**Acceptance Criteria:**
- [ ] Upload → KB → Tests → Script works
- [ ] All steps complete successfully
- [ ] Generated script is valid
- [ ] No errors in pipeline

**Steps:**
1. Create integration test
2. Upload test documents
3. Build KB
4. Generate test cases
5. Generate script
6. Verify output
7. Clean up

**Deliverables:**
- Integration test suite

---

### Task 5.6: Test Generated Scripts with Selenium
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 2 hours  
**Dependencies:** Task 4.8

**Acceptance Criteria:**
- [ ] Can execute generated scripts
- [ ] Scripts interact with HTML correctly
- [ ] Assertions work
- [ ] No runtime errors

**Steps:**
1. Generate multiple scripts
2. Set up Selenium environment
3. Run each script
4. Verify functionality
5. Document any issues
6. Fix common problems

**Deliverables:**
- Script execution tests
- Issue documentation

---

### Task 5.7: UI/UX Testing
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1.5 hours  
**Dependencies:** Task 4.11

**Acceptance Criteria:**
- [ ] All UI elements functional
- [ ] No broken buttons
- [ ] Error messages clear
- [ ] User flow intuitive

**Steps:**
1. Test complete user journey
2. Verify all buttons work
3. Test error scenarios
4. Check responsiveness
5. Verify feedback messages
6. Document issues
7. Fix critical bugs

**Deliverables:**
- UI test report
- Bug fixes

---

### Task 5.8: Performance Testing
**Status:** 🔴 Not Started  
**Priority:** P1  
**Estimate:** 1 hour  
**Dependencies:** Task 5.5

**Acceptance Criteria:**
- [ ] KB build under 30 seconds
- [ ] Test generation under 20 seconds
- [ ] Script generation under 15 seconds
- [ ] No memory leaks

**Steps:**
1. Time all operations
2. Test with various document sizes
3. Monitor memory usage
4. Identify bottlenecks
5. Optimize if needed

**Deliverables:**
- Performance report
- Optimization recommendations

---

### Task 5.9: Error Handling Review
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1 hour  
**Dependencies:** Task 5.7

**Acceptance Criteria:**
- [ ] All errors handled gracefully
- [ ] No uncaught exceptions
- [ ] Error messages helpful
- [ ] System recovers properly

**Steps:**
1. Review error handling
2. Test error scenarios
3. Verify error messages
4. Check logging
5. Improve as needed

**Deliverables:**
- Error handling audit
- Improvements

---

### Task 5.10: Code Quality Review
**Status:** 🔴 Not Started  
**Priority:** P1  
**Estimate:** 1 hour  
**Dependencies:** Task 5.9

**Acceptance Criteria:**
- [ ] Code follows PEP 8
- [ ] No linting errors
- [ ] Type hints present
- [ ] Docstrings complete

**Steps:**
1. Run flake8
2. Run black
3. Run mypy
4. Check docstrings
5. Fix issues

**Deliverables:**
- Clean codebase
- Linting report

---

## Phase 6: Documentation & Demo
**Duration:** Days 11-12 (8 hours)  
**Goal:** Complete documentation and demo video

### Task 6.1: Write README.md
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 2 hours  
**Dependencies:** Task 5.10

**Acceptance Criteria:**
- [ ] Project overview clear
- [ ] Setup instructions complete
- [ ] Usage examples provided
- [ ] Architecture explained
- [ ] Dependencies documented

**Steps:**
1. Write project description
2. Add installation instructions
3. Document configuration
4. Provide usage examples
5. Explain architecture
6. Add screenshots
7. Include troubleshooting

**Deliverables:**
- Comprehensive README.md

---

### Task 6.2: Create API Documentation
**Status:** 🔴 Not Started  
**Priority:** P1  
**Estimate:** 1 hour  
**Dependencies:** Task 6.1

**Acceptance Criteria:**
- [ ] All endpoints documented
- [ ] Request/response examples
- [ ] Error codes explained
- [ ] FastAPI docs enhanced

**Steps:**
1. Review FastAPI auto-docs
2. Add descriptions
3. Add examples
4. Document error codes
5. Export as markdown

**Deliverables:**
- API documentation

---

### Task 6.3: Document Support Files
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 0.5 hours  
**Dependencies:** Task 1.12

**Acceptance Criteria:**
- [ ] Each support document explained
- [ ] Purpose documented
- [ ] Format described
- [ ] Examples provided

**Steps:**
1. Create docs for each file:
   - product_specs.md
   - ui_ux_guide.txt
   - api_endpoints.json
   - checkout.html
2. Explain purpose
3. Show structure
4. Provide examples

**Deliverables:**
- Support document documentation

---

### Task 6.4: Create Setup Script
**Status:** 🔴 Not Started  
**Priority:** P1  
**Estimate:** 1 hour  
**Dependencies:** Task 6.1

**Acceptance Criteria:**
- [ ] Automated setup script
- [ ] Installs dependencies
- [ ] Creates directories
- [ ] Validates environment

**Steps:**
1. Create setup.sh or setup.py
2. Check Python version
3. Create venv
4. Install dependencies
5. Create directories
6. Verify installation

**Deliverables:**
- Setup automation script

---

### Task 6.5: Prepare Demo Assets
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 0.5 hours  
**Dependencies:** Task 1.12

**Acceptance Criteria:**
- [ ] All assets in place
- [ ] Test documents ready
- [ ] HTML file complete
- [ ] System ready to demo

**Steps:**
1. Verify all assets present
2. Check file quality
3. Test with system
4. Prepare backup copies

**Deliverables:**
- Demo-ready assets

---

### Task 6.6: Write Demo Script
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 1 hour  
**Dependencies:** Task 6.5

**Acceptance Criteria:**
- [ ] Step-by-step demo script
- [ ] 5-10 minute duration
- [ ] Covers all features
- [ ] Natural narrative

**Steps:**
1. Outline demo flow
2. Write narrative
3. Time each section
4. Prepare talking points
5. Practice demo

**Deliverables:**
- Demo script

---

### Task 6.7: Record Demo Video
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 2 hours  
**Dependencies:** Task 6.6

**Acceptance Criteria:**
- [ ] 5-10 minute video
- [ ] All features shown
- [ ] Audio clear
- [ ] Screen recording crisp

**Steps:**
1. Set up recording software
2. Test audio/video
3. Record demo following script:
   - Introduction (1 min)
   - Upload documents (1 min)
   - Build KB (1 min)
   - Generate tests (2 min)
   - Select test case (1 min)
   - Generate script (2 min)
   - Show script execution (1 min)
   - Conclusion (1 min)
4. Review recording
5. Edit if needed
6. Export final video

**Deliverables:**
- Demo video (MP4)

---

### Task 6.8: Create Project Archive
**Status:** 🔴 Not Started  
**Priority:** P0  
**Estimate:** 0.5 hours  
**Dependencies:** Task 6.7

**Acceptance Criteria:**
- [ ] All files included
- [ ] Proper structure maintained
- [ ] .git folder excluded
- [ ] Clean archive

**Steps:**
1. Create project archive
2. Exclude unnecessary files
3. Verify completeness
4. Test extraction
5. Create submission package

**Deliverables:**
- Project archive (.zip)

---

## Task Dependencies

### Critical Path
```
1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.7 → 
2.1 → 2.7 → 2.8 → 2.11 → 2.14 → 
3.7 → 3.10 → 3.13 → 
4.3 → 4.8 → 4.11 → 
5.5 → 5.6 → 
6.1 → 6.6 → 6.7 → 6.8
```

### Dependency Graph

```
Phase 1 (Setup)
    ├─ 1.1 Project Structure
    │   ├─ 1.2 Virtual Environment
    │   │   ├─ 1.3 Requirements
    │   │   │   └─ 1.4 Install Dependencies
    │   │   │       └─ 1.5 FastAPI Setup
    │   │   │           ├─ 1.6 Configuration
    │   │   │           │   ├─ 1.7 Data Models
    │   │   │           │   └─ 1.8 Directory Service
    │   │   │           │       └─ 1.9 Logging
    │   │   └─ 1.10 Frontend Requirements
    │   │       └─ 1.11 Streamlit App
    │   └─ 1.12 Sample Assets

Phase 2 (Knowledge Base)
    ├─ 2.1 Parser Interface
    │   ├─ 2.2 Markdown Parser
    │   ├─ 2.3 Text Parser
    │   ├─ 2.4 JSON Parser
    │   ├─ 2.5 HTML Parser
    │   └─ 2.6 PDF Parser
    │       └─ 2.7 Text Chunking
    │           └─ 2.8 Document Processor
    │               └─ 2.12 Upload Endpoint
    ├─ 2.9 ChromaDB Setup
    │   └─ 2.10 Embedding Model
    │       └─ 2.11 Vector Store Service
    │           ├─ 2.14 Build KB Endpoint
    │           └─ 2.15 KB Status Endpoint
    └─ 2.13 HTML Upload Endpoint

Phase 3 (Test Generation)
    ├─ 3.1 LLM Client Interface
    │   ├─ 3.2 Groq Client
    │   └─ 3.3 Ollama Client
    │       └─ 3.4 Client Factory
    ├─ 3.5 Test Prompts
    ├─ 3.6 HTML Extractor
    └─ 3.4, 3.5, 3.6, 2.11 → 3.7 RAG Engine
        ├─ 3.8 JSON Parser
        │   └─ 3.9 Test Validator
        │       └─ 3.10 Generate Endpoint
        │           ├─ 3.11 Upload UI
        │           │   └─ 3.12 KB Build UI
        │           │       └─ 3.13 Test Gen UI
        └─ ...

Phase 4 (Script Generation)
    ├─ 4.1 Selenium Prompts
    ├─ 4.2 Selector Extraction
    └─ 4.1, 4.2, 3.4 → 4.3 Selenium Generator
        ├─ 4.4 Code Cleaning
        │   ├─ 4.5 Syntax Validation
        │   └─ 4.6 Selector Validation
        │       └─ 4.7 Validation Service
        │           ├─ 4.8 Generate Endpoint
        │           │   ├─ 4.9 Download Endpoint
        │           │   ├─ 4.10 Selection UI
        │           │   │   └─ 4.11 Script Gen UI
        │           │   │       └─ 4.12 Syntax Highlighting
        │           │   ├─ 4.13 Script Storage
        │           │   └─ 4.14 Regeneration

Phase 5 (Testing)
    ├─ 5.1 Parser Tests
    ├─ 5.2 Vector Store Tests
    ├─ 5.3 RAG Engine Tests
    ├─ 5.4 Selenium Gen Tests
    └─ 5.1-5.4 → 5.5 Integration Tests
        └─ 5.6 Script Execution Tests
            └─ 5.7 UI/UX Tests
                ├─ 5.8 Performance Tests
                └─ 5.9 Error Handling Review
                    └─ 5.10 Code Quality Review

Phase 6 (Documentation)
    └─ 5.10 → 6.1 README
        ├─ 6.2 API Docs
        ├─ 6.3 Support Docs
        └─ 6.4 Setup Script
            └─ 6.5 Demo Assets
                └─ 6.6 Demo Script
                    └─ 6.7 Demo Video
                        └─ 6.8 Project Archive
```

---

## Daily Schedule

### Day 1 (8 hours)
**Focus:** Project initialization and basic infrastructure

| Time | Task | Description |
|------|------|-------------|
| 0-1h | 1.1-1.4 | Setup project structure and environment |
| 1-3h | 1.5-1.7 | Create FastAPI app and data models |
| 3-4h | 1.8-1.9 | Setup directories and logging |
| 4-5h | 1.10-1.11 | Create basic Streamlit UI |
| 5-8h | 1.12 | Create sample assets (HTML + docs) |

**Deliverables:** Working project structure, basic FastAPI + Streamlit, sample assets

---

### Day 2 (8 hours)
**Focus:** Document processing system

| Time | Task | Description |
|------|------|-------------|
| 0-2h | 2.1-2.6 | Create all document parsers |
| 2-4h | 2.7-2.8 | Implement chunking and processor |
| 4-6h | 2.9-2.11 | Setup ChromaDB and vector store |
| 6-8h | 2.12-2.15 | Create API endpoints for documents |

**Deliverables:** Complete document processing pipeline, vector store working

---

### Day 3 (8 hours)
**Focus:** LLM integration and RAG setup

| Time | Task | Description |
|------|------|-------------|
| 0-2h | 3.1-3.4 | Setup LLM clients |
| 2-4h | 3.5-3.6 | Create prompts and HTML extractor |
| 4-7h | 3.7-3.9 | Implement RAG engine |
| 7-8h | 3.10 | Create test generation endpoint |

**Deliverables:** Working RAG pipeline, test case generation

---

### Day 4 (8 hours)
**Focus:** Test generation UI

| Time | Task | Description |
|------|------|-------------|
| 0-2h | 3.11 | Create document upload UI |
| 2-4h | 3.12 | Create KB build UI |
| 4-8h | 3.13 | Create test generation UI |

**Deliverables:** Complete frontend for test generation

---

### Day 5 (8 hours)
**Focus:** Selenium generation backend

| Time | Task | Description |
|------|------|-------------|
| 0-2h | 4.1-4.2 | Create prompts and selector extraction |
| 2-5h | 4.3 | Implement Selenium generator |
| 5-7h | 4.4-4.7 | Implement validation |
| 7-8h | 4.8-4.9 | Create API endpoints |

**Deliverables:** Working Selenium script generation

---

### Day 6 (8 hours)
**Focus:** Selenium generation UI

| Time | Task | Description |
|------|------|-------------|
| 0-2h | 4.10 | Test case selection UI |
| 2-4h | 4.11 | Script generation UI |
| 4-5h | 4.12 | Add syntax highlighting |
| 5-7h | 4.13-4.14 | Script storage and regeneration |
| 7-8h | Testing and fixes |

**Deliverables:** Complete frontend for script generation

---

### Day 7 (8 hours)
**Focus:** Testing - Unit tests

| Time | Task | Description |
|------|------|-------------|
| 0-2h | 5.1 | Parser unit tests |
| 2-4h | 5.2 | Vector store tests |
| 4-6h | 5.3 | RAG engine tests |
| 6-8h | 5.4 | Selenium generator tests |

**Deliverables:** Comprehensive unit test suite

---

### Day 8 (8 hours)
**Focus:** Testing - Integration and validation

| Time | Task | Description |
|------|------|-------------|
| 0-2h | 5.5 | Integration tests |
| 2-4h | 5.6 | Script execution tests |
| 4-6h | 5.7 | UI/UX testing and fixes |
| 6-7h | 5.8 | Performance testing |
| 7-8h | 5.9-5.10 | Error handling and code review |

**Deliverables:** Fully tested system, all bugs fixed

---

### Day 9 (4 hours)
**Focus:** Documentation

| Time | Task | Description |
|------|------|-------------|
| 0-2h | 6.1 | Write comprehensive README |
| 2-3h | 6.2-6.3 | API and support docs |
| 3-4h | 6.4-6.5 | Setup script and demo prep |

**Deliverables:** Complete documentation

---

### Day 10 (4 hours)
**Focus:** Demo video

| Time | Task | Description |
|------|------|-------------|
| 0-1h | 6.6 | Write demo script |
| 1-3h | 6.7 | Record and edit demo video |
| 3-4h | 6.8 | Create final submission package |

**Deliverables:** Demo video, submission ready

---

## Risk Mitigation

| Risk | Impact | Mitigation | Tasks Affected |
|------|--------|------------|----------------|
| LLM hallucinations | High | Strict prompts, validation | 3.7, 4.3 |
| Script generation errors | High | Multiple validation layers | 4.5-4.7 |
| Vector DB performance | Medium | Optimize chunk size | 2.7, 2.11 |
| API rate limits | Medium | Local Ollama fallback | 3.2, 3.3 |
| Time constraints | High | Focus on P0 tasks first | All |
| Integration issues | Medium | Early integration testing | 5.5 |

---

## Success Metrics

### Quantitative
- [ ] All P0 tasks completed (72 tasks)
- [ ] Test coverage > 70%
- [ ] KB build time < 30 seconds
- [ ] Test generation time < 20 seconds
- [ ] Script generation time < 15 seconds
- [ ] 95% of generated scripts execute successfully

### Qualitative
- [ ] System easy to use (no training needed)
- [ ] Test cases always cite sources
- [ ] Scripts use correct selectors
- [ ] Documentation clear and complete
- [ ] Demo video professional

---

## Notes

### Development Environment Requirements
- Python 3.10+
- 16GB RAM (recommended)
- 10GB disk space
- Chrome/Firefox for Selenium testing
- (Optional) Ollama for local LLM

### External Dependencies
- Groq API key (free tier) OR
- Ollama local installation

### Time Buffers
- 10% buffer built into estimates
- Flexible P2 tasks can be skipped
- Focus on critical path tasks first

---

**Document Status:** Final  
**Total Estimated Effort:** 84 hours over 12 days  
**Last Review:** 2025-11-18
