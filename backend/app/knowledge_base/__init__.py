"""
Knowledge Base module for document processing and RAG.

This module provides functionality for:
- Document loading from multiple formats
- Text chunking and splitting
- Embedding generation
- Vector storage with ChromaDB
- Semantic search and retrieval
"""

from .document_loader import DocumentLoader

__all__ = [
    "DocumentLoader",
]
