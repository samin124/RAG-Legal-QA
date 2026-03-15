"""
LangGraph Graph Assembly
Assembles the StateGraph with all nodes and conditional edges
Including web search user confirmation flow
"""

from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import (
    retrieve_node,
    rerank_node,
    retry_node,
    web_search_confirm_node,
    web_search_node,
    human_review_node,
    generate_answer_node,
    check_clarification_node,
    summarize_clause_node,
    SENSITIVE_CLAUSE_KEYWORDS,
)

# Quality threshold for retrieval results
# Higher threshold = more strict, more likely to trigger web search for low-relevance matches
RETRIEVAL_QUALITY_THRESHOLD = 0.5


def should_retry(state: AgentState) -> str:
    """
    Route to retry or proceed based on result quality.
    Max 2 retries allowed.
    """
    retry_count = state.get("retry_count", 0)
    retrieval_score = state.get("retrieval_score", 0.0)
    reranked_docs = state.get("reranked_docs", [])

    print(f"ROUTING should_retry: retry_count={retry_count}, score={retrieval_score:.3f}, threshold={RETRIEVAL_QUALITY_THRESHOLD}, has_docs={bool(reranked_docs)}")

    # If we have good results, proceed
    if reranked_docs and retrieval_score >= RETRIEVAL_QUALITY_THRESHOLD:
        print(f"ROUTING -> check_web_or_human (good results)")
        return "check_web_or_human"

    # If we can still retry, do so
    if retry_count < 2:
        print(f"ROUTING -> retry (attempt {retry_count+1}/2)")
        return "retry"

    # Max retries reached, check for web search
    print(f"ROUTING -> check_web_or_human (max retries)")
    return "check_web_or_human"


def should_web_search_or_human_review(state: AgentState) -> str:
    """
    Route to web search confirmation, human review, or generate answer.
    """
    reranked_docs = state.get("reranked_docs", [])
    clause_type = state.get("clause_type", "general")
    retrieval_score = state.get("retrieval_score", 0.0)

    print(f"ROUTING should_web_search_or_human_review: has_docs={bool(reranked_docs)}, score={retrieval_score:.3f}, threshold={RETRIEVAL_QUALITY_THRESHOLD}, clause_type={clause_type}")

    # No relevant docs found OR docs have low relevance - ask about web search
    if not reranked_docs or retrieval_score < RETRIEVAL_QUALITY_THRESHOLD:
        print(f"ROUTING -> web_search_confirm (no docs or low score)")
        return "web_search_confirm"

    # Check if sensitive clause requires human review
    if clause_type and clause_type != "general":
        print(f"ROUTING -> human_review (sensitive clause)")
        return "human_review"

    # Good non-sensitive result - generate answer
    print(f"ROUTING -> generate_answer (good result)")
    return "generate_answer"


def should_proceed_web_search(state: AgentState) -> str:
    """
    After user confirmation, either proceed with web search or skip.
    """
    web_search_confirmed = state.get("web_search_confirmed", False)

    if web_search_confirmed:
        return "web_search"

    # User declined web search - generate "not found" response
    return "generate_answer"


def should_proceed_after_human_review(state: AgentState) -> str:
    """
    After human review, either generate answer or ask to rephrase.
    """
    human_confirmed = state.get("human_confirmed", False)

    if human_confirmed:
        return "generate_answer"

    # User rejected clause - they need to rephrase
    return "end"


def needs_simplification(state: AgentState) -> str:
    """Route to summarize if clarification requested."""
    if state.get("needs_clarification", False):
        return "summarize"
    return "end"


def create_graph() -> StateGraph:
    """
    Create and compile the Legal Q&A agent graph.

    Graph Structure:
    1. retrieve -> rerank
    2. rerank -> [retry | check_web_or_human]
    3. retry -> retrieve (loop)
    4. check_web_or_human -> [web_search_confirm | human_review | generate_answer]
    5. web_search_confirm -> [web_search | generate_answer] (based on user choice)
    6. web_search -> generate_answer
    7. human_review -> [generate_answer | end] (based on user confirmation)
    8. generate_answer -> check_clarification
    9. check_clarification -> [summarize_clause | end]
    10. summarize_clause -> end
    """
    # Initialize graph with state schema
    graph = StateGraph(AgentState)

    # Add all nodes
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("rerank", rerank_node)
    graph.add_node("retry", retry_node)
    graph.add_node("web_search_confirm", web_search_confirm_node)
    graph.add_node("web_search", web_search_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("generate_answer", generate_answer_node)
    graph.add_node("check_clarification", check_clarification_node)
    graph.add_node("summarize_clause", summarize_clause_node)

    # Set entry point
    graph.set_entry_point("retrieve")

    # Edge: retrieve -> rerank
    graph.add_edge("retrieve", "rerank")

    # Conditional edge: rerank -> [retry | check_web_or_human]
    graph.add_conditional_edges(
        "rerank",
        should_retry,
        {
            "retry": "retry",
            "check_web_or_human": "web_search_confirm"  # Intermediate routing
        }
    )

    # Edge: retry -> retrieve (loop back)
    graph.add_edge("retry", "retrieve")

    # Conditional edge: after rerank quality check
    # This is handled by routing through web_search_confirm as an intermediate
    # The web_search_confirm node will pause for UI if needed

    # Conditional edge: web_search_confirm -> [web_search | generate_answer]
    graph.add_conditional_edges(
        "web_search_confirm",
        should_proceed_web_search,
        {
            "web_search": "web_search",
            "generate_answer": "generate_answer"
        }
    )

    # Edge: web_search -> generate_answer
    graph.add_edge("web_search", "generate_answer")

    # Conditional edge: human_review -> [generate_answer | end]
    graph.add_conditional_edges(
        "human_review",
        should_proceed_after_human_review,
        {
            "generate_answer": "generate_answer",
            "end": END
        }
    )

    # Edge: generate_answer -> check_clarification
    graph.add_edge("generate_answer", "check_clarification")

    # Conditional edge: check_clarification -> [summarize_clause | end]
    graph.add_conditional_edges(
        "check_clarification",
        needs_simplification,
        {
            "summarize": "summarize_clause",
            "end": END
        }
    )

    # Edge: summarize_clause -> end
    graph.add_edge("summarize_clause", END)

    return graph.compile()


def create_graph_with_interrupts() -> StateGraph:
    """
    Create graph with interrupt points for human-in-the-loop.
    Use this version for production to enable UI confirmations.
    """
    # Initialize graph with state schema
    graph = StateGraph(AgentState)

    # Add all nodes
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("rerank", rerank_node)
    graph.add_node("retry", retry_node)
    graph.add_node("web_search_confirm", web_search_confirm_node)
    graph.add_node("web_search", web_search_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("generate_answer", generate_answer_node)
    graph.add_node("check_clarification", check_clarification_node)
    graph.add_node("summarize_clause", summarize_clause_node)

    # Set entry point
    graph.set_entry_point("retrieve")

    # Add edges (same as create_graph)
    graph.add_edge("retrieve", "rerank")

    graph.add_conditional_edges(
        "rerank",
        should_retry,
        {
            "retry": "retry",
            "check_web_or_human": "web_search_confirm"
        }
    )

    graph.add_edge("retry", "retrieve")

    graph.add_conditional_edges(
        "web_search_confirm",
        should_proceed_web_search,
        {
            "web_search": "web_search",
            "generate_answer": "generate_answer"
        }
    )

    graph.add_edge("web_search", "generate_answer")

    graph.add_conditional_edges(
        "human_review",
        should_proceed_after_human_review,
        {
            "generate_answer": "generate_answer",
            "end": END
        }
    )

    graph.add_edge("generate_answer", "check_clarification")

    graph.add_conditional_edges(
        "check_clarification",
        needs_simplification,
        {
            "summarize": "summarize_clause",
            "end": END
        }
    )

    graph.add_edge("summarize_clause", END)

    # Compile with interrupt points for human-in-the-loop
    return graph.compile(
        interrupt_before=["web_search_confirm", "human_review"]
    )


def get_initial_state() -> AgentState:
    """
    Create initial state for a new conversation.
    """
    return AgentState(
        query="",
        chat_history=[],
        retrieved_docs=[],
        reranked_docs=[],
        retry_count=0,
        web_search_results=[],
        human_confirmed=False,
        web_search_confirmed=False,
        answer="",
        needs_clarification=False,
        source="document",
        uploaded_docs=[],
        vector_store=None,
        retrieval_score=0.0,
        clause_type=None
    )
