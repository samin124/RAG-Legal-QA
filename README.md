# Legal Document Q&A Assistant

> An intelligent conversational assistant that simplifies legal contract analysis through natural language understanding and document-grounded responses.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-red.svg)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-green.svg)](https://langchain.com)

## Overview

Legal contracts are complex documents filled with jargon that most people struggle to interpret. This assistant bridges that gap by providing an intuitive chat interface where users can upload contracts and ask questions in plain English, receiving accurate, document-grounded answers instantly.

## Key Features

| Feature | Description |
|---------|-------------|
| **Document Ingestion** | Upload and process multiple PDF legal documents |
| **Semantic Search** | RAG-powered retrieval with reranking for precise clause matching |
| **Grounded Responses** | Answers strictly based on uploaded document content |
| **Plain English Mode** | Simplify complex legal terminology on demand |
| **Source Attribution** | View exact clauses used for each response |
| **Web Fallback** | Supplementary legal context when documents lack coverage |
| **Human Review** | Confirmation workflow for sensitive clause interpretation |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit UI                             │
├─────────────────────────────────────────────────────────────────┤
│                      LangGraph Agent                            │
│  ┌──────────┐  ┌────────┐  ┌───────────┐  ┌──────────────────┐ │
│  │ Retrieve │→ │ Rerank │→ │ Generate  │→ │ Check/Summarize  │ │
│  └──────────┘  └────────┘  └───────────┘  └──────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  ChromaDB          OpenAI GPT-4o          Tavily Search         │
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Agent Framework | LangChain, LangGraph |
| Vector Store | ChromaDB |
| LLM | OpenAI GPT-4o |
| Embeddings | OpenAI text-embedding-3-small |
| Reranking | Cohere / Flashrank |
| Web Search | Tavily API |
| Frontend | Streamlit |

## Project Structure

```
RAG-Legal-QA/
├── app.py                    # Application entry point
├── graph/
│   ├── state.py              # Agent state schema
│   ├── nodes.py              # Pipeline nodes
│   └── graph.py              # Graph orchestration
├── rag/
│   ├── loader.py             # Document processing
│   ├── embeddings.py         # Vector operations
│   └── retriever.py          # Search & reranking
├── prompts/
│   └── templates.py          # Prompt engineering
├── requirements.txt
├── .env.example
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API Key
- Tavily API Key (optional)

### Installation

```bash
# Clone repository
git clone https://github.com/samin124/RAG-Legal-QA.git
cd RAG-Legal-QA

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your API keys to .env
```

### Run Application

```bash
streamlit run app.py
```

## Configuration

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key      # Optional
COHERE_API_KEY=your_cohere_key      # Optional
```

## Usage

1. **Upload** - Add PDF documents via the sidebar
2. **Query** - Ask questions in natural language
3. **Review** - Verify answers against source clauses
4. **Simplify** - Request plain English explanations

## Roadmap

- [ ] Document ingestion pipeline
- [ ] Core RAG chain implementation
- [ ] LangGraph agent with conditional routing
- [ ] Conversation memory
- [ ] Streamlit chat interface
- [ ] Testing & optimization

## Author

**Samin** - [@samin124](https://github.com/samin124)

## License

This project is for educational purposes.
