"""
LangGraph Agent Nodes - Complete Implementation
Contains all 9 nodes for the Legal Q&A pipeline with full logic:

1. Retrieve: Qdrant vector store similarity search
2. Rerank: Re-score and select best chunk using Cohere/Flashrank
3. Retry: Rephrase query on poor results
4. Web Search Confirm: Ask user before searching web
5. Web Search: Tavily fallback for external legal context
6. Human Review: Pause for user confirmation on sensitive clauses
7. Generate Answer: LLM response generation
8. Check Clarification: Detect simplification requests
9. Summarize Clause: Plain-English rewrite
"""

from typing import Dict, Any, List
import os
from .state import AgentState

# Import configuration to check which LLM to use
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# ============================================================================
# CONFIGURATION - Sensitive clause keywords for human review routing
# ============================================================================
SENSITIVE_CLAUSE_KEYWORDS = [
    "liability", "indemnification", "indemnify",
    "termination", "terminate", "governing law",
    "jurisdiction", "arbitration", "penalty",
    "damages", "limitation of liability", "warranty",
    "confidentiality", "non-compete", "non-disclosure",
    "force majeure", "insurance", "intellectual property"
]


# ============================================================================
# HELPER FUNCTION - Get LLM based on configuration
# ============================================================================
def get_llm(model: str = None, temperature: float = 0.0):
    """
    Get the configured LLM (Groq or OpenAI).

    Args:
        model: Specific model name (optional, uses config default)
        temperature: Temperature for generation

    Returns:
        LLM instance (ChatGroq or ChatOpenAI)
    """
    # Decide which LLM to use based on config
    if config.llm.use_groq:
        # Use Groq (faster, free tier available)
        from langchain_groq import ChatGroq
        model_name = model or config.llm.default_model
        print(f"Using Groq model: {model_name}")
        return ChatGroq(
            model=model_name,
            temperature=temperature,
            max_tokens=config.llm.max_tokens
        )
    else:
        # Fallback to OpenAI
        from langchain_openai import ChatOpenAI
        model_name = model or config.llm.fallback_model
        print(f"Using OpenAI model: {model_name}")
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=config.llm.max_tokens
        )


# ============================================================================
# NODE 1: RETRIEVE - Fetch relevant chunks from vector store
# ============================================================================
def retrieve_node(state: AgentState) -> Dict[str, Any]:
    """
    Retrieve relevant document chunks from Qdrant vector store.

    Process:
    1. Get the user query from state
    2. Get vector store reference from state
    3. Create a retriever with k=5 (top 5 most similar chunks)
    4. Execute semantic similarity search
    5. Return retrieved documents and initial quality score

    Args:
        state: Current agent state containing query and vector_store

    Returns:
        Dictionary with retrieved_docs and retrieval_score
    """
    from rag.retriever import retrieve_documents, create_retriever

    query = state.get("query", "")
    vector_store = state.get("vector_store")

    # Guard clause: If no vector store, return empty results
    if not vector_store:
        print("WARNING: No vector store available for retrieval")
        return {"retrieved_docs": [], "retrieval_score": 0.0}

    try:
        # Create retriever with top 5 results for initial recall
        retriever = create_retriever(vector_store, k=5)

        # Execute semantic search
        docs = retrieve_documents(retriever, query)

        # Calculate initial quality score (1.0 if we got results, 0.0 otherwise)
        score = 1.0 if docs else 0.0

        print(f"Retrieved {len(docs)} documents with score {score}")
        return {"retrieved_docs": docs, "retrieval_score": score}

    except Exception as e:
        print(f"Retrieval error: {e}")
        return {"retrieved_docs": [], "retrieval_score": 0.0}


# ============================================================================
# NODE 2: RERANK - Select the single best matching chunk
# ============================================================================
def rerank_node(state: AgentState) -> Dict[str, Any]:
    """
    Re-score retrieved chunks and select the best match using reranking model.

    Process:
    1. Get retrieved documents from previous node
    2. Use Cohere Rerank (or Flashrank) to re-score for relevance
    3. Select top-1 most relevant chunk
    4. Detect clause type for sensitive routing
    5. Calculate refined quality score

    Why reranking?
    - Initial retrieval uses embeddings (fast, broad recall)
    - Reranking uses cross-encoder models (slower, better precision)
    - Dramatically improves quality of final selected chunk

    Args:
        state: Current agent state with retrieved_docs

    Returns:
        Dictionary with reranked_docs (top 1), retrieval_score, clause_type
    """
    from rag.retriever import create_reranking_retriever, create_retriever

    retrieved_docs = state.get("retrieved_docs", [])
    query = state.get("query", "")
    vector_store = state.get("vector_store")

    # Guard clause: No docs to rerank
    if not retrieved_docs or not vector_store:
        print("WARNING: No documents to rerank")
        return {"reranked_docs": [], "retrieval_score": 0.0, "clause_type": None}

    try:
        # Create base retriever
        base_retriever = create_retriever(vector_store, k=5)

        # Apply reranking model to select best match
        # Cohere Rerank is state-of-the-art for legal text
        reranking_retriever = create_reranking_retriever(
            base_retriever,
            reranker_type="cohere",  # Can switch to "flashrank" if no API key
            top_n=1  # Select only the single best match
        )

        # Execute reranking
        reranked = reranking_retriever.invoke(query)

        # Detect if this is a sensitive clause requiring human review
        clause_type = detect_clause_type(reranked[0].page_content if reranked else "")

        # Calculate quality score based on actual relevance
        if reranked:
            # Check if Cohere reranker provided a relevance score in metadata
            print(f"DEBUG: Reranked doc metadata: {reranked[0].metadata if reranked else 'None'}")

            # Try to get relevance_score from Cohere reranker
            if hasattr(reranked[0], 'metadata') and 'relevance_score' in reranked[0].metadata:
                score = reranked[0].metadata['relevance_score']
                print(f"DEBUG: Using Cohere relevance score: {score}")
            else:
                # Fallback: Use conservative scoring
                # Check if query keywords actually appear meaningfully in document
                query_lower = query.lower()
                doc_lower = reranked[0].page_content.lower()

                # Extract key legal terms from query (ignore common words)
                stop_words = {'what', 'are', 'the', 'for', 'to', 'a', 'an', 'is', 'of', 'in', 'on', 'at', 'by'}
                query_terms = [word for word in query_lower.split() if word not in stop_words and len(word) > 3]

                # Count how many key terms appear in document
                matches = sum(1 for term in query_terms if term in doc_lower)
                score = matches / len(query_terms) if query_terms else 0.0

                print(f"DEBUG: Using fallback scoring - Query terms: {query_terms}, Matches: {matches}, Score: {score:.2f}")
        else:
            score = 0.0

        print(f"Reranked to {len(reranked)} document(s), FINAL relevance score: {score:.2f}, clause type: {clause_type}")

        # If score is too low, don't return any documents (trigger web search)
        # This prevents returning completely irrelevant documents
        if score < 0.3:  # Minimum relevance threshold
            print(f"Score {score:.2f} below minimum threshold 0.3 - clearing documents to trigger web search")
            return {
                "reranked_docs": [],
                "retrieval_score": score,
                "clause_type": None
            }

        return {
            "reranked_docs": reranked,
            "retrieval_score": score,
            "clause_type": clause_type
        }

    except Exception as e:
        print(f"WARNING: Reranking failed, using fallback: {e}")
        # Fallback: Return top retrieved doc without reranking
        # Use term overlap to estimate relevance instead of hardcoded score
        if retrieved_docs:
            from rag.retriever import evaluate_retrieval_quality
            _, score = evaluate_retrieval_quality(retrieved_docs[:1], query, threshold=0.3)
        else:
            score = 0.0

        print(f"FALLBACK: relevance score: {score:.2f}")

        # Same threshold check as main path - don't return irrelevant docs
        if score < 0.3:
            print(f"FALLBACK: Score {score:.2f} below minimum threshold 0.3 - clearing documents to trigger web search")
            return {
                "reranked_docs": [],
                "retrieval_score": score,
                "clause_type": None
            }

        return {
            "reranked_docs": retrieved_docs[:1] if retrieved_docs else [],
            "retrieval_score": score,
            "clause_type": detect_clause_type(retrieved_docs[0].page_content if retrieved_docs else "")
        }


# ============================================================================
# HELPER: Detect clause type for sensitive routing
# ============================================================================
def detect_clause_type(content: str) -> str:
    """
    Detect the type of clause based on keyword matching.

    Sensitive clauses trigger human review to ensure accuracy.

    Args:
        content: Text content of the clause

    Returns:
        String: keyword found (e.g., "liability") or "general"
    """
    content_lower = content.lower()

    # Check each sensitive keyword
    for keyword in SENSITIVE_CLAUSE_KEYWORDS:
        if keyword in content_lower:
            return keyword.replace(" ", "_")

    return "general"


# ============================================================================
# NODE 3: RETRY - Rephrase query and retry retrieval
# ============================================================================
def retry_node(state: AgentState) -> Dict[str, Any]:
    """
    Rephrase the user query and increment retry counter.

    Process:
    1. Get current query and chat history
    2. Use LLM to rephrase query with legal terminology
    3. Increment retry counter
    4. Return rephrased query for re-retrieval

    Why retry?
    - User queries may use informal language
    - Legal documents use specific terminology
    - Rephrasing bridges this vocabulary gap

    Args:
        state: Current agent state with query and retry_count

    Returns:
        Dictionary with rephrased query and incremented retry_count
    """
    from prompts.templates import QUERY_REPHRASE_PROMPT

    query = state.get("query", "")
    chat_history = state.get("chat_history", [])
    retry_count = state.get("retry_count", 0)

    try:
        # Use same model as main generation for better query understanding
        # For Groq: use llama-3.3-70b-versatile (high quality)
        # For OpenAI: use gpt-4o-mini
        if config.llm.use_groq:
            llm = get_llm(model="llama-3.3-70b-versatile", temperature=0)
        else:
            llm = get_llm(model="gpt-4o-mini", temperature=0)
        chain = QUERY_REPHRASE_PROMPT | llm

        # Rephrase with context from recent conversation
        rephrased = chain.invoke({
            "question": query,
            "chat_history": str(chat_history[-3:]) if chat_history else ""
        })

        print(f"Query rephrased: '{query}' -> '{rephrased.content}'")

        return {
            "query": rephrased.content,
            "retry_count": retry_count + 1
        }

    except Exception as e:
        print(f"WARNING: Query rephrase error: {e}")
        # If rephrasing fails, just increment counter
        return {"retry_count": retry_count + 1}


# ============================================================================
# NODE 4: WEB SEARCH CONFIRM - Ask user before web search
# ============================================================================
def web_search_confirm_node(state: AgentState) -> Dict[str, Any]:
    """
    Pause and signal UI to ask user for web search confirmation.

    Process:
    1. Set web_search_confirmed to False
    2. Set source to "pending_web_confirmation"
    3. UI will detect this and show confirmation dialog
    4. Graph execution pauses here (interrupt point)

    Why ask user?
    - Web results are external, not from user's document
    - User should be aware answer comes from web, not their contract
    - Transparency is critical for legal information

    Args:
        state: Current agent state

    Returns:
        Dictionary signaling pending confirmation
    """
    print("Pausing for web search user confirmation")

    return {
        "web_search_confirmed": False,
        "source": "pending_web_confirmation"
    }


# ============================================================================
# NODE 5: WEB SEARCH - Fetch external legal context via Tavily
# ============================================================================
def web_search_node(state: AgentState) -> Dict[str, Any]:
    """
    Search web using Tavily when document has no relevant clause.

    Process:
    1. Check if user confirmed web search
    2. If yes, call Tavily API with legal-focused query
    3. Format and return top 3 web results
    4. Mark source as "web"

    Tavily is optimized for:
    - Factual accuracy
    - Legal and professional content
    - Summarized, relevant excerpts

    Args:
        state: Current agent state with query and web_search_confirmed

    Returns:
        Dictionary with web_search_results and source="web"
    """
    from tavily import TavilyClient

    query = state.get("query", "")
    web_search_confirmed = state.get("web_search_confirmed", False)

    # User declined web search
    if not web_search_confirmed:
        print("Web search declined by user")
        return {"web_search_results": [], "source": "document"}

    try:
        # Initialize Tavily client
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

        # Search with legal context
        response = client.search(
            query=f"legal contract clause: {query}",
            search_depth="advanced",  # More thorough search
            max_results=3  # Top 3 most relevant results
        )

        # Format results for LLM context
        results = [
            f"**Source:** {r['url']}\n\n{r['content']}"
            for r in response.get("results", [])
        ]

        print(f"Web search completed: {len(results)} results found")

        return {
            "web_search_results": results,
            "source": "web"
        }

    except Exception as e:
        print(f"Web search error: {e}")
        return {"web_search_results": [], "source": "web_error"}


# ============================================================================
# NODE 6: HUMAN REVIEW - Pause for user confirmation on sensitive clauses
# ============================================================================
def human_review_node(state: AgentState) -> Dict[str, Any]:
    """
    Pause for user confirmation when sensitive clause is detected.

    Process:
    1. Mark human_confirmed as False
    2. Store clause_type for UI display
    3. UI will show clause and ask: "Is this the clause you meant?"
    4. Graph execution pauses (interrupt point)
    5. User confirms or declines

    Why human review?
    - Sensitive clauses have high impact (liability, termination, etc.)
    - Wrong clause = incorrect legal interpretation
    - Human verification adds safety layer

    Args:
        state: Current agent state with reranked_docs and clause_type

    Returns:
        Dictionary signaling pending human confirmation
    """
    clause_type = state.get("clause_type", "general")

    print(f"Pausing for human review of {clause_type} clause")

    return {
        "human_confirmed": False,
        "clause_type": clause_type
    }


# ============================================================================
# NODE 7: GENERATE ANSWER - Create LLM response from context
# ============================================================================
def generate_answer_node(state: AgentState) -> Dict[str, Any]:
    """
    Generate LLM response using retrieved context or web results.

    Process:
    1. Determine source: document clause or web results
    2. Select appropriate prompt template
    3. Format context with chat history
    4. Call GPT-4o to generate grounded answer
    5. Return answer with source attribution

    Prompt engineering ensures:
    - Answers stay grounded in provided context
    - No hallucination beyond source material
    - Appropriate caveats for web-sourced answers

    Args:
        state: Current agent state with query, context, and history

    Returns:
        Dictionary with generated answer and source type
    """
    from prompts.templates import LEGAL_QA_PROMPT, WEB_SEARCH_PROMPT

    query = state.get("query", "")
    chat_history = state.get("chat_history", [])
    reranked_docs = state.get("reranked_docs", [])
    web_search_results = state.get("web_search_results", [])
    source = state.get("source", "document")

    try:
        # Use configured LLM for high-quality legal analysis
        # Groq: llama-3.3-70b-versatile or OpenAI: gpt-4o
        llm = get_llm(temperature=0)

        # Route to appropriate prompt based on source
        if source == "web" and web_search_results:
            # Web-sourced answer with disclaimers
            chain = WEB_SEARCH_PROMPT | llm
            response = chain.invoke({
                "web_results": "\n\n".join(web_search_results),
                "question": query
            })
            print("Generated answer from web results")

        else:
            # Document-grounded answer
            if not reranked_docs:
                # No relevant documents found - return helpful message
                return {
                    "answer": "I couldn't find any relevant information in your document to answer this question. Please try:\n\n1. Asking a more specific question about a particular clause or topic\n2. Rephrasing your question\n3. Checking if the information exists in your document",
                    "source": "document"
                }

            context = reranked_docs[0].page_content
            chain = LEGAL_QA_PROMPT | llm
            response = chain.invoke({
                "context": context,
                "chat_history": format_chat_history(chat_history),
                "question": query
            })
            print("Generated answer from document")

        return {
            "answer": response.content,
            "source": source if source != "pending_web_confirmation" else "document"
        }

    except Exception as e:
        print(f"Answer generation error: {e}")
        return {
            "answer": "I apologize, but I encountered an error generating the answer. Please try again.",
            "source": "error"
        }


# ============================================================================
# HELPER: Format chat history for LLM context
# ============================================================================
def format_chat_history(chat_history: List[dict]) -> str:
    """
    Format conversation history for inclusion in LLM prompt.

    Process:
    1. Take last 5 messages (context window management)
    2. Format as "User: ... / Assistant: ..."
    3. Provides conversation context for follow-up questions

    Args:
        chat_history: List of message dictionaries

    Returns:
        Formatted string of conversation history
    """
    if not chat_history:
        return "No previous conversation."

    formatted = []
    for msg in chat_history[-5:]:  # Last 5 messages for context
        role = msg.get("role", "user")
        content = msg.get("content", "")
        formatted.append(f"{role.capitalize()}: {content}")

    return "\n".join(formatted)


# ============================================================================
# NODE 8: CHECK CLARIFICATION - Detect if user wants simpler explanation
# ============================================================================
def check_clarification_node(state: AgentState) -> Dict[str, Any]:
    """
    Detect if user is requesting a plain-English simplification.

    Process:
    1. Analyze current query for simplification triggers
    2. Check for keywords like "simplify", "explain", "plain english"
    3. Set needs_clarification flag
    4. Router decides whether to invoke summarize node

    Trigger words:
    - "simplify", "simpler", "plain english"
    - "what does that mean", "don't understand"
    - "ELI5", "layman terms", "easier"

    Args:
        state: Current agent state with query

    Returns:
        Dictionary with needs_clarification boolean
    """
    query = state.get("query", "").lower()

    # List of simplification trigger phrases
    simplification_triggers = [
        "simplify", "simpler", "plain english", "plain language",
        "explain", "what does that mean", "don't understand",
        "confused", "eli5", "layman", "easier", "clearer",
        "break it down", "dumb it down", "simple terms"
    ]

    # Check if any trigger is present in query
    needs_clarification = any(trigger in query for trigger in simplification_triggers)

    if needs_clarification:
        print("Simplification requested")
    else:
        print("No clarification needed")

    return {"needs_clarification": needs_clarification}


# ============================================================================
# NODE 9: SUMMARIZE CLAUSE - Rewrite in plain English
# ============================================================================
def summarize_clause_node(state: AgentState) -> Dict[str, Any]:
    """
    Rewrite legal answer in plain, jargon-free English.

    Process:
    1. Get current answer (may contain legal jargon)
    2. Use specialized simplification prompt
    3. Call LLM to rewrite in accessible language
    4. Preserve factual accuracy while improving clarity
    5. Return simplified version

    Simplification guidelines:
    - Replace legal terms with everyday words
    - Break complex sentences into shorter ones
    - Use examples where helpful
    - Maintain accuracy (no information loss)

    Args:
        state: Current agent state with answer

    Returns:
        Dictionary with simplified answer
    """
    from prompts.templates import SIMPLIFICATION_PROMPT

    answer = state.get("answer", "")

    # Guard clause: No answer to simplify
    if not answer:
        return {"answer": ""}

    try:
        # Use same model as main generation for consistent quality
        # For Groq: use llama-3.3-70b-versatile (high quality)
        # For OpenAI: use gpt-4o-mini
        if config.llm.use_groq:
            llm = get_llm(model="llama-3.3-70b-versatile", temperature=0.3)
        else:
            llm = get_llm(model="gpt-4o-mini", temperature=0.3)
        chain = SIMPLIFICATION_PROMPT | llm

        # Generate plain-English version
        simplified = chain.invoke({"answer": answer})

        print("Answer simplified to plain English")

        return {"answer": simplified.content}

    except Exception as e:
        print(f"WARNING: Simplification error: {e}")
        # Return original if simplification fails
        return {"answer": answer}
