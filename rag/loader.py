"""
PDF Loading and Chunking
Handles document parsing and text splitting
"""

from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


def load_pdf(file_path: str) -> List[Document]:
    """
    Load and parse a PDF document.

    Args:
        file_path: Path to the PDF file

    Returns:
        List of Document objects, one per page
    """
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    return documents


def load_pdf_from_bytes(file_bytes: bytes, filename: str) -> List[Document]:
    """
    Load PDF from uploaded bytes (for Streamlit uploads).

    Args:
        file_bytes: Raw PDF file bytes
        filename: Original filename for metadata

    Returns:
        List of Document objects
    """
    import tempfile
    import os

    # Write to temp file for PyPDFLoader
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        documents = load_pdf(tmp_path)
        # Add source filename to metadata
        for doc in documents:
            doc.metadata["source"] = filename
        return documents
    finally:
        os.unlink(tmp_path)


def chunk_documents(
    documents: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Document]:
    """
    Split documents into overlapping chunks.

    Args:
        documents: List of Document objects to split
        chunk_size: Target size for each chunk (in characters)
        chunk_overlap: Overlap between consecutive chunks

    Returns:
        List of chunked Document objects
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = text_splitter.split_documents(documents)
    return chunks
