# ⚡ Django RAG Platform (Groq + ChromaDB + LangChain)

A modern, production-grade **Retrieval-Augmented Generation (RAG)** application built with **Django**, **ChromaDB**, **LangChain**, and **Groq LLMs** (featuring high-speed inference on `openai/gpt-oss-120b`, `llama-3.3-70b-versatile`, etc.).

---

## 🌟 Key Features

1. **Groq LLM Acceleration**: Lightning-fast question answering and multi-turn conversational reasoning using LangChain's `ChatGroq`.
2. **ChromaDB Vector Store**: Local, persistent vector store with strict per-user and per-document isolation.
3. **Document Ingestion**:
   - Automated parsing for **PDF (`pypdf`)**, **Word (`docx2txt`)**, **TXT / MD / CSV**.
   - Recursive character chunking (`RecursiveCharacterTextSplitter`).
   - Local, zero-cost ONNX vector embeddings (no paid embedding API key required).
4. **Modern Glassmorphic HTML UI**:
   - **Interactive RAG Chat**: Real-time AJAX responses, expandable source citations, conversation history sidebar, and quick prompt suggestions.
   - **Knowledge Base Manager**: Drag-and-drop file upload using Django Forms, chunk analysis, status tracking, and re-indexing.
   - **Analytics Dashboard**: Live metrics on total documents, indexed vector chunks, and conversations.
   - **Django Authentication**: Secure session login, registration, and logout.
5. **REST API**: Full JSON endpoints for JWT authentication, document uploads, conversation management, and programmatic RAG querying.

---

## 🚀 Quick Start (Windows)

### Option 1: One-Click Setup
1. Double-click `backend\setup_env.bat` to create the virtual environment and install all dependencies.
2. Double-click `backend\run_server.bat` to start the server.
3. Open your browser at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### Option 2: Manual Terminal Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate       # On Linux/macOS: source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply database migrations
python manage.py makemigrations accounts documents chat
python manage.py migrate

# 5. Start development server
python manage.py runserver 127.0.0.1:8000
```

---

## ⚙️ Configuration (`backend/.env`)

The `.env` file is pre-configured with your Groq API key:

```ini
SECRET_KEY=django-insecure-development-secret-key-super-safe-987654321
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,*
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000,http://127.0.0.1:8000

# Groq LLM Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b

# ChromaDB & RAG Chunking
CHROMA_PERSIST_DIRECTORY=chroma_db
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K=4
```

---

## 📂 Project Architecture

```
django_rag_project/
├── backend/
│   ├── config/             # Django settings, main URLs & REST API routing
│   ├── accounts/           # User authentication, forms, views, serializers
│   ├── documents/          # Document models, forms, services, vector sync
│   ├── chat/               # Conversations, messages, AJAX RAG queries
│   ├── rag/                # LangChain pipeline, ChromaDB vector store, Groq LLM
│   ├── templates/          # Modern HTML templates (Dashboard, Chat, Docs, Auth)
│   ├── static/             # CSS (Glassmorphism & animations) & JS handlers
│   ├── requirements.txt    # Python package dependencies
│   ├── manage.py
│   ├── run_server.bat      # Windows dev server runner
│   └── setup_env.bat       # Environment setup script
├── README.md
```

---

## 🧪 Testing & Verification

Run the test suite:

```bash
# Run unit & integration tests
python manage.py test documents.tests chat.tests accounts.tests

# Run end-to-end RAG verification
python test_rag_pipeline.py
```
