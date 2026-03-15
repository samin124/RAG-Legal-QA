"""
Agent State Schema
Shared TypedDict state object across all LangGraph nodes
"""

from typing import TypedDict, List, Optional, Any
from langchain_core.documents import Document


class AgentState(TypedDict):
    """State schema for the Legal Q&A Agent"""

    # Current user question
    query: str

    # Conversation history (list of Q&A pairs)
    chat_history: List[dict]

    # Retrieved document chunks from vector store
    retrieved_docs: List[Document]

    # Top-ranked chunk after reranking
    reranked_docs: List[Document]

    # Number of retrieval retries attempted (max 2)
    retry_count: int

    # Results from Tavily when document has no answer
    web_search_results: List[str]

    # True once user confirms clause during human review
    human_confirmed: bool

    # True once user confirms web search fallback
    web_search_confirmed: bool

    # Generated LLM response
    answer: str

    # True if user requests plain-English simplification
    needs_clarification: bool

    # Source type: "document" or "web"
    source: str

    # Uploaded documents for processing
    uploaded_docs: List[Any]

    # Vector store reference (Qdrant)
    vector_store: Optional[Any]

    # Current retrieval quality score
    retrieval_score: float

    # Detected clause type for sensitive clause routing
    clause_type: Optional[str]
