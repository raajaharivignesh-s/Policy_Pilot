# POLICY PILOT AI — MASTER PROJECT CONTEXT

## Project Overview

I am building a **production-quality AI capstone project** called **PolicyPilot AI**.

This is **not** a chatbot, **not** a simple RAG application, and **not** just a wrapper around an LLM.

PolicyPilot AI is a **multi-agent AI platform** that helps citizens discover Tamil Nadu government schemes they are eligible for by understanding their profile, searching trusted government knowledge, verifying information, evaluating eligibility, and providing personalized recommendations with official sources.

The project is intended to demonstrate modern AI engineering practices including:

- FastAPI Backend
- React Frontend
- LangGraph Multi-Agent Workflow
- OpenAI-compatible LLM APIs
- RAG (Retrieval Augmented Generation)
- ChromaDB Vector Database
- OpenAI Embeddings
- Hybrid Retrieval (Vector DB + Live Web Search)
- Deterministic Eligibility Engine
- Modular Production Architecture

The goal is to build software that resembles a production AI system rather than a college prototype.

---

# Problem Statement

Tamil Nadu has many government schemes covering:

- Agriculture
- Education
- Healthcare
  However, citizens struggle because:

- Information is scattered across multiple government portals.
- Government PDFs are difficult to understand.
- Eligibility differs for every scheme.
- Schemes frequently change.
- Most users don't know which schemes they qualify for.
- Existing chatbots often hallucinate or provide outdated information.
  PolicyPilot solves this problem by acting as an intelligent AI assistant that:

- Understands the user's situation.
- Identifies the relevant domain.
- Searches government knowledge.
- Verifies information.
- Evaluates eligibility.
- Recommends the best schemes.
- Explains why they qualify.
- Lists required documents.
- Provides official sources.

---

# Overall Solution

The application follows this workflow:

```
User
    │
    ▼
FastAPI Backend
    │
    ▼
LangGraph Workflow
    │
    ▼
AI Agents
    │
    ▼
Hybrid Retrieval
(Vector DB + Official Web Search)
    │
    ▼
Verification
    │
    ▼
Eligibility Engine
    │
    ▼
Recommendation
    │
    ▼
Response
```

The frontend never talks directly to OpenAI.

Everything goes through the backend.

---

# Development Philosophy

The project is being built like a real software product.

We are **not** writing everything at once.

Instead we are building it layer by layer.

Current development order:

```
Project Structure

↓

Configuration

↓

FastAPI Initialization

↓

Logging

↓

OpenAI Services

↓

Embedding Services

↓

Database

↓

Vector Database

↓

Knowledge Pipeline

↓

RAG

↓

LangGraph

↓

AI Agents

↓

API Layer

↓

Frontend

↓

Deployment
```

Each layer depends on the previous one.

---

# Software Architecture Philosophy

The project follows **Separation of Concerns**.

Each file has exactly one responsibility.

We avoid placing unrelated logic inside the same file.

Example:

settings.py

↓

Configuration only

NOT OpenAI.

NOT FastAPI.

NOT Database.

---

main.py

↓

Application initialization only.

NOT business logic.

NOT AI.

NOT RAG.

---

openai_service.py

↓

Only creates OpenAI client.

NOT prompts.

NOT embeddings.

NOT RAG.

---

llm_service.py

↓

Only communicates with LLM.

---

embedding_service.py

↓

Only generates embeddings.

---

This modular architecture makes the project scalable.

---

# Folder Structure

```
PolicyPilot/

backend/

frontend/

knowledge_base/

docs/

docker/

scripts/
```

---

Backend:

```
backend/

app/

agents/

api/

config/

core/

database/

graph/

models/

prompts/

rag/

schemas/

services/

tools/

utils/

main.py

requirements/

storage/

logs/

tests/

venv/

.env
```

---

Knowledge Base:

```
knowledge_base/

raw/

agriculture/

education/

healthcare/

processed/

chunks/

metadata/
```

---

Storage:

```
storage/

chroma_db/

uploads/

cache/
```

---

The knowledge base contains source data.

The storage folder contains generated runtime data.

---

# Coding Methodology

Every module is implemented using the same process.

For every file:

1. Explain its purpose.
2. Explain why it exists.
3. Explain where it fits in the architecture.
4. Generate complete code.
   No line-by-line explanation unless specifically requested.

The objective is to understand the architecture rather than memorize syntax.

---

# Current Progress

Completed:

Project Structure

Backend Folder Structure

Knowledge Base Structure

Virtual Environment

Requirements Management

Configuration (.env)

settings.py

main.py (basic initialization)

Logging architecture planned

OpenAI architecture designed

Embedding architecture designed

Still pending:

Logging implementation

OpenAI Services

Database

ChromaDB

Knowledge Pipeline

RAG

LangGraph

Agents

Frontend

Deployment

---

# Configuration Philosophy

Everything configurable should come from .env.

Never hardcode:

API Keys

Base URLs

Model Names

Database URLs

Storage Paths

Current configuration:

Application

OpenAI-compatible API

Embedding Model

LLM Model

Chroma Path

Database URL

Future Search API

---

# AI Architecture

The AI layer is intentionally divided into services.

Instead of allowing every module to create its own OpenAI client, we use centralized services.

Architecture:

```
settings.py

↓

openai_service.py

↓

llm_service.py

embedding_service.py

↓

AI Agents
```

Responsibilities:

openai_service.py

Creates OpenAI-compatible client.

---

llm_service.py

Handles all LLM text generation.

---

embedding_service.py

Generates embeddings.

---

Future:

search_service.py

Handles live web search.

---

vector_service.py

Handles ChromaDB.

---

No AI agent directly creates an OpenAI client.

---

# Multi-Agent Philosophy

This project is intentionally agentic.

Agents include:

Intent Agent

Profile Agent

Domain Agent

Research Agent

Verification Agent

Eligibility Agent

Recommendation Agent

Document Agent

Response Agent

Each agent performs one specialized responsibility.

LangGraph orchestrates the workflow.

---

# LangGraph Philosophy

LangGraph is the orchestration engine.

It manages:

Shared State

Conditional Routing

Loops

Clarifications

Verification

Agent Communication

FastAPI never orchestrates AI.

LangGraph does.

---

# RAG Philosophy

The knowledge source is not manually written JSON.

Instead:

Government PDFs

↓

Text Extraction

↓

Cleaning

↓

Chunking

↓

Embeddings

↓

ChromaDB

Metadata is stored separately.

Vectors are stored inside storage/chroma_db.

---

# Hybrid Retrieval

The system does NOT always perform web search.

Workflow:

Vector Search

↓

Enough Information?

YES

↓

Continue

NO

↓

Official Web Search

↓

Verification

↓

Continue

This makes the system agentic instead of wasteful.

---

# Eligibility Philosophy

Eligibility should never rely completely on an LLM.

Instead:

LLM

↓

Extract rules

↓

Python

↓

Deterministic evaluation

Examples:

Age

Income

State

Student

Occupation

Land

are checked using Python logic.

This improves reliability.

---

# API Philosophy

There will NOT be separate endpoints like:

/education

/agriculture

/healthcare

Instead there will be one intelligent endpoint.

```
POST /chat
```

The AI determines the domain automatically.

This makes the system scalable.

---

# Development Style

The project is intentionally being built like a professional software product.

The assistant guiding development should:

Explain architecture first.

Explain why each file exists.

Explain where it fits.

Then generate complete code.

Avoid jumping directly into implementation.

Avoid combining multiple responsibilities into one file.

Prioritize clean architecture over quick implementation.

If architecture improvements are identified during development, suggest them before writing code.

---

# Overall Goal

PolicyPilot AI should ultimately become a production-quality multi-agent AI platform demonstrating:

- Modular FastAPI backend
- LangGraph orchestration
- RAG with ChromaDB
- OpenAI-compatible services
- Deterministic eligibility engine
- Hybrid retrieval
- Official government knowledge
- Clean software engineering practices
  The emphasis is on **architecture, maintainability, scalability, and explainable AI**, not just producing working code.

---

I recommend keeping this as **`PROJECT_CONTEXT.md`** in the root of your repository (`PolicyPilot/PROJECT_CONTEXT.md`).

This will serve as the **single source of truth** for the project. If you ever start a new ChatGPT conversation, work with another AI assistant, or collaborate with another developer, sharing this one document will provide enough context for them to continue the project with the same architectural approach and development methodology.
