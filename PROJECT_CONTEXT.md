# POLICY PILOT AI — MASTER PROJECT CONTEXT

## 1. Project Overview

PolicyPilot AI is a production-oriented AI capstone project designed to help citizens discover and understand government schemes and evaluate their eligibility based on their profile.

The system is designed as a **multi-agent AI platform**, not as a simple chatbot or basic RAG application.

The backend combines:

* FastAPI
* PostgreSQL
* SQLAlchemy
* LangGraph
* OpenAI-compatible LLM APIs
* ChromaDB
* RAG
* Hybrid retrieval
* Web search
* Source trust and verification
* Deterministic eligibility evaluation
* Scheme recommendation
* Structured API responses

The frontend is being developed separately by another team member/team.

---

# 2. Current Project Goal

The current MVP focuses on three government-service domains:

1. Agriculture
2. Education
3. Healthcare

The system should allow a citizen to ask questions naturally, such as:

```text
What financial assistance is available for farmers?
```

or:

```text
What government schemes are available for students?
```

or:

```text
What government schemes provide financial assistance for healthcare?
```

The backend determines the user's intent and domain automatically and processes the request through the appropriate workflow.

Additional domains can be added later without redesigning the core API.

---

# 3. Problem Statement

Citizens often struggle to find suitable government schemes because:

* Government information is distributed across multiple portals.
* Government documents can be difficult to understand.
* Eligibility requirements differ between schemes.
* Scheme information can change over time.
* Citizens may not know which schemes apply to them.
* Generic AI systems may hallucinate or provide unsupported information.

PolicyPilot addresses this by combining:

```text
Citizen Query
      ↓
Intent Understanding
      ↓
Domain Detection
      ↓
Knowledge Retrieval
      ↓
Source Verification
      ↓
Eligibility Evaluation
      ↓
Recommendation
      ↓
Final Citizen-Friendly Response
```

---

# 4. Overall Architecture

The current backend architecture is:

```text
                    FRONTEND
                       │
                       │ POST /api/v1/query
                       ▼
                ┌──────────────┐
                │   FastAPI    │
                │  Query API   │
                └──────┬───────┘
                       │
              ┌────────┴─────────┐
              │                  │
           user_id          user_profile
              │                  │
              ▼                  │
         PostgreSQL              │
              │                  │
              └────────┬─────────┘
                       ▼
              LangGraph Workflow
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
     Intent         Research       Eligibility
      Agent           Agent           Agent
        │              │              │
        ▼              ▼              ▼
     Domain          RAG/Web         Rules
      Agent         Retrieval      Evaluation
                       │
                       ▼
                 Verification
                       │
                       ▼
                Recommendation
                       │
                       ▼
                Final Response
                       │
                       ▼
                   FastAPI
                       │
                       ▼
                    FRONTEND
```

The frontend does not directly communicate with the LLM, ChromaDB, PostgreSQL, or internal agents.

All AI processing goes through the backend API.

---

# 5. Backend Technology Stack

## Backend Framework

```text
FastAPI
```

FastAPI provides:

* REST API
* Request validation
* Response validation
* Swagger documentation
* Error handling

---

## Programming Language

```text
Python 3.11
```

---

## Database

```text
PostgreSQL
SQLAlchemy
Alembic
```

PostgreSQL is used for persistent citizen/profile information and application data.

---

## AI Orchestration

```text
LangGraph
```

LangGraph manages:

* Shared workflow state
* Agent execution
* Conditional routing
* Workflow sequencing
* Eligibility processing
* Recommendation flow
* Final response generation

FastAPI does not directly orchestrate individual AI agents.

---

## LLM

The backend uses an OpenAI-compatible LLM service.

Current configured model:

```text
gpt-4.1-nano
```

The model is configured through environment variables.

---

## Embeddings

Current configured embedding model:

```text
text-embedding-3-small
```

Embeddings are used for semantic retrieval.

---

## Vector Database

```text
ChromaDB
```

ChromaDB stores vector representations used by the RAG retrieval system.

Runtime vector storage is kept under:

```text
backend/storage/
```

Generated storage is not committed to Git.

---

## Web Search

```text
Tavily
```

Web search is used as part of the hybrid retrieval architecture when additional information is required.

---

# 6. Project Folder Structure

Current high-level repository structure:

```text
Policy-Pilot/
│
├── backend/
│
├── frontend/
│
├── knowledge_base/
│
├── docs/
│
├── docker/
│
├── scripts/
│
├── PROJECT_CONTEXT.md
│
├── README.md
│
├── docker-compose.yml
│
└── .gitignore
```

---

# 7. Backend Structure

The backend follows separation of concerns.

Important areas include:

```text
backend/
│
├── app/
│   │
│   ├── agents/
│   │
│   ├── api/
│   │
│   ├── config/
│   │
│   ├── core/
│   │
│   ├── database/
│   │
│   ├── graph/
│   │
│   ├── models/
│   │
│   ├── prompts/
│   │
│   ├── rag/
│   │
│   ├── schemas/
│   │
│   ├── services/
│   │
│   ├── tools/
│   │
│   └── main.py
│
├── alembic/
│
├── requirements/
│
├── tests/
│
├── storage/
│
├── logs/
│
├── .env
│
└── .env.example
```

---

# 8. Configuration

Configuration is centralized in:

```text
backend/app/core/settings.py
```

Current settings include:

```text
APP_NAME
APP_VERSION
OPENAI_API_KEY
OPENAI_BASE_URL
LLM_MODEL
EMBEDDING_MODEL
DATABASE_URL
CHROMA_DB_PATH
TAVILY_API_KEY
```

Secrets and environment-specific values are stored in:

```text
backend/.env
```

The `.env` file is ignored by Git.

A safe template is provided as:

```text
backend/.env.example
```

Never commit real API keys or secrets.

---

# 9. FastAPI Application

The main application is:

```text
backend/app/main.py
```

Current application endpoints:

```text
GET /
GET /health
POST /api/v1/query
```

---

# 10. Root Endpoint

Endpoint:

```text
GET /
```

Purpose:

Checks whether the application is running.

Example response:

```json
{
  "application": "PolicyPilot AI",
  "version": "1.0.0",
  "status": "Running"
}
```

---

# 11. Health Endpoint

Endpoint:

```text
GET /health
```

Example response:

```json
{
  "status": "Healthy"
}
```

---

# 12. Main Query API

The primary backend endpoint is:

```text
POST /api/v1/query
```

Local development URL:

```text
http://127.0.0.1:8000/api/v1/query
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

OpenAPI:

```text
http://127.0.0.1:8000/openapi.json
```

---

# 13. Query Request

The request model is:

```json
{
  "query": "string",
  "user_id": "string or null",
  "user_profile": {}
}
```

## query

Required.

Type:

```text
string
```

Contains the citizen's natural-language question.

Example:

```json
{
  "query": "What financial assistance is available for farmers?"
}
```

---

## user_id

Optional.

Type:

```text
string
```

Represents the citizen's PostgreSQL user ID.

When supplied:

```text
user_id
   ↓
UUID validation
   ↓
PostgreSQL
   ↓
CitizenProfile
   ↓
Workflow
```

Invalid UUID:

```text
HTTP 400
```

---

## user_profile

Optional.

Type:

```text
object
```

Default:

```json
{}
```

Used when `user_id` is not supplied.

Example:

```json
{
  "user_profile": {
    "age": 24,
    "state": "Tamil Nadu",
    "district": "Erode",
    "occupation": "Farmer",
    "annual_income": 150000,
    "is_student": false,
    "land_acres": 2.5
  }
}
```

Additional fields can be supplied when required by eligibility rules.

---

# 14. Profile Handling

There are two ways to provide profile information.

## Method 1 — Direct Profile

```json
{
  "query": "Am I eligible for PM-KISAN?",
  "user_profile": {
    "occupation": "Farmer"
  }
}
```

The supplied profile is passed into the workflow.

---

## Method 2 — Database Profile

```json
{
  "query": "Am I eligible for PM-KISAN?",
  "user_id": "VALID-UUID"
}
```

The backend retrieves the citizen profile from PostgreSQL.

When `user_id` is explicitly supplied, the database profile is used.

---

# 15. LangGraph Shared State

The shared workflow state is defined in:

```text
backend/app/graph/state.py
```

The state contains:

```text
query
user_profile
intent
domain
retrieved_documents
verified_information
eligibility_results
recommendations
required_documents
final_response
needs_clarification
clarification_question
errors
```

The state allows individual agents to read required information and write their results back into the shared workflow.

---

# 16. Agent Architecture

The backend uses specialized agents.

Current important agents include:

```text
Intent Agent
Domain Agent
Research Agent
Verification Agent
Eligibility Agent
Recommendation Agent
Final Response Agent
```

Each agent has a specialized responsibility.

The objective is to avoid placing all AI logic into a single large module.

---

# 17. Intent Detection

The intent agent determines what the citizen is trying to accomplish.

Current important intents include:

```text
scheme_discovery
eligibility_check
general_query
```

Example:

```text
"What schemes are available for farmers?"
```

Expected:

```text
scheme_discovery
```

Example:

```text
"Am I eligible for PM-KISAN?"
```

Expected:

```text
eligibility_check
```

---

# 18. Domain Detection

The domain agent identifies the relevant government-service domain.

Current MVP domains:

```text
agriculture
education
healthcare
```

Example:

```text
"What financial assistance is available for farmers?"
```

Expected:

```text
agriculture
```

Example:

```text
"What government schemes are available for students?"
```

Expected:

```text
education
```

Example:

```text
"What government schemes provide financial assistance for healthcare?"
```

Expected:

```text
healthcare
```

Additional domains can be added later.

---

# 19. RAG Architecture

The RAG system uses knowledge-base content and vector retrieval.

General process:

```text
Government Knowledge
        ↓
Document Processing
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
        ↓
Semantic Retrieval
        ↓
Research Agent
```

The knowledge base contains domain-specific information.

Current MVP domains:

```text
knowledge_base/
├── raw/
│   ├── agriculture/
│   ├── education/
│   └── healthcare/
│
└── processed/
```

---

# 20. Hybrid Retrieval

The system uses hybrid retrieval.

The general architecture is:

```text
Citizen Query
      ↓
Vector Retrieval
      ↓
Is enough reliable information available?
      │
      ├── YES → Continue
      │
      └── NO
           ↓
       Web Search
           ↓
       Verification
           ↓
         Continue
```

The objective is to avoid unnecessary web searches while still allowing the system to obtain additional information when local knowledge is insufficient.

---

# 21. Source Trust and Verification

Retrieved information is not automatically treated as reliable.

The verification stage checks whether information is sufficiently supported before it is used for recommendations.

The project includes:

```text
Source Trust Service
Verification Agent
```

The verification layer helps prevent unsupported or low-confidence information from being presented as a reliable government scheme recommendation.

This is an important part of the system's reliability architecture.

---

# 22. Eligibility Architecture

Eligibility is not intended to rely entirely on LLM reasoning.

The architecture separates:

```text
LLM
 ↓
Understand / extract relevant information
 ↓
Deterministic eligibility evaluation
 ↓
Eligibility result
```

Eligibility can consider scheme-specific information such as:

```text
Age
Income
State
Occupation
Student status
Land
Citizenship
Farmer status
Aadhaar verification
Bank account requirements
e-KYC
```

The exact requirements depend on the scheme.

Important principle:

```text
Being a student should not automatically make a citizen
eligible or ineligible for a scheme unless the scheme's
actual eligibility rules contain a student-related condition.
```

---

# 23. Eligibility Result

Eligibility results follow a structured format.

Example:

```json
{
  "scheme_name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
  "status": "eligible",
  "matched_rules": [],
  "failed_rules": [],
  "missing_information": [],
  "reason": "Eligibility requirements are satisfied."
}
```

Possible states include:

```text
eligible
ineligible
insufficient_information
```

---

# 24. Recommendation Architecture

The recommendation stage uses verified information rather than blindly recommending every retrieved document.

General flow:

```text
Retrieved Information
        ↓
Verification
        ↓
Supported Information
        ↓
Recommendation Agent
        ↓
Recommended Schemes
```

A vague or insufficiently supported document should not automatically become a recommendation.

---

# 25. Final Response Architecture

The final response agent converts the structured workflow results into a citizen-friendly response.

The final response can contain:

* Scheme name
* Benefits
* Eligibility information
* Important conditions
* Required documents
* Clarification questions
* Other relevant information

The final response should be based on verified workflow information.

---

# 26. API Response

The main query API returns:

```json
{
  "query": "string",
  "intent": "string",
  "domain": "string",
  "retrieved_documents": [],
  "verified_information": [],
  "eligibility_results": [],
  "recommendations": [],
  "required_documents": [],
  "final_response": "string",
  "needs_clarification": false,
  "clarification_question": "",
  "errors": []
}
```

---

# 27. Important Response Fields for Frontend

The frontend should primarily use:

```text
final_response
recommendations
eligibility_results
required_documents
needs_clarification
clarification_question
errors
```

The following fields are mainly useful for debugging or advanced interfaces:

```text
retrieved_documents
verified_information
```

---

# 28. Error Handling

The backend handles important API failures.

## Invalid User ID

```text
HTTP 400
```

Example:

```json
{
  "detail": "Invalid user_id."
}
```

---

## Citizen Profile Not Found

```text
HTTP 404
```

Example:

```json
{
  "detail": "Citizen profile not found."
}
```

---

## Profile Loading Failure

```text
HTTP 500
```

Example:

```json
{
  "detail": "Failed to load citizen profile."
}
```

---

## Workflow Failure

```text
HTTP 500
```

Example:

```json
{
  "detail": "Workflow execution failed."
}
```

---

## Invalid Workflow Result

```text
HTTP 500
```

Example:

```json
{
  "detail": "Workflow returned an invalid response."
}
```

---

# 29. Successful Request With No Recommendation

A request can successfully return HTTP 200 while having no recommendations.

Example:

```json
{
  "recommendations": [],
  "errors": [],
  "final_response": "I couldn't find sufficiently verified government scheme information to answer this question reliably."
}
```

This does not mean the backend failed.

It means the backend successfully processed the request but did not find sufficiently reliable information to recommend a scheme.

---

# 30. Logging

The project contains logging infrastructure using Loguru.

Log files are located under:

```text
backend/logs/
```

Current log files:

```text
backend.log
error.log
```

Runtime logs are local/generated artifacts and should not be committed if they are not required by the repository.

---

# 31. Environment and Generated Files

The following should remain local and should not be committed:

```text
.env
venv/
backend/venv/
backend/storage/
generated runtime data
```

The repository contains:

```text
backend/.env.example
```

as the safe configuration template.

---

# 32. Testing Status

The backend has been extensively tested.

Current automated test result:

```text
110 passed
1 warning
```

The warning is related to the installed Starlette/httpx test-client compatibility notice.

The test suite covers:

* API endpoints
* Query validation
* Agriculture workflow
* Education workflow
* Healthcare workflow
* Eligibility
* Profile loading
* Invalid user IDs
* Missing profiles
* Workflow failures
* Research agent
* Knowledge ingestion
* Router behavior
* Verification agent
* Final response agent
* Source trust service
* Response schema

The backend test suite has reached a stable MVP state.

---

# 33. Manual API Testing

Manual testing through Swagger has verified the three current domains.

## Agriculture

Example:

```text
What financial assistance is available for farmers?
```

Verified:

```text
Intent → scheme_discovery
Domain → agriculture
Retrieval → working
Verification → working
Recommendation → working
Final response → working
```

---

## Education

Example:

```text
What government schemes are available for students?
```

Verified:

```text
Intent → scheme_discovery
Domain → education
Retrieval → working
Verification → working
Recommendation → working
Final response → working
```

---

## Healthcare

Example:

```text
What government schemes provide financial assistance for healthcare?
```

Verified:

```text
Intent → scheme_discovery
Domain → healthcare
Retrieval → working
Verification → working
Recommendation → working
Final response → working
```

---

# 34. API Documentation

The frontend integration documentation is maintained separately at:

```text
docs/BACKEND_API.md
```

That document contains:

* API endpoints
* Request format
* Response format
* Examples
* Error handling
* Frontend integration guidance

`PROJECT_CONTEXT.md` describes the overall project.

`docs/BACKEND_API.md` describes the backend API contract.

---

# 35. Frontend Integration

The frontend is being developed separately.

The frontend should communicate with the backend through:

```text
POST /api/v1/query
```

The frontend should not directly communicate with:

```text
OpenAI
ChromaDB
PostgreSQL
Tavily
LangGraph
```

The backend is responsible for all of these operations.

---

# 36. Recommended Frontend Flow

```text
Citizen
   ↓
Frontend UI
   ↓
POST /api/v1/query
   ↓
FastAPI
   ↓
LangGraph Workflow
   ↓
AI Processing
   ↓
Structured JSON
   ↓
Frontend
   ↓
Citizen-Friendly UI
```

The frontend should display the most relevant response information and avoid exposing internal retrieval/debugging details unless an administrator/debug interface is intentionally created.

---

# 37. Backend Development Status

## Completed

```text
Project Structure                  ✅
Backend Structure                  ✅
Configuration                      ✅
Environment Management             ✅
FastAPI Initialization             ✅
PostgreSQL Integration             ✅
SQLAlchemy                         ✅
Alembic                            ✅
OpenAI Service Architecture        ✅
Embedding Service                  ✅
Vector Database                    ✅
Knowledge Retrieval                ✅
RAG                                ✅
Web Search                         ✅
Hybrid Retrieval                   ✅
LangGraph Workflow                 ✅
Intent Agent                       ✅
Domain Agent                       ✅
Research Agent                     ✅
Verification Agent                 ✅
Source Trust Service               ✅
Eligibility Agent                  ✅
Recommendation Agent               ✅
Final Response Agent               ✅
API Layer                          ✅
Error Handling                     ✅
Automated Tests                    ✅
Manual API Testing                 ✅
API Documentation                  ✅
Git Integration                    ✅
```

---

# 38. Current MVP Domains

The current MVP intentionally supports three domains:

```text
Agriculture
Education
Healthcare
```

This is sufficient for the current capstone MVP.

The architecture should remain extensible so that additional domains can be added later.

Possible future domains can include:

```text
Housing
Employment
Women Welfare
Social Welfare
Senior Citizens
Disability Support
```

These are future expansion areas and are not part of the current MVP unless explicitly implemented.

---

# 39. Current Project Boundary

The backend MVP is now considered complete.

The immediate priority is no longer adding more backend domains or unnecessary backend features.

The next project phase is:

```text
Backend MVP
     ↓
Frontend Integration
     ↓
End-to-End Testing
     ↓
Deployment Preparation
```

Backend changes should now be made only when:

* Frontend integration requires an API change.
* A real bug is discovered.
* Testing identifies a problem.
* Security/reliability improvements are required.
* Deployment requires configuration changes.

Avoid unnecessary architectural changes while frontend integration is in progress.

---

# 40. Git Status and Branching

The completed backend work was developed on:

```text
Rag_and_Web-search
```

The completed backend MVP was committed as:

```text
Complete PolicyPilot backend MVP
```

The completed work has been merged into:

```text
main
```

and pushed to:

```text
origin/main
```

The repository's `main` branch is now the stable baseline for frontend development.

The feature branch:

```text
Rag_and_Web-search
```

can remain as project history unless the team later decides to delete it.

---

# 41. Development Philosophy

The project follows separation of concerns.

Each component should have a clear responsibility.

Examples:

```text
settings.py
    ↓
Configuration

main.py
    ↓
FastAPI application initialization

openai_service.py
    ↓
OpenAI client/service access

search_service.py
    ↓
Web search

vector_service.py
    ↓
Vector database operations

research_agent.py
    ↓
Research and retrieval orchestration

verification_agent.py
    ↓
Information verification

eligibility_agent.py
    ↓
Eligibility evaluation

recommendation_agent.py
    ↓
Scheme recommendation

final_response_agent.py
    ↓
Citizen-facing response
```

Avoid combining unrelated responsibilities into a single file.

---

# 42. Development Methodology

When continuing development:

1. Understand the requirement.
2. Identify which architectural layer is responsible.
3. Check the existing implementation before creating new code.
4. Preserve separation of concerns.
5. Make the smallest appropriate change.
6. Add or update tests.
7. Run the relevant tests.
8. Run the complete test suite when appropriate.
9. Manually test API behavior when required.
10. Update documentation when the API or architecture changes.
11. Commit changes only after verification.

Do not rewrite working architecture without a clear reason.

---

# 43. Important Architectural Principles

## Principle 1 — FastAPI is the API Layer

FastAPI handles:

```text
HTTP
Request Validation
Response Validation
API Errors
```

It should not contain complex AI orchestration logic.

---

## Principle 2 — LangGraph is the Workflow Layer

LangGraph handles:

```text
Agent orchestration
State
Routing
Workflow execution
```

---

## Principle 3 — Agents Have Specialized Responsibilities

Agents should not become large all-purpose modules.

---

## Principle 4 — Retrieval and Verification Are Separate

Retrieving information does not automatically make it trustworthy.

The system should verify information before using it for recommendations.

---

## Principle 5 — Eligibility Should Be Deterministic Where Possible

LLMs can help understand information, but final rule evaluation should rely on explicit logic wherever possible.

---

## Principle 6 — Secrets Must Never Be Committed

API keys belong in:

```text
.env
```

and not in Git.

---

## Principle 7 — Generated Runtime Data Must Remain Local

Examples:

```text
venv/
backend/storage/
logs/
```

should not be treated as source code.

---

# 44. Current End-to-End Workflow

The complete current workflow is:

```text
Citizen Query
      ↓
FastAPI
      ↓
Load Profile
      ↓
LangGraph State
      ↓
Intent Detection
      ↓
Domain Detection
      ↓
Research
      ↓
Vector Retrieval
      ↓
Web Search When Needed
      ↓
Source Trust / Verification
      ↓
Eligibility Evaluation
      ↓
Recommendation
      ↓
Required Documents
      ↓
Final Response
      ↓
Structured API Response
      ↓
Frontend
```

Not every query necessarily uses every stage in exactly the same way because LangGraph routing depends on the detected intent and workflow state.

---

# 45. Future Work

Future improvements can include:

```text
Additional government domains
More government schemes
More official sources
Improved source freshness
Authentication
Role-based access
Citizen profile management
Conversation history
Caching
Redis-based scaling
Background jobs
Advanced observability
Production deployment
Docker optimization
CI/CD
Frontend integration
End-to-end testing
Performance optimization
```

These are future improvements and should not be treated as completed functionality unless implemented.

---

# 46. Project Completion Definition

The backend MVP is considered complete when:

```text
FastAPI API                         ✅
Database integration                ✅
RAG                                 ✅
Vector database                     ✅
Web search                          ✅
Source verification                 ✅
LangGraph orchestration             ✅
Eligibility                         ✅
Recommendations                     ✅
Final responses                     ✅
Three MVP domains                   ✅
Automated tests                     ✅
Manual API testing                  ✅
API documentation                   ✅
GitHub main                         ✅
```

This condition has now been achieved.

---

# 47. Immediate Next Phase

The next phase is **Frontend Integration**.

The frontend team should use:

```text
POST /api/v1/query
```

and refer to:

```text
docs/BACKEND_API.md
```

for the API contract.

The backend should remain stable during frontend development unless an actual integration requirement or defect requires a change.

---

# 48. Master Project Summary

PolicyPilot AI is a production-oriented multi-agent government scheme discovery and eligibility platform.

The current backend provides:

```text
FastAPI
   +
PostgreSQL
   +
LangGraph
   +
RAG
   +
ChromaDB
   +
Web Search
   +
Source Verification
   +
Eligibility Engine
   +
Recommendation Engine
   +
Final Response Generation
```

Current MVP domains:

```text
Agriculture
Education
Healthcare
```

Current primary API:

```text
POST /api/v1/query
```

Current backend testing:

```text
110 tests passed
```

Current backend status:

```text
MVP COMPLETE
```

Current next phase:

```text
FRONTEND INTEGRATION
```

The project should continue to prioritize:

```text
Reliability
Maintainability
Separation of Concerns
Explainability
Scalability
Security
Testability
Production-oriented architecture
```

This document is the master context for continuing PolicyPilot AI development.
