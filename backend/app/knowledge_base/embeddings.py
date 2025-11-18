"""
Embedding service using sentence-transformers.

Generates vector embeddings for text chunks to enable semantic search
in the vector database.
"""

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

from backend.app.config import settings
from backend.app.utils.logger import setup_logging

logger = setup_logging()


class EmbeddingService:
    """
    Generate embeddings for text using sentence-transformers.

    Uses all-MiniLM-L6-v2 model by default for efficient embedding generation
    with good performance on semantic similarity tasks.
    """

    def __init__(self, model_name: str = None):
        """
        Initialize embedding service with specified model.

        Args:
            model_name: Name of sentence-transformer model
                       (default from settings: all-MiniLM-L6-v2)
        """
        self.model_name = model_name or settings.embedding_model
        self.dimension = settings.embedding_dimension

        logger.info(f"Loading embedding model: {self.model_name}")

        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(
                f"Embedding model loaded successfully "
                f"(dimension: {self.dimension})"
            )
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.

        Args:
            text: Text string to embed

        Returns:
            Numpy array of embedding vector
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return np.zeros(self.dimension)

        try:
            embedding = self.model.encode(
                text,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            return embedding

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = False
    ) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts in batches.

        More efficient than embedding one at a time for large collections.

        Args:
            texts: List of text strings to embed
            batch_size: Number of texts to process in each batch
            show_progress: Whether to show progress bar

        Returns:
            List of numpy arrays (embeddings)
        """
        if not texts:
            logger.warning("Empty text list provided for batch embedding")
            return []

        # Filter out empty texts
        valid_texts = [text for text in texts if text and text.strip()]

        if len(valid_texts) < len(texts):
            logger.warning(
                f"Filtered {len(texts) - len(valid_texts)} empty texts "
                f"from batch"
            )

        if not valid_texts:
            return [np.zeros(self.dimension) for _ in texts]

        try:
            logger.info(
                f"Generating embeddings for {len(valid_texts)} texts "
                f"(batch_size={batch_size})"
            )

            embeddings = self.model.encode(
                valid_texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True
            )

            logger.info(f"Generated {len(embeddings)} embeddings")

            return list(embeddings)

        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model.

        Returns:
            Embedding dimension (384 for all-MiniLM-L6-v2)
        """
        return self.dimension

    def compute_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score (0-1, higher is more similar)
        """
        # Normalize vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        # Compute cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)

        return float(similarity)

    def find_most_similar(
        self,
        query_embedding: np.ndarray,
        candidate_embeddings: List[np.ndarray],
        top_k: int = 5
    ) -> List[tuple[int, float]]:
        """
        Find the most similar embeddings to a query embedding.

        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: List of candidate embedding vectors
            top_k: Number of top results to return

        Returns:
            List of (index, similarity_score) tuples, sorted by similarity
        """
        if not candidate_embeddings:
            return []

        # Compute similarities for all candidates
        similarities = [
            (idx, self.compute_similarity(query_embedding, emb))
            for idx, emb in enumerate(candidate_embeddings)
        ]

        # Sort by similarity (descending) and take top k
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]

    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a search query.

        Same as embed_text() but provided for clarity in search contexts.

        Args:
            query: Search query string

        Returns:
            Numpy array of embedding vector
        """
        return self.embed_text(query)

    def embed_documents(self, documents: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for a list of documents.

        Same as embed_batch() but provided for clarity in document contexts.

        Args:
            documents: List of document texts

        Returns:
            List of embedding vectors
        """
        return self.embed_batch(documents, show_progress=True)
