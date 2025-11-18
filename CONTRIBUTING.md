# Contributing to Autonomous QA Agent

Thank you for your interest in contributing to the Autonomous QA Agent project! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, gender, gender identity and expression, sexual orientation, disability, personal appearance, body size, race, ethnicity, age, religion, or nationality.

### Expected Behavior

- Be respectful and considerate
- Use welcoming and inclusive language
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other contributors

### Unacceptable Behavior

- Harassment, trolling, or insulting comments
- Publishing others' private information
- Other conduct which could reasonably be considered inappropriate

---

## Getting Started

### Prerequisites

1. Python 3.10 or higher
2. Git
3. Familiarity with FastAPI, Streamlit, and LangChain
4. Understanding of RAG (Retrieval-Augmented Generation) concepts

### Setup Development Environment

```bash
# 1. Fork the repository
# 2. Clone your fork
git clone https://github.com/your-username/oceanai-assignment.git
cd oceanai-assignment

# 3. Add upstream remote
git remote add upstream https://github.com/original-repo/oceanai-assignment.git

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 5. Install dependencies
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt

# 6. Install development dependencies
pip install pytest pytest-cov black flake8 mypy isort

# 7. Set up pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

---

## Development Process

### Branching Strategy

We follow a feature branch workflow:

```
main (protected)
  ├── feature/document-parser
  ├── feature/rag-engine
  ├── feature/selenium-generator
  └── bugfix/issue-123
```

### Creating a Feature Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Add your feature"

# Push to your fork
git push origin feature/your-feature-name
```

### Commit Message Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
git commit -m "feat(rag): implement document retrieval with ChromaDB"
git commit -m "fix(parser): handle empty PDF files correctly"
git commit -m "docs(readme): update installation instructions"
git commit -m "test(selenium): add validation tests for script generator"
```

---

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line Length**: Maximum 100 characters
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for strings, single quotes for short identifiers
- **Import Order**: Standard library → Third-party → Local application

### Code Formatting

Use **Black** for automatic formatting:

```bash
# Format all Python files
black backend/ frontend/

# Check formatting without changes
black --check backend/ frontend/
```

### Linting

Use **Flake8** for linting:

```bash
# Run linter
flake8 backend/ frontend/ --max-line-length=100

# With specific configuration
flake8 backend/ --config=.flake8
```

### Type Hints

All functions must include type hints:

```python
# Good
def process_document(file_path: str, metadata: dict) -> List[DocumentChunk]:
    """Process a document and return chunks."""
    pass

# Bad
def process_document(file_path, metadata):
    pass
```

Run **mypy** for type checking:

```bash
mypy backend/ --ignore-missing-imports
```

### Docstrings

Use Google-style docstrings:

```python
def generate_test_cases(
    query: str,
    html_content: str,
    top_k: int = 5
) -> TestCaseResponse:
    """Generate test cases using RAG pipeline.

    Args:
        query: Natural language query for test generation
        html_content: HTML content to analyze
        top_k: Number of documents to retrieve

    Returns:
        TestCaseResponse containing generated test cases and sources

    Raises:
        ValueError: If query is empty
        LLMError: If LLM generation fails

    Example:
        >>> response = generate_test_cases(
        ...     query="Test discount codes",
        ...     html_content="<html>...</html>",
        ...     top_k=5
        ... )
        >>> len(response.test_cases)
        10
    """
    pass
```

---

## Testing Guidelines

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_rag_engine.py -v

# Run tests matching pattern
pytest tests/ -k "test_document" -v
```

### Writing Tests

#### Unit Tests

```python
import pytest
from app.services.document_processor import DocumentProcessor

class TestDocumentProcessor:
    """Test suite for DocumentProcessor."""

    @pytest.fixture
    def processor(self):
        """Create DocumentProcessor instance."""
        return DocumentProcessor()

    def test_process_markdown_file(self, processor):
        """Test processing of markdown files."""
        chunks = processor.process_document(
            file_path="test.md",
            metadata={"source": "test.md"}
        )
        assert len(chunks) > 0
        assert all(chunk.text for chunk in chunks)

    def test_process_invalid_file_raises_error(self, processor):
        """Test that invalid files raise appropriate errors."""
        with pytest.raises(UnsupportedFormatError):
            processor.process_document(
                file_path="test.xyz",
                metadata={"source": "test.xyz"}
            )
```

#### Integration Tests

```python
import pytest
from app.main import app
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

def test_full_workflow(client):
    """Test complete workflow from upload to script generation."""
    # Upload document
    response = client.post(
        "/documents/upload",
        files={"file": ("test.md", b"# Test Document")}
    )
    assert response.status_code == 200
    doc_id = response.json()["document_id"]

    # Build KB
    response = client.post(
        "/knowledge-base/build",
        json={"document_ids": [doc_id]}
    )
    assert response.status_code == 200

    # Generate test cases
    response = client.post(
        "/test-cases/generate",
        json={"query": "Test feature"}
    )
    assert response.status_code == 200
    assert len(response.json()["test_cases"]) > 0
```

### Test Coverage Requirements

- **Minimum Coverage**: 70%
- **Critical Paths**: 90%+ coverage
- All public APIs must have tests
- Edge cases and error conditions must be tested

---

## Pull Request Process

### Before Submitting

1. **Update from upstream:**
   ```bash
   git checkout main
   git pull upstream main
   git checkout feature/your-feature
   git rebase main
   ```

2. **Run all checks:**
   ```bash
   # Format code
   black backend/ frontend/

   # Run linter
   flake8 backend/ frontend/

   # Type checking
   mypy backend/

   # Run tests
   pytest tests/ --cov=app
   ```

3. **Update documentation:**
   - Update README if adding new features
   - Add docstrings to all new functions
   - Update API documentation if endpoints changed

### Submitting Pull Request

1. **Push your branch:**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request on GitHub:**
   - Use a clear, descriptive title
   - Reference any related issues
   - Provide detailed description of changes
   - Include screenshots for UI changes
   - List any breaking changes

3. **PR Template:**
   ```markdown
   ## Description
   Brief description of what this PR does

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Related Issues
   Fixes #123

   ## Testing
   - [ ] Unit tests added/updated
   - [ ] Integration tests added/updated
   - [ ] All tests passing
   - [ ] Manual testing completed

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Comments added for complex code
   - [ ] Documentation updated
   - [ ] No new warnings generated
   - [ ] Tests provide good coverage

   ## Screenshots (if applicable)
   [Add screenshots here]
   ```

### Review Process

- Maintainers will review within 48 hours
- Address all review comments
- Keep PR updated with main branch
- Once approved, maintainer will merge

---

## Reporting Bugs

### Before Reporting

1. Check existing issues
2. Try to reproduce with latest version
3. Collect error messages and logs

### Bug Report Template

```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g. Ubuntu 22.04]
 - Python version: [e.g. 3.10.5]
 - Package versions: [from pip freeze]

**Additional context**
Add any other context about the problem here.

**Logs**
```
Paste relevant logs here
```
```

---

## Suggesting Enhancements

### Enhancement Request Template

```markdown
**Is your feature request related to a problem?**
A clear and concise description of what the problem is.

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features.

**Additional context**
Add any other context or screenshots about the feature request here.

**Implementation ideas (optional)**
If you have ideas about how to implement this, share them here.
```

---

## Project Structure Guidelines

When adding new features, follow the existing project structure:

```
backend/app/
├── models/          # Data models (Pydantic, dataclasses)
├── services/        # Business logic (RAG, generators)
├── prompts/         # LLM prompt templates
├── utils/           # Utility functions (parsers, helpers)
└── main.py          # FastAPI application

tests/
├── unit/            # Unit tests
├── integration/     # Integration tests
└── fixtures/        # Test fixtures and data
```

### Adding New Endpoints

1. Define Pydantic models in `models/schemas.py`
2. Implement business logic in appropriate service
3. Add endpoint to `main.py`
4. Write tests in `tests/`
5. Update API documentation

### Adding New Services

1. Create service file in `services/`
2. Define clear interface (abstract class if needed)
3. Add comprehensive docstrings
4. Write unit tests
5. Update README if user-facing

---

## Questions?

- **GitHub Discussions**: For general questions
- **GitHub Issues**: For bug reports and feature requests
- **Email**: your-email@example.com

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Autonomous QA Agent!** 🚀
