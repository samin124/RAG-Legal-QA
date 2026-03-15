"""
Legal Document Q&A Assistant - Modern ChatGPT-Style UI
========================================================
Redesigned with dark theme, chat history sidebar, and modern interface
"""

import streamlit as st
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import uuid

# Load environment variables
load_dotenv()

# Import configuration
from config import config

# Import RAG components
from rag import process_uploaded_document, create_vector_store_from_chunks, add_documents_to_store

# Import Graph components
from graph import create_graph, get_initial_state, AgentState

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Legal AI Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

# Chat conversations storage
if "conversations" not in st.session_state:
    st.session_state.conversations = {}

# Current conversation ID
if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None

# Current messages (for active conversation)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Vector store
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

# Processed files
if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()

# Agent state
if "agent_state" not in st.session_state:
    st.session_state.agent_state = get_initial_state()

# Human-in-the-loop flags
if "pending_confirmation" not in st.session_state:
    st.session_state.pending_confirmation = False

if "pending_human_review" not in st.session_state:
    st.session_state.pending_human_review = False

# ============================================================================
# MODERN DARK THEME CSS
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Reset */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hide Streamlit branding */
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Main app background - Dark theme */
    .stApp {
        background: #1a1a1a !important;
    }

    /* Container */
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* Sidebar - Chat History */
    [data-testid="stSidebar"] {
        background: #0d0d0d !important;
        border-right: 1px solid #2a2a2a !important;
        padding: 1rem !important;
    }

    [data-testid="stSidebar"] * {
        color: #e5e5e5 !important;
    }

    /* Chat messages */
    .stChatMessage {
        background: transparent !important;
        padding: 2rem 1rem !important;
        margin: 1rem 0 !important;
    }

    /* User messages */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageContent"]:first-child:last-child) {
        background: #1a1a1a !important;
    }

    [data-testid="stChatMessage"]:has([data-testid="stChatMessageContent"]:first-child:last-child) [data-testid="stChatMessageContent"] {
        background: #2d2d2d !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        padding: 18px 24px !important;
        border: 1px solid #3a3a3a !important;
        line-height: 1.6 !important;
    }

    /* Assistant messages */
    .stChatMessage:not(:has([data-testid="stChatMessageContent"]:first-child:last-child)) [data-testid="stChatMessageContent"] {
        background: #1a1a1a !important;
        color: #e5e5e5 !important;
        border-radius: 12px !important;
        padding: 18px 24px !important;
        border: 1px solid #2a2a2a !important;
        line-height: 1.6 !important;
    }

    /* Chat input */
    [data-testid="stChatInput"] {
        background: #1a1a1a !important;
        border-top: 1px solid #2a2a2a !important;
        padding: 1.5rem 0 !important;
    }

    [data-testid="stChatInput"] > div {
        background: #2d2d2d !important;
        border: 1px solid #3a3a3a !important;
        border-radius: 24px !important;
    }

    [data-testid="stChatInput"] textarea {
        background: #2d2d2d !important;
        color: #ffffff !important;
        border: none !important;
        font-size: 15px !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #808080 !important;
    }

    /* Buttons */
    .stButton > button {
        background: #2d2d2d !important;
        color: #ffffff !important;
        border: 1px solid #3a3a3a !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }

    .stButton > button:hover {
        background: #3a3a3a !important;
        border-color: #4a4a4a !important;
    }

    /* Primary button */
    .stButton > button[kind="primary"] {
        background: #0066ff !important;
        border: none !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: #0052cc !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #2d2d2d !important;
        border: 2px dashed #3a3a3a !important;
        border-radius: 12px !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #2d2d2d !important;
        border: 1px solid #3a3a3a !important;
        color: #e5e5e5 !important;
        border-radius: 8px !important;
    }

    .streamlit-expanderContent {
        background: #2d2d2d !important;
        border: 1px solid #3a3a3a !important;
        color: #e5e5e5 !important;
    }

    /* Text colors */
    h1, h2, h3, h4, h5, h6, p, span, div {
        color: #e5e5e5 !important;
    }

    /* Message spacing */
    [data-testid="stChatMessageContent"] p {
        margin-bottom: 0.8rem !important;
    }

    [data-testid="stChatMessageContent"] ol,
    [data-testid="stChatMessageContent"] ul {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
        padding-left: 1.5rem !important;
    }

    [data-testid="stChatMessageContent"] li {
        margin-bottom: 0.5rem !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #1a1a1a;
    }

    ::-webkit-scrollbar-thumb {
        background: #3a3a3a;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #4a4a4a;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_new_conversation():
    """Create a new conversation"""
    conv_id = str(uuid.uuid4())
    st.session_state.conversations[conv_id] = {
        "id": conv_id,
        "title": "New Chat",
        "messages": [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    st.session_state.current_conversation_id = conv_id
    st.session_state.messages = []
    st.rerun()

def load_conversation(conv_id):
    """Load a conversation"""
    if conv_id in st.session_state.conversations:
        st.session_state.current_conversation_id = conv_id
        st.session_state.messages = st.session_state.conversations[conv_id]["messages"]
        st.rerun()

def save_current_conversation():
    """Save current messages to conversation"""
    if st.session_state.current_conversation_id:
        conv_id = st.session_state.current_conversation_id
        st.session_state.conversations[conv_id]["messages"] = st.session_state.messages
        st.session_state.conversations[conv_id]["updated_at"] = datetime.now().isoformat()

        # Update title from first message
        if st.session_state.messages and len(st.session_state.messages) > 0:
            first_msg = st.session_state.messages[0]["content"]
            title = first_msg[:50] + "..." if len(first_msg) > 50 else first_msg
            st.session_state.conversations[conv_id]["title"] = title

def validate_api_keys():
    """Validate that all required API keys are configured"""
    missing_keys = config.get_missing_required_keys()
    if missing_keys:
        st.error(f"⚠️ Missing API keys: {', '.join(missing_keys)}")
        return False
    return True

def display_source_info(source_type: str, source_docs=None):
    """Display source information below the answer"""
    if source_type == "web":
        st.markdown("""
        <div style='margin-top: 16px; padding-top: 12px; border-top: 1px solid #2a2a2a;'>
            <p style='font-size: 11px; color: #888; margin: 0;'>
                🌐 Source: <span style='color: #60a5fa;'>Web Search</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
    elif source_type == "document" and source_docs and len(source_docs) > 0:
        # Get first source document
        doc = source_docs[0]
        page_num = doc.metadata.get("page", "Unknown")
        source_text = doc.page_content

        # Show source header with page number
        st.markdown(f"""
        <div style='margin-top: 16px; padding-top: 12px; border-top: 1px solid #2a2a2a;'>
            <p style='font-size: 11px; color: #888; margin-bottom: 8px;'>
                📄 Source: <span style='color: #4ade80;'>Page {page_num}</span>
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Show source text in expandable section
        with st.expander("📖 View source text from document", expanded=False):
            st.markdown(f"""
            <div style='background: #0d0d0d; padding: 16px; border-radius: 8px; border: 1px solid #2a2a2a;'>
                <p style='font-size: 13px; color: #b0b0b0; line-height: 1.6; margin: 0; white-space: pre-wrap;'>{source_text}</p>
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - CHAT HISTORY
# ============================================================================

with st.sidebar:
    # Header
    st.markdown("<h2 style='margin-bottom: 1rem;'>⚖️ Legal AI</h2>", unsafe_allow_html=True)

    # New Chat button
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        create_new_conversation()

    st.markdown("---")

    # Documents Section
    st.markdown("### 📁 Documents")

    uploaded_files = st.file_uploader(
        "Upload documents",
        type=["pdf", "png", "jpg", "jpeg", "docx", "md"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        new_files = [f for f in uploaded_files if f.name not in st.session_state.processed_files]

        if new_files and validate_api_keys():
            from rag.loader import process_uploaded_document
            all_new_chunks = []

            for file in new_files:
                with st.spinner(f"Processing {file.name}..."):
                    try:
                        chunks = process_uploaded_document(
                            file_bytes=file.read(),
                            filename=file.name,
                            chunk_size=config.document.chunk_size,
                            chunk_overlap=config.document.chunk_overlap,
                            use_ocr=config.document.enable_ocr
                        )
                        all_new_chunks.extend(chunks)
                        st.session_state.processed_files.add(file.name)
                    except Exception as e:
                        st.error(f"Error: {file.name}")

            if all_new_chunks:
                with st.spinner("Creating embeddings..."):
                    try:
                        if st.session_state.vector_store is None:
                            st.session_state.vector_store = create_vector_store_from_chunks(all_new_chunks)
                        else:
                            add_documents_to_store(st.session_state.vector_store, all_new_chunks)
                        st.success("✓ Ready")
                    except Exception as e:
                        st.error("Error processing")

    if st.session_state.processed_files:
        st.success(f"✓ {len(st.session_state.processed_files)} document(s)")

    st.markdown("---")

    # Chat History
    st.markdown("### 💬 Recent Chats")

    if st.session_state.conversations:
        # Sort by updated_at
        sorted_convs = sorted(
            st.session_state.conversations.items(),
            key=lambda x: x[1]["updated_at"],
            reverse=True
        )

        for conv_id, conv in sorted_convs[:10]:  # Show last 10
            is_active = conv_id == st.session_state.current_conversation_id
            button_type = "primary" if is_active else "secondary"

            if st.button(
                f"{'📍' if is_active else '💬'} {conv['title']}",
                key=f"conv_{conv_id}",
                use_container_width=True,
                type=button_type
            ):
                load_conversation(conv_id)
    else:
        st.caption("No conversations yet")

    # Footer
    st.markdown("---")
    st.caption("Powered by AI")
    st.caption("© 2024 Legal AI Assistant")

# ============================================================================
# MAIN CHAT AREA
# ============================================================================

# Create conversation if none exists
if not st.session_state.current_conversation_id:
    create_new_conversation()

# Header
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.markdown("<h3>Legal Document Assistant</h3>", unsafe_allow_html=True)
with col2:
    if st.button("🔄 Clear Chat"):
        st.session_state.messages = []
        save_current_conversation()
        st.rerun()
with col3:
    if st.button("📥 Export"):
        export_text = "\n\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])
        st.download_button("Download", export_text, "chat.txt", "text/plain")

st.markdown("---")

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Show answer first
        st.markdown(message["content"])

        # Show source info below for assistant messages
        if message["role"] == "assistant" and "source" in message:
            source_docs = message.get("source_docs")
            display_source_info(message["source"], source_docs)

# Chat input
if prompt := st.chat_input("Ask me anything about your documents..."):
    if not st.session_state.processed_files:
        st.warning("⚠️ Please upload a document first")
        st.stop()

    if not validate_api_keys():
        st.stop()

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Update agent state
    st.session_state.agent_state["query"] = prompt
    st.session_state.agent_state["vector_store"] = st.session_state.vector_store
    st.session_state.agent_state["chat_history"] = st.session_state.messages.copy()

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                graph = create_graph()
                result = graph.invoke(st.session_state.agent_state)

                answer = result.get("answer", "I couldn't find relevant information.")
                source = result.get("source", "document")  # Get source type from result
                source_docs = result.get("reranked_docs", [])

                # Display answer first
                st.markdown(answer)

                # Display source info below
                display_source_info(source, source_docs)

                # Save message with source information
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "source": source,
                    "source_docs": source_docs
                })
                save_current_conversation()

            except Exception as e:
                error_msg = "⚠️ Something went wrong. Please try again."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Disclaimer
st.markdown("---")
st.caption("⚠️ This tool provides information only. Consult a qualified attorney for legal advice.")
