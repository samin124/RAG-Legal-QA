# Legal Document Q&A Assistant — Product Requirements Document

**Version:** 1.0
**Status:** Draft — For Review
**Target Release:** 3 Weeks from Kickoff
**Platform:** Web Application (Streamlit)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Goals & Non-Goals](#goals--non-goals)
4. [User Personas](#user-personas)
5. [Epic 1 — Document Ingestion](#epic-1--document-ingestion)
6. [Epic 2 — Retrieval & Reranking Pipeline](#epic-2--retrieval--reranking-pipeline)
7. [Epic 3 — Agent Graph & Routing Logic](#epic-3--agent-graph--routing-logic)
8. [Epic 4 — Answer Generation & Simplification](#epic-4--answer-generation--simplification)
9. [Epic 5 — Web Search Fallback](#epic-5--web-search-fallback)
10. [Epic 6 — Human-in-the-Loop Review](#epic-6--human-in-the-loop-review)
11. [Epic 7 — Conversation Memory](#epic-7--conversation-memory)
12. [Epic 8 — Chat UI (Streamlit)](#epic-8--chat-ui-streamlit)
13. [Non-Functional Requirements](#non-functional-requirements)
14. [Tech Stack Reference](#tech-stack-reference)
15. [State Schema Reference](#state-schema-reference)
16. [Development Timeline](#development-timeline)
17. [Risks & Mitigations](#risks--mitigations)
18. [Future Considerations](#future-considerations)

---

## Executive Summary

Legal contracts are dense, jargon-heavy documents that most people cannot interpret without professional help. Individuals routinely sign agreements containing clauses on liability, termination, and payment without fully understanding their implications — often resulting in financial or legal consequences they did not anticipate.

The **Legal Document Q&A Assistant** addresses this gap by providing a conversational interface through which any user can upload a contract and ask plain-language questions about it. The system retrieves the most relevant clause from the document, generates a grounded natural-language answer, and — on request — re-states the answer in simplified English.

> **Core Value Proposition:** Upload any contract. Ask any question. Get a clear, document-grounded answer — instantly, in plain English.

---

## Problem Statement

### The Problem

Reading and interpreting legal documents is a significant barrier for the majority of people who are not trained lawyers:

- **Complexity** — Legal language is inaccessible to non-lawyers.
- **Time cost** — Reviewing a full contract manually takes hours.
- **Hidden risk** — Important clauses on liability, indemnification, and termination are often buried.
- **Cost of counsel** — Professional legal review is expensive and disproportionate for everyday contracts.
- **Gap in tooling** — No simple consumer-grade tool exists for interactive document-level Q&A on legal contracts.

### Who is Affected

Freelancers, tenants, new employees, small business owners, students, and anyone who signs contracts without a legal background.

---

## Goals & Non-Goals

### Goals

- Enable any user to upload a PDF legal document and ask questions in natural language.
- Return answers strictly grounded in the content of the uploaded document.
- Support follow-up questions and multi-turn conversation within a session.
- Provide plain-English simplification of any legal clause on request.
- Show the exact source clause alongside every answer for user verification.
- Fall back gracefully to web-based legal context when the document contains no relevant clause.
- Confirm retrieved clauses with the user before answering sensitive topics.

### Non-Goals

- Does **not** provide professional legal advice or replace a licensed attorney.
- Does **not** store documents or conversation history between sessions.
- Does **not** support document editing, annotation, or clause redlining.
- **No** user authentication, accounts, or subscription management in v1.0.
- **Not** designed for bulk document processing or enterprise ingestion pipelines.

---

## User Personas

| Persona | Background | Primary Need |
|---|---|---|
| The Independent Freelancer | Designer/developer reviewing a client services agreement | Understand payment terms and IP ownership clauses quickly |
| The Renter | Individual reviewing a residential lease | Understand termination, deposit, and maintenance responsibilities |
| The First-Time Employee | New hire reading an employment contract or NDA | Understand non-compete, confidentiality, and notice period obligations |
| The Small Business Owner | Entrepreneur reviewing a vendor/partnership agreement | Identify liability caps, indemnification, and auto-renewal terms |
| The Researcher / Student | Academic reviewing a publishing or licensing agreement | Understand rights assignment, exclusivity, and royalty terms |

---

---

# EPICS

---

## Epic 1 — Document Ingestion

**Goal:** Allow users to upload one or more PDF legal documents and have them automatically processed, chunked, embedded, and indexed for semantic retrieval within the session.

---

### Story 1.1 — PDF Upload via Sidebar

**As a** user,
**I want to** upload a PDF file from the sidebar,
**So that** I can begin asking questions about my document.

**Acceptance Criteria:**
- A file uploader widget is visible in the Streamlit sidebar.
- Only PDF files are accepted; non-PDF uploads show a clear error message.
- Corrupted or unreadable PDFs display a user-friendly error.
- After upload, the filename is listed in the sidebar as confirmation.
- Multiple PDFs can be uploaded in the same session.

---

### Story 1.2 — Document Parsing and Loading

**As a** system,
**I want to** parse the uploaded PDF into raw text,
**So that** the content can be processed for retrieval.

**Acceptance Criteria:**
- PyPDFLoader successfully extracts text from standard PDF formats.
- Multi-page documents are fully parsed page by page.
- Parsing completes without crashing on documents up to 50 pages.
- Extracted text is available in memory for the chunking step.

---

### Story 1.3 — Text Chunking

**As a** system,
**I want to** split the parsed document text into overlapping chunks,
**So that** semantically meaningful segments can be individually embedded and retrieved.

**Acceptance Criteria:**
- RecursiveCharacterTextSplitter is used for chunking.
- Chunk size and overlap are configurable via parameters.
- Chunks preserve sentence and clause boundaries where possible.
- Chunk metadata includes the source document name.

---

### Story 1.4 — Embedding and Vector Store Indexing

**As a** system,
**I want to** embed all chunks and store them in a vector store,
**So that** they can be retrieved by semantic similarity at query time.

**Acceptance Criteria:**
- Chunks are embedded using OpenAIEmbeddings or HuggingFaceEmbeddings.
- All embedded chunks are indexed into a Chroma in-memory vector store.
- The vector store is session-scoped and does not persist after the session ends.
- Indexing completes within 30 seconds for documents up to 50 pages.
- A loading indicator or status message is shown to the user during ingestion.

---

### Story 1.5 — Multi-Document Support

**As a** user,
**I want to** upload more than one document in a session,
**So that** I can query across multiple contracts at once.

**Acceptance Criteria:**
- MultiVectorRetriever is used to index and query across all uploaded documents.
- Each chunk retains its source document identifier in metadata.
- Queries return results from any of the uploaded documents.
- The sidebar lists all currently uploaded documents.

---

---

## Epic 2 — Retrieval & Reranking Pipeline

**Goal:** For any user query, retrieve the most semantically relevant document chunks and select the single best-matching clause using a reranking model.

---

### Story 2.1 — Semantic Retrieval from Vector Store

**As a** system,
**I want to** search the vector store for chunks most relevant to the user's query,
**So that** the most relevant document content is surfaced as candidates for the answer.

**Acceptance Criteria:**
- The Retrieve node searches the Chroma vector store using the user's query.
- Top-K semantically similar chunks are returned as candidates.
- Retrieved chunks are stored in the `retrieved_docs` state field.
- Retrieval completes without error even when the vector store is empty.

---

### Story 2.2 — Reranking Retrieved Chunks

**As a** system,
**I want to** re-score all retrieved chunks using a reranking model,
**So that** the single most relevant clause is passed to the answer generation step.

**Acceptance Criteria:**
- CohereRerank or FlashrankRerank re-scores all retrieved candidates.
- The single top-ranked chunk overwrites `retrieved_docs` with `reranked_docs`.
- Loosely related or low-relevance chunks are discarded before reaching the LLM.
- Reranking completes without blocking the response for more than 3 seconds.

---

### Story 2.3 — Automatic Query Retry on Poor Results

**As a** system,
**I want to** automatically rephrase the query and retry retrieval when results are low quality,
**So that** the system recovers gracefully from poor initial retrieval without user intervention.

**Acceptance Criteria:**
- The Retry node evaluates whether reranked results meet a quality threshold.
- If below threshold and retry count < 2, the query is rephrased and Retrieve is re-invoked.
- The `retry_count` state field is incremented on each retry (maximum: 2).
- After 2 failed retries, the system proceeds to the Web Search fallback path.
- The user is not shown any indication of internal retry attempts.

---

---

## Epic 3 — Agent Graph & Routing Logic

**Goal:** Implement the full LangGraph stateful agent with all 8 nodes, conditional routing edges, and a shared TypedDict state schema.

---

### Story 3.1 — Define State Schema

**As a** developer,
**I want to** define a TypedDict state schema shared across all agent nodes,
**So that** all fields are consistently typed and accessible throughout the graph.

**Acceptance Criteria:**
- A TypedDict class defines all state fields listed in the State Schema Reference section.
- All node functions read and write exclusively to this shared state object.
- State is initialized at the start of each user query turn.
- Chat history persists across turns within the same session.

---

### Story 3.2 — Build the StateGraph with All 8 Nodes

**As a** developer,
**I want to** define the StateGraph with all nodes connected by edges,
**So that** the agent can execute the full retrieval-to-answer pipeline.

**Acceptance Criteria:**
- StateGraph includes all 8 nodes: Retrieve, Rerank, Retry, Web Search, Human Review, Generate Answer, Check Clarification, Summarize Clause.
- Unconditional edges connect nodes that always fire in sequence.
- Conditional edges implement the 4 routing decisions described below.
- The graph compiles without errors.

---

### Story 3.3 — Conditional Routing: Retry vs Proceed

**As a** system,
**I want to** route to Retry when reranked results are below threshold,
**So that** the system attempts to improve retrieval quality before generating an answer.

**Acceptance Criteria:**
- After the Rerank node, a conditional edge evaluates result quality.
- If quality is below threshold AND `retry_count` < 2, route to Retry.
- Otherwise, proceed to the Web Search check.

---

### Story 3.4 — Conditional Routing: Document vs Web Search

**As a** system,
**I want to** route to Web Search only when no relevant clause is found in the document,
**So that** web results supplement rather than replace document-grounded answers.

**Acceptance Criteria:**
- After Rerank/Retry, a conditional edge checks whether a usable clause exists.
- If a clause is found, skip Web Search and proceed to Human Review check.
- If no clause is found, invoke the Web Search node.

---

### Story 3.5 — Conditional Routing: Sensitive Clause Detection

**As a** system,
**I want to** detect sensitive clause types and route to Human Review,
**So that** users confirm the right clause before a legally significant answer is generated.

**Acceptance Criteria:**
- A pre-defined list of sensitive clause categories is maintained (liability, termination, indemnification, governing law, etc.).
- The clause type is detected from the retrieved chunk's content or metadata.
- If sensitive, route to Human Review. Otherwise proceed to Generate Answer.

---

### Story 3.6 — Conditional Routing: Clarification Detection

**As a** system,
**I want to** detect when the user wants a simpler explanation after an answer is generated,
**So that** the Summarize Clause node is triggered only when needed.

**Acceptance Criteria:**
- The Check Clarification node analyses the user's follow-up intent.
- If simplification is requested, `needs_clarification` is set to true and the graph routes to Summarize Clause.
- Otherwise, the current answer is returned as the final response.

---

---

## Epic 4 — Answer Generation & Simplification

**Goal:** Generate accurate, document-grounded answers using an LLM and provide plain-English rewrites on request.

---

### Story 4.1 — Prompt Construction

**As a** system,
**I want to** construct a structured prompt combining the query, top clause, and chat history,
**So that** the LLM has all required context to produce a grounded, coherent answer.

**Acceptance Criteria:**
- ChatPromptTemplate constructs the prompt with three inputs: user question, top retrieved clause (or web result), and `chat_history`.
- The prompt explicitly instructs the LLM to answer only from the provided clause.
- The prompt includes a system instruction forbidding speculation or hallucination beyond the source material.

---

### Story 4.2 — LLM Answer Generation

**As a** system,
**I want to** call the LLM with the constructed prompt and store the response,
**So that** a grounded answer is available to return to the user.

**Acceptance Criteria:**
- The Generate Answer node calls OpenAI GPT-4o (default) or Groq as a fallback.
- The generated answer is stored in the `answer` state field.
- The `source` field is set to "document" or "web" based on the input used.
- The node handles API errors gracefully without crashing the application.

---

### Story 4.3 — Plain-English Summarization

**As a** user,
**I want to** ask for a simpler explanation of any answer,
**So that** I can understand legal language without any prior knowledge.

**Acceptance Criteria:**
- The Summarize Clause node is invoked only when `needs_clarification` is true.
- The node rewrites the existing `answer` in plain, jargon-free English.
- The simplified text replaces the prior answer as the final response shown in the UI.
- The simplified answer preserves the factual content and meaning of the original.

---

---

## Epic 5 — Web Search Fallback

**Goal:** When the uploaded document contains no relevant clause, fetch external legal context from the web to supplement the answer.

---

### Story 5.1 — Tavily Web Search Integration

**As a** system,
**I want to** call the Tavily Search API when document retrieval yields no usable result,
**So that** users receive helpful legal context even when their document doesn't cover the topic.

**Acceptance Criteria:**
- The Web Search node is only invoked after document retrieval has failed.
- The Tavily Search API is called with the user's rephrased query.
- Results are stored in `web_search_results`.
- The API key is loaded from environment variables and never hardcoded.

---

### Story 5.2 — Web Result Passed to Answer Generation

**As a** system,
**I want to** pass web search results to the Generate Answer node as the context input,
**So that** the LLM can produce an answer based on external legal information.

**Acceptance Criteria:**
- When `web_search_results` is populated, it is used as the context in the LLM prompt instead of a document clause.
- The `source` field is set to "web".
- The answer is generated with the same quality and structure as a document-sourced answer.

---

---

## Epic 6 — Human-in-the-Loop Review

**Goal:** For sensitive clause types, pause the agent and ask the user to confirm the retrieved clause before generating an answer.

---

### Story 6.1 — Sensitive Clause Detection Logic

**As a** system,
**I want to** classify whether a retrieved clause belongs to a sensitive category,
**So that** high-stakes clauses trigger user confirmation before an answer is given.

**Acceptance Criteria:**
- A configurable list of sensitive clause categories is defined (e.g. liability, termination, indemnification, governing law, arbitration, penalty).
- Clause classification is based on keyword matching or LLM-based classification of the retrieved chunk.
- The classification result determines whether Human Review routing is triggered.

---

### Story 6.2 — Agent Pause and User Confirmation UI

**As a** user,
**I want to** be shown the retrieved clause and asked to confirm it before the system answers,
**So that** I can verify the system is referencing the correct part of the document.

**Acceptance Criteria:**
- When Human Review is triggered, the graph pauses execution.
- The retrieved clause text is displayed in a highlighted box in the chat UI.
- The system asks: *"Is this the clause you meant?"* with Yes and No options.
- Selecting **Yes** sets `human_confirmed` to true and resumes the graph to Generate Answer.
- Selecting **No** prompts the user to rephrase their question and re-initiates the flow.

---

---

## Epic 7 — Conversation Memory

**Goal:** Maintain a session-scoped conversation history so the agent can handle contextual follow-up questions without requiring the user to repeat prior context.

---

### Story 7.1 — Chat History Accumulation

**As a** system,
**I want to** append each Q&A pair to a running conversation history,
**So that** the LLM has context from earlier in the conversation for follow-up questions.

**Acceptance Criteria:**
- Each completed Q&A pair (user query + assistant answer) is appended to `chat_history` after generation.
- `chat_history` is included in every subsequent LLM prompt call.
- History is maintained for the duration of the session only.
- History does not persist after the user closes or refreshes the application.

---

### Story 7.2 — Contextual Follow-Up Question Handling

**As a** user,
**I want to** ask follow-up questions that reference my previous questions,
**So that** I don't have to repeat context with every message.

**Acceptance Criteria:**
- The LLM correctly resolves pronouns and references to earlier answers using `chat_history`.
- Follow-up questions such as "What does that mean?" or "Can you simplify the last answer?" are handled correctly.
- The simplification follow-up correctly targets the most recent answer.

---

---

## Epic 8 — Chat UI (Streamlit)

**Goal:** Build the complete Streamlit-based chat interface including the sidebar upload panel, chat window, source display, and human review confirmation components.

---

### Story 8.1 — Main Chat Window

**As a** user,
**I want to** see a clean chat interface with my messages and the assistant's responses,
**So that** I can have a natural conversation about my document.

**Acceptance Criteria:**
- User messages appear on the right; assistant messages on the left.
- The full message history for the session is visible and scrollable.
- A text input at the bottom allows the user to type and submit questions.
- The input is cleared after each submission.
- The interface is responsive and does not break on standard screen sizes.

---

### Story 8.2 — Sidebar Document Upload Panel

**As a** user,
**I want to** upload PDFs from a sidebar panel,
**So that** document management is separate from the chat interface.

**Acceptance Criteria:**
- The sidebar contains a clearly labelled file uploader.
- After upload, a confirmation message and the filename appear in the sidebar.
- All currently uploaded documents are listed by filename.
- The user can upload additional documents during the session without resetting the chat.

---

### Story 8.3 — Source Clause Display

**As a** user,
**I want to** see the exact clause or web excerpt that was used to answer my question,
**So that** I can verify the response against the original document.

**Acceptance Criteria:**
- Every assistant response includes an expandable "View Source" section below the answer.
- Expanding it reveals the full text of the retrieved clause or web excerpt.
- A badge or label clearly shows whether the source is "Document" or "Web".
- The source section is collapsed by default to keep the UI clean.

---

### Story 8.4 — Human Review Confirmation Component

**As a** user,
**I want to** see a clear confirmation prompt when the system detects a sensitive clause,
**So that** I can verify the correct clause is being referenced before the answer is shown.

**Acceptance Criteria:**
- The retrieved clause is displayed in a visually distinct highlighted box.
- A prompt asks: *"Is this the clause you meant?"*
- Two buttons — **Yes, proceed** and **No, rephrase** — are displayed.
- Clicking Yes continues to answer generation; clicking No clears the input and prompts the user to rephrase.

---

### Story 8.5 — Error and Edge Case Handling

**As a** user,
**I want to** see clear, helpful messages when something goes wrong,
**So that** I am never left confused about the state of the application.

**Acceptance Criteria:**
- If no document is uploaded and the user submits a question, a message prompts them to upload a document first.
- If retrieval fails after max retries and web search also returns no result, a clear "no information found" message is displayed.
- Unsupported or corrupted file uploads show a friendly error message.
- API errors (LLM or Tavily) are caught and displayed as a graceful error message rather than a crash.
- Loading spinners or status indicators are shown during ingestion and answer generation.

---

---

## Non-Functional Requirements

| Requirement | Specification |
|---|---|
| Response Latency | Answer generation completes within 10 seconds for typical queries on documents up to 50 pages |
| Ingestion Speed | PDF ingestion, chunking, embedding, and indexing complete within 30 seconds for documents up to 50 pages |
| Accuracy | The system must not hallucinate clauses; all answers must be traceable to a source |
| Graceful Degradation | Handles retrieval failures, API timeouts, and empty results without crashing |
| Transparency | Every response cites its source; web-sourced answers are clearly labelled |
| Portability | Runs locally via a single command; no persistent server or database required |
| Security | API keys managed via environment variables; never exposed in UI or logs |

---

## Tech Stack Reference

### LangChain

| Component | Role |
|---|---|
| PyPDFLoader | Loads and parses uploaded PDF documents |
| RecursiveCharacterTextSplitter | Splits document text into overlapping chunks |
| OpenAIEmbeddings / HuggingFaceEmbeddings | Converts text chunks to dense vectors |
| Chroma | In-memory vector store for semantic retrieval |
| LCEL | Composes retrieval and generation pipelines |
| ChatPromptTemplate | Constructs structured prompts for the LLM |
| CohereRerank / FlashrankRerank | Re-scores retrieved chunks and selects the best match |
| MultiVectorRetriever | Enables simultaneous search across multiple documents |

### LangGraph

| Component | Role |
|---|---|
| StateGraph | Defines the overall agent graph structure |
| TypedDict State Schema | Shared typed state object across all nodes |
| Conditional Edges | Implements the 4 routing decisions at runtime |
| Human-in-the-Loop | Pauses graph execution for user confirmation |

### External Services

| Service | Purpose |
|---|---|
| OpenAI GPT-4o / Groq | Primary LLM for answer generation and simplification |
| Tavily Search API | Web fallback for external legal context |
| Streamlit | Chat interface framework |
| Python-dotenv | Environment variable and API key management |

---

## State Schema Reference

| Field | Type | Purpose |
|---|---|---|
| `query` | str | Current user question |
| `chat_history` | list | All previous Q&A pairs for multi-turn memory |
| `retrieved_docs` | list | Clauses fetched from vector store |
| `reranked_docs` | list | Top-ranked clause after reranking |
| `retry_count` | int | Number of retrieval retries attempted (max 2) |
| `web_search_results` | list | Results from Tavily when document has no answer |
| `human_confirmed` | bool | True once user confirms clause during human review |
| `answer` | str | Generated LLM response |
| `needs_clarification` | bool | True if user requests plain-English simplification |
| `source` | str | "document" or "web" — displayed in UI |

---

## Development Timeline

| Week | Focus | Deliverable |
|---|---|---|
| Week 1 | Project setup, PDF ingestion pipeline, chunking, embedding, Chroma vector store, basic RAG chain | Working retrieval chain that accepts a PDF and returns relevant clauses |
| Week 2 | LangGraph agent graph with all 8 nodes, conditional routing, retry logic, web search fallback, human-in-the-loop, conversation memory | Fully functional agent with state management and multi-turn memory |
| Week 3 | Streamlit chat UI, source display, human review UI, end-to-end testing on real contracts, bug fixes, polish | Production-ready Streamlit app tested on real legal documents |

---

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| LLM hallucination on legal content | Prompt engineering constrains answers to the retrieved clause only; source transparency lets users verify |
| Poor retrieval quality on dense legal text | Reranking selects best match; retry logic rephrases queries on poor results |
| Sensitive clauses misclassified | Human review node provides safety check; users can override and rephrase |
| Web search returns unreliable results | Web fallback is supplemental only; clearly labelled in UI |
| Slow ingestion on large documents | Chunk parameters are tunable; loading indicator manages user expectations |
| API rate limits or downtime | Groq available as LLM fallback; error handling ensures graceful degradation |

---

## Future Considerations

- Support for additional formats beyond PDF (DOCX, plain text).
- Persistent document history and session storage across logins.
- User authentication and personal document libraries.
- Side-by-side contract comparison mode.
- Automatic clause flagging and risk scoring.
- Export annotated summaries as PDF or DOCX.
- Integration with legal databases (Westlaw, LexisNexis).
- Mobile-responsive UI and dedicated mobile application.
- Compliance mode for specific contract types (NDAs, leases, employment contracts).

---

*Legal Document Q&A Assistant — PRD v1.0 — Confidential, Internal Use Only*
