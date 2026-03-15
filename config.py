"""
Configuration Management
Centralized configuration for the Legal Document Q&A Assistant
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class LLMConfig:
    """LLM configuration settings."""
    default_model: str = "llama-3.3-70b-versatile"  # Groq
    fallback_model: str = "gpt-4o"  # OpenAI fallback
    temperature: float = 0.0
    max_tokens: int = 2048
    use_groq: bool = True  # Primary LLM provider


@dataclass
class EmbeddingConfig:
    """Embedding configuration settings."""
    text_model: str = "models/gemini-embedding-001"
    multimodal_model: str = "models/gemini-embedding-2-preview"


@dataclass
class DocumentConfig:
    """Document processing configuration."""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    enable_ocr: bool = True
    max_pages: int = 50


@dataclass
class RetrievalConfig:
    """Retrieval configuration settings."""
    top_k: int = 5
    rerank_top_n: int = 3
    quality_threshold: float = 0.3
    max_retries: int = 2
    reranker_type: str = "cohere"  # "cohere" or "flashrank"


@dataclass
class QdrantConfig:
    """Qdrant vector store configuration."""
    collection_name: str = "legal_docs"
    location: str = ":memory:"  # ":memory:" for in-memory, or path/URL
    url: Optional[str] = None
    api_key: Optional[str] = None


class Config:
    """Main configuration class."""

    def __init__(self):
        self.llm = LLMConfig(
            default_model=os.getenv("DEFAULT_LLM_MODEL", "llama-3.3-70b-versatile"),
            use_groq=os.getenv("USE_GROQ", "true").lower() == "true",
        )

        self.embedding = EmbeddingConfig(
            text_model=os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001"),
        )

        self.document = DocumentConfig(
            chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),
            enable_ocr=os.getenv("ENABLE_OCR", "true").lower() == "true",
        )

        self.retrieval = RetrievalConfig()

        self.qdrant = QdrantConfig(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
        )

    @property
    def openai_api_key(self) -> Optional[str]:
        return os.getenv("OPENAI_API_KEY")

    @property
    def google_api_key(self) -> Optional[str]:
        return os.getenv("GOOGLE_API_KEY")

    @property
    def llama_cloud_api_key(self) -> Optional[str]:
        return os.getenv("LLAMA_CLOUD_API_KEY")

    @property
    def tavily_api_key(self) -> Optional[str]:
        return os.getenv("TAVILY_API_KEY")

    @property
    def cohere_api_key(self) -> Optional[str]:
        return os.getenv("COHERE_API_KEY")

    @property
    def groq_api_key(self) -> Optional[str]:
        return os.getenv("GROQ_API_KEY")

    def validate(self) -> dict:
        """
        Validate required API keys and return status.

        Returns:
            Dictionary with validation status for each key
        """
        return {
            "openai": bool(self.openai_api_key and self.openai_api_key != "sk-demo-replace-with-your-key"),
            "google": bool(self.google_api_key and self.google_api_key != "demo-replace-with-your-google-api-key"),
            "llama_cloud": bool(self.llama_cloud_api_key and self.llama_cloud_api_key != "llx-demo-replace-with-your-key"),
            "tavily": bool(self.tavily_api_key and self.tavily_api_key != "tvly-demo-replace-with-your-key"),
            "cohere": bool(self.cohere_api_key and self.cohere_api_key != "demo-replace-if-using-cohere"),
            "groq": bool(self.groq_api_key and self.groq_api_key != "demo-replace-if-using-groq"),
        }

    def get_missing_required_keys(self) -> list:
        """
        Get list of missing required API keys.

        Returns:
            List of missing key names
        """
        validation = self.validate()

        # Required keys depend on whether using Groq or OpenAI
        if self.llm.use_groq:
            required_keys = ["groq", "google", "llama_cloud", "tavily"]
        else:
            required_keys = ["openai", "google", "llama_cloud", "tavily"]

        return [key for key in required_keys if not validation[key]]


# Global config instance
config = Config()


# Sensitive clause categories for human review
SENSITIVE_CLAUSE_CATEGORIES = [
    "liability",
    "termination",
    "indemnification",
    "governing_law",
    "arbitration",
    "penalty",
    "damages",
    "limitation_of_liability",
    "warranty",
    "confidentiality",
    "non_compete",
    "non_disclosure",
]


# Web search confirmation message
WEB_SEARCH_CONFIRMATION_MESSAGE = (
    "No relevant clause found in your document. "
    "Would you like me to search the web for legal context?"
)


# Human review confirmation message
HUMAN_REVIEW_CONFIRMATION_MESSAGE = (
    "I found a clause that may be relevant. Is this the clause you meant?"
)
