"""
Prompts Module
All prompt templates for the Legal Q&A pipeline
"""

from .templates import (
    LEGAL_QA_PROMPT,
    SIMPLIFICATION_PROMPT,
    QUERY_REPHRASE_PROMPT,
    WEB_SEARCH_PROMPT,
)

__all__ = [
    "LEGAL_QA_PROMPT",
    "SIMPLIFICATION_PROMPT",
    "QUERY_REPHRASE_PROMPT",
    "WEB_SEARCH_PROMPT",
]
