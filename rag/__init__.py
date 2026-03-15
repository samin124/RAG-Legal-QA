"""
RAG Module
Document loading, embedding, and retrieval components
"""

from .loader import (
    load_pdf_with_llamaparse,
    load_pdf_from_bytes,
    load_pdf_fallback,
    load_image_from_bytes,
    load_docx_from_bytes,
    load_markdown_from_bytes,
    chunk_documents,
    process_uploaded_pdf,
    process_uploaded_document,
)

from .embeddings import (
    GeminiEmbeddings,
    GeminiMultiModalEmbeddings,
    create_text_embeddings,
    create_multimodal_embeddings,
    create_qdrant_vector_store,
    create_qdrant_from_existing,
    add_documents_to_store,
    create_vector_store_from_chunks,
)

from .retriever import (
    create_retriever,
    retrieve_documents,
    retrieve_with_scores,
    create_reranking_retriever,
    create_multi_query_retriever,
    evaluate_retrieval_quality,
    get_unique_sources,
)

__all__ = [
    # Loader
    "load_pdf_with_llamaparse",
    "load_pdf_from_bytes",
    "load_pdf_fallback",
    "load_image_from_bytes",
    "load_docx_from_bytes",
    "load_markdown_from_bytes",
    "chunk_documents",
    "process_uploaded_pdf",
    "process_uploaded_document",
    # Embeddings
    "GeminiEmbeddings",
    "GeminiMultiModalEmbeddings",
    "create_text_embeddings",
    "create_multimodal_embeddings",
    "create_qdrant_vector_store",
    "create_qdrant_from_existing",
    "add_documents_to_store",
    "create_vector_store_from_chunks",
    # Retriever
    "create_retriever",
    "retrieve_documents",
    "retrieve_with_scores",
    "create_reranking_retriever",
    "create_multi_query_retriever",
    "evaluate_retrieval_quality",
    "get_unique_sources",
]
