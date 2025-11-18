"""
RAG (Retrieval-Augmented Generation) service.

Orchestrates document loading, embedding, storage, and retrieval
for the knowledge base system.
"""

from typing import List, Dict, Optional, Tuple
from pathlib import Path

from backend.app.knowledge_base.document_loader import DocumentLoader, Document
from backend.app.knowledge_base.text_processor import TextProcessor, TextChunk
from backend.app.knowledge_base.embeddings import EmbeddingService
from backend.app.knowledge_base.vector_store import VectorStoreService
from backend.app.config import settings
from backend.app.utils.logger import setup_logging
from backend.app.utils.filesystem import sanitize_filename

logger = setup_logging()


class RAGService:
    """
    Orchestrate the complete RAG pipeline.

    Handles end-to-end workflow:
    1. Document loading and parsing
    2. Text chunking
    3. Embedding generation
    4. Vector storage
    5. Semantic search and retrieval
    """

    def __init__(self):
        """Initialize all RAG components."""
        logger.info("Initializing RAG Service...")

        try:
            self.document_loader = DocumentLoader()
            self.text_processor = TextProcessor()
            self.embedding_service = EmbeddingService()
            self.vector_store = VectorStoreService()

            logger.info("RAG Service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize RAG Service: {e}")
            raise

    def ingest_document(
        self,
        file_path: str,
        overwrite: bool = False
    ) -> Dict:
        """
        Ingest a single document into the knowledge base.

        Complete pipeline: Load -> Chunk -> Embed -> Store

        Args:
            file_path: Path to document file
            overwrite: Whether to overwrite existing document

        Returns:
            Dictionary with ingestion statistics
        """
        logger.info(f"Ingesting document: {file_path}")

        try:
            # Step 1: Load document
            doc = self.document_loader.load_document(file_path)

            # Check if document already exists
            if not overwrite:
                existing = self.vector_store.search_by_metadata(
                    {"source_filename": doc.filename},
                    limit=1
                )
                if existing:
                    logger.warning(f"Document already exists: {doc.filename}")
                    return {
                        "status": "skipped",
                        "message": "Document already exists (use overwrite=True to replace)",
                        "filename": doc.filename
                    }
            else:
                # Delete existing chunks if overwriting
                deleted_count = self.vector_store.delete_by_filename(doc.filename)
                if deleted_count > 0:
                    logger.info(f"Deleted {deleted_count} existing chunks for {doc.filename}")

            # Step 2: Process into chunks
            chunks = self.text_processor.process_document(
                doc.content,
                doc.filename,
                doc.metadata
            )

            if not chunks:
                return {
                    "status": "error",
                    "message": "No chunks generated from document",
                    "filename": doc.filename
                }

            # Step 3: Generate embeddings
            chunk_texts = [chunk.text for chunk in chunks]
            embeddings = self.embedding_service.embed_batch(
                chunk_texts,
                show_progress=True
            )

            # Step 4: Store in vector database
            self.vector_store.add_chunks(chunks, embeddings)

            stats = {
                "status": "success",
                "filename": doc.filename,
                "file_type": doc.file_type,
                "chunks_created": len(chunks),
                "total_characters": sum(len(c.text) for c in chunks),
            }

            logger.info(
                f"Successfully ingested {doc.filename}: "
                f"{stats['chunks_created']} chunks"
            )

            return stats

        except Exception as e:
            logger.error(f"Failed to ingest document {file_path}: {e}")
            return {
                "status": "error",
                "message": str(e),
                "filename": Path(file_path).name
            }

    def ingest_multiple(
        self,
        file_paths: List[str],
        overwrite: bool = False
    ) -> Dict:
        """
        Ingest multiple documents.

        Args:
            file_paths: List of document file paths
            overwrite: Whether to overwrite existing documents

        Returns:
            Dictionary with aggregated statistics
        """
        logger.info(f"Ingesting {len(file_paths)} documents...")

        results = []
        for file_path in file_paths:
            result = self.ingest_document(file_path, overwrite=overwrite)
            results.append(result)

        # Aggregate statistics
        successful = sum(1 for r in results if r['status'] == 'success')
        skipped = sum(1 for r in results if r['status'] == 'skipped')
        failed = sum(1 for r in results if r['status'] == 'error')
        total_chunks = sum(r.get('chunks_created', 0) for r in results)

        summary = {
            "total_documents": len(file_paths),
            "successful": successful,
            "skipped": skipped,
            "failed": failed,
            "total_chunks": total_chunks,
            "results": results
        }

        logger.info(
            f"Ingestion complete: {successful} succeeded, "
            f"{skipped} skipped, {failed} failed"
        )

        return summary

    def ingest_directory(
        self,
        directory: str,
        recursive: bool = False,
        file_types: Optional[List[str]] = None,
        overwrite: bool = False
    ) -> Dict:
        """
        Ingest all documents from a directory.

        Args:
            directory: Directory path
            recursive: Whether to search subdirectories
            file_types: Optional list of file types to include
            overwrite: Whether to overwrite existing documents

        Returns:
            Dictionary with aggregated statistics
        """
        logger.info(f"Ingesting documents from directory: {directory}")

        # Load documents
        docs = self.document_loader.load_from_directory(
            directory,
            recursive=recursive,
            file_types=file_types
        )

        # Extract file paths (we need to reconstruct them)
        # For now, we'll process the already-loaded documents
        return self._ingest_loaded_documents(docs, overwrite=overwrite)

    def _ingest_loaded_documents(
        self,
        documents: List[Document],
        overwrite: bool = False
    ) -> Dict:
        """
        Ingest documents that are already loaded.

        Args:
            documents: List of Document objects
            overwrite: Whether to overwrite existing documents

        Returns:
            Dictionary with statistics
        """
        results = []

        for doc in documents:
            try:
                # Check if exists
                if not overwrite:
                    existing = self.vector_store.search_by_metadata(
                        {"source_filename": doc.filename},
                        limit=1
                    )
                    if existing:
                        results.append({
                            "status": "skipped",
                            "filename": doc.filename
                        })
                        continue
                else:
                    self.vector_store.delete_by_filename(doc.filename)

                # Process and store
                chunks = self.text_processor.process_document(
                    doc.content,
                    doc.filename,
                    doc.metadata
                )

                if chunks:
                    chunk_texts = [chunk.text for chunk in chunks]
                    embeddings = self.embedding_service.embed_batch(chunk_texts)
                    self.vector_store.add_chunks(chunks, embeddings)

                    results.append({
                        "status": "success",
                        "filename": doc.filename,
                        "chunks_created": len(chunks)
                    })
                else:
                    results.append({
                        "status": "error",
                        "filename": doc.filename,
                        "message": "No chunks created"
                    })

            except Exception as e:
                logger.error(f"Failed to ingest {doc.filename}: {e}")
                results.append({
                    "status": "error",
                    "filename": doc.filename,
                    "message": str(e)
                })

        # Aggregate stats
        successful = sum(1 for r in results if r['status'] == 'success')
        skipped = sum(1 for r in results if r['status'] == 'skipped')
        failed = sum(1 for r in results if r['status'] == 'error')
        total_chunks = sum(r.get('chunks_created', 0) for r in results)

        return {
            "total_documents": len(documents),
            "successful": successful,
            "skipped": skipped,
            "failed": failed,
            "total_chunks": total_chunks,
            "results": results
        }

    def search(
        self,
        query: str,
        top_k: int = None,
        min_similarity: float = None,
        source_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Search the knowledge base for relevant chunks.

        Args:
            query: Search query text
            top_k: Number of results to return (default from settings)
            min_similarity: Minimum similarity threshold (default from settings)
            source_filter: Optional source filename to filter by

        Returns:
            List of result dictionaries with text, metadata, and scores
        """
        top_k = top_k or settings.top_k_retrieval
        min_similarity = min_similarity or settings.min_similarity_score

        logger.info(
            f"Searching knowledge base: '{query[:50]}...' "
            f"(top_k={top_k}, min_sim={min_similarity})"
        )

        try:
            # Generate query embedding
            query_embedding = self.embedding_service.embed_query(query)

            # Build metadata filter if needed
            where_filter = None
            if source_filter:
                where_filter = {"source_filename": source_filter}

            # Query vector store
            documents, metadatas, distances = self.vector_store.query(
                query_embedding,
                n_results=top_k,
                where_filter=where_filter
            )

            # Convert distances to similarity scores
            # ChromaDB returns L2 distances, convert to similarity (1 / (1 + distance))
            similarities = [1.0 / (1.0 + d) for d in distances]

            # Filter by minimum similarity
            results = []
            for doc, metadata, sim in zip(documents, metadatas, similarities):
                if sim >= min_similarity:
                    results.append({
                        "text": doc,
                        "metadata": metadata,
                        "similarity_score": sim,
                        "source_filename": metadata.get("source_filename", "unknown")
                    })

            logger.info(
                f"Found {len(results)} results above similarity threshold "
                f"(min={min_similarity})"
            )

            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def get_knowledge_base_stats(self) -> Dict:
        """
        Get statistics about the knowledge base.

        Returns:
            Dictionary with knowledge base statistics
        """
        try:
            stats = self.vector_store.get_collection_stats()

            logger.debug(f"Knowledge base stats: {stats}")

            return stats

        except Exception as e:
            logger.error(f"Failed to get knowledge base stats: {e}")
            return {}

    def delete_document(self, filename: str) -> bool:
        """
        Delete a document from the knowledge base.

        Args:
            filename: Name of file to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            count = self.vector_store.delete_by_filename(filename)

            if count > 0:
                logger.info(f"Deleted document: {filename} ({count} chunks)")
                return True
            else:
                logger.warning(f"Document not found: {filename}")
                return False

        except Exception as e:
            logger.error(f"Failed to delete document {filename}: {e}")
            return False

    def clear_knowledge_base(self) -> bool:
        """
        Clear all documents from the knowledge base.

        WARNING: This deletes all data.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.vector_store.clear_collection()
            logger.info("Knowledge base cleared")
            return True

        except Exception as e:
            logger.error(f"Failed to clear knowledge base: {e}")
            return False

    def list_documents(self) -> List[str]:
        """
        List all documents in the knowledge base.

        Returns:
            List of document filenames
        """
        try:
            # Get sample to find all unique sources
            stats = self.vector_store.get_collection_stats()
            total = stats.get('total_chunks', 0)

            if total == 0:
                return []

            # Get all chunks to extract unique filenames
            # This could be optimized with metadata-only queries
            all_chunks = self.vector_store.search_by_metadata(
                metadata_filter={},  # No filter = all
                limit=total
            )

            filenames = set()
            for chunk in all_chunks:
                filename = chunk['metadata'].get('source_filename')
                if filename:
                    filenames.add(filename)

            return sorted(list(filenames))

        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            return []
