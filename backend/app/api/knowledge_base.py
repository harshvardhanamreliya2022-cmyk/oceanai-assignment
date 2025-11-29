"""
Knowledge Base API endpoints.

Provides REST API for document management and semantic search.
"""

from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import shutil
from pathlib import Path

from ..knowledge_base import RAGService
from ..config import settings
from ..utils.filesystem import ensure_directories, sanitize_filename
from ..utils.logger import setup_logging

logger = setup_logging()

# Initialize router
router = APIRouter(prefix="/knowledge-base", tags=["Knowledge Base"])

# Initialize RAG service (will be lazily loaded)
_rag_service = None


def get_rag_service() -> RAGService:
    """Get or create RAG service instance."""
    global _rag_service
    if _rag_service is None:
        logger.info("Initializing RAG service for API")
        _rag_service = RAGService()
    return _rag_service


# Request/Response Models
class SearchRequest(BaseModel):
    """Request model for knowledge base search."""
    query: str = Field(..., description="Search query text", min_length=1)
    top_k: int = Field(5, description="Number of results to return", ge=1, le=50)
    min_similarity: float = Field(0.5, description="Minimum similarity score", ge=0.0, le=1.0)
    source_filter: Optional[str] = Field(None, description="Filter by source filename")


class SearchResult(BaseModel):
    """Single search result."""
    text: str
    source_filename: str
    similarity_score: float
    metadata: dict


class SearchResponse(BaseModel):
    """Response model for search results."""
    query: str
    results: List[SearchResult]
    total_results: int


class DocumentInfo(BaseModel):
    """Information about a document in the knowledge base."""
    filename: str
    chunk_count: Optional[int] = None


class KnowledgeBaseStats(BaseModel):
    """Knowledge base statistics."""
    total_chunks: int
    unique_sources: int
    collection_name: str


class UploadResponse(BaseModel):
    """Response for document upload."""
    status: str
    message: str
    filename: str
    chunks_created: Optional[int] = None


# Endpoints

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    overwrite: bool = Query(False, description="Overwrite if document already exists")
):
    """
    Upload and ingest a document into the knowledge base.

    Supported formats: .md, .txt, .json, .html, .pdf

    The document will be:
    1. Validated and saved to disk
    2. Parsed and chunked
    3. Embedded using sentence-transformers
    4. Stored in the vector database

    Returns ingestion statistics.
    """
    try:
        # Validate file type
        file_ext = Path(file.filename).suffix.lstrip('.').lower()
        if file_ext not in settings.allowed_document_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: .{file_ext}. "
                       f"Supported types: {', '.join(settings.allowed_document_types)}"
            )

        # Validate file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        if file_size > settings.max_upload_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.max_upload_size / 1024 / 1024:.1f}MB"
            )

        # Sanitize filename
        safe_filename = sanitize_filename(file.filename)

        # Ensure upload directory exists
        ensure_directories()
        upload_path = Path(settings.upload_dir) / safe_filename

        # Save file
        logger.info(f"Saving uploaded file: {safe_filename}")
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Ingest into knowledge base
        rag_service = get_rag_service()
        result = rag_service.ingest_document(str(upload_path), overwrite=overwrite)

        # Return response
        return UploadResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/search", response_model=SearchResponse)
async def search_knowledge_base(request: SearchRequest):
    """
    Search the knowledge base for relevant content.

    Uses semantic similarity to find the most relevant text chunks
    for the given query.

    Returns ranked results with similarity scores and source metadata.
    """
    try:
        rag_service = get_rag_service()

        results = rag_service.search(
            query=request.query,
            top_k=request.top_k,
            min_similarity=request.min_similarity,
            source_filter=request.source_filter
        )

        # Convert to response model
        search_results = [
            SearchResult(
                text=r["text"],
                source_filename=r["source_filename"],
                similarity_score=r["similarity_score"],
                metadata=r["metadata"]
            )
            for r in results
        ]

        return SearchResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results)
        )

    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/stats", response_model=KnowledgeBaseStats)
async def get_stats():
    """
    Get knowledge base statistics.

    Returns information about the number of documents and chunks stored.
    """
    try:
        rag_service = get_rag_service()
        stats = rag_service.get_knowledge_base_stats()

        return KnowledgeBaseStats(
            total_chunks=stats.get("total_chunks", 0),
            unique_sources=stats.get("unique_sources", 0),
            collection_name=stats.get("collection_name", "unknown")
        )

    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.get("/documents", response_model=List[str])
async def list_documents():
    """
    List all documents in the knowledge base.

    Returns a list of document filenames.
    """
    try:
        rag_service = get_rag_service()
        documents = rag_service.list_documents()

        return documents

    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.delete("/documents/{filename}")
async def delete_document(filename: str):
    """
    Delete a document from the knowledge base.

    Removes all chunks associated with the specified document.
    """
    try:
        rag_service = get_rag_service()
        success = rag_service.delete_document(filename)

        if not success:
            raise HTTPException(status_code=404, detail=f"Document not found: {filename}")

        return JSONResponse(
            content={
                "status": "success",
                "message": f"Document deleted: {filename}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@router.post("/clear")
async def clear_knowledge_base():
    """
    Clear all documents from the knowledge base.

    WARNING: This deletes all stored documents and cannot be undone.
    """
    try:
        rag_service = get_rag_service()
        success = rag_service.clear_knowledge_base()

        if not success:
            raise HTTPException(status_code=500, detail="Failed to clear knowledge base")

        return JSONResponse(
            content={
                "status": "success",
                "message": "Knowledge base cleared successfully"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear knowledge base: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear knowledge base: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint for knowledge base service.

    Returns the status and basic information about the RAG service.
    """
    try:
        rag_service = get_rag_service()
        stats = rag_service.get_knowledge_base_stats()

        return JSONResponse(
            content={
                "status": "healthy",
                "service": "Knowledge Base",
                "total_chunks": stats.get("total_chunks", 0),
                "unique_sources": stats.get("unique_sources", 0)
            }
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "Knowledge Base",
                "error": str(e)
            }
        )
