"""
Embeddings and Vector Store
Handles embedding generation and ChromaDB indexing
"""

from typing import List, Optional
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma


def create_embeddings(model: str = "text-embedding-3-small") -> OpenAIEmbeddings:
    """
    Create OpenAI embeddings instance.

    Args:
        model: OpenAI embedding model name

    Returns:
        OpenAIEmbeddings instance
    """
    return OpenAIEmbeddings(model=model)


def create_vector_store(
    documents: List[Document],
    embeddings: Optional[OpenAIEmbeddings] = None,
    collection_name: str = "legal_docs"
) -> Chroma:
    """
    Create an in-memory Chroma vector store from documents.

    Args:
        documents: List of Document objects to index
        embeddings: Embeddings instance (creates default if None)
        collection_name: Name for the Chroma collection

    Returns:
        Chroma vector store instance
    """
    if embeddings is None:
        embeddings = create_embeddings()

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=collection_name
    )

    return vector_store


def add_documents_to_store(
    vector_store: Chroma,
    documents: List[Document]
) -> None:
    """
    Add additional documents to existing vector store.

    Args:
        vector_store: Existing Chroma vector store
        documents: New documents to add
    """
    vector_store.add_documents(documents)
