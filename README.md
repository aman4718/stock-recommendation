# AI Stock RAG Chatbot — Monorepo

An AI-powered stock recommendation chatbot using Retrieval-Augmented Generation (RAG).

## Structure

```
AI-Agent/
├── backend/          # Python — FastAPI + LangChain + ChromaDB Cloud
│   ├── phase1/       # Data ingestion & processing
│   ├── phase2/       # Embeddings & vector storage (Chroma Cloud)
│   ├── phase3/       # RAG pipeline
│   ├── phase4/       # FastAPI server
│   ├── phase5/       # Scheduler
│   ├── data/         # Generated data (git-ignored)
│   ├── logs/         # Log files (git-ignored)
│   ├── .env          # Secrets (git-ignored)
│   └── requirements.txt
├── frontend/         # Next.js chat UI (Phase 6)
├── phasewise.md
└── problemStatement.md
```

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env   # fill in your keys

# Run Phase 1 — Data ingestion
cd phase1 && python main.py

# Run Phase 2 — Embed & store in Chroma Cloud
cd ../phase2 && python main.py
```

## Tech Stack
- **LLM**: Groq (LLaMA)
- **RAG**: LangChain
- **Vector DB**: ChromaDB Cloud
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Backend**: FastAPI
- **Frontend**: Next.js
