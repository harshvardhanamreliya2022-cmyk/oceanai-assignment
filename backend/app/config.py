"""
Configuration management for QA Agent.

Uses pydantic-settings for environment variable management
and configuration validation.
"""

from typing import Optional
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Calculate project root (where .env file is located)
# This file is in backend/app/config.py, so project root is 2 levels up
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
ENV_FILE_PATH = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via .env file or environment variables.
    """

    # Application Settings
    app_name: str = "QA Agent"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # LLM Settings
    llm_provider: str = "groq"  # groq, ollama, or openai
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.3-70b-versatile"  # Updated: mixtral-8x7b-32768 decommissioned

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"

    # LLM Generation Parameters
    llm_temperature: float = 0.0  # Deterministic for test generation
    llm_max_tokens: int = 2000

    # Vector Database Settings
    vectordb_path: str = "./data/vectordb"
    vectordb_collection_name: str = "qa_knowledge_base"

    # Embedding Model Settings
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    # Document Processing Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    text_splitter_separators: list = ["\n\n", "\n", ". ", " ", ""]

    # File Upload Settings
    upload_dir: str = "./data/uploads"
    max_upload_size: int = 10485760  # 10MB in bytes
    allowed_document_types: list = ["md", "txt", "json", "html", "pdf"]

    # Generated Scripts Settings
    scripts_dir: str = "./data/scripts"

    # Logging Settings
    log_dir: str = "./data/logs"
    log_level: str = "INFO"
    log_file: str = "app.log"
    log_max_bytes: int = 10485760  # 10MB
    log_backup_count: int = 5

    # RAG Settings
    top_k_retrieval: int = 5  # Number of chunks to retrieve
    min_similarity_score: float = 0.5  # Minimum similarity for retrieval

    # Test Case Generation Settings
    max_test_cases_per_request: int = 50

    # Performance Settings
    request_timeout: int = 300  # 5 minutes for heavy operations

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE_PATH),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get application settings instance.

    Returns:
        Settings: Application configuration
    """
    return settings


def validate_llm_config() -> bool:
    """
    Validate LLM configuration based on selected provider.

    Returns:
        bool: True if configuration is valid

    Raises:
        ValueError: If required configuration is missing
    """
    if settings.llm_provider == "groq":
        if not settings.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable is required when using Groq"
            )
    elif settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required when using OpenAI"
            )
    elif settings.llm_provider == "ollama":
        # Ollama runs locally, no API key needed
        pass
    else:
        raise ValueError(
            f"Invalid LLM provider: {settings.llm_provider}. "
            f"Must be 'groq', 'ollama', or 'openai'"
        )

    return True
