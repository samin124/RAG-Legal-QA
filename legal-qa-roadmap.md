# Legal Document Q&A Assistant — Project Roadmap

---

## Phase 1: Environment Setup & Foundations (Day 1–2)

**Goal:** Get your workspace ready before writing a single line of project code.

- Set up a Python virtual environment
- Install core dependencies:
  - `langchain`, `langgraph`, `langchain-community`
  - `pypdf` or `pdfplumber` (PDF loading)
  - `sentence-transformers` or OpenAI embeddings
  - `chromadb` or `faiss-cpu` (vector store)
  - `python-dotenv` (API key management)
- Set up your `.env` file with your LLM API key (OpenAI / Groq / Gemini)
- Test a basic LangChain LLM call to confirm everything works

---

## Phase 2: Document Ingestion Pipeline (Day 3–4)

**Goal:** Be able to take a PDF and turn it into searchable chunks stored in a vector database.

### Steps:
1. **Load** the PDF using `PyPDFLoader` from LangChain
2. **Split** the document into chunks using `RecursiveCharacterTextSplitter`
   - Recommended: chunk size ~500–800 tokens, overlap ~100
3. **Embed** the chunks using an embedding model
4. **Store** the embeddings in ChromaDB or FAISS
5. Test by retrieving the top-k chunks for a sample query

### Deliverable:
A working script that takes a PDF and saves embeddings locally.

---

## Phase 3: Core RAG Chain (Day 5–6)

**Goal:** Build a basic Retrieve → Answer pipeline using LangChain.

### Steps:
1. Create a **retriever** from your vector store
2. Write a **prompt template** tailored for legal Q&A:
   - "You are a legal assistant. Based only on the provided clauses, answer the question..."
3. Build a `RetrievalQA` or LCEL chain: `retriever | prompt | llm | output_parser`
4. Test with sample legal questions:
   - "What is the termination clause?"
   - "What are the payment terms?"

### Deliverable:
A working Q&A chain that answers questions from an uploaded document.

---

## Phase 4: LangGraph Agent Flow (Day 7–10)

**Goal:** Convert the linear RAG chain into a stateful, multi-node LangGraph agent.

### Graph Architecture:

```
[User Query]
     ↓
[Intent Classification Node]
  - Is this a new question or a follow-up?
     ↓
[Retrieval Node]
  - Fetch top-k relevant clauses from vector store
     ↓
[Answer Generation Node]
  - Generate answer using retrieved context + LLM
     ↓
[Clarification Check Node]
  - Did the user ask for a simpler explanation?
  - If yes → Summarization Node
  - If no → Return Final Answer
     ↓
[Summarization Node] (conditional)
  - Simplify the legal clause in plain English
     ↓
[Final Response]
```

### State Schema (TypedDict):
```python
class AgentState(TypedDict):
    query: str
    chat_history: list
    retrieved_docs: list
    answer: str
    needs_clarification: bool
```

### Nodes to Build:
| Node | Responsibility |
|---|---|
| `classify_intent` | Detect new query vs follow-up |
| `retrieve_docs` | Vector store similarity search |
| `generate_answer` | LLM answers based on context |
| `check_clarification` | Router: needs simplification? |
| `summarize_clause` | Plain-English simplification |

### Deliverable:
A LangGraph graph that runs end-to-end for a question with conditional routing.

---

## Phase 5: Memory & Follow-up Support (Day 11–12)

**Goal:** Support multi-turn conversations so users can ask follow-up questions.

- Add `chat_history` to the agent state
- Pass previous Q&A pairs as context into the prompt
- Handle questions like:
  - "Can you explain that in simpler terms?"
  - "What does that mean for me as a contractor?"
- Use `ConversationBufferMemory` or manage history manually in state

### Deliverable:
The agent remembers the last 3–5 exchanges and uses them for context.

---

## Phase 6: Chat UI with Streamlit (Day 13–15)

**Goal:** Build a clean, usable frontend for the agent.

### Features:
- PDF upload widget → triggers ingestion pipeline
- Chat input box → sends query to LangGraph agent
- Chat history display (user + assistant bubbles)
- "Retrieved Clauses" expander showing source sections
- Simple "Summarize this clause" button

### Recommended Stack:
- **Streamlit** (fastest for prototyping, no frontend knowledge needed)
- Optional later: Gradio or a basic FastAPI + HTML frontend

### Deliverable:
A Streamlit app where you can upload a PDF and chat with it.

---

## Phase 7: Testing & Refinement (Day 16–18)

**Goal:** Make sure the system actually works on real legal documents.

### Test Cases to Cover:
- Short contract (1–2 pages) vs long agreement (20+ pages)
- Ambiguous questions ("What happens if I break the contract?")
- Questions outside the document scope ("What is GDPR?" → should say "not found in document")
- Follow-up and clarification requests

### Things to Tune:
- Chunk size and overlap
- Number of retrieved docs (k value)
- Prompt wording for legal context
- Guardrail: answer only from document, not general LLM knowledge

---

## Phase 8: Final Polish & Submission (Day 19–21)

**Goal:** Package everything cleanly.

- Write a clear `README.md` with setup instructions
- Record a short demo (Loom or screen recording)
- Push to GitHub with a clean folder structure:

```
legal-qa-assistant/
├── app.py               # Streamlit UI
├── graph/
│   ├── nodes.py         # All LangGraph nodes
│   ├── state.py         # AgentState TypedDict
│   └── graph.py         # Graph assembly
├── rag/
│   ├── loader.py        # PDF loading & chunking
│   ├── embeddings.py    # Embedding + vector store
│   └── retriever.py     # Retrieval logic
├── prompts/
│   └── templates.py     # All prompt templates
├── .env.example
├── requirements.txt
└── README.md
```

---

## Summary Timeline

| Week | Focus |
|---|---|
| Week 1 | Setup + Document Ingestion + Core RAG Chain |
| Week 2 | LangGraph Agent + Memory + Conditional Routing |
| Week 3 | Streamlit UI + Testing + Polish + Submission |

---

## Key Learning You'll Reinforce

| Concept | Where It's Used |
|---|---|
| Document loaders & chunking | Phase 2 |
| Embeddings & vector stores | Phase 2 |
| LCEL chains | Phase 3 |
| LangGraph state & nodes | Phase 4 |
| Conditional edges / routing | Phase 4 |
| Conversation memory | Phase 5 |
| Prompt engineering | Phases 3, 4, 5 |
| RAG (from Coursera) | Phases 2–5 |
