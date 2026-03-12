"""
LangGraph Graph Assembly
Assembles the StateGraph with all nodes and conditional edges
"""

from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import (
    retrieve_node,
    rerank_node,
    retry_node,
    web_search_node,
    human_review_node,
    generate_answer_node,
    check_clarification_node,
    summarize_clause_node,
)


def should_retry(state: AgentState) -> str:
    """Route to retry or proceed based on result quality."""
    # TODO: Implement quality threshold check
    if state.get("retry_count", 0) < 2 and not state.get("reranked_docs"):
        return "retry"
    return "proceed"


def should_web_search(state: AgentState) -> str:
    """Route to web search if no relevant clause found."""
    if not state.get("reranked_docs"):
        return "web_search"
    return "human_review_check"


def is_sensitive_clause(state: AgentState) -> str:
    """Route to human review for sensitive clauses."""
    # TODO: Implement sensitive clause detection
    sensitive_keywords = ["liability", "termination", "indemnification", "governing law"]
    # Placeholder logic
    return "generate"


def needs_simplification(state: AgentState) -> str:
    """Route to summarize if clarification requested."""
    if state.get("needs_clarification"):
        return "summarize"
    return "end"


def create_graph() -> StateGraph:
    """
    Create and compile the Legal Q&A agent graph.

    Graph Structure:
    retrieve -> rerank -> [retry/proceed] -> [web_search/human_review]
    -> generate_answer -> check_clarification -> [summarize/end]
    """
    # Initialize graph with state schema
    graph = StateGraph(AgentState)

    # Add all nodes
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("rerank", rerank_node)
    graph.add_node("retry", retry_node)
    graph.add_node("web_search", web_search_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("generate_answer", generate_answer_node)
    graph.add_node("check_clarification", check_clarification_node)
    graph.add_node("summarize_clause", summarize_clause_node)

    # Set entry point
    graph.set_entry_point("retrieve")

    # Add edges
    graph.add_edge("retrieve", "rerank")

    # Conditional: retry or proceed
    graph.add_conditional_edges(
        "rerank",
        should_retry,
        {
            "retry": "retry",
            "proceed": "generate_answer"  # Simplified for now
        }
    )

    graph.add_edge("retry", "retrieve")
    graph.add_edge("web_search", "generate_answer")
    graph.add_edge("human_review", "generate_answer")
    graph.add_edge("generate_answer", "check_clarification")

    # Conditional: summarize or end
    graph.add_conditional_edges(
        "check_clarification",
        needs_simplification,
        {
            "summarize": "summarize_clause",
            "end": END
        }
    )

    graph.add_edge("summarize_clause", END)

    return graph.compile()
