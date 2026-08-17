# Requirements Document

## Introduction

This document defines the requirements for four sequential enhancements to the PolicyPilot application — an AI-powered Government Scheme Discovery and Eligibility platform built with FastAPI, LangGraph, React, and PostgreSQL.

The four features are designed to be delivered and approved one at a time:

1. **Persistent Conversation Memory** — ensure all LangGraph agents use conversation history for contextual follow-up answers.
2. **User Dashboard with Document Wallet** — replace the static profile panel with a user dashboard containing a folder-based document management system.
3. **Document Upload During Chat + Smart Document Processing** — allow users to upload documents during a conversation, store them in the wallet, and use them for scheme eligibility checks.
4. **Login Page (Open Email-Based Authentication)** — add an email-based login flow so every user has a persistent identity used across the entire app.

Each feature group is fully self-contained so that tasks can be implemented and approved independently before the next group begins.

---

## Glossary

- **PolicyPilot_System**: The complete PolicyPilot application (FastAPI backend + React frontend + LangGraph workflow).
- **LangGraph_Workflow**: The LangGraph-based multi-agent pipeline that processes citizen queries through intent detection, domain classification, RAG research, verification, eligibility checking, and recommendation.
- **Conversation_History**: An ordered list of `{role, content}` message objects representing the prior turns in a single conversation session between a citizen and the PolicyPilot_System.
- **Conversation_Session**: A single conversation identified by a `conversation_id`, containing one or more turns.
- **Intent_Agent**: The LangGraph agent responsible for classifying the citizen's query intent (e.g., `eligibility_check`, `scheme_discovery`).
- **Final_Response_Agent**: The LangGraph agent responsible for generating the final natural-language response presented to the citizen.
- **Citizen**: A user of the PolicyPilot_System who queries government schemes.
- **Authenticated_User**: A Citizen who has completed the email-based login flow and has a confirmed identity in the database (`User` record).
- **Anonymous_User**: A Citizen who interacts with the PolicyPilot_System without logging in.
- **Document_Wallet**: A folder-based document storage system associated with an Authenticated_User, where documents can be organised by Person_Folder.
- **Person_Folder**: A named container within a Document_Wallet representing a person (e.g., "Myself", "Father", "Mother") under whose name documents are stored.
- **Wallet_Document**: A file (PDF, image, or scanned document) stored inside a Person_Folder within a Document_Wallet.
- **User_Dashboard**: A page or panel in the frontend that displays the Authenticated_User's identity details and provides access to the Document_Wallet.
- **OCR_Processor**: A backend service that extracts text content from image-based Wallet_Documents.
- **PDF_Reader**: A backend service that extracts text content from PDF-based Wallet_Documents.
- **Auth_Service**: The backend service responsible for creating, validating, and managing Authenticated_User sessions via email-based authentication.
- **JWT_Token**: A signed JSON Web Token issued by the Auth_Service to an Authenticated_User upon successful login, used to authenticate subsequent API requests.
- **RAG_Pipeline**: The Retrieval-Augmented Generation pipeline within the LangGraph_Workflow consisting of the research agent and verification agent.

---

## Requirements

---

## Feature 1: Persistent Conversation Memory

---

### Requirement 1.1: Conversation History Forwarded to All Agents

**User Story:** As a Citizen, I want to ask follow-up questions in the same conversation without repeating context, so that the PolicyPilot_System can give relevant, contextual answers.

#### Acceptance Criteria

1. WHEN a query is submitted with a non-empty `conversation_history`, THE Intent_Agent SHALL include the full `conversation_history` in the LLM prompt used for intent classification, so that follow-up questions like "what about healthcare?" are classified in context of the prior turn.
2. WHEN a query is submitted with a non-empty `conversation_history`, THE Final_Response_Agent SHALL include the full `conversation_history` in the LLM prompt used to generate the final response, so that the response references prior turns where relevant.
3. WHEN a query is submitted with a non-empty `conversation_history`, THE LangGraph_Workflow SHALL propagate the `conversation_history` list unchanged through all agents without modification.
4. WHEN a `conversation_history` entry is missing a `role` or `content` key, THE Intent_Agent SHALL skip that entry rather than raise an exception.
5. WHEN a `conversation_history` entry is missing a `role` or `content` key, THE Final_Response_Agent SHALL skip that entry rather than raise an exception.

---

### Requirement 1.2: Server-Side History Accumulation

**User Story:** As a Citizen, I want the backend to remember what I said earlier in the session, so that my conversation context is preserved even if the frontend does not send history.

#### Acceptance Criteria

1. WHEN the backend processes a query and produces a non-empty `final_response`, THE PolicyPilot_System SHALL append a `{role: "user", content: query}` entry and a `{role: "assistant", content: final_response}` entry to the server-side history store keyed by `conversation_id`.
2. WHEN a query arrives with an empty `conversation_history` field and a known `conversation_id`, THE PolicyPilot_System SHALL use the server-side accumulated history for that `conversation_id` as the `conversation_history` for the LangGraph_Workflow invocation.
3. WHEN a query arrives with a non-empty `conversation_history` field, THE PolicyPilot_System SHALL use the frontend-provided list as the authoritative `conversation_history` and SHALL NOT override it with the server-side history.
4. WHEN the server-side history for a `conversation_id` exceeds 20 entries, THE PolicyPilot_System SHALL truncate the history to the 20 most recent entries before appending new messages.
5. WHEN a new `conversation_id` is generated (no reuse), THE PolicyPilot_System SHALL initialise a new empty history list for that `conversation_id` in the server-side store.

---

### Requirement 1.3: Frontend Conversation History Construction

**User Story:** As a Citizen, I want the frontend to correctly build and send conversation history on every follow-up query, so that the backend always has the full context of the current session.

#### Acceptance Criteria

1. WHEN the frontend submits a query, THE PolicyPilot_System SHALL send a `conversation_history` field in the request body containing all prior `{role, content}` pairs from the current Conversation_Session, excluding the message being submitted in the current request.
2. WHEN the active chat session has no prior messages, THE PolicyPilot_System SHALL send an empty list as `conversation_history`.
3. WHEN an assistant message in the chat history does not contain a `final_response` field, THE PolicyPilot_System SHALL exclude that message from the `conversation_history` sent to the backend.
4. THE PolicyPilot_System SHALL cap the `conversation_history` sent from the frontend to the 20 most recent `{role, content}` pairs to prevent excessively large request payloads.

---

## Feature 2: Clickable User Profile → User Dashboard

---

### Requirement 2.1: User Dashboard Page

**User Story:** As an Authenticated_User, I want a dedicated dashboard page that shows my identity and document wallet, so that I can manage personal information and documents from one place.

#### Acceptance Criteria

1. WHEN an Authenticated_User clicks their profile area in the sidebar or navigation, THE PolicyPilot_System SHALL navigate to the User_Dashboard page without reloading the entire application.
2. THE User_Dashboard SHALL display the Authenticated_User's `name` (when available) and `email` address fetched from the backend.
3. WHEN the Authenticated_User's `name` is null or empty, THE User_Dashboard SHALL display the email address as the primary identifier.
4. WHEN the User_Dashboard is accessed by an Anonymous_User, THE PolicyPilot_System SHALL redirect the Anonymous_User to the login page.
5. THE User_Dashboard SHALL contain a Document_Wallet section as specified in Requirement 2.2.

---

### Requirement 2.2: Document Wallet — Folder Management

**User Story:** As an Authenticated_User, I want to create named folders in my Document Wallet for different people, so that I can organise documents by individual.

#### Acceptance Criteria

1. THE User_Dashboard SHALL display all existing Person_Folders belonging to the Authenticated_User, ordered by creation date ascending.
2. WHEN an Authenticated_User submits a non-empty folder name via the "Create Folder" form, THE PolicyPilot_System SHALL create a new Person_Folder record in the database associated with the Authenticated_User's `user_id`.
3. WHEN a folder name submitted during creation contains only whitespace, THE PolicyPilot_System SHALL reject the request and display a validation error without creating a record.
4. WHEN an Authenticated_User deletes a Person_Folder, THE PolicyPilot_System SHALL delete the Person_Folder record and all associated Wallet_Document records from the database in a single cascading operation.
5. WHEN a Person_Folder is deleted, THE User_Dashboard SHALL update the folder list to remove the deleted folder without requiring a full page reload.
6. THE PolicyPilot_System SHALL expose a `GET /api/v1/wallet/folders` endpoint that returns all Person_Folders for the Authenticated_User identified by the JWT_Token in the request.
7. THE PolicyPilot_System SHALL expose a `POST /api/v1/wallet/folders` endpoint that accepts a folder name and creates a new Person_Folder for the Authenticated_User.
8. THE PolicyPilot_System SHALL expose a `DELETE /api/v1/wallet/folders/{folder_id}` endpoint that deletes a Person_Folder owned by the Authenticated_User.
9. IF the `DELETE /api/v1/wallet/folders/{folder_id}` request targets a folder not owned by the requesting Authenticated_User, THEN THE PolicyPilot_System SHALL return HTTP 403.

---

### Requirement 2.3: Document Wallet — Document Management

**User Story:** As an Authenticated_User, I want to upload and view documents inside each folder, so that I can keep relevant files organised by person.

#### Acceptance Criteria

1. WHEN an Authenticated_User uploads a file to a Person_Folder, THE PolicyPilot_System SHALL store the file in persistent storage and create a Wallet_Document record in the database with the `folder_id`, original filename, file size in bytes, MIME type, and storage path.
2. THE PolicyPilot_System SHALL accept the following MIME types for upload: `application/pdf`, `image/jpeg`, `image/png`, `image/webp`.
3. IF an uploaded file exceeds 10 megabytes, THEN THE PolicyPilot_System SHALL reject the upload and return HTTP 413 with a descriptive error message.
4. IF an uploaded file has a MIME type not in the accepted list, THEN THE PolicyPilot_System SHALL reject the upload and return HTTP 415 with a descriptive error message.
5. WHEN an Authenticated_User selects a Person_Folder in the User_Dashboard, THE User_Dashboard SHALL display all Wallet_Documents in that folder showing filename, file size, upload date, and a delete action.
6. WHEN an Authenticated_User deletes a Wallet_Document, THE PolicyPilot_System SHALL remove the Wallet_Document record from the database and delete the corresponding file from persistent storage.
7. THE PolicyPilot_System SHALL expose a `GET /api/v1/wallet/folders/{folder_id}/documents` endpoint that returns all Wallet_Documents in the specified folder.
8. THE PolicyPilot_System SHALL expose a `POST /api/v1/wallet/folders/{folder_id}/documents` endpoint that accepts a multipart file upload and stores the document.
9. THE PolicyPilot_System SHALL expose a `DELETE /api/v1/wallet/documents/{document_id}` endpoint that deletes the specified Wallet_Document.
10. IF the `DELETE /api/v1/wallet/documents/{document_id}` request targets a document not owned by the requesting Authenticated_User, THEN THE PolicyPilot_System SHALL return HTTP 403.

---

## Feature 3: Document Upload During Chat + Smart Document Processing

---

### Requirement 3.1: File Attachment in Chat Input

**User Story:** As a Citizen, I want to attach a document directly in the chat window, so that the PolicyPilot_System can use my document to answer eligibility questions.

#### Acceptance Criteria

1. THE ChatInput component SHALL render a file attachment button adjacent to the text input field.
2. WHEN a Citizen selects a file via the attachment button, THE PolicyPilot_System SHALL display the filename and file size in a preview chip above the text input before submission.
3. WHEN a Citizen removes the attached file by clicking the chip dismiss button, THE PolicyPilot_System SHALL clear the attachment and restore the empty input state.
4. THE PolicyPilot_System SHALL accept attachment files with MIME types: `application/pdf`, `image/jpeg`, `image/png`, `image/webp` in the chat input.
5. IF the attached file exceeds 10 megabytes, THEN THE PolicyPilot_System SHALL display an inline validation error and prevent submission.
6. WHEN a Citizen submits a query with an attached file, THE PolicyPilot_System SHALL send the file as a multipart upload together with the query text, `conversation_id`, and `conversation_history` to the backend.

---

### Requirement 3.2: Document Text Extraction

**User Story:** As a Citizen, I want the system to read my uploaded document and extract its content automatically, so that I do not have to manually re-enter the information it contains.

#### Acceptance Criteria

1. WHEN a file with MIME type `application/pdf` is received by the backend, THE PDF_Reader SHALL extract all readable text from the document and return it as a UTF-8 string.
2. WHEN a file with MIME type `image/jpeg`, `image/png`, or `image/webp` is received by the backend, THE OCR_Processor SHALL perform optical character recognition and return the extracted text as a UTF-8 string.
3. WHEN extracted text is non-empty, THE PolicyPilot_System SHALL append the extracted text to the `user_profile` passed into the LangGraph_Workflow under the key `document_context`, so agents can reference its content.
4. IF the PDF_Reader encounters an encrypted or unreadable PDF, THEN THE PolicyPilot_System SHALL return a user-facing error message explaining the file could not be read, without crashing the workflow.
5. IF the OCR_Processor returns empty text for an image file, THEN THE PolicyPilot_System SHALL inform the Citizen that no readable text was found in the document and ask them to try a clearer image.
6. THE PDF_Reader and OCR_Processor SHALL complete extraction within 30 seconds per document; IF extraction exceeds this threshold, THEN THE PolicyPilot_System SHALL time out the extraction and continue the workflow without document context.
7. FOR ALL non-empty UTF-8 strings extracted from a document, parsing the text into the `document_context` field and then serialising `document_context` back to a string SHALL produce an equivalent string (round-trip property).

---

### Requirement 3.3: "For Whom?" Person Selection Flow

**User Story:** As a Citizen, I want the system to ask me which person a scheme query is for, so that the correct person's documents are used for eligibility checking.

#### Acceptance Criteria

1. WHEN an Authenticated_User submits an `eligibility_check` query and the Document_Wallet contains at least one Person_Folder, THE PolicyPilot_System SHALL respond with a "For whom?" prompt listing all Person_Folder names from the Authenticated_User's wallet before executing the eligibility workflow.
2. WHEN the Authenticated_User selects a Person_Folder name in response to the "For whom?" prompt, THE PolicyPilot_System SHALL proceed with the eligibility check using the documents in the selected Person_Folder.
3. WHEN the selected Person_Folder contains no Wallet_Documents, THE PolicyPilot_System SHALL ask the Citizen to upload the required documents before proceeding with the eligibility check.
4. WHEN the Citizen uploads documents in response to the upload request during a chat session, THE PolicyPilot_System SHALL store the uploaded file(s) in the selected Person_Folder in the Document_Wallet before executing the eligibility check.
5. WHEN an Anonymous_User submits an `eligibility_check` query with an attached document, THE PolicyPilot_System SHALL process the document for the current session only and SHALL NOT persist the document to any wallet.
6. WHEN an `eligibility_check` query is submitted by a user whose Document_Wallet contains no Person_Folders, THE PolicyPilot_System SHALL proceed directly to the eligibility workflow without the "For whom?" prompt.

---

### Requirement 3.4: Document-Augmented Eligibility Workflow

**User Story:** As a Citizen, I want the PolicyPilot_System to use the text extracted from my documents when checking my eligibility, so that I get a more accurate assessment without manually filling in every detail.

#### Acceptance Criteria

1. WHEN document text has been extracted and stored in `document_context`, THE Eligibility_Agent SHALL read the `document_context` field from the LangGraph_Workflow state and use its content to supplement the `user_profile` for eligibility evaluation.
2. WHEN the `document_context` field supplies a value for a profile attribute (e.g., age, income, state) that is absent from `user_profile`, THE Eligibility_Agent SHALL use the document-derived value for eligibility evaluation.
3. WHEN both `user_profile` and `document_context` supply a value for the same profile attribute, THE Eligibility_Agent SHALL prefer the `user_profile` value and ignore the `document_context` value for that attribute.
4. THE Final_Response_Agent SHALL NOT reveal the raw `document_context` string in the final citizen-facing response.

---

## Feature 4: Login Page (Open Email-Based Authentication)

---

### Requirement 4.1: Email-Based Registration and Login

**User Story:** As a Citizen, I want to log in with my email address without requiring an invitation, so that I can access the full features of PolicyPilot with a persistent identity.

#### Acceptance Criteria

1. THE PolicyPilot_System SHALL display a Login page as the initial entry point for all users who do not have an active session.
2. WHEN a Citizen submits a valid email address on the Login page, THE Auth_Service SHALL look up an existing User record by email or create a new User record if none exists, then issue a JWT_Token valid for 7 days.
3. WHEN a Citizen submits an email address that does not match the RFC 5322 format, THE Auth_Service SHALL reject the request and return a validation error without creating any database record.
4. WHEN the Auth_Service issues a JWT_Token, THE PolicyPilot_System SHALL store the JWT_Token in `localStorage` on the frontend and use it as a Bearer token in all subsequent API requests.
5. WHEN a JWT_Token is present in `localStorage` and is not expired, THE PolicyPilot_System SHALL skip the Login page and navigate directly to the main application.
6. WHEN a JWT_Token is present in `localStorage` but is expired, THE PolicyPilot_System SHALL remove the token from `localStorage` and redirect the Citizen to the Login page.
7. THE PolicyPilot_System SHALL expose a `POST /api/v1/auth/login` endpoint that accepts `{email: string}` and returns `{access_token: string, token_type: "bearer", user_id: string, email: string, name: string | null}`.
8. IF the `POST /api/v1/auth/login` request body is missing the `email` field, THEN THE Auth_Service SHALL return HTTP 422 with a validation error.

---

### Requirement 4.2: Authenticated Session Throughout the App

**User Story:** As an Authenticated_User, I want my identity to be used across all features of the app, so that my conversations, wallet, and profile are all linked to my account.

#### Acceptance Criteria

1. WHEN an Authenticated_User submits a query, THE PolicyPilot_System SHALL include the `user_id` from the JWT_Token in the query request payload so the backend links the conversation to the correct User record.
2. WHEN an Authenticated_User creates a new Conversation_Session, THE PolicyPilot_System SHALL associate the Conversation record in the database with the Authenticated_User's `user_id`.
3. WHEN an Authenticated_User accesses the chat history sidebar, THE PolicyPilot_System SHALL display only Conversation_Sessions associated with the Authenticated_User's `user_id`.
4. WHILE an Authenticated_User is logged in, THE PolicyPilot_System SHALL display the user's name (or email if name is null) in the navigation bar or sidebar header.
5. WHEN an Authenticated_User clicks "Log out", THE PolicyPilot_System SHALL remove the JWT_Token from `localStorage` and redirect the user to the Login page.
6. WHEN an API request is received with an invalid or expired JWT_Token, THE PolicyPilot_System SHALL return HTTP 401 for all protected endpoints.
7. THE PolicyPilot_System SHALL expose a `GET /api/v1/auth/me` endpoint that returns `{user_id: string, email: string, name: string | null}` for the Authenticated_User identified by the Bearer token.
8. IF the `GET /api/v1/auth/me` request is made without a Bearer token, THEN THE PolicyPilot_System SHALL return HTTP 401.

---

### Requirement 4.3: Anonymous User Fallback

**User Story:** As an Anonymous_User, I want to be able to use the basic chat features without logging in, so that I can explore the app before committing to creating an account.

#### Acceptance Criteria

1. WHERE the PolicyPilot_System supports a "guest mode", THE PolicyPilot_System SHALL allow an Anonymous_User to submit queries and receive responses without a JWT_Token.
2. WHILE an Anonymous_User is using the chat, THE PolicyPilot_System SHALL store conversation history in the browser's `localStorage` only and SHALL NOT persist any conversation data to the database.
3. WHEN an Anonymous_User attempts to access the User_Dashboard or Document_Wallet, THE PolicyPilot_System SHALL redirect them to the Login page.
4. WHEN an Anonymous_User logs in after using the app as a guest, THE PolicyPilot_System SHALL NOT automatically migrate the guest conversation history to the newly created account.
5. THE PolicyPilot_System SHALL display a persistent, non-blocking banner to Anonymous_Users explaining that login is optional but enables conversation history, document wallet, and personalised eligibility checks.

---

## Cross-Feature Acceptance Criteria

### Requirement 5.1: Database Schema Integrity

**User Story:** As a developer, I want all new database tables to be created via Alembic migrations, so that the schema is version-controlled and reproducible.

#### Acceptance Criteria

1. THE PolicyPilot_System SHALL introduce an Alembic migration for each new database table: `person_folders` and `wallet_documents`.
2. WHEN the Alembic migration for `person_folders` is applied, THE PolicyPilot_System SHALL create the table with columns: `id` (UUID, PK), `user_id` (FK → `users.id`, CASCADE DELETE), `name` (VARCHAR 150, NOT NULL), `created_at` (TIMESTAMPTZ), `updated_at` (TIMESTAMPTZ).
3. WHEN the Alembic migration for `wallet_documents` is applied, THE PolicyPilot_System SHALL create the table with columns: `id` (UUID, PK), `folder_id` (FK → `person_folders.id`, CASCADE DELETE), `filename` (VARCHAR 255, NOT NULL), `file_size_bytes` (INTEGER, NOT NULL), `mime_type` (VARCHAR 100, NOT NULL), `storage_path` (TEXT, NOT NULL), `created_at` (TIMESTAMPTZ).
4. FOR ALL Alembic migrations introduced by this feature set, applying the `upgrade` migration followed by the `downgrade` migration SHALL return the database schema to its prior state (round-trip property).

### Requirement 5.2: API Security

**User Story:** As a developer, I want all wallet and dashboard endpoints to be protected by authentication, so that users can only access their own data.

#### Acceptance Criteria

1. THE PolicyPilot_System SHALL require a valid JWT_Token for all `/api/v1/wallet/*` endpoints.
2. THE PolicyPilot_System SHALL require a valid JWT_Token for all `/api/v1/auth/me` endpoint requests.
3. IF a wallet API request is made by an Authenticated_User attempting to access a resource owned by a different user, THEN THE PolicyPilot_System SHALL return HTTP 403.
4. THE `/api/v1/query` endpoint SHALL remain accessible to Anonymous_Users without a JWT_Token so that the guest mode described in Requirement 4.3 is preserved.
