"""
Retrieval Logic
Handles semantic search and retrieval from vector store
"""

from typing import List, Optional
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain.retrievers import ContextualCompressionRetriever


def create_retriever(
    vector_store: Chroma,
    search_type: str = "similarity",
    k: int = 5
):
    """
    Create a retriever from the vector store.

    Args:
        vector_store: Chroma vector store instance
        search_type: Type of search ("similarity" or "mmr")
        k: Number of documents to retrieve

    Returns:
        Retriever instance
    """
    retriever = vector_store.as_retriever(
        search_type=search_type,
        search_kwargs={"k": k}
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


def create_reranking_retriever(
    base_retriever,
    reranker_type: str = "cohere"
) -> ContextualCompressionRetriever:
    """
    Create a retriever with reranking capability.

    Args:
        base_retriever: Base retriever to wrap
        reranker_type: Type of reranker ("cohere" or "flashrank")

    Returns:
        ContextualCompressionRetriever with reranking
    """
    if reranker_type == "cohere":
        from langchain.retrievers.document_compressors import CohereRerank
        compressor = CohereRerank(top_n=3)
    else:
        from langchain.retrievers.document_compressors import FlashrankRerank
        compressor = FlashrankRerank(top_n=3)

    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=base_retriever
    )

    return compression_retriever
