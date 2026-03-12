"""
Legal Document Q&A Assistant
Main Streamlit Application Entry Point
"""

import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Legal Document Q&A Assistant",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar - Document Upload
with st.sidebar:
    st.header("Document Upload")
    uploaded_files = st.file_uploader(
        "Upload PDF documents",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload one or more legal documents to analyze"
    )

    if uploaded_files:
        st.success(f"{len(uploaded_files)} document(s) uploaded")
        for file in uploaded_files:
            st.write(f"- {file.name}")

    st.divider()
    st.caption("Legal Document Q&A Assistant v1.0")

# Main chat interface
st.title("Legal Document Q&A Assistant")
st.markdown("Upload a contract and ask questions in plain English.")

# Check for API key
if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY").startswith("sk-demo"):
    st.warning(
        "Please set your OpenAI API key in the `.env` file to enable the assistant."
    )
    st.info(
        "Get your API key at: https://platform.openai.com/api-keys"
    )

# Chat interface placeholder
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about your document..."):
    if not uploaded_files:
        st.error("Please upload a document first.")
    else:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Placeholder response (will be replaced with actual agent logic)
        with st.chat_message("assistant"):
            st.markdown("*Agent integration coming soon...*")
            st.session_state.messages.append({
                "role": "assistant",
                "content": "*Agent integration coming soon...*"
            })
