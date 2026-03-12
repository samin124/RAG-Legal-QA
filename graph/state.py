"""
Agent State Schema
Shared TypedDict state object across all LangGraph nodes
"""

from typing import TypedDict, List, Optional


class AgentState(TypedDict):
    """State schema for the Legal Q&A Agent"""

    # Current user question
    query: str

    # Conversation history (list of Q&A pairs)
    chat_history: List[dict]

    # Retrieved document chunks from vector store
    retrieved_docs: List[str]

    # Top-ranked chunk after reranking
    reranked_docs: List[str]

    # Number of retrieval retries attempted (max 2)
    retry_count: int

    # Results from Tavily when document has no answer
    web_search_results: List[str]

    # True once user confirms clause during human review
    human_confirmed: bool

    # Generated LLM response
    answer: str

    # True if user requests plain-English simplification
    needs_clarification: bool

    # Source type: "document" or "web"
    source: str
