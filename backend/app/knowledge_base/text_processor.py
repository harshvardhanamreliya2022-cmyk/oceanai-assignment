"""
Text processing and chunking for knowledge base.

Handles text splitting with overlap to maintain context continuity
and preserve document structure for optimal RAG retrieval.
"""

from typing import List, Dict
from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.app.config import settings
from backend.app.utils.logger import setup_logging

logger = setup_logging()


@dataclass
class TextChunk:
    """
    Represents a chunk of text with source metadata.
    """
    text: str
    chunk_id: str
    source_filename: str
    chunk_index: int
    metadata: Dict[str, str]


class TextProcessor:
    """
    Process and chunk text documents for embedding and storage.

    Uses recursive character-based splitting to maintain semantic coherence
    while keeping chunks within optimal size for embeddings.
    """

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
        separators: List[str] = None
    ):
        """
        Initialize text processor with chunking parameters.

        Args:
            chunk_size: Maximum characters per chunk (default from settings)
            chunk_overlap: Character overlap between chunks (default from settings)
            separators: List of separators for splitting (default from settings)
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self.separators = separators or settings.text_splitter_separators

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators,
            length_function=len,
            is_separator_regex=False,
        )

        logger.info(
            f"TextProcessor initialized - "
            f"chunk_size={self.chunk_size}, "
            f"overlap={self.chunk_overlap}"
        )

    def process_document(
        self,
        content: str,
        filename: str,
        metadata: Dict[str, str]
    ) -> List[TextChunk]:
        """
        Process a document into text chunks.

        Args:
            content: Document content text
            filename: Source filename for metadata
            metadata: Additional metadata to attach to chunks

        Returns:
            List of TextChunk objects
        """
        if not content or not content.strip():
            logger.warning(f"Empty content for document: {filename}")
            return []

        # Clean the text
        cleaned_content = self._clean_text(content)

        # Split into chunks
        text_chunks = self.text_splitter.split_text(cleaned_content)

        logger.info(
            f"Split {filename} into {len(text_chunks)} chunks "
            f"(original: {len(content)} chars)"
        )

        # Create TextChunk objects with metadata
        chunks = []
        for idx, chunk_text in enumerate(text_chunks):
            chunk_id = f"{filename}:chunk_{idx}"

            chunk = TextChunk(
                text=chunk_text,
                chunk_id=chunk_id,
                source_filename=filename,
                chunk_index=idx,
                metadata={
                    **metadata,  # Original document metadata
                    "chunk_count": str(len(text_chunks)),
                    "char_count": str(len(chunk_text)),
                }
            )
            chunks.append(chunk)

        return chunks

    def _clean_text(self, text: str) -> str:
        """
        Clean text content before chunking.

        - Remove excessive whitespace
        - Normalize line breaks
        - Remove control characters

        Args:
            text: Raw text content

        Returns:
            Cleaned text
        """
        # Normalize line breaks
        cleaned = text.replace('\r\n', '\n').replace('\r', '\n')

        # Remove excessive blank lines (more than 2 consecutive)
        lines = cleaned.split('\n')
        result_lines = []
        blank_count = 0

        for line in lines:
            if line.strip():
                result_lines.append(line)
                blank_count = 0
            else:
                blank_count += 1
                if blank_count <= 2:  # Keep up to 2 blank lines
                    result_lines.append(line)

        cleaned = '\n'.join(result_lines)

        # Remove excessive spaces (more than 2 consecutive)
        import re
        cleaned = re.sub(r' {3,}', '  ', cleaned)

        return cleaned.strip()

    def merge_chunks(
        self,
        chunks: List[TextChunk],
        separator: str = "\n\n"
    ) -> str:
        """
        Merge multiple chunks back into a single text.

        Useful for reconstructing context from retrieved chunks.

        Args:
            chunks: List of TextChunk objects to merge
            separator: String to use between chunks

        Returns:
            Merged text content
        """
        if not chunks:
            return ""

        # Sort by chunk index to maintain order
        sorted_chunks = sorted(chunks, key=lambda c: c.chunk_index)

        # Merge text content
        merged = separator.join(chunk.text for chunk in sorted_chunks)

        logger.debug(f"Merged {len(chunks)} chunks into {len(merged)} chars")

        return merged

    def get_chunk_statistics(self, chunks: List[TextChunk]) -> Dict:
        """
        Calculate statistics about chunks.

        Args:
            chunks: List of TextChunk objects

        Returns:
            Dictionary with statistics
        """
        if not chunks:
            return {
                "total_chunks": 0,
                "avg_chunk_size": 0,
                "min_chunk_size": 0,
                "max_chunk_size": 0,
                "total_characters": 0
            }

        chunk_sizes = [len(chunk.text) for chunk in chunks]

        stats = {
            "total_chunks": len(chunks),
            "avg_chunk_size": sum(chunk_sizes) / len(chunk_sizes),
            "min_chunk_size": min(chunk_sizes),
            "max_chunk_size": max(chunk_sizes),
            "total_characters": sum(chunk_sizes)
        }

        return stats

    def process_multiple_documents(
        self,
        documents: List[tuple[str, str, Dict[str, str]]]
    ) -> List[TextChunk]:
        """
        Process multiple documents into chunks.

        Args:
            documents: List of (content, filename, metadata) tuples

        Returns:
            Combined list of all chunks from all documents
        """
        all_chunks = []

        for content, filename, metadata in documents:
            chunks = self.process_document(content, filename, metadata)
            all_chunks.extend(chunks)

        logger.info(
            f"Processed {len(documents)} documents into {len(all_chunks)} total chunks"
        )

        return all_chunks

    def get_chunk_by_id(
        self,
        chunks: List[TextChunk],
        chunk_id: str
    ) -> TextChunk:
        """
        Retrieve a specific chunk by its ID.

        Args:
            chunks: List of chunks to search
            chunk_id: Chunk ID to find

        Returns:
            TextChunk if found, None otherwise
        """
        for chunk in chunks:
            if chunk.chunk_id == chunk_id:
                return chunk

        return None

    def get_chunks_by_filename(
        self,
        chunks: List[TextChunk],
        filename: str
    ) -> List[TextChunk]:
        """
        Retrieve all chunks from a specific source file.

        Args:
            chunks: List of chunks to search
            filename: Source filename to filter by

        Returns:
            List of TextChunk objects from the specified file
        """
        matching_chunks = [
            chunk for chunk in chunks
            if chunk.source_filename == filename
        ]

        return sorted(matching_chunks, key=lambda c: c.chunk_index)
