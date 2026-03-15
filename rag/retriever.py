"""
Retrieval Logic
Handles semantic search and retrieval from Qdrant vector store
"""

from typing import List, Optional
from langchain_core.documents import Document


def create_retriever(
    vector_store,
    search_type: str = "similarity",
    k: int = 5,
    score_threshold: Optional[float] = None
):
    """
    Create a retriever from the Qdrant vector store.

    Args:
        vector_store: Qdrant vector store instance
        search_type: Type of search ("similarity", "mmr", or "similarity_score_threshold")
        k: Number of documents to retrieve
        score_threshold: Minimum similarity score (only for similarity_score_threshold)

    Returns:
        Retriever instance
    """
    search_kwargs = {"k": k}

    if search_type == "similarity_score_threshold" and score_threshold:
        search_kwargs["score_threshold"] = score_threshold

    retriever = vector_store.as_retriever(
        search_type=search_type,
        search_kwargs=search_kwargs
    )

    return retriever


def retrieve_documents(
    retriever,
    query: str
) -> List[Document]:
    """
    Retrieve relevant documents for a query.

    Args:
        retriever: Retriever instance
        query: User query string

    Returns:
        List of relevant Document objects
    """
    return retriever.invoke(query)


def retrieve_with_scores(
    vector_store,
    query: str,
    k: int = 5
) -> List[tuple]:
    """
    Retrieve documents with similarity scores.

    Args:
        vector_store: Qdrant vector store instance
        query: User query string
        k: Number of documents to retrieve

    Returns:
        List of (Document, score) tuples
    """
    return vector_store.similarity_search_with_score(query, k=k)


def create_reranking_retriever(
    base_retriever,
    reranker_type: str = "cohere",
    top_n: int = 3
):
    """
    Create a retriever with reranking capability.

    Args:
        base_retriever: Base retriever to wrap
        reranker_type: Type of reranker ("cohere" or "flashrank")
        top_n: Number of top documents to return after reranking

    Returns:
        ContextualCompressionRetriever with reranking
    """
    from langchain_community.retrievers import ContextualCompressionRetriever

    if reranker_type == "cohere":
        from langchain_cohere import CohereRerank
        compressor = CohereRerank(top_n=top_n)
    else:
        from langchain_community.document_compressors import FlashrankRerank
        compressor = FlashrankRerank(top_n=top_n)

    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=base_retriever
    )

    return compression_retriever


def create_multi_query_retriever(
    vector_store,
    llm,
    k: int = 5
):
    """
    Create a multi-query retriever that generates multiple queries.

    Args:
        vector_store: Qdrant vector store instance
        llm: LLM for query generation
        k: Number of documents per query

    Returns:
        MultiQueryRetriever instance
    """
    from langchain_community.retrievers import MultiQueryRetriever

    base_retriever = create_retriever(vector_store, k=k)

    retriever = MultiQueryRetriever.from_llm(
        retriever=base_retriever,
        llm=llm
    )

    return retriever


def evaluate_retrieval_quality(
    documents: List[Document],
    query: str,
    threshold: float = 0.5
) -> tuple:
    """
    Evaluate the quality of retrieved documents.

    Args:
        documents: List of retrieved documents
        query: Original query
        threshold: Minimum score threshold

    Returns:
        Tuple of (is_quality_sufficient, best_score)
    """
    if not documents:
        return False, 0.0

    # Simple heuristic based on document content matching
    query_terms = set(query.lower().split())
    best_score = 0.0

    for doc in documents:
        doc_terms = set(doc.page_content.lower().split())
        overlap = len(query_terms & doc_terms) / max(len(query_terms), 1)
        best_score = max(best_score, overlap)

    return best_score >= threshold, best_score


def get_unique_sources(documents: List[Document]) -> List[str]:
    """
    Get unique source documents from retrieved chunks.

    Args:
        documents: List of Document objects

    Returns:
        List of unique source filenames
    """
    sources = set()
    for doc in documents:
        if "source" in doc.metadata:
            sources.add(doc.metadata["source"])

    return list(sources)
