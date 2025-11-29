"""
LLM service with multi-provider support.

Implements adapter pattern for different LLM providers.
"""

from typing import Optional, List, Dict
from abc import ABC, abstractmethod

from groq import Groq

from ..config import settings, validate_llm_config
from ..utils.logger import setup_logging

logger = setup_logging()


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate text from prompt.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0 = deterministic)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        pass


class GroqProvider(LLMProvider):
    """Groq API provider (Mixtral, LLaMA)."""

    def __init__(self, api_key: str, model: str):
        """
        Initialize Groq provider.

        Args:
            api_key: Groq API key
            model: Model name (e.g., mixtral-8x7b-32768)
        """
        self.client = Groq(api_key=api_key)
        self.model = model
        logger.info(f"Initialized Groq provider with model: {model}")

    def generate(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 2000
    ) -> str:
        """Generate text using Groq API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a QA automation expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )

            generated_text = response.choices[0].message.content
            return generated_text

        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            raise


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""

    def __init__(self, base_url: str, model: str):
        """
        Initialize Ollama provider.

        Args:
            base_url: Ollama server URL
            model: Model name (e.g., llama3)
        """
        self.base_url = base_url
        self.model = model
        logger.info(f"Initialized Ollama provider with model: {model}")

    def generate(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 2000
    ) -> str:
        """Generate text using Ollama API."""
        try:
            import requests

            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                timeout=120
            )

            response.raise_for_status()
            result = response.json()

            return result.get("response", "")

        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise


class OpenAIProvider(LLMProvider):
    """OpenAI API provider (GPT-4, GPT-3.5)."""

    def __init__(self, api_key: str, model: str):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model name (e.g., gpt-4-turbo-preview)
        """
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.model = model
            logger.info(f"Initialized OpenAI provider with model: {model}")
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. "
                "Install with: pip install openai"
            )

    def generate(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 2000
    ) -> str:
        """Generate text using OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a QA automation expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )

            generated_text = response.choices[0].message.content
            return generated_text

        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise


class LLMService:
    """
    LLM service with multi-provider support.

    Automatically selects the configured provider (Groq, Ollama, or OpenAI)
    and provides a unified interface for text generation.
    """

    def __init__(self):
        """Initialize LLM service with configured provider."""
        # Validate configuration
        validate_llm_config()

        provider = settings.llm_provider.lower()

        logger.info(f"Initializing LLM service with provider: {provider}")

        # Initialize the appropriate provider
        if provider == "groq":
            self.provider = GroqProvider(
                api_key=settings.groq_api_key,
                model=settings.groq_model
            )
        elif provider == "ollama":
            self.provider = OllamaProvider(
                base_url=settings.ollama_base_url,
                model=settings.ollama_model
            )
        elif provider == "openai":
            self.provider = OpenAIProvider(
                api_key=settings.openai_api_key,
                model=settings.openai_model
            )
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens

        logger.info("LLM service initialized successfully")

    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text from prompt.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature (default from settings)
            max_tokens: Maximum tokens (default from settings)

        Returns:
            Generated text
        """
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens

        logger.debug(f"Generating text (temp={temp}, max_tokens={tokens})")

        try:
            result = self.provider.generate(
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens
            )

            logger.debug(f"Generated {len(result)} characters")
            return result

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise

    def generate_with_context(
        self,
        query: str,
        context_chunks: List[Dict],
        system_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text with retrieved context (RAG).

        Args:
            query: User query
            context_chunks: Retrieved context chunks from knowledge base
            system_prompt: System prompt template
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Returns:
            Generated text with context
        """
        # Format context
        context_text = self._format_context(context_chunks)

        # Build full prompt
        full_prompt = system_prompt.format(
            context=context_text,
            query=query
        )

        return self.generate(
            prompt=full_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )

    def _format_context(self, chunks: List[Dict]) -> str:
        """
        Format retrieved chunks into context string.

        Args:
            chunks: List of chunk dictionaries with text and metadata

        Returns:
            Formatted context string
        """
        if not chunks:
            return "No relevant context found."

        context_parts = []
        for idx, chunk in enumerate(chunks, 1):
            source = chunk.get("source_filename", "Unknown")
            text = chunk.get("text", "")
            similarity = chunk.get("similarity_score", 0.0)

            context_parts.append(
                f"[Source {idx}: {source} (relevance: {similarity:.2f})]\n{text}"
            )

        return "\n\n---\n\n".join(context_parts)

    def get_provider_info(self) -> Dict:
        """
        Get information about the current LLM provider.

        Returns:
            Dictionary with provider details
        """
        return {
            "provider": settings.llm_provider,
            "model": getattr(
                settings,
                f"{settings.llm_provider}_model"
            ),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
