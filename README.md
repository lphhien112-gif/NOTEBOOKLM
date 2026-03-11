# 📚 NotebookLM - Offline RAG Document Chat

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![React: 18](https://img.shields.io/badge/React-18-61dafb.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg)

A full-stack application that allows users to upload documents (PDF, DOCX, TXT) and interact with them using Retrieval-Augmented Generation (RAG). By leveraging local LLMs (via Ollama) and an embedded vector database, this application ensures complete data privacy while providing intelligent querying capabilities.

## 🚀 Features

- **Document Management:** Securely upload, store, and process multiple document formats.
- **Intelligent Contextual Chat:** Q&A based entirely on the contents of your uploaded documents.
- **Advanced NLP Tasks:** Generate summaries, extract keywords, and automatically formulate review questions.
- **Hybrid Search Engine:** Combines Semantic Vector Search (ChromaDB) and Keyword Search (BM25) with re-ranking for superior retrieval accuracy.
- **Privacy First:** Designed to work entirely offline with local LLMs (Ollama) so your data never leaves your machine.
- **Modern User Interface:** Responsive, user-friendly frontend built with React and Tailwind CSS.

## 🛠️ Technology Stack

### Frontend
- **React.js** - UI Component Library
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client for API communication
- **React Hot Toast** - Elegant UI notifications

### Backend
- **Python & FastAPI** - High-performance asynchronous RESTful API
- **ChromaDB** - Embedded vector database for semantic search
- **Sentence-Transformers** - Embeddings generation
- **Rank-BM25** - Keyword-based document retrieval
- **LangChain** - Framework for document parsing & chunking

## ⚙️ Local Development Setup

Follow these steps to run the project locally on your machine.

### 1. Prerequisites
- [Python 3.10+](https://www.python.org/)
- [Node.js 18+](https://nodejs.org/)
- [Ollama](https://ollama.ai/) installed and running locally. We recommend pulling a model like `llama3` or `mistral`. (e.g., `ollama pull mistral`)

### 2. Clone the Repository
```bash
git clone https://github.com/lphhien112-gif/NOTEBOOKLM.git
cd NOTEBOOKLM
```

### 3. Backend Setup
Navigate to the backend directory and set up the Python environment:
```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate the environment:
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn app.main:app --reload
```
*The backend API will be available at: `http://localhost:8000` (Access the Swagger UI at `/docs`)*

### 4. Frontend Setup
Open a new terminal session, navigate to the frontend directory:
```bash
cd frontend

# Install package dependencies
npm install

# Start the development server
npm start
```
*The React application will be available at: `http://localhost:3000`*

## 🐳 Docker Deployment

For a standardized, production-ready setup, orchestrate the entire stack using Docker Compose. Make sure Docker is running on your machine.

```bash
# Build and start all containers in detached mode
docker-compose up -d --build
```
- **Frontend** UI will be accessible on port `3000`
- **Backend API** will be accessible on port `8000`

*Note: You may need to configure Ollama networking (e.g., `OLLAMA_HOST=0.0.0.0`) so the Docker containers can reach your local Ollama instance on `host.docker.internal`.*

## 📂 Project Structure

To understand the core architecture and directory layout, please refer to [flow.md](./flow.md) for a detailed breakdown.

## 🤝 Contributing

Contributions are always welcome! 
1. Fork the project.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.
