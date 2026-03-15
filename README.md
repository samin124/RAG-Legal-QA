# Legal Document Q&A Assistant ⚖️

> An intelligent conversational assistant that simplifies legal contract analysis through natural language understanding and document-grounded responses.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-red.svg)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-green.svg)](https://langchain.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-orange.svg)](https://langchain.com/langgraph)

## Overview

Legal contracts are complex documents filled with jargon that most people struggle to interpret. This assistant bridges that gap by providing an intuitive chat interface where users can upload contracts and ask questions in plain English, receiving accurate, document-grounded answers instantly.

**Built according to the complete PRD specification** with all features implemented.

---

## Key Features

| Feature | Description | Status |
|---------|-------------|--------|
| **📄 Multi-Format Upload** | Upload PDFs, Images (PNG/JPG), DOCX, MD with OCR | ✅ Complete |
| **🔍 Semantic Search** | RAG-powered retrieval with Qdrant vector store | ✅ Complete |
| **🎯 Reranking** | Cohere/Flashrank reranking for precision | ✅ Complete |
| **🤖 Answer Generation** | GPT-4o for document-grounded responses | ✅ Complete |
| **📝 Plain English Mode** | Simplify legal jargon on demand | ✅ Complete |
| **📚 Source Attribution** | View exact clauses used for each response | ✅ Complete |
| **🌐 Web Fallback** | Tavily search when document lacks coverage | ✅ Complete |
| **👤 Human-in-the-Loop** | Confirmation for sensitive clauses | ✅ Complete |
| **🔁 Retry Logic** | Automatic query rephrasing on poor results | ✅ Complete |
| **💬 Conversation Memory** | Multi-turn dialogue with context | ✅ Complete |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          Streamlit UI Layer                               │
│  (File Upload, Chat Interface, Human-in-the-Loop Confirmations)          │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────────────────┐
│                        LangGraph Agent Graph                              │
│                                                                            │
│  ┌──────────┐  ┌────────┐  ┌────────┐  ┌─────────────┐  ┌────────────┐ │
│  │ Retrieve │→ │ Rerank │→ │ Retry  │→ │ Web Confirm │→ │ Web Search │ │
│  └──────────┘  └────────┘  └────────┘  └─────────────┘  └────────────┘ │
│        │                          │               │                       │
│        └──────────────────────────┴───────────────▼──────────────┐       │
│                                             ┌───────────────────┐ │       │
│                                             │   Human Review    │ │       │
│                                             └─────────┬─────────┘ │       │
│                                                       │           │       │
│                                                ┌──────▼──────┐    │       │
│                                                │  Generate   │◄───┘       │
│                                                │   Answer    │            │
│                                                └──────┬──────┘            │
│                                                       │                   │
│                                                ┌──────▼──────┐            │
│                                                │   Check     │            │
│                                                │Clarification│            │
│                                                └──────┬──────┘            │
│                                                       │                   │
│                                                ┌──────▼──────┐            │
│                                                │  Summarize  │            │
│                                                │   Clause    │            │
│                                                └─────────────┘            │
└────────────────────────────────────────────────────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────────────────┐
│                          RAG Components                                   │
│                                                                            │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────────┐ │
│  │   LlamaParse    │  │ Gemini Embeddings│  │   Qdrant Vector Store   │ │
│  │  (PDF + OCR)    │  │  (Text + Images) │  │    (In-Memory/Cloud)    │ │
│  └─────────────────┘  └──────────────────┘  └─────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────────────────┐
│                         External Services                                 │
│                                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │   GPT-4o     │  │    Gemini    │  │    Tavily    │  │   Cohere    │ │
│  │  (Answers)   │  │ (Embeddings) │  │(Web Search)  │  │ (Reranking) │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

### Core Framework
| Component | Technology | Purpose |
|-----------|------------|---------|
| **Agent Orchestration** | LangGraph | State machine for multi-step reasoning |
| **RAG Framework** | LangChain | Document loading, embedding, retrieval |
| **Frontend** | Streamlit | Chat interface and file upload |

### AI/ML Services
| Component | Technology | Purpose |
|-----------|------------|---------|
| **LLM** | OpenAI GPT-4o | Answer generation and query rephrasing |
| **Embeddings** | Google Gemini | Text and multi-modal embeddings |
| **Document Parser** | LlamaParse | PDF parsing with OCR for scanned documents |
| **Reranking** | Cohere Rerank | Precision ranking of retrieved chunks |
| **Web Search** | Tavily Search | External legal context fallback |

### Infrastructure
| Component | Technology | Purpose |
|-----------|------------|---------|
| **Vector Store** | Qdrant | Semantic similarity search |
| **Environment** | Python-dotenv | API key management |

---

## Project Structure

```
Project_Kalim_Sir/
│
├── app.py                      # Main Streamlit application
├── config.py                   # Centralized configuration management
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── Legal_QA_PRD.md             # Complete Product Requirements Document
│
├── graph/                      # LangGraph Agent
│   ├── __init__.py             # Module exports
│   ├── state.py                # TypedDict state schema
│   ├── nodes.py                # All 9 agent nodes with full implementation
│   └── graph.py                # Graph assembly and routing logic
│
├── rag/                        # RAG Pipeline
│   ├── __init__.py             # Module exports
│   ├── loader.py               # PDF loading with LlamaParse + OCR
│   ├── embeddings.py           # Gemini embeddings + Qdrant vector store
│   └── retriever.py            # Semantic search + reranking
│
├── prompts/                    # Prompt Engineering
│   ├── __init__.py             # Module exports
│   └── templates.py            # All prompt templates
│
└── venv/                       # Virtual environment (not in git)
```

---

## Quick Start

### Prerequisites

- **Python 3.10+**
- **Required API Keys:**
  - OpenAI API Key (GPT-4o)
  - Google AI API Key (Gemini)
  - LlamaCloud API Key (LlamaParse)
  - Tavily API Key (Web Search)
- **Optional API Keys:**
  - Cohere API Key (Reranking)
  - Groq API Key (LLM fallback)

### Installation

```bash
# Clone or navigate to the repository
cd Project_Kalim_Sir

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Copy .env.example to .env and add your API keys
cp .env.example .env

# Edit .env with your API keys
# OPENAI_API_KEY=sk-your-key
# GOOGLE_API_KEY=your-key
# LLAMA_CLOUD_API_KEY=llx-your-key
# TAVILY_API_KEY=tvly-your-key
```

### API Key Setup

1. **OpenAI (GPT-4o)** → https://platform.openai.com/api-keys
2. **Google AI (Gemini)** → https://makersuite.google.com/app/apikey
3. **LlamaCloud (LlamaParse)** → https://cloud.llamaindex.ai/
4. **Tavily (Web Search)** → https://tavily.com/
5. **Cohere (Optional)** → https://dashboard.cohere.com/api-keys

### Run Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

---

## Usage

### 1. Upload Documents

1. Click **"Browse files"** in the sidebar
2. Select one or more documents:
   - **PDFs** (.pdf) - Digital or scanned
   - **Images** (.png, .jpg, .jpeg, .bmp, .tiff, .gif) - Photos or screenshots
   - **Word Docs** (.docx) - Microsoft Word files
   - **Markdown** (.md) - Plain text markdown
3. Upload multiple files of different types simultaneously
4. Wait for processing (with OCR for images and scanned PDFs)
5. Click **"💡 Generate Sample Questions"** to see what you can ask
6. Status shows when ready

### 2. Ask Questions

Type natural language questions like:
- "What are the payment terms?"
- "When can I terminate this contract?"
- "What are my liabilities under this agreement?"
- "Explain the non-compete clause in simple terms"

### 3. Review Answers

- **Answer:** The AI-generated response
- **Source:** Click to view the exact clause used
- **Metadata:** Document name, page number, chunk info

### 4. Special Features

**Plain-English Simplification:**
- Ask: *"Can you simplify that?"* or *"Explain in plain English"*
- The system rewrites legal jargon into accessible language

**Web Fallback:**
- If no relevant clause found, system asks to search the web
- Click "Yes" for external legal context
- Clearly labeled as web-sourced

**Sensitive Clause Review:**
- For high-impact clauses (liability, termination), system pauses
- Shows you the retrieved clause
- Asks: "Is this the clause you meant?"
- Proceed or rephrase

---

## Features in Detail

### 1. Document Ingestion (Epic 1)

**Multi-Format Support:**
- **PDFs:** LlamaParse with OCR for both digital and scanned documents
- **Images:** PNG, JPG, JPEG, BMP, TIFF, GIF with OCR (Gemini 2.0 Flash)
- **DOCX:** Native Microsoft Word document parsing
- **Markdown:** Plain text markdown file support
- Upload multiple files of different types simultaneously
- All documents combined into unified searchable knowledge base

**LlamaParse with OCR:**
- Handles both digital and scanned PDFs
- Uses Gemini 2.0 Flash for multi-modal understanding
- Extracts text from images and photos of documents
- Fallback to PyPDF if LlamaParse unavailable

**Chunking:**
- `RecursiveCharacterTextSplitter`
- Default: 1000 chars with 200 char overlap
- Preserves clause and sentence boundaries
- Metadata tracking (source, page, chunk index)

**Question Generation:**
- Analyze uploaded documents with AI
- Generate 5 relevant sample questions
- Helps users understand document content
- Click "💡 Generate Sample Questions" button

### 2. Retrieval & Reranking (Epic 2)

**Semantic Search:**
- Qdrant vector store (in-memory by default)
- Gemini text-embedding-004
- Top-5 initial retrieval for recall

**Reranking:**
- Cohere Rerank or Flashrank
- Cross-encoder models for precision
- Selects single best matching chunk
- Fallback to top retrieved if reranking fails

### 3. Agent Graph (Epic 3)

**9 Nodes:**
1. **Retrieve** - Fetch top-k chunks
2. **Rerank** - Select best match
3. **Retry** - Rephrase query (max 2 attempts)
4. **Web Search Confirm** - Ask user permission
5. **Web Search** - Tavily fallback
6. **Human Review** - Confirm sensitive clauses
7. **Generate Answer** - GPT-4o response
8. **Check Clarification** - Detect simplification requests
9. **Summarize Clause** - Plain-English rewrite

**Routing Logic:**
- Quality-based retry (up to 2 attempts)
- Web search only after user confirmation
- Human review for sensitive clause types
- Conditional simplification

### 4. Answer Generation (Epic 4)

**Document-Grounded:**
- Prompt constrains LLM to use only provided clause
- No hallucination beyond source material
- Explicit instruction against speculation

**Web-Sourced:**
- Different prompt with disclaimers
- Clear indication of external source
- Recommendation to consult attorney

### 5. Web Search Fallback (Epic 5)

**User Confirmation:**
- System pauses before searching web
- Shows message: "No relevant clause found. Search web?"
- Yes/No buttons
- Transparent about external sources

**Tavily Integration:**
- Advanced search depth
- Legal context focus
- Top 3 most relevant results
- Source URLs included

### 6. Human-in-the-Loop (Epic 6)

**Sensitive Clause Detection:**
- Keywords: liability, termination, indemnification, etc.
- Automatic classification
- Triggers confirmation workflow

**Confirmation UI:**
- Shows clause type
- Displays full clause text
- Yes/No buttons
- Option to rephrase

### 7. Conversation Memory (Epic 7)

**Context Preservation:**
- Full chat history in session state
- Last 5 messages included in LLM context
- Follow-up questions resolved correctly
- Pronoun resolution ("what does that mean?")

### 8. Chat UI (Epic 8)

**Streamlit Interface:**
- Clean chat bubbles
- Expandable source sections
- File upload sidebar
- API status indicators
- Reset session button
- Error handling with tracebacks

---

## Configuration

### Environment Variables (.env)

```env
# REQUIRED
OPENAI_API_KEY=sk-your-openai-key
GOOGLE_API_KEY=your-google-ai-key
LLAMA_CLOUD_API_KEY=llx-your-llamacloud-key
TAVILY_API_KEY=tvly-your-tavily-key

# OPTIONAL
COHERE_API_KEY=your-cohere-key
GROQ_API_KEY=your-groq-key

# SETTINGS
ENABLE_OCR=true
DEFAULT_LLM_MODEL=gpt-4o
EMBEDDING_MODEL=models/text-embedding-004
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Qdrant Configuration

By default, Qdrant runs in-memory. For persistent storage:

```env
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your-qdrant-key  # For Qdrant Cloud
```

---

## Development

### Adding New Nodes

1. Define node function in `graph/nodes.py`
2. Add to graph in `graph/graph.py`
3. Update state schema in `graph/state.py` if needed
4. Export in `graph/__init__.py`

### Customizing Prompts

Edit templates in `prompts/templates.py`:
- `LEGAL_QA_PROMPT` - Document-grounded answers
- `WEB_SEARCH_PROMPT` - Web-sourced answers
- `SIMPLIFICATION_PROMPT` - Plain-English rewrites
- `QUERY_REPHRASE_PROMPT` - Retry logic

### Testing

```bash
# Run with test document
streamlit run app.py

# Check logs for debugging
# Node execution logged to console with emojis:
# ✓ Success
# ⚠️ Warning
# ❌ Error
# 🔄 Retry
# ⏸️ Pause (human-in-the-loop)
```

---

## Troubleshooting

### Common Issues

**Issue:** "Missing API keys"
**Solution:** Check .env file is in root directory with all required keys

**Issue:** LlamaParse fails
**Solution:** Falls back to PyPDF automatically. Check LLAMA_CLOUD_API_KEY

**Issue:** Reranking error
**Solution:** Falls back to top retrieved doc. Check COHERE_API_KEY

**Issue:** Web search not working
**Solution:** Check TAVILY_API_KEY is valid

**Issue:** "No vector store available"
**Solution:** Upload a document first

---

## Performance

**Typical Response Times:**
- Document upload: 10-30 seconds (depends on OCR)
- Vector store creation: 5-10 seconds
- Query processing: 3-7 seconds
- Web search (if needed): +2-3 seconds

**Scalability:**
- Max document size: 50 pages (configurable)
- In-memory vector store: Suitable for single user
- For production: Use Qdrant Cloud or self-hosted

---

## Security

- API keys stored in `.env` (not in git)
- No document persistence (session-only)
- No user authentication required
- All data processing in memory
- Clear disclaimers about legal advice

---

## Limitations

- **Not Legal Advice:** For informational purposes only
- **Document Types:** PDF, Images, DOCX, Markdown (English only)
- **Language:** English only
- **Session-Based:** No persistent storage
- **Single User:** Not designed for concurrent users
- **Image Quality:** OCR accuracy depends on image clarity

---

##PRD Compliance

✅ **All PRD Requirements Implemented:**

- Epic 1: Document Ingestion (LlamaParse + OCR)
- Epic 2: Retrieval & Reranking (Qdrant + Cohere)
- Epic 3: Agent Graph (9 nodes, conditional routing)
- Epic 4: Answer Generation (GPT-4o)
- Epic 5: Web Search Fallback (Tavily with confirmation)
- Epic 6: Human-in-the-Loop (Sensitive clause review)
- Epic 7: Conversation Memory (Multi-turn context)
- Epic 8: Chat UI (Streamlit interface)

---

## License

This project is for educational purposes only.

---

## Disclaimer

⚠️ **Important:** This tool is designed to help understand legal documents but does NOT provide legal advice. Always consult with a qualified attorney for legal matters.

---

**Built with ❤️ using LangChain, LangGraph, and Streamlit**
