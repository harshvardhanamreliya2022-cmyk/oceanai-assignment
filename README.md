# Autonomous QA Agent for Test Case and Script Generation

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-planning-yellow.svg)](https://github.com)

> An intelligent, autonomous QA agent that constructs a "testing brain" from project documentation and generates comprehensive test cases and executable Selenium scripts for web applications.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development Roadmap](#development-roadmap)
- [Technology Stack](#technology-stack)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Overview

The **Autonomous QA Agent** is an AI-powered system that automates the creation of test cases and Selenium test scripts by analyzing project documentation. It uses Retrieval-Augmented Generation (RAG) to ensure all generated tests are grounded in actual documentation, eliminating hallucinations and ensuring test accuracy.

### What Problem Does This Solve?

- **Manual Test Writing is Time-Consuming**: QA engineers spend hours writing test cases and Selenium scripts manually
- **Documentation Goes Unused**: Product specs, API docs, and UI guides are often disconnected from test creation
- **Inconsistent Test Coverage**: Manual processes lead to gaps in test coverage
- **Knowledge Silos**: Testing knowledge is locked in individual team members' heads

### How Does This Help?

1. **Upload Documentation**: Product specs, API docs, UI/UX guides, HTML files
2. **Build Knowledge Base**: The system creates a searchable vector database from your documents
3. **Generate Test Cases**: Ask for test cases in natural language, get comprehensive test scenarios
4. **Create Selenium Scripts**: Convert test cases into executable Python Selenium scripts automatically

---

## Key Features

### 1. Intelligent Document Processing
- Supports multiple formats: Markdown, TXT, JSON, HTML, PDF
- Automatic text chunking with semantic boundaries
- Metadata preservation for source attribution

### 2. RAG-Powered Test Generation
- **Grounded Generation**: Every test case cites its source document
- **No Hallucinations**: Only creates tests based on provided documentation
- **Context-Aware**: Uses retrieved documentation context for accurate test creation
- **Positive & Negative Tests**: Generates both happy path and edge case scenarios

### 3. Selenium Script Generation
- **HTML-Aware**: Parses HTML to extract valid selectors (ID, name, CSS, XPath)
- **Best Practices**: Includes explicit waits, error handling, assertions
- **Validation**: Syntax checking and selector verification before delivery
- **Ready to Run**: Generated scripts are immediately executable

### 4. User-Friendly Interface
- **Streamlit Frontend**: Simple, intuitive web interface
- **FastAPI Backend**: RESTful API for all operations
- **Real-time Feedback**: Progress indicators and status updates
- **Download Scripts**: Get .py files ready for your test suite

### 5. Flexible LLM Support
- **Groq** (Recommended): Fast, free tier available
- **Ollama**: Fully local, privacy-preserving option
- **OpenAI**: High-quality outputs (paid)

---

## Architecture

The system follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend (Port 8501)               │
│  [Upload Docs] [Build KB] [Generate Tests] [Generate Scripts]  │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP/REST
┌───────────────────────────▼─────────────────────────────────────┐
│                    FastAPI Backend (Port 8000)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐       │
│  │  Document    │  │  RAG Engine  │  │    Selenium    │       │
│  │  Processor   │  │  (Retrieval  │  │    Generator   │       │
│  │              │  │  + Generate) │  │                │       │
│  └──────────────┘  └──────────────┘  └────────────────┘       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│              ChromaDB Vector Database (Persistent)              │
│  [Document Embeddings] [Metadata] [Similarity Search]          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                      LLM Providers                              │
│      [Groq API]    [Ollama Local]    [OpenAI API]             │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

1. **Document Processor**: Parses documents (MD, TXT, JSON, HTML, PDF), chunks text, preserves metadata
2. **Vector Store**: ChromaDB for embedding storage and semantic search
3. **RAG Engine**: Orchestrates retrieval and generation with strict grounding rules
4. **Selenium Generator**: Extracts HTML selectors and generates executable scripts
5. **LLM Client**: Abstraction layer supporting multiple LLM providers

---

## Project Structure

```
oceanai-assignment/
├── README.md                    # This file
├── requirements.md              # Detailed requirements and user stories
├── design.md                    # System design document
├── tasks.md                     # Development task breakdown
├── .gitignore                   # Git ignore rules
├── .env.example                 # Environment variables template
│
├── backend/                     # FastAPI backend (to be implemented)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI application
│   │   ├── config.py           # Configuration management
│   │   ├── models/             # Data models
│   │   │   ├── schemas.py      # Pydantic models for API
│   │   │   └── test_case.py    # Test case data classes
│   │   ├── services/           # Business logic
│   │   │   ├── document_processor.py
│   │   │   ├── vector_store.py
│   │   │   ├── rag_engine.py
│   │   │   ├── selenium_generator.py
│   │   │   └── llm_client.py
│   │   ├── prompts/            # LLM prompt templates
│   │   │   ├── test_case_prompts.py
│   │   │   └── selenium_prompts.py
│   │   └── utils/              # Utilities
│   │       ├── parsers.py      # Document parsers
│   │       ├── text_chunker.py
│   │       └── logger.py
│   ├── tests/                  # Unit and integration tests
│   └── requirements.txt        # Python dependencies
│
├── frontend/                   # Streamlit frontend (to be implemented)
│   ├── app.py                 # Main Streamlit application
│   ├── components/            # Reusable UI components
│   └── requirements.txt       # Frontend dependencies
│
├── data/                      # Data storage (created at runtime)
│   ├── uploads/              # Uploaded documents
│   ├── vectordb/             # ChromaDB persistent storage
│   ├── scripts/              # Generated Selenium scripts
│   └── logs/                 # Application logs
│
└── assets/                   # Sample files and resources
    ├── checkout.html         # Example HTML file
    └── support_docs/         # Example documentation
        ├── product_specs.md
        ├── ui_ux_guide.txt
        └── api_endpoints.json
```

---

## Prerequisites

Before setting up the project, ensure you have:

### Required
- **Python 3.10 or higher**
  ```bash
  python --version  # Should show 3.10.x or higher
  ```

- **pip** (Python package manager)
  ```bash
  pip --version
  ```

### Optional but Recommended
- **Chrome or Firefox** (for running generated Selenium scripts)
- **ChromeDriver or GeckoDriver** (matching your browser version)
- **Git** (for version control)

### System Requirements
- **RAM**: 8GB minimum, 16GB recommended
- **Disk Space**: 10GB free space
- **OS**: Linux, macOS, or Windows

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/oceanai-assignment.git
cd oceanai-assignment
```

### Step 2: Create Virtual Environment

**On Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Backend Dependencies

```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

**Backend Dependencies** (see `backend/requirements.txt`):
```
# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Vector Database & Embeddings
chromadb==0.4.18
sentence-transformers==2.2.2

# LLM Integration
langchain==0.1.0
langchain-community==0.0.10
groq==0.4.1

# Document Processing
unstructured==0.11.0
pymupdf==1.23.8
beautifulsoup4==4.12.2
markdown==3.5.1

# Utilities
python-dotenv==1.0.0
aiofiles==23.2.1
pydantic==2.5.0
pydantic-settings==2.1.0
```

### Step 4: Install Frontend Dependencies

```bash
cd ../frontend
pip install -r requirements.txt
```

**Frontend Dependencies** (see `frontend/requirements.txt`):
```
streamlit==1.29.0
requests==2.31.0
pandas==2.1.4
```

### Step 5: Install Selenium (for script execution)

```bash
pip install selenium==4.15.2
pytest==7.4.3
```

### Step 6: Install ChromeDriver (for Selenium)

**Option 1: Using webdriver-manager (Recommended)**
```bash
pip install webdriver-manager
```

**Option 2: Manual Installation**
- Download ChromeDriver from [official site](https://chromedriver.chromium.org/)
- Extract and add to PATH

---

## Configuration

### 1. Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```bash
# ==================== LLM Configuration ====================

# LLM Provider (groq, ollama, or openai)
LLM_PROVIDER=groq

# Groq Configuration (Recommended)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=mixtral-8x7b-32768

# Ollama Configuration (Local option)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# OpenAI Configuration (Optional)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# ==================== Vector Database ====================

VECTORDB_PATH=./data/vectordb
EMBEDDING_MODEL=all-MiniLM-L6-v2

# ==================== Application Settings ====================

UPLOAD_DIR=./data/uploads
SCRIPTS_DIR=./data/scripts
LOGS_DIR=./data/logs

# Chunking Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# API Configuration
BACKEND_URL=http://localhost:8000
FRONTEND_PORT=8501
```

### 2. Getting API Keys

#### Groq (Free, Recommended)
1. Visit [https://console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste into `.env` file

#### Ollama (Local, No API Key Needed)
1. Install Ollama: [https://ollama.ai/download](https://ollama.ai/download)
2. Pull a model: `ollama pull llama3`
3. Start Ollama: `ollama serve`
4. Set `LLM_PROVIDER=ollama` in `.env`

#### OpenAI (Paid)
1. Visit [https://platform.openai.com](https://platform.openai.com)
2. Create account and add payment method
3. Generate API key
4. Copy to `.env` file

### 3. Directory Setup

Create necessary directories:

```bash
mkdir -p data/uploads data/vectordb data/scripts data/logs
```

---

## Usage

### Starting the Application

#### 1. Start the Backend Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

Access API documentation at: `http://localhost:8000/docs`

#### 2. Start the Frontend

Open a new terminal:

```bash
cd frontend
streamlit run app.py
```

You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### Workflow

#### Step 1: Upload Documentation

1. Navigate to the **Documents** tab
2. Upload your documentation files:
   - Product specifications (`.md`)
   - UI/UX guidelines (`.txt`)
   - API documentation (`.json`)
   - PDF documents
3. Upload your HTML file (the page you want to test)
4. Verify all files appear in the uploaded documents list

#### Step 2: Build Knowledge Base

1. Click the **"Build Knowledge Base"** button
2. Wait for processing (typically 10-30 seconds)
3. Verify the success message shows:
   - Number of documents processed
   - Number of chunks created
   - Build completion time

#### Step 3: Generate Test Cases

1. Navigate to the **Test Cases** tab
2. Enter your testing query, for example:
   - "Generate test cases for the discount code feature"
   - "Create negative test cases for the checkout form"
   - "Test all payment method validations"
3. Click **"Generate Test Cases"**
4. Review the generated test cases:
   - Each test case shows its source document
   - Test steps are detailed and actionable
   - Expected results are clear

#### Step 4: Generate Selenium Script

1. Navigate to the **Scripts** tab
2. Select a test case from the list
3. Click **"Generate Selenium Script"**
4. Review the generated script:
   - Check syntax highlighting
   - Verify selectors match your HTML
   - Review validation warnings (if any)
5. Click **"Download Script"** to get the `.py` file

#### Step 5: Run the Script

```bash
cd data/scripts
python test_tc_001.py
```

Or using pytest:
```bash
pytest test_tc_001.py -v
```

---

## API Documentation

The backend exposes a RESTful API. Full documentation is available at `http://localhost:8000/docs` when the server is running.

### Key Endpoints

#### Health Check
```http
GET /health
```

#### Upload Document
```http
POST /documents/upload
Content-Type: multipart/form-data
```

#### Build Knowledge Base
```http
POST /knowledge-base/build
Content-Type: application/json

{
  "document_ids": ["doc_1", "doc_2"],
  "html_id": "html_1",
  "chunk_size": 1000,
  "chunk_overlap": 200
}
```

#### Generate Test Cases
```http
POST /test-cases/generate
Content-Type: application/json

{
  "query": "Generate test cases for discount codes",
  "include_negative": true,
  "max_test_cases": 10,
  "top_k_retrieval": 5
}
```

#### Generate Selenium Script
```http
POST /selenium/generate
Content-Type: application/json

{
  "test_case_id": "TC-001",
  "include_assertions": true,
  "include_logging": true
}
```

See [design.md](design.md) for complete API specifications.

---

## Development Roadmap

This project is currently in the **planning phase**. The implementation will follow this roadmap:

### Phase 1: Project Setup (Days 1-2)
- [x] Project structure design
- [x] Requirements documentation
- [x] System design documentation
- [ ] FastAPI application setup
- [ ] Streamlit frontend setup
- [ ] Sample assets creation

### Phase 2: Knowledge Base (Days 3-4)
- [ ] Document parser implementation
- [ ] Text chunking logic
- [ ] ChromaDB integration
- [ ] Embedding generation
- [ ] Vector store operations

### Phase 3: Test Case Generation (Days 5-6)
- [ ] LLM client abstraction
- [ ] RAG engine implementation
- [ ] Test case generation prompts
- [ ] JSON response parsing
- [ ] Grounding validation

### Phase 4: Selenium Script Generation (Days 7-8)
- [ ] HTML selector extraction
- [ ] Selenium generation prompts
- [ ] Script validation
- [ ] Code generation
- [ ] Download functionality

### Phase 5: Testing & Validation (Days 9-10)
- [ ] Unit tests
- [ ] Integration tests
- [ ] Script execution tests
- [ ] UI/UX testing
- [ ] Performance optimization

### Phase 6: Documentation & Demo (Days 11-12)
- [ ] README completion
- [ ] API documentation
- [ ] Demo video creation
- [ ] Project packaging

**Current Status**: ✅ Planning Complete | 🚧 Implementation Pending

---

## Technology Stack

### Backend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **API Framework** | FastAPI | 0.104+ | RESTful API server |
| **Server** | Uvicorn | 0.24+ | ASGI server |
| **Vector DB** | ChromaDB | 0.4.18 | Embedding storage |
| **Embeddings** | Sentence Transformers | 2.2+ | Text vectorization |
| **LLM Framework** | LangChain | 0.1+ | RAG orchestration |
| **LLM Providers** | Groq/Ollama/OpenAI | - | Text generation |

### Frontend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **UI Framework** | Streamlit | 1.29+ | Web interface |
| **HTTP Client** | Requests | 2.31+ | API communication |
| **Data Handling** | Pandas | 2.1+ | Data display |

### Document Processing
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **HTML Parser** | BeautifulSoup4 | 4.12+ | HTML extraction |
| **PDF Parser** | PyMuPDF | 1.23+ | PDF processing |
| **Markdown** | Python-Markdown | 3.5+ | MD processing |
| **Text Splitter** | LangChain | 0.1+ | Semantic chunking |

### Testing & Automation
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Browser Automation** | Selenium | 4.15+ | Script execution |
| **Test Framework** | Pytest | 7.4+ | Test runner |
| **Driver Manager** | webdriver-manager | - | Browser driver |

---

## Contributing

Contributions are welcome! Please follow these guidelines:

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Run tests: `pytest tests/`
5. Commit your changes: `git commit -m "Add your feature"`
6. Push to the branch: `git push origin feature/your-feature-name`
7. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use type hints for all function parameters and returns
- Write docstrings for all public methods
- Add unit tests for new features
- Update documentation as needed

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_rag_engine.py -v
```

---

## Troubleshooting

### Common Issues

#### 1. ChromaDB Import Error

**Error:**
```
ImportError: cannot import name 'PersistentClient' from 'chromadb'
```

**Solution:**
```bash
pip install --upgrade chromadb
```

#### 2. Sentence Transformers Download Fails

**Error:**
```
OSError: Can't load 'all-MiniLM-L6-v2'
```

**Solution:**
Ensure you have internet connectivity for first-time model download. The model will be cached locally after the first download.

#### 3. Groq API Rate Limit

**Error:**
```
RateLimitError: Rate limit exceeded
```

**Solution:**
- Wait a few minutes before retrying
- Switch to Ollama for local processing: Set `LLM_PROVIDER=ollama` in `.env`

#### 4. Selenium Script Fails

**Error:**
```
selenium.common.exceptions.WebDriverException: 'chromedriver' executable needs to be in PATH
```

**Solution:**
```bash
pip install webdriver-manager
```

Then in your script:
```python
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
```

#### 5. FastAPI Port Already in Use

**Error:**
```
ERROR: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --port 8001
```

#### 6. Streamlit Connection Error

**Error:**
```
ConnectionError: Failed to connect to backend
```

**Solution:**
1. Ensure backend is running: `curl http://localhost:8000/health`
2. Check `BACKEND_URL` in frontend configuration
3. Verify no firewall blocking connections

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/yourusername/oceanai-assignment/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/oceanai-assignment/discussions)
- **Email**: your-email@example.com

---

## Performance Benchmarks

Expected performance on a standard development machine (8GB RAM, i5 processor):

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| Document Upload | < 1 second | Per file, up to 10MB |
| Knowledge Base Build | 10-30 seconds | For 5 documents |
| Test Case Generation | 10-20 seconds | For 5-10 test cases |
| Script Generation | 8-15 seconds | Per script |
| Document Retrieval | < 500ms | From vector DB |

---

## Security Considerations

### Data Privacy
- All processing can be done locally using Ollama
- No data is sent to external services (except chosen LLM provider)
- Uploaded documents are stored locally only

### Input Validation
- File type validation (whitelist only)
- File size limits (10MB default)
- HTML sanitization before display
- No execution of user-provided code

### Generated Code Safety
- Syntax validation before delivery
- Sandbox execution for validation
- No eval() or exec() in generated scripts
- Read-only file system access during validation

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **LangChain** for RAG framework
- **ChromaDB** for vector database
- **Groq** for fast LLM inference
- **Streamlit** for rapid UI development
- **FastAPI** for modern Python web framework

---

## Project Status

**Current Phase**: 🟡 Planning & Design Complete

**Next Steps**:
1. Implement backend API (FastAPI)
2. Create document processing pipeline
3. Build RAG engine
4. Develop Selenium generator
5. Create Streamlit frontend
6. Write comprehensive tests
7. Create demo video

---

## Contact

**Project Lead**: Your Name
**Email**: your.email@example.com
**GitHub**: [@yourusername](https://github.com/yourusername)
**Project Link**: [https://github.com/yourusername/oceanai-assignment](https://github.com/yourusername/oceanai-assignment)

---

**Built with ❤️ for automated QA testing**
