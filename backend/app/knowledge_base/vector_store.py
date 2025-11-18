"""
Vector store service using ChromaDB.

Provides storage and retrieval of text embeddings for semantic search
in the RAG pipeline.
"""

from typing import List, Dict, Optional, Tuple
import chromadb
from chromadb.config import Settings as ChromaSettings
import numpy as np

from backend.app.config import settings
from backend.app.knowledge_base.text_processor import TextChunk
from backend.app.utils.logger import setup_logging

logger = setup_logging()


class VectorStoreService:
    """
    Manage vector storage and retrieval using ChromaDB.

    Stores text chunks with embeddings and metadata for efficient
    semantic search during RAG retrieval.
    """

    def __init__(
        self,
        collection_name: str = None,
        persist_directory: str = None
    ):
        """
        Initialize vector store with ChromaDB.

        Args:
            collection_name: Name of the collection (default from settings)
            persist_directory: Directory to persist the database (default from settings)
        """
        self.collection_name = collection_name or settings.vectordb_collection_name
        self.persist_directory = persist_directory or settings.vectordb_path

        logger.info(
            f"Initializing ChromaDB - "
            f"collection={self.collection_name}, "
            f"path={self.persist_directory}"
        )

        # Initialize ChromaDB client
        try:
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )

            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )

            logger.info(
                f"ChromaDB initialized - "
                f"collection '{self.collection_name}' ready "
                f"({self.collection.count()} existing documents)"
            )

        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    def add_chunks(
        self,
        chunks: List[TextChunk],
        embeddings: List[np.ndarray]
    ) -> None:
        """
        Add text chunks with embeddings to the vector store.

        Args:
            chunks: List of TextChunk objects
            embeddings: List of embedding vectors (must match chunks order)

        Raises:
            ValueError: If chunks and embeddings lengths don't match
        """
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Chunks count ({len(chunks)}) must match "
                f"embeddings count ({len(embeddings)})"
            )

        if not chunks:
            logger.warning("No chunks to add to vector store")
            return

        # Prepare data for ChromaDB
        ids = [chunk.chunk_id for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        embeddings_list = [emb.tolist() for emb in embeddings]

        # Prepare metadata
        metadatas = []
        for chunk in chunks:
            metadata = {
                "source_filename": chunk.source_filename,
                "chunk_index": chunk.chunk_index,
                **chunk.metadata
            }
            metadatas.append(metadata)

        try:
            logger.info(f"Adding {len(chunks)} chunks to vector store")

            self.collection.add(
                ids=ids,
                embeddings=embeddings_list,
                documents=documents,
                metadatas=metadatas
            )

            logger.info(
                f"Successfully added {len(chunks)} chunks. "
                f"Total documents: {self.collection.count()}"
            )

        except Exception as e:
            logger.error(f"Failed to add chunks to vector store: {e}")
            raise

    def query(
        self,
        query_embedding: np.ndarray,
        n_results: int = 5,
        where_filter: Optional[Dict] = None
    ) -> Tuple[List[str], List[Dict], List[float]]:
        """
        Query the vector store for similar chunks.

        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where_filter: Optional metadata filter (e.g., {"source_filename": "doc.md"})

        Returns:
            Tuple of (documents, metadatas, distances)
        """
        try:
            logger.debug(f"Querying vector store for {n_results} results")

            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=n_results,
                where=where_filter
            )

            # Extract results
            documents = results['documents'][0] if results['documents'] else []
            metadatas = results['metadatas'][0] if results['metadatas'] else []
            distances = results['distances'][0] if results['distances'] else []

            logger.debug(f"Found {len(documents)} results")

            return documents, metadatas, distances

        except Exception as e:
            logger.error(f"Failed to query vector store: {e}")
            raise

    def query_by_text(
        self,
        query_text: str,
        n_results: int = 5,
        where_filter: Optional[Dict] = None
    ) -> Tuple[List[str], List[Dict], List[float]]:
        """
        Query using text (ChromaDB will handle embedding internally).

        Note: This requires ChromaDB's default embedding function.
        For production, use query() with pre-computed embeddings.

        Args:
            query_text: Query text string
            n_results: Number of results to return
            where_filter: Optional metadata filter

        Returns:
            Tuple of (documents, metadatas, distances)
        """
        try:
            logger.debug(f"Querying vector store with text: '{query_text[:50]}...'")

            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where_filter
            )

            documents = results['documents'][0] if results['documents'] else []
            metadatas = results['metadatas'][0] if results['metadatas'] else []
            distances = results['distances'][0] if results['distances'] else []

            logger.debug(f"Found {len(documents)} results")

            return documents, metadatas, distances

        except Exception as e:
            logger.error(f"Failed to query vector store by text: {e}")
            raise

    def get_by_id(self, chunk_id: str) -> Optional[Dict]:
        """
        Retrieve a specific chunk by its ID.

        Args:
            chunk_id: Chunk identifier

        Returns:
            Dictionary with chunk data, or None if not found
        """
        try:
            results = self.collection.get(ids=[chunk_id])

            if not results['ids']:
                return None

            return {
                "id": results['ids'][0],
                "document": results['documents'][0],
                "metadata": results['metadatas'][0]
            }

        except Exception as e:
            logger.error(f"Failed to get chunk by ID: {e}")
            return None

    def delete_by_filename(self, filename: str) -> int:
        """
        Delete all chunks from a specific source file.

        Args:
            filename: Source filename to delete

        Returns:
            Number of chunks deleted
        """
        try:
            # Get all chunks from this file
            results = self.collection.get(
                where={"source_filename": filename}
            )

            if not results['ids']:
                logger.info(f"No chunks found for filename: {filename}")
                return 0

            # Delete them
            self.collection.delete(ids=results['ids'])

            count = len(results['ids'])
            logger.info(f"Deleted {count} chunks from {filename}")

            return count

        except Exception as e:
            logger.error(f"Failed to delete chunks by filename: {e}")
            raise

    def clear_collection(self) -> None:
        """
        Clear all documents from the collection.

        WARNING: This deletes all data in the collection.
        """
        try:
            # Delete the collection
            self.client.delete_collection(self.collection_name)

            # Recreate it
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )

            logger.info(f"Cleared collection '{self.collection_name}'")

        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            raise

    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the collection.

        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()

            # Get sample of metadata to understand sources
            sample = self.collection.peek(limit=100)
            sources = set()

            if sample['metadatas']:
                for metadata in sample['metadatas']:
                    if 'source_filename' in metadata:
                        sources.add(metadata['source_filename'])

            stats = {
                "total_chunks": count,
                "unique_sources": len(sources),
                "collection_name": self.collection_name,
                "persist_directory": self.persist_directory
            }

            return stats

        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {}

    def update_chunk(
        self,
        chunk_id: str,
        text: Optional[str] = None,
        embedding: Optional[np.ndarray] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Update an existing chunk.

        Args:
            chunk_id: ID of chunk to update
            text: New text (optional)
            embedding: New embedding (optional)
            metadata: New metadata (optional)

        Returns:
            True if successful, False otherwise
        """
        try:
            update_data = {"ids": [chunk_id]}

            if text is not None:
                update_data["documents"] = [text]

            if embedding is not None:
                update_data["embeddings"] = [embedding.tolist()]

            if metadata is not None:
                update_data["metadatas"] = [metadata]

            self.collection.update(**update_data)

            logger.info(f"Updated chunk: {chunk_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update chunk {chunk_id}: {e}")
            return False

    def search_by_metadata(
        self,
        metadata_filter: Dict,
        limit: int = 100
    ) -> List[Dict]:
        """
        Search for chunks by metadata criteria.

        Args:
            metadata_filter: Metadata filter dictionary
            limit: Maximum number of results

        Returns:
            List of chunk dictionaries
        """
        try:
            results = self.collection.get(
                where=metadata_filter,
                limit=limit
            )

            chunks = []
            for i in range(len(results['ids'])):
                chunks.append({
                    "id": results['ids'][i],
                    "document": results['documents'][i],
                    "metadata": results['metadatas'][i]
                })

            logger.debug(f"Found {len(chunks)} chunks matching metadata filter")

            return chunks

        except Exception as e:
            logger.error(f"Failed to search by metadata: {e}")
            return []
