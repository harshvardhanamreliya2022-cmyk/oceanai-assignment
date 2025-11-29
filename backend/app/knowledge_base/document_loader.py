"""
Document loader for multiple file formats.

Supports: Markdown (.md), Text (.txt), JSON (.json), HTML (.html), PDF (.pdf)
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import markdown

from ..utils.logger import setup_logging

logger = setup_logging()


@dataclass
class Document:
    """
    Represents a loaded document with content and metadata.
    """
    content: str
    filename: str
    file_type: str
    metadata: Dict[str, str]


class DocumentLoader:
    """
    Load and parse documents from various file formats.

    Supported formats:
    - Markdown (.md)
    - Plain text (.txt)
    - JSON (.json)
    - HTML (.html)
    - PDF (.pdf)
    """

    SUPPORTED_FORMATS = ["md", "txt", "json", "html", "pdf"]

    def __init__(self):
        """Initialize the document loader."""
        logger.info("DocumentLoader initialized")

    def load_document(self, file_path: str) -> Document:
        """
        Load a document from file path.

        Args:
            file_path: Path to the document file

        Returns:
            Document object with content and metadata

        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file does not exist
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_extension = path.suffix.lstrip('.').lower()

        if file_extension not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported file format: .{file_extension}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        logger.info(f"Loading document: {path.name} (type: {file_extension})")

        # Route to appropriate loader based on file type
        loaders = {
            "md": self._load_markdown,
            "txt": self._load_text,
            "json": self._load_json,
            "html": self._load_html,
            "pdf": self._load_pdf,
        }

        loader_func = loaders[file_extension]
        content, metadata = loader_func(path)

        document = Document(
            content=content,
            filename=path.name,
            file_type=file_extension,
            metadata=metadata
        )

        logger.info(f"Loaded document: {path.name} ({len(content)} chars)")
        return document

    def _load_markdown(self, path: Path) -> tuple[str, Dict[str, str]]:
        """
        Load Markdown file and convert to plain text.

        Args:
            path: Path to markdown file

        Returns:
            Tuple of (content, metadata)
        """
        with open(path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Convert markdown to HTML then to plain text for better structure preservation
        html = markdown.markdown(md_content)
        soup = BeautifulSoup(html, 'html.parser')
        text_content = soup.get_text(separator='\n', strip=True)

        # Also keep the raw markdown as it may be useful for some contexts
        # For now, we'll use the plain text version

        metadata = {
            "source_type": "markdown",
            "original_format": "md"
        }

        return text_content, metadata

    def _load_text(self, path: Path) -> tuple[str, Dict[str, str]]:
        """
        Load plain text file.

        Args:
            path: Path to text file

        Returns:
            Tuple of (content, metadata)
        """
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        metadata = {
            "source_type": "text",
            "original_format": "txt"
        }

        return content, metadata

    def _load_json(self, path: Path) -> tuple[str, Dict[str, str]]:
        """
        Load JSON file and convert to structured text.

        For API endpoint documentation and structured data.

        Args:
            path: Path to JSON file

        Returns:
            Tuple of (content, metadata)
        """
        with open(path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        # Convert JSON to readable text format
        content = self._json_to_text(json_data)

        metadata = {
            "source_type": "json",
            "original_format": "json"
        }

        return content, metadata

    def _json_to_text(self, data, indent=0) -> str:
        """
        Convert JSON data to readable text format.

        This preserves structure while making it searchable by the RAG system.

        Args:
            data: JSON data (dict, list, or primitive)
            indent: Current indentation level

        Returns:
            Formatted text representation
        """
        lines = []
        prefix = "  " * indent

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"{prefix}{key}:")
                    lines.append(self._json_to_text(value, indent + 1))
                else:
                    lines.append(f"{prefix}{key}: {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    lines.append(f"{prefix}- Item {i + 1}:")
                    lines.append(self._json_to_text(item, indent + 1))
                else:
                    lines.append(f"{prefix}- {item}")
        else:
            lines.append(f"{prefix}{data}")

        return "\n".join(lines)

    def _load_html(self, path: Path) -> tuple[str, Dict[str, str]]:
        """
        Load HTML file and extract text content.

        Preserves semantic structure while removing HTML tags.

        Args:
            path: Path to HTML file

        Returns:
            Tuple of (content, metadata)
        """
        with open(path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Extract text with structure preservation
        text_content = soup.get_text(separator='\n', strip=True)

        # Also extract title if present
        title = soup.find('title')
        title_text = title.get_text() if title else path.stem

        metadata = {
            "source_type": "html",
            "original_format": "html",
            "title": title_text
        }

        return text_content, metadata

    def _load_pdf(self, path: Path) -> tuple[str, Dict[str, str]]:
        """
        Load PDF file and extract text content.

        Uses PyMuPDF for text extraction.

        Args:
            path: Path to PDF file

        Returns:
            Tuple of (content, metadata)
        """
        doc = fitz.open(path)

        # Extract text from all pages
        pages = []
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text()
            if text.strip():  # Only add non-empty pages
                pages.append(f"--- Page {page_num} ---\n{text}")

        content = "\n\n".join(pages)

        # Extract PDF metadata
        pdf_metadata = doc.metadata

        metadata = {
            "source_type": "pdf",
            "original_format": "pdf",
            "page_count": str(len(doc)),
            "title": pdf_metadata.get("title", ""),
            "author": pdf_metadata.get("author", ""),
        }

        doc.close()

        return content, metadata

    def load_multiple(self, file_paths: List[str]) -> List[Document]:
        """
        Load multiple documents from a list of file paths.

        Args:
            file_paths: List of paths to document files

        Returns:
            List of Document objects
        """
        documents = []

        for file_path in file_paths:
            try:
                doc = self.load_document(file_path)
                documents.append(doc)
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
                # Continue with other files

        logger.info(f"Loaded {len(documents)}/{len(file_paths)} documents successfully")
        return documents

    def load_from_directory(
        self,
        directory: str,
        recursive: bool = False,
        file_types: Optional[List[str]] = None
    ) -> List[Document]:
        """
        Load all supported documents from a directory.

        Args:
            directory: Path to directory
            recursive: Whether to search subdirectories
            file_types: Optional list of file types to load (e.g., ['md', 'txt'])
                       If None, loads all supported types

        Returns:
            List of Document objects
        """
        dir_path = Path(directory)

        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not dir_path.is_dir():
            raise ValueError(f"Not a directory: {directory}")

        # Determine which file types to load
        types_to_load = file_types if file_types else self.SUPPORTED_FORMATS

        # Find all matching files
        file_paths = []

        if recursive:
            for ext in types_to_load:
                file_paths.extend(dir_path.rglob(f"*.{ext}"))
        else:
            for ext in types_to_load:
                file_paths.extend(dir_path.glob(f"*.{ext}"))

        logger.info(
            f"Found {len(file_paths)} files in {directory} "
            f"(types: {', '.join(types_to_load)})"
        )

        # Load all documents
        return self.load_multiple([str(p) for p in file_paths])
