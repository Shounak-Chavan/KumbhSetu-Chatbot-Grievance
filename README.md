<p align="center">
	<img src="https://img.shields.io/badge/Python-3.13-blue?logo=python" />
	<img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi" />
	<img src="https://img.shields.io/badge/LangChain-RAG-1C3C3C" />
	<img src="https://img.shields.io/badge/Qdrant-Vector%20DB-EA4AAA" />
	<img src="https://img.shields.io/badge/HuggingFace-Embeddings-FFB000?logo=huggingface" />
	<img src="https://img.shields.io/badge/Groq-LLM-000000" />
</p>

# KumbhSetu Chatbot & Grievance Backend

### Unified AI + API platform for Kumbh information retrieval and grievance-ready backend foundations

Short description: A Python 3.13 FastAPI backend with JWT auth, role-aware access patterns, and a LangChain-powered RAG pipeline over local Kumbh dataset documents using HuggingFace embeddings and Qdrant hybrid retrieval.

This repository combines:

- A production-oriented FastAPI backend (authentication, token lifecycle, DB models, Alembic)
- A retrieval-augmented generation (RAG) pipeline for Nashik Kumbh Mela information
- Notebook and script workflows for ingestion, indexing, retrieval, and experimentation
- Supporting scraper utilities and dataset organization for iterative knowledge-base improvements

---

## Features

- JWT authentication with access + refresh token flow
- Refresh token persistence, revocation, and HttpOnly cookie-based session renewal
- Role-aware architecture hooks (admin/user controls via RBAC utilities)
- Async SQLAlchemy setup for scalable DB operations
- Alembic migration support for schema evolution
- Hybrid RAG retrieval pipeline:
	- Dense retrieval (Qdrant vector search)
	- Sparse retrieval (BM25)
	- Ensemble weighting
	- Cross-encoder reranking
- Semantic + recursive chunking strategy for better context segmentation
- Query rewriting before retrieval to improve recall quality
- Notebook workflow for experimentation and tuning
- Dataset and scraper modules for ongoing corpus enrichment

---

## Architecture Overview

1. Documents are loaded from the local dataset tree (`dataset/kumbh_rag_dataset/`).
2. Metadata is normalized (`category`, `doc_name`, optional source link).
3. Documents are semantically chunked, then recursively split for size control.
4. Chunks are embedded using `sentence-transformers/all-MiniLM-L6-v2`.
5. Dense vectors are stored in Qdrant.
6. At query time, the system performs hybrid retrieval (Qdrant + BM25), deduplicates, reranks, and prompts Groq LLM.
7. API layer provides auth/session backbone for application-level integration.

---

## Tech Stack

- Python 3.13+
- FastAPI + Uvicorn
- SQLAlchemy (async) + Alembic
- PostgreSQL (recommended via async driver)
- LangChain ecosystem
- Qdrant (`qdrant-client`, `langchain-qdrant`)
- HuggingFace sentence-transformer embeddings
- Groq (`langchain-groq`) for LLM inference
- BM25 + cross-encoder reranking (`sentence-transformers`)
- Jupyter Notebook for RAG experimentation

---

## Project Structure

```text
ChatBot/
├── alembic.ini
├── pyproject.toml
├── requirements.txt
├── uv.lock
├── README.md
├── alembic/
│   ├── env.py
│   └── versions/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── routers_auth.py
│   ├── core/
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   ├── rbac.py
│   │   └── security.py
│   ├── db/
│   │   ├── base.py
│   │   ├── init_db.py
│   │   └── session.py
│   ├── models/
│   │   ├── complaint.py
│   │   ├── token.py
│   │   └── user.py
│   ├── rag/
│   │   ├── build_vector_db.py
│   │   └── rag_chatbot.py
│   └── schemas/
│       ├── auth.py
│       └── complaints.py
├── dataset/
│   └── kumbh_rag_dataset/
├── notebooks/
│   ├── build_vector_db.ipynb
│   └── rag_chatbot.ipynb
└── scraper/
		├── osm_scraper.py
		├── scraper_links.py
		└── selenium_retry.py
```

---

## API Surface (Current)

Base app:

- `GET /health` -> health check

Auth routes (`/auth`):

- `POST /auth/register` -> register user
- `POST /auth/login` -> get access token + set refresh cookie
- `POST /auth/refresh` -> rotate access token from refresh cookie
- `POST /auth/logout` -> revoke refresh token + clear cookie

OpenAPI docs after running server:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

---

## Getting Started

### 1) Prerequisites

- Python 3.13+
- PostgreSQL instance
- Qdrant instance (local Docker or remote)
- Groq API key

### 2) Clone

```bash
git clone https://github.com/Shounak-Chavan/KumbhSetu-Chatbot-Grievance.git
cd KumbhSetu-Chatbot-Grievance
```

### 3) Install Dependencies

Option A (`uv`, recommended if you use lockfile):

```bash
uv sync
```

Option B (`pip`):

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
pip install -r requirements.txt
```

### 4) Environment Variables

Create a `.env` in project root and set at least:

```env
APP_NAME=KumbhSetu API

DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/kumbhsetu

ACCESS_TOKEN_SECRET_KEY=replace_with_strong_secret
REFRESH_TOKEN_SECRET_KEY=replace_with_strong_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=optional

# Keep false for public deployments unless explicitly required
ALLOW_ADMIN_EMAIL_DOMAINS=false
```

### 5) Apply Migrations / Initialize Database

If using Alembic migrations:

```bash
alembic upgrade head
```

Or create tables directly (development utility):

```bash
python -m app.db.init_db
```

### 6) Run API Server

```bash
uvicorn app.main:app --reload
```

---

## RAG Pipeline Usage

### Script-Based Flow

1. Ensure Qdrant is running at `localhost:6333`.
2. Ensure dataset text files are available under `dataset/kumbh_rag_dataset/`.
3. Build chunks + embeddings + Qdrant collection:

```bash
python app/rag/build_vector_db.py
```

4. Start conversational retrieval chain utilities:

```bash
python app/rag/rag_chatbot.py
```

### Notebook Flow

Use notebooks for iterative experimentation:

- `notebooks/build_vector_db.ipynb`
- `notebooks/rag_chatbot.ipynb`

Run cells top-to-bottom to execute ingestion, indexing, retrieval, and QA chain experiments.

---

## Local Qdrant Quick Start (Docker)

```bash
docker run -d --name qdrant \
	-p 6333:6333 \
	-v qdrant_storage:/qdrant/storage \
	qdrant/qdrant
```

---

## Security Notes

- Do not commit `.env` or secrets.
- Use strong token secret keys in production.
- Switch cookie `secure=True` behind HTTPS in production.
- Restrict CORS origins in production (currently permissive for development).
- Keep `ALLOW_ADMIN_EMAIL_DOMAINS=false` unless domain-based admin assignment is explicitly needed.

---

## Current Limitations

- Complaint data model exists, but complaint API routes are not yet exposed.
- RAG scripts are pipeline-oriented and not yet mounted as FastAPI endpoints.
- No Dockerfile is currently included in this repository.

---

## Suggested Next Milestones

1. Expose RAG inference as authenticated FastAPI endpoints.
2. Add complaint create/list/update routes with RBAC enforcement.
3. Add automated tests for auth, token refresh, and retrieval quality.
4. Add CI workflow for linting, tests, and migration checks.
5. Add containerization for API + Qdrant compose deployment.

---

## Author

Built by Shounak for practical GenAI engineering and grievance platform development.

