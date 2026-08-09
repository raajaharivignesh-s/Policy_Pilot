# PolicyPilot Backend API Documentation

## 1. Overview

PolicyPilot is an AI-powered government scheme discovery and eligibility platform.

The backend provides a REST API that accepts a citizen's natural-language question and processes it through the complete PolicyPilot workflow.

The backend workflow includes:

1. Query understanding
2. Intent detection
3. Domain detection
4. Knowledge retrieval
5. Source verification
6. Eligibility evaluation
7. Scheme recommendation
8. Required-document identification
9. Final response generation

---

# 2. Backend Technology

The backend is built using:

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- LangGraph
- LangChain
- OpenAI
- ChromaDB
- Tavily
- Pydantic

---

# 3. Base URL

## Local Development

```text
http://127.0.0.1:8000
```

Main API:

```text
http://127.0.0.1:8000/api/v1/query
```

---

# 4. API Documentation

FastAPI automatically provides interactive API documentation.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

OpenAPI specification:

```text
http://127.0.0.1:8000/openapi.json
```

---

# 5. Available Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Check application status |
| GET | `/health` | Health check |
| POST | `/api/v1/query` | Process a citizen query |

---

# 6. Root Endpoint

## Request

```http
GET /
```

## Example

```text
GET http://127.0.0.1:8000/
```

## Response

```json
{
  "application": "PolicyPilot AI",
  "version": "1.0.0",
  "status": "Running"
}
```

---

# 7. Health Endpoint

## Request

```http
GET /health
```

## Example

```text
GET http://127.0.0.1:8000/health
```

## Response

```json
{
  "status": "Healthy"
}
```

---

# 8. Main Query Endpoint

## Endpoint

```http
POST /api/v1/query
```

This is the primary endpoint used by the frontend.

The endpoint accepts a citizen's question and optionally accepts either:

- a PostgreSQL `user_id`
- a manually supplied `user_profile`

---

# 9. Request Schema

The request body is:

```json
{
  "query": "string",
  "user_id": "string or null",
  "user_profile": {}
}
```

## Fields

### query

Type:

```text
string
```

Required:

```text
Yes
```

Description:

```text
The citizen's natural-language question.
```

Example:

```json
{
  "query": "What financial assistance is available for farmers?"
}
```

The query must contain at least one character.

---

### user_id

Type:

```text
string
```

Required:

```text
No
```

Description:

```text
PostgreSQL user ID of the citizen.
```

The backend converts this value into a UUID.

Example:

```json
{
  "query": "Am I eligible for PM-KISAN?",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

When `user_id` is supplied, the backend attempts to retrieve the citizen's profile from PostgreSQL.

---

### user_profile

Type:

```text
object
```

Required:

```text
No
```

Default:

```json
{}
```

Description:

```text
Optional citizen profile information.

Used when user_id is not provided.
```

Example:

```json
{
  "user_profile": {
    "age": 35,
    "state": "Tamil Nadu",
    "district": "Erode",
    "occupation": "Farmer",
    "annual_income": 150000,
    "is_student": false,
    "land_acres": 3.5
  }
}
```

Additional scheme-specific fields can also be supplied when required by the eligibility rules.

Example:

```json
{
  "user_profile": {
    "age": 35,
    "state": "Tamil Nadu",
    "district": "Erode",
    "occupation": "Farmer",
    "annual_income": 150000,
    "is_student": false,
    "land_acres": 3.5,
    "is_indian_citizen": true,
    "owns_cultivable_land": true,
    "is_registered_farmer_family": true,
    "aadhaar_verified": true,
    "aadhaar_linked_bank_account": true,
    "ekyc_completed": true
  }
}
```

---

# 10. Profile Priority

There are two possible ways to provide citizen information.

### Option 1 — user_profile

```json
{
  "query": "Am I eligible for PM-KISAN?",
  "user_profile": {
    "occupation": "Farmer"
  }
}
```

The supplied profile is used directly.

### Option 2 — user_id

```json
{
  "query": "Am I eligible for PM-KISAN?",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

The backend retrieves the profile from PostgreSQL.

When `user_id` is supplied, the database profile is used as the workflow profile.

---

# 11. Simple Scheme Discovery Request

## Request

```json
{
  "query": "What financial assistance is available for farmers?"
}
```

## Expected workflow

```text
Citizen Query
      ↓
Intent Detection
      ↓
scheme_discovery
      ↓
Domain Detection
      ↓
agriculture
      ↓
Research / Retrieval
      ↓
Verification
      ↓
Recommendation
      ↓
Final Response
```

---

# 12. Education Example

## Request

```json
{
  "query": "What government schemes are available for students?"
}
```

Expected intent:

```text
scheme_discovery
```

Expected domain:

```text
education
```

---

# 13. Healthcare Example

## Request

```json
{
  "query": "What government schemes provide financial assistance for healthcare?"
}
```

Expected intent:

```text
scheme_discovery
```

Expected domain:

```text
healthcare
```

---

# 14. Eligibility Request

## Request

```json
{
  "query": "Am I eligible for PM-KISAN?",
  "user_profile": {
    "age": 35,
    "state": "Tamil Nadu",
    "district": "Erode",
    "occupation": "Farmer",
    "annual_income": 150000,
    "is_student": false,
    "land_acres": 3.5,
    "is_indian_citizen": true,
    "owns_cultivable_land": true,
    "is_registered_farmer_family": true,
    "aadhaar_verified": true,
    "aadhaar_linked_bank_account": true,
    "ekyc_completed": true
  }
}
```

Expected intent:

```text
eligibility_check
```

Expected domain:

```text
agriculture
```

The eligibility agent evaluates the supplied profile against the available scheme rules.

---

# 15. Response Schema

The successful response contains:

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

# 16. Response Fields

## query

The original processed citizen question.

Example:

```json
{
  "query": "What financial assistance is available for farmers?"
}
```

---

## intent

The detected purpose of the query.

Examples:

```text
scheme_discovery
eligibility_check
general_query
```

---

## domain

The detected government-service domain.

Currently supported domains include:

```text
agriculture
education
healthcare
```

More domains can be added later.

---

## retrieved_documents

Contains documents retrieved from the knowledge retrieval layer.

Example structure:

```json
[
  {
    "text": "Scheme information...",
    "metadata": {
      "domain": "agriculture",
      "scheme_name": "Example Scheme",
      "source_type": "knowledge_base"
    },
    "distance": 0.61
  }
]
```

This field is mainly useful for debugging and administrative interfaces.

The normal citizen-facing frontend does not need to display it.

---

## verified_information

Contains information that passed the verification stage.

Example:

```json
[
  {
    "scheme_name": "Example Scheme",
    "section": "Benefits",
    "supported": true,
    "reason": "Verified scheme information.",
    "evidence": "Verified evidence...",
    "trust_level": "high",
    "trust_score": 1,
    "trusted_source": true
  }
]
```

The frontend normally does not need to display the complete contents of this field.

---

## eligibility_results

Contains eligibility evaluation results.

Example:

```json
[
  {
    "scheme_name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
    "status": "eligible",
    "matched_rules": [],
    "failed_rules": [],
    "missing_information": [],
    "reason": "Eligibility requirements are satisfied."
  }
]
```

Possible status values include:

```text
eligible
ineligible
insufficient_information
```

---

## recommendations

Contains schemes recommended by the recommendation agent.

Example:

```json
[
  {
    "scheme_name": "Per Drop More Crop (Micro Irrigation)",
    "section": "Benefits",
    "reason": "Provides financial assistance and subsidies for micro irrigation."
  }
]
```

---

## required_documents

Contains documents identified as necessary for the request.

Example:

```json
[
  "Aadhaar Card",
  "Family Card",
  "Bank Account Details"
]
```

---

## final_response

Contains the final citizen-friendly response generated by the final response agent.

Example:

```text
Based on the available verified information, the following government schemes are recommended...
```

This is the primary response field that should normally be displayed to the citizen.

---

## needs_clarification

Boolean value indicating whether the workflow requires additional information.

Possible values:

```text
true
false
```

---

## clarification_question

Contains the question that should be presented to the citizen when:

```text
needs_clarification = true
```

Example:

```json
{
  "needs_clarification": true,
  "clarification_question": "Are you currently enrolled in a recognized educational institution?"
}
```

If clarification is not required:

```json
{
  "needs_clarification": false,
  "clarification_question": ""
}
```

---

## errors

Contains workflow-level errors when applicable.

Example:

```json
{
  "errors": []
}
```

An empty list indicates that the workflow did not report an internal workflow error.

---

# 17. Important Difference: Empty Result vs API Error

A successful API request can return:

```json
{
  "recommendations": [],
  "errors": [],
  "final_response": "I couldn't find sufficiently verified government scheme information to answer this question reliably."
}
```

This is still:

```text
HTTP 200
```

It means the backend successfully processed the request but did not find sufficiently verified information.

This is different from an actual backend failure.

---

# 18. HTTP Error Responses

## 400 — Invalid Request

Example:

```json
{
  "query": "What schemes are available?",
  "user_id": "not-a-valid-uuid"
}
```

Response:

```json
{
  "detail": "Invalid user_id."
}
```

---

## 404 — Citizen Profile Not Found

If a valid UUID is supplied but no citizen profile exists:

```json
{
  "detail": "Citizen profile not found."
}
```

---

## 500 — Profile Loading Failure

If PostgreSQL/profile retrieval fails:

```json
{
  "detail": "Failed to load citizen profile."
}
```

---

## 500 — Workflow Failure

If LangGraph execution fails:

```json
{
  "detail": "Workflow execution failed."
}
```

---

## 500 — Invalid Workflow Result

If the workflow does not return the expected dictionary:

```json
{
  "detail": "Workflow returned an invalid response."
}
```

---

# 19. Frontend Integration

The frontend should primarily use these response fields:

```text
final_response
recommendations
eligibility_results
required_documents
needs_clarification
clarification_question
errors
```

The following fields are mainly useful for debugging or advanced/admin interfaces:

```text
retrieved_documents
verified_information
```

---

# 20. Recommended Frontend Flow

```text
User enters question
        ↓
Frontend creates JSON request
        ↓
POST /api/v1/query
        ↓
FastAPI
        ↓
PolicyPilot LangGraph
        ↓
Workflow processing
        ↓
JSON response
        ↓
Frontend reads response
        ↓
Display final_response
        ↓
Display recommendations
        ↓
Display eligibility results
        ↓
Display required documents
```

---

# 21. Example Frontend Request

```javascript
const response = await fetch(
  "http://127.0.0.1:8000/api/v1/query",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      query: "What financial assistance is available for farmers?"
    })
  }
);

const data = await response.json();

console.log(data);
```

---

# 22. Example Frontend Handling

```javascript
if (!response.ok) {
  // Handle HTTP errors
  console.error(data.detail);
  return;
}

if (data.needs_clarification) {
  // Ask the citizen the clarification question
  console.log(data.clarification_question);
  return;
}

// Display the final answer
console.log(data.final_response);

// Display recommended schemes
console.log(data.recommendations);

// Display eligibility information
console.log(data.eligibility_results);
```

---

# 23. Current Supported Domains

The current MVP supports:

```text
Agriculture
Education
Healthcare
```

The architecture is designed so additional domains can be added later without changing the main API contract.

---

# 24. Backend Architecture

```text
Frontend
    |
    | POST /api/v1/query
    ↓
FastAPI
    |
    ↓
Query Route
    |
    ├── user_id
    │      ↓
    │  PostgreSQL
    │      ↓
    │  Citizen Profile
    │
    └── user_profile
           ↓
      LangGraph Workflow
           |
           ├── Intent Detection
           |
           ├── Domain Detection
           |
           ├── Research Agent
           |
           ├── RAG / ChromaDB
           |
           ├── Web Search
           |
           ├── Source Trust
           |
           ├── Verification Agent
           |
           ├── Eligibility Agent
           |
           ├── Recommendation Agent
           |
           └── Final Response Agent
                    |
                    ↓
              Structured JSON
                    |
                    ↓
                 Frontend
```

---

# 25. Backend Testing Status

The backend currently has a complete automated regression suite.

Current status:

```text
110 tests passed
0 tests failed
0 warnings
```

Manual API testing has also verified:

```text
Agriculture scheme discovery      ✅
Education scheme discovery        ✅
Healthcare scheme discovery       ✅
Eligibility - insufficient info   ✅
Eligibility - eligible            ✅
```

---

# 26. API Contract Summary

The frontend team only needs to know:

```text
POST /api/v1/query
```

Request:

```json
{
  "query": "Citizen question",
  "user_id": "Optional UUID",
  "user_profile": {}
}
```

Response:

```json
{
  "query": "...",
  "intent": "...",
  "domain": "...",
  "retrieved_documents": [],
  "verified_information": [],
  "eligibility_results": [],
  "recommendations": [],
  "required_documents": [],
  "final_response": "...",
  "needs_clarification": false,
  "clarification_question": "",
  "errors": []
}
```

The frontend does not need to know the internal LangGraph implementation to consume this API.