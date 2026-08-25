# 🏛️ Policy Pilot AI

> **An AI-powered multi-agent platform for citizens to discover government schemes, extract profile attributes from documents, engage via real-time Voice AI, and evaluate deterministic eligibility.**

---

## 📌 Overview

**Policy Pilot AI** addresses a major challenge faced by citizens: discovering relevant government schemes, understanding complex eligibility criteria, and navigating fragmented public portals. Generic AI chatbots often hallucinate rules or provide outdated information. Policy Pilot solves this by combining **LangGraph multi-agent orchestration**, **hybrid RAG & live web search**, **official source verification**, and **deterministic eligibility evaluation**.

---

## ✨ Key Features

- 🤖 **LangGraph Multi-Agent Architecture**:
  - **Intent & Domain Agent**: Classifies query intent and routes to specific domains (Agriculture, Education, Healthcare, Social Welfare, etc.).
  - **Research Agent**: Performs hybrid retrieval using vector embeddings (**ChromaDB**) and live web search (**Tavily API**).
  - **Official Source Resolver**: Verifies facts strictly against government portals (`.gov.in`, `.nic.in`).
  - **Eligibility Agent**: Evaluates rule-based eligibility deterministically against citizen profile attributes.
  - **Recommendation Agent**: Ranks top applicable schemes with action plans and document checklists.
- 🎙️ **Real-Time Voice AI Pipeline**:
  - Interactive WebSocket interface (`/ws/voice`) for speech-to-text input, agent processing, and audio output.
- 📄 **Document Vault & Intelligent Parsing**:
  - Upload citizen documents (PDF, DOCX, images) to automatically extract profile attributes (income, category, state, age, occupation) and match required scheme documents.
- 🛡️ **Source Trust & Verification**:
  - Multi-tier source trust verification to filter untrusted sources and enforce factual grounding.
- 🎨 **Modern React 19 Frontend**:
  - Built with **React 19**, **Vite**, and **Tailwind CSS**.
  - Interactive step-by-step processing visualizer, eligibility status cards, required document drawers, and citizen profile dashboard.

---

## 🏗️ System Architecture

```text
                               ┌─────────────────────────┐
                               │       React 19 UI       │
                               │  (Vite + Tailwind CSS)  │
                               └────────────┬────────────┘
                                            │
                     REST API / WebSockets  │  POST /api/v1/query
                                            ▼
                               ┌─────────────────────────┐
                               │   FastAPI Gateway API   │
                               └────────────┬────────────┘
                                            │
                               ┌────────────▼────────────┐
                               │   LangGraph Workflow    │
                               └────────────┬────────────┘
                                            │
         ┌──────────────────┬───────────────┼───────────────┬──────────────────┐
         ▼                  ▼               ▼               ▼                  ▼
  ┌──────────────┐   ┌─────────────┐  ┌───────────┐  ┌─────────────┐   ┌──────────────┐
  │ Intent Agent │   │  Research   │  │ Official  │  │ Eligibility │   │Recommendation│
  │   & Domain   │   │    Agent    │  │  Source   │  │    Agent    │   │    Agent     │
  └──────────────┘   └──────┬──────┘  │ Resolver  │  └──────┬──────┘   └──────────────┘
                            │         └───────────┘         │
                   ┌────────┴────────┐             ┌────────┴────────┐
                   ▼                 ▼             ▼                 ▼
             ┌───────────┐     ┌───────────┐  ┌───────────┐   ┌─────────────┐
             │ ChromaDB  │     │  Tavily   │  │ Rule-Based│   │ Citizen     │
             │ (RAG Vector│     │ Web Search│  │ Engine    │   │ Profile DB  │
             └───────────┘     └───────────┘  └───────────┘   └─────────────┘
```

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11) & Uvicorn
- **AI Orchestration**: LangGraph, LangChain
- **LLM & Embeddings**: OpenAI API (`gpt-4.1-nano`, `text-embedding-3-small`)
- **Vector DB**: ChromaDB
- **Web Search**: Tavily Search API
- **Database**: PostgreSQL with SQLAlchemy ORM & Alembic migrations
- **Document Processing**: PyMuPDF (`fitz`), `python-docx`, BeautifulSoup4
- **Voice / Streaming**: WebSockets (`websockets`)

### Frontend
- **Framework**: React 19 & Vite
- **Styling**: Tailwind CSS & PostCSS
- **Linting**: Oxlint

---

## 📁 Repository Structure

```text
Policy_Pilot/
├── backend/
│   ├── app/
│   │   ├── agents/          # LangGraph agents (Intent, Research, Eligibility, etc.)
│   │   ├── api/             # FastAPI routers (Query, Auth, Documents)
│   │   ├── config/          # Application settings & environment configs
│   │   ├── core/            # Core utilities, Auth, JSON parsers
│   │   ├── database/        # Database models & connections
│   │   ├── graph/           # LangGraph workflow definitions
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── rag/             # RAG retrievers & ChromaDB wrappers
│   │   ├── services/        # Business logic & external service integrations
│   │   └── voice/           # WebSocket voice pipeline
│   ├── alembic/             # Database migration scripts
│   ├── tests/               # Pytest suite for agents & API endpoints
│   ├── ingest_knowledge_base.py  # Knowledge base vector index script
│   └── requirements/        # Python dependency manifests
├── frontend/
│   ├── src/
│   │   ├── api/             # Frontend API clients (query, auth, wallet)
│   │   ├── components/      # UI Components (Chat, Cards, Dashboards, Navbar)
│   │   ├── hooks/           # Custom React hooks (useQuery, useAuth)
│   │   └── pages/           # Application views (Landing, Chat, Dashboard, Login)
│   ├── package.json
│   └── vite.config.js
├── knowledge_base/          # Raw scheme documentation & reference data
├── docker-compose.yml
├── PROJECT_CONTEXT.md       # Master technical documentation
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed on your machine:
- **Python**: `v3.11` or higher
- **Node.js**: `v18.0.0` or higher
- **PostgreSQL**: Running locally or via Docker
- **API Keys**: OpenAI API Key, Tavily API Key

---

### Backend Setup

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment**:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements/base.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in the `backend/` directory by copying `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Fill in your parameters:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   TAVILY_API_KEY=your_tavily_api_key
   DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/policypilot
   LLM_MODEL=gpt-4.1-nano
   EMBEDDING_MODEL=text-embedding-3-small
   CHROMA_DB_PATH=./storage/chroma_db
   ```

5. **Run Database Migrations & Auto-Creation**:
   ```bash
   alembic upgrade head
   ```

6. **Ingest Scheme Knowledge Base**:
   ```bash
   python ingest_knowledge_base.py
   ```

7. **Start the FastAPI Development Server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   The API will be live at `http://localhost:8000`. Interactive docs are available at `http://localhost:8000/docs`.

---

### Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the Vite development server**:
   ```bash
   npm run dev
   ```
   Open your browser at `http://localhost:5173`.

---

### Running via Docker Compose

To spin up PostgreSQL, the backend service, and frontend in Docker:

```bash
docker-compose up --build
```

---

## 🔌 API Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` / `/api/health` | Service health status check |
| `POST` | `/api/v1/query` | Primary endpoint processing citizen queries through LangGraph |
| `POST` | `/api/v1/auth/register` | Register a new citizen account |
| `POST` | `/api/v1/auth/login` | Authenticate user & issue JWT token |
| `GET` | `/api/v1/documents` | List uploaded citizen documents |
| `POST` | `/api/v1/documents/upload` | Upload PDF/DOCX for extraction and profile sync |
| `WS` | `/ws/voice` | Real-time WebSocket connection for Voice AI queries |

---

## 🧪 Testing

To execute the automated backend test suite:

```bash
cd backend
pytest
```

To run frontend lint checks:

```bash
cd frontend
npm run lint
```

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
