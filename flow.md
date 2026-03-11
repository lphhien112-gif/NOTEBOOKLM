# Project Architecture & Flow

This document outlines the standard directory tree and functional modules for the NotebookLM project.

```text
NOTEBOOKLM/
├── backend/                  # Server-side source code (Python/FastAPI)
│   ├── app/
│   │   ├── api/              # API Routing Layer
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── endpoints/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── chat.py         # API for conversational Q&A via RAG
│   │   │       │   ├── documents.py    # API for document operations (upload, delete)
│   │   │       │   └── tasks.py        # API for specialized tasks (summarization, extraction)
│   │   │       └── schemas.py          # Pydantic data validation schemas
│   │   ├── core/             # Application Configuration Layer
│   │   │   ├── __init__.py
│   │   │   └── config.py               # Centralized config (Variables, Paths)
│   │   ├── services/         # Business Logic Layer
│   │   │   ├── __init__.py
│   │   │   ├── rag_pipeline.py         # Core logic: LLM integration and RAG orchestration
│   │   │   ├── vector_store.py         # Hybrid search engine (Vector + Keyword)
│   │   │   └── document_parser.py      # Parses and chunks various document formats
│   │   └── main.py                     # FastAPI application entry point
│   ├── .env                            # Environment variables (Ignored by Git)
│   ├── Dockerfile                      # Backend Docker container configuration
│   └── requirements.txt                # Python package dependencies
│
├── data/                               # Persistent Storage Directory (Ignored by Git)
│   ├── vector_store/                   # Vector database storage (ChromaDB)
│   ├── uploaded_docs/                  # Raw user-uploaded source documents
│   ├── keyword_index.json              # Token/Keyword index for BM25 hybrid search
│   └── state.json                      # Application persistent state tracker
│
├── frontend/                           # Client-side source code (ReactJS)
│   ├── public/                         # Static Public Assets
│   │   └── index.html                  # Root HTML template
│   ├── src/                            # React Application Source
│   │   ├── api/
│   │   │   └── index.js                # Axios client configurations and API wrappers
│   │   ├── components/                 # Reusable UI Components
│   │   │   ├── ChatWindow.jsx          # Interactive chat and task interface
│   │   │   ├── DocumentList.jsx        # Sidebar managing uploaded documents
│   │   │   └── FileUploader.jsx        # Drag-and-drop document upload handler
│   │   ├── pages/                      # Page Level Components
│   │   │   └── MainPage.jsx            # Main dashboard structural layout
│   │   ├── App.jsx                     # Root React Component orchestrating contexts/routes
│   │   └── index.js                    # JavaScript application entry point
│   ├── Dockerfile                      # Frontend standard Nginx Docker build
│   ├── package.json                    # JS dependencies and NPM execution scripts
│   └── tailwind.config.js              # Tailwind CSS utility framework configuration
│
├── .gitignore                          # Global rules for untracked files
├── docker-compose.yml                  # Container orchestration network for the whole stack
├── flow.md                             # You are here - Architectural directory insight
└── README.md                           # Master project documentation
```