"""
Embeddings and Vector Store
Handles Google Gemini embeddings (text + multi-modal) and Qdrant indexing
"""

from typing import List, Optional, Union
import os
from langchain_core.documents import Document


class GeminiEmbeddings:
    """Google Gemini text embeddings wrapper for LangChain compatibility."""

    def __init__(
        self,
        model: str = "models/gemini-embedding-001",
        api_key: Optional[str] = None
    ):
        """
        Initialize Gemini embeddings.

        Args:
            model: Gemini embedding model name
            api_key: Google API key (defaults to env var)
        """
        import google.generativeai as genai

        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model

        genai.configure(api_key=self.api_key)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        import google.generativeai as genai

        embeddings = []
        for text in texts:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_document"
            )
            embeddings.append(result['embedding'])

        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query.

        Args:
            text: Query text to embed

        Returns:
            Embedding vector
        """
        import google.generativeai as genai

        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type="retrieval_query"
        )

        return result['embedding']


class GeminiMultiModalEmbeddings:
    """Google Gemini multi-modal embeddings for images and tables."""

    def __init__(
        self,
        model: str = "models/gemini-embedding-2-preview",
        api_key: Optional[str] = None
    ):
        """
        Initialize multi-modal embeddings.

        Args:
            model: Gemini multi-modal model name
            api_key: Google API key (defaults to env var)
        """
        import google.generativeai as genai

        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model

        genai.configure(api_key=self.api_key)

    def embed_image(self, image_path: str) -> List[float]:
        """
        Embed an image file.

        Args:
            image_path: Path to image file

        Returns:
            Embedding vector
        """
        import google.generativeai as genai
        from PIL import Image

        image = Image.open(image_path)
        result = genai.embed_content(
            model=self.model,
            content=image,
            task_type="retrieval_document"
        )

        return result['embedding']

    def embed_image_bytes(self, image_bytes: bytes) -> List[float]:
        """
        Embed image from bytes.

        Args:
            image_bytes: Raw image bytes

        Returns:
            Embedding vector
        """
        import google.generativeai as genai
        from PIL import Image
        import io

        image = Image.open(io.BytesIO(image_bytes))
        result = genai.embed_content(
            model=self.model,
            content=image,
            task_type="retrieval_document"
        )

        return result['embedding']


def create_text_embeddings(
    model: str = "models/gemini-embedding-001"
):
    """
    Create Google Generative AI text embeddings instance using langchain integration.

    Args:
        model: Google embedding model name (e.g. "models/gemini-embedding-001", "models/gemini-embedding-2-preview")

    Returns:
        GoogleGenerativeAIEmbeddings instance
    """
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    import os

    return GoogleGenerativeAIEmbeddings(
        model=model,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )


def create_multimodal_embeddings(
    model: str = "models/gemini-embedding-2-preview"
) -> GeminiMultiModalEmbeddings:
    """
    Create Gemini multi-modal embeddings instance.

    Args:
        model: Gemini multi-modal model name

    Returns:
        GeminiMultiModalEmbeddings instance
    """
    return GeminiMultiModalEmbeddings(model=model)


def create_qdrant_vector_store(
    documents: List[Document],
    embeddings: Optional[GeminiEmbeddings] = None,
    collection_name: str = "legal_docs",
    location: str = ":memory:"
):
    """
    Create a Qdrant vector store from documents.

    Args:
        documents: List of Document objects to index
        embeddings: Embeddings instance (creates default if None)
        collection_name: Name for the Qdrant collection
        location: Qdrant location (":memory:" for in-memory, or path/URL)

    Returns:
        Qdrant vector store instance
    """
    from langchain_qdrant import QdrantVectorStore
    from qdrant_client import QdrantClient

    if embeddings is None:
        embeddings = create_text_embeddings()

    # Initialize Qdrant client
    if location == ":memory:":
        client = QdrantClient(location=":memory:")
    else:
        client = QdrantClient(path=location)

    # Create vector store
    vector_store = QdrantVectorStore.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=collection_name,
        location=location
    )

    return vector_store


def create_qdrant_from_existing(
    collection_name: str = "legal_docs",
    embeddings: Optional[GeminiEmbeddings] = None,
    location: str = ":memory:"
):
    """
    Connect to an existing Qdrant collection.

    Args:
        collection_name: Name of the existing collection
        embeddings: Embeddings instance (creates default if None)
        location: Qdrant location

    Returns:
        Qdrant vector store instance
    """
    from langchain_qdrant import QdrantVectorStore
    from qdrant_client import QdrantClient

    if embeddings is None:
        embeddings = create_text_embeddings()

    client = QdrantClient(location=location)

    vector_store = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings
    )

    return vector_store


def add_documents_to_store(
    vector_store,
    documents: List[Document]
) -> None:
    """
    Add additional documents to existing vector store.

    Args:
        vector_store: Existing Qdrant vector store
        documents: New documents to add
    """
    vector_store.add_documents(documents)


def create_vector_store_from_chunks(
    chunks: List[Document],
    collection_name: str = "legal_docs"
):
    """
    Convenience function to create vector store directly from chunked documents.

    Args:
        chunks: List of chunked Document objects
        collection_name: Name for the collection

    Returns:
        Qdrant vector store instance ready for retrieval
    """
    embeddings = create_text_embeddings()
    vector_store = create_qdrant_vector_store(
        documents=chunks,
        embeddings=embeddings,
        collection_name=collection_name
    )

    return vector_store
