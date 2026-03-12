# Legal Document Q&A Assistant

A conversational AI assistant that helps users understand legal contracts by answering questions in plain English. Upload any contract, ask questions, and get document-grounded answers instantly.

## Features

- **PDF Document Upload**: Upload one or more legal documents for analysis
- **Natural Language Q&A**: Ask questions in plain English about your contracts
- **Document-Grounded Answers**: All responses are based strictly on your uploaded documents
- **Plain English Simplification**: Request simplified explanations of complex legal language
- **Source Transparency**: View the exact clause used to generate each answer
- **Web Search Fallback**: Get general legal context when documents don't contain relevant information
- **Human-in-the-Loop**: Confirm sensitive clauses before receiving answers

## Tech Stack

- **LangChain & LangGraph**: Agent orchestration and RAG pipeline
- **ChromaDB**: In-memory vector storage for semantic search
- **OpenAI GPT-4o**: LLM for answer generation
- **Streamlit**: Chat interface
- **Tavily**: Web search fallback

## Project Structure

```
├── app.py                    # Streamlit UI entry point
├── graph/
│   ├── state.py              # AgentState TypedDict
│   ├── nodes.py              # LangGraph nodes (8 nodes)
│   └── graph.py              # Graph assembly
├── rag/
│   ├── loader.py             # PDF loading & chunking
│   ├── embeddings.py         # OpenAI embeddings + ChromaDB
│   └── retriever.py          # Retrieval & reranking
├── prompts/
│   └── templates.py          # Prompt templates
├── requirements.txt
└── .env.example
```

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/samin124/RAG-Legal-Document.git
cd RAG-Legal-Document
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
# Edit .env and add your API keys
```

**Required API Keys:**
- [OpenAI API Key](https://platform.openai.com/api-keys)
- [Tavily API Key](https://tavily.com/) (free tier available)

### 5. Run the application
```bash
streamlit run app.py
```

## Usage

1. Upload a PDF legal document using the sidebar
2. Ask questions about your document in the chat
3. Request simplified explanations if needed
4. View source clauses for verification

## Contributors

| Contributor | Role |
|-------------|------|
| [Samin](https://github.com/samin124) | Project Lead & Developer |
| Claude (Anthropic) | AI Pair Programming Assistant |

## License

This project is for educational purposes.

---

*Legal Document Q&A Assistant v1.0*
