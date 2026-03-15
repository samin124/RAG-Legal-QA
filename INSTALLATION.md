# 🚀 Installation & Setup Guide - Legal AI Assistant

Complete step-by-step guide to run this project on a fresh computer.

---

## 📋 Prerequisites

Before starting, make sure you have:

1. **Python 3.10 or higher** installed
   - Check: `python --version` or `python3 --version`
   - Download from: https://www.python.org/downloads/

2. **Git** installed
   - Check: `git --version`
   - Download from: https://git-scm.com/downloads

---

## 🔧 Step-by-Step Installation

### **Step 1: Clone the Repository**

```bash
git clone https://github.com/samin124/RAG-Legal-QA.git
cd RAG-Legal-QA
```

---

### **Step 2: Create Virtual Environment**

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

---

### **Step 3: Install Dependencies**

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- Streamlit (UI)
- LangGraph (agent workflow)
- Google Generative AI (embeddings)
- Groq (LLM)
- Qdrant (vector database)
- LlamaParse (document processing)

---

### **Step 4: Get API Keys**

You need to get **FREE** API keys from these services:

#### **Required API Keys:**

1. **Groq API Key** (Required - Free)
   - Go to: https://console.groq.com/keys
   - Sign up → Create API key
   - Copy your key (starts with `gsk_`)

2. **Google API Key** (Required - Free)
   - Go to: https://makersuite.google.com/app/apikey
   - Sign in with Google → Create API key
   - Copy your key (starts with `AIza`)

3. **LlamaCloud API Key** (Required - Free tier available)
   - Go to: https://cloud.llamaindex.ai/
   - Sign up → Get API key
   - Copy your key (starts with `llx-`)

4. **Tavily API Key** (Required - Free tier: 1000 requests/month)
   - Go to: https://tavily.com/
   - Sign up → Get API key
   - Copy your key (starts with `tvly-`)

#### **Optional API Keys:**

5. **Cohere API Key** (Optional - for better retrieval)
   - Go to: https://dashboard.cohere.com/api-keys
   - Sign up → Create API key

---

### **Step 5: Configure Environment Variables**

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

   **On Windows (if `cp` doesn't work):**
   ```bash
   copy .env.example .env
   ```

2. **Edit `.env` file** and add your API keys:

   Open `.env` in any text editor and replace placeholders:

   ```env
   # Required API Keys
   GROQ_API_KEY=gsk_YOUR_ACTUAL_GROQ_KEY_HERE
   GOOGLE_API_KEY=AIza_YOUR_ACTUAL_GOOGLE_KEY_HERE
   LLAMA_CLOUD_API_KEY=llx_YOUR_ACTUAL_LLAMACLOUD_KEY_HERE
   TAVILY_API_KEY=tvly_YOUR_ACTUAL_TAVILY_KEY_HERE

   # Optional
   COHERE_API_KEY=your_cohere_api_key_here
   OPENAI_API_KEY=sk-demo-replace-with-your-key

   # App Settings (these are fine as-is)
   ENABLE_OCR=true
   DEFAULT_LLM_MODEL=llama-3.3-70b-versatile
   USE_GROQ=true
   EMBEDDING_MODEL=models/gemini-embedding-001
   CHUNK_SIZE=1000
   CHUNK_OVERLAP=200
   ```

3. **Save the file**

---

### **Step 6: Run the Application**

```bash
streamlit run app.py
```

The app will open automatically in your browser at:
- **Local URL:** http://localhost:8501
- **Network URL:** http://[your-ip]:8501

---

## 📖 How to Use

### **1. Upload Document**
- Click "Browse files" in the sidebar
- Upload a PDF, DOCX, PNG, JPG, or MD file
- Wait for processing (with OCR enabled, it may take 10-30 seconds)
- You'll see "✓ 1 document(s)" when ready

### **2. Ask Questions**
- Type your question in the chat input at the bottom
- Example: "What is the main objective of this regulation?"
- Press Enter or click Send

### **3. View Responses**
- Answer appears with clean formatting
- Source information shown below each answer:
  - "📄 Source: Page X"
  - Click "📖 View source text from document" to see the exact text from your document

### **4. Chat History**
- Click "➕ New Chat" to start a new conversation
- Previous conversations appear in the sidebar under "Recent Chats"
- Click any conversation to reload it
- Active conversation marked with 📍

### **5. Export Chat**
- Click "📥 Export" button in the header
- Download conversation as .txt file

### **6. Clear Chat**
- Click "🔄 Clear Chat" to clear current conversation

---

## 🎨 Features

✅ **Modern ChatGPT-style dark theme**
✅ **Multi-format document support** (PDF, DOCX, Images with OCR)
✅ **Smart question answering** with AI-powered retrieval
✅ **Source attribution** with page numbers
✅ **Expandable source text viewer**
✅ **Chat history management**
✅ **Conversation persistence**
✅ **Export functionality**
✅ **Web search fallback** (when answer not in document)
✅ **Agentic workflow** with LangGraph
✅ **Semantic search** with vector embeddings

---

## ⚠️ Troubleshooting

### **Issue: "Module not found" error**
**Solution:**
```bash
# Make sure virtual environment is activated
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Then reinstall dependencies
pip install -r requirements.txt
```

---

### **Issue: "Missing API keys" error**
**Solution:**
- Check that `.env` file exists in the project root (not `.env.example`)
- Verify all required API keys are filled in
- Make sure no extra spaces before/after API keys
- Restart the Streamlit app after editing `.env`

---

### **Issue: "Port 8501 is not available"**
**Solution:**
```bash
# Use a different port
streamlit run app.py --server.port 8502
```

---

### **Issue: Document processing takes too long**
**Solution:**
- For scanned PDFs, OCR processing can take 30-60 seconds
- To disable OCR, edit `.env`:
  ```env
  ENABLE_OCR=false
  ```
- Smaller documents process faster

---

### **Issue: "Reranking failed" warning in console**
**Solution:**
- This is just a warning, the app still works fine
- For better retrieval accuracy, add a Cohere API key to `.env`:
  ```env
  COHERE_API_KEY=your_actual_cohere_key
  ```

---

### **Issue: "Rate limit exceeded" error**
**Solution:**
- You've hit the free tier API limits
- Wait a few minutes and try again
- For Groq: Free tier has rate limits
- For Tavily: Free tier is 1000 requests/month
- Consider upgrading to paid tiers if needed

---

### **Issue: Streamlit app won't start**
**Solution:**
```bash
# Check if port is already in use
# Kill any running Streamlit processes
# On Windows:
taskkill /F /IM streamlit.exe

# On macOS/Linux:
pkill -f streamlit

# Then try running again
streamlit run app.py
```

---

### **Issue: "No module named 'dotenv'" error**
**Solution:**
```bash
pip install python-dotenv
```

---

## 🛠️ System Requirements

**Minimum:**
- Python 3.10+
- 4GB RAM
- 1GB free disk space
- Internet connection (for API calls)

**Recommended:**
- Python 3.11 or 3.12
- 8GB RAM
- 2GB free disk space
- Fast internet connection (for better OCR performance)

---

## 📝 Project Structure

```
RAG-Legal-QA/
├── app.py              # Main Streamlit application (Modern UI)
├── config.py           # Configuration management
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment variables
├── .env               # Your actual API keys (create this)
├── .gitignore         # Git ignore rules
├── README.md          # Project documentation
├── INSTALLATION.md    # This file
│
├── graph/             # LangGraph agent workflow
│   ├── __init__.py
│   ├── graph.py       # State machine & routing logic
│   ├── nodes.py       # Processing nodes (retrieve, rerank, generate)
│   └── state.py       # State schema definition
│
├── rag/               # Document processing & retrieval
│   ├── __init__.py
│   ├── loader.py      # Document loading with OCR support
│   ├── embeddings.py  # Embedding generation (Google Gemini)
│   └── retriever.py   # Vector search & reranking
│
└── prompts/           # LLM prompt templates
    ├── __init__.py
    └── templates.py   # Prompt engineering templates
```

---

## 🔒 Security Notes

⚠️ **IMPORTANT:**
- Never commit your `.env` file to Git
- Keep your API keys private
- Don't share your `.env` file with anyone
- The `.gitignore` file is configured to exclude `.env` automatically

---

## 📚 Additional Resources

**Documentation:**
- Detailed features: See `README.md`
- Product requirements: See `Legal_QA_PRD.md`

**API Documentation:**
- Groq: https://console.groq.com/docs
- Google AI: https://ai.google.dev/docs
- LlamaParse: https://docs.cloud.llamaindex.ai/
- Tavily: https://docs.tavily.com/
- Streamlit: https://docs.streamlit.io/

**Technologies Used:**
- **LangGraph:** https://langchain-ai.github.io/langgraph/
- **Qdrant:** https://qdrant.tech/documentation/
- **Cohere:** https://docs.cohere.com/

---

## 🆘 Getting Help

If you encounter issues:

1. **Check this troubleshooting guide** first
2. **Read the error message carefully** - most errors explain the problem
3. **Verify your API keys** are correct in `.env`
4. **Check your internet connection** - all features require internet
5. **Open an issue on GitHub:** https://github.com/samin124/RAG-Legal-QA/issues

---

## 🎉 Quick Start Checklist

After installation, verify everything works:

- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip list` shows packages)
- [ ] `.env` file created with API keys
- [ ] Streamlit app runs (`streamlit run app.py`)
- [ ] App opens in browser (http://localhost:8501)
- [ ] Can upload a document
- [ ] Can ask a question
- [ ] Receives answer with source attribution

If all checkboxes are ticked, you're ready! ✅

---

## 🚀 You're All Set!

Once you see the Streamlit interface:

1. ✅ Upload a legal document (PDF, DOCX, or image)
2. ✅ Wait for processing to complete
3. ✅ Ask questions about the document
4. ✅ Get AI-powered answers with source references
5. ✅ View page numbers and source text
6. ✅ Export your conversations

**Enjoy your Legal AI Assistant!** ⚖️

---

**Version:** 1.0
**Last Updated:** March 2026
**License:** See LICENSE file
**Repository:** https://github.com/samin124/RAG-Legal-QA
