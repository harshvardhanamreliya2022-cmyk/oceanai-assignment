"""
LLM integration module.

Provides adapters for multiple LLM providers:
- Groq (Mixtral, LLaMA)
- Ollama (local models)
- OpenAI (GPT-4, GPT-3.5)
"""

from .llm_service import LLMService
from .prompts import PromptTemplates

__all__ = [
    "LLMService",
    "PromptTemplates",
]
