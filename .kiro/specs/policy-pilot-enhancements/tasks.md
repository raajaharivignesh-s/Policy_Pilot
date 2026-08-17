# Implementation Plan: PolicyPilot Enhancements

## Overview

This implementation plan breaks down the four PolicyPilot enhancements into sequential phases. Each phase is designed to be completed and approved before moving to the next phase, as requested by the user. The plan follows a backend-first approach within each phase, includes comprehensive testing, and organizes tasks for efficient parallel execution where possible.

## Tasks

### Phase 1: Persistent Conversation Memory

**Objective:** Ensure all LangGraph agents properly consume and use conversation history for contextual follow-up answers.

- [ ] 1. Backend: Conversation History Service
  - [-] 1.1 Create `ConversationHistoryService` class in `backend/app/services/conversation_history_service.py`
    - Implement `get_history(conversation_id)` method
    - Implement `append_to_history(conversation_id, role, content)` method
    - Implement `truncate_history(conversation_id, max_entries=20)` method
    - Implement `initialize_history(conversation_id)` method
    - _Requirements: 1.2.1, 1.2.2, 1.2.4_
  - [ ]\* 1.2 Write unit tests for `ConversationHistoryService`
    - Test history initialization and retrieval
    - Test history truncation at 20 entries
    - Test concurrent access scenarios
    - _Requirements: 1.2.4_

  - [~] 1.3 Implement history entry validation function
    - Create validation function that checks for required `role` and `content` fields
    - Validate `role` is either "user" or "assistant"
    - Return `True` for valid entries, `False` for invalid
    - _Requirements: 1.1.4, 1.1.5_

  - [ ]\* 1.4 Write property test for history entry filtering
    - **Property 4: History Entry Filtering**
    - **Validates: Requirements 1.1.4, 1.1.5**
    - Test that validation function returns only entries with valid role and non-empty content

- [ ] 2. Backend: Query API Enhancement
  - [~] 2.1 Update query API endpoint in `backend/app/api/v1/query.py`
    - Integrate server-side history with frontend-provided history
    - Implement logic: if frontend provides history, use it; otherwise use server-side
    - Truncate history to 20 most recent entries before processing
    - Append new messages to server-side history after workflow execution
    - _Requirements: 1.2.1, 1.2.2, 1.2.3, 1.2.4_

  - [ ]\* 2.2 Write integration tests for query API with history
    - Test first query creates new conversation_id
    - Test follow-up query uses accumulated history
    - Test frontend-provided history overrides server history
    - Test history truncation at 20 entries
    - _Requirements: 1.2.1, 1.2.2, 1.2.3_

- [ ] 3. Frontend: History Construction Enhancement
  - [~] 3.1 Update `buildConversationHistory` function in `frontend/src/hooks/useQuery.js`
    - Ensure only messages with `final_response` field are included for assistant messages
    - Cap history to 20 most recent entries before sending to backend
    - Handle empty message list scenario
    - _Requirements: 1.3.1, 1.3.2, 1.3.3, 1.3.4_

  - [ ]\* 3.2 Write unit tests for frontend history construction
    - Test history building with mixed valid/invalid messages
    - Test capping to 20 entries
    - Test empty conversation scenario
    - _Requirements: 1.3.1, 1.3.4_

- [~] 4. Phase 1 Completion Checkpoint
  - Ensure all tests pass for Phase 1 implementation
  - Verify conversation history flows correctly end-to-end
  - Confirm backward compatibility with existing functionality
  - _Requirements: All Phase 1 requirements_

---

### Phase 2: User Dashboard + Document Wallet

**Objective:** Create user dashboard with folder-based document management system.

- [ ] 5. Backend: Database Models and Migrations
  - [~] 5.1 Create `PersonFolder` model in `backend/app/models/person_folder.py`
    - Define fields: `id` (UUID), `user_id` (FK to users), `name` (string), `created_at`, `updated_at`
    - Add relationship to `User` model
    - Add relationship to `WalletDocument` model with cascade delete
    - _Requirements: 2.2.2, 5.1.2_

  - [~] 5.2 Create `WalletDocument` model in `backend/app/models/wallet_document.py`
    - Define fields: `id` (UUID), `folder_id` (FK to person_folders), `filename`, `file_size_bytes`, `mime_type`, `storage_path`, `created_at`
    - Add relationship to `PersonFolder` model
    - _Requirements: 2.3.1, 5.1.3_

  - [~] 5.3 Create Alembic migration for wallet tables
    - Create migration file with `upgrade()` and `downgrade()` functions
    - Add foreign key constraints with CASCADE DELETE
    - Create indexes on `user_id` and `folder_id` columns
    - _Requirements: 5.1.1, 5.1.2, 5.1.3_

  - [ ]\* 5.4 Write property test for Alembic migration round-trip
    - **Property 3: Alembic Migration Round-Trip**
    - **Validates: Requirements 5.1.4**
    - Test that applying upgrade then downgrade returns schema to original state

  - [~] 5.5 Update `User` model relationship
    - Add `folders` relationship to `User` model in `backend/app/models/user.py`
    - Configure cascade delete behavior
    - _Requirements: 2.2.1_

- [ ] 6. Backend: File Storage Service
  - [~] 6.1 Create `FileStorageService` in `backend/app/services/file_storage_service.py`
    - Implement file validation for MIME types and size limits
    - Implement `store_file()` method with path generation logic
    - Implement `delete_file()` method
    - Configure storage directory structure: `storage/wallet/{user_id}/{folder_id}/`
    - _Requirements: 2.3.1, 2.3.2, 2.3.3, 2.3.4_

  - [ ]\* 6.2 Write unit tests for `FileStorageService`
    - Test file validation for allowed MIME types
    - Test file size limit enforcement
    - Test storage and deletion operations
    - _Requirements: 2.3.2, 2.3.3, 2.3.4_

- [ ] 7. Backend: Wallet API Endpoints
  - [~] 7.1 Create wallet API router in `backend/app/api/v1/wallet.py`
    - Implement folder endpoints: `GET /folders`, `POST /folders`, `DELETE /folders/{folder_id}`
    - Implement document endpoints: `GET /folders/{folder_id}/documents`, `POST /folders/{folder_id}/documents`, `DELETE /documents/{document_id}`
    - Add request/response schemas for validation
    - _Requirements: 2.2.6, 2.2.7, 2.2.8, 2.3.7, 2.3.8, 2.3.9_

  - [~] 7.2 Implement authorization checks in wallet API
    - Add ownership verification for all wallet endpoints
    - Return HTTP 403 for unauthorized access attempts
    - Validate folder name is not empty/whitespace-only
    - _Requirements: 2.2.9, 2.3.10, 5.2.3_

  - [ ]\* 7.3 Write integration tests for wallet API
    - Test full CRUD flow for folders and documents
    - Test authorization failures (403 responses)
    - Test validation errors (empty folder names, invalid file types)
    - Test file size limit enforcement (413 responses)
    - _Requirements: 2.2.3, 2.2.4, 2.2.5, 2.3.3, 2.3.4, 2.3.6_

- [ ] 8. Frontend: User Dashboard Components
  - [~] 8.1 Create `UserDashboard` page component in `frontend/src/pages/UserDashboard.jsx`
    - Implement authentication check and redirect to login for anonymous users
    - Display user's name and email from backend
    - Integrate `ProfileSection` and `WalletSection` components
    - _Requirements: 2.1.1, 2.1.2, 2.1.3, 2.1.4_

  - [~] 8.2 Create `WalletSection` component in `frontend/src/components/WalletSection.jsx`
    - Display list of person folders with creation date
    - Implement folder creation form with validation
    - Implement folder deletion with confirmation
    - Integrate `DocumentList` component for selected folder
    - _Requirements: 2.1.5, 2.2.1, 2.2.5_

  - [~] 8.3 Create `DocumentList` component in `frontend/src/components/DocumentList.jsx`
    - Display documents in selected folder with filename, size, and upload date
    - Implement document upload button with file selection
    - Implement document deletion with confirmation
    - Show file size in human-readable format
    - _Requirements: 2.3.5, 2.3.6_

  - [~] 8.4 Create `useWallet` hook in `frontend/src/hooks/useWallet.js`
    - Implement API calls for folder CRUD operations
    - Implement API calls for document CRUD operations
    - Handle loading states and errors
    - Manage local state for folders and documents
    - _Requirements: 2.2.6, 2.2.7, 2.2.8, 2.3.7, 2.3.8, 2.3.9_

  - [ ]\* 8.5 Write unit tests for frontend wallet components
    - Test folder creation and deletion
    - Test document upload and display
    - Test error handling for API failures
    - Test validation for empty folder names
    - _Requirements: 2.2.3, 2.2.4_

- [~] 9. Phase 2 Completion Checkpoint
  - Ensure all tests pass for Phase 2 implementation
  - Verify user dashboard loads correctly for authenticated users
  - Test full document wallet functionality end-to-end
  - Confirm anonymous users are redirected to login when accessing dashboard
  - _Requirements: All Phase 2 requirements_

---

### Phase 3: Document Upload During Chat + Smart Processing

**Objective:** Allow users to upload documents during chat conversations, extract text content, and use it for eligibility checks.

- [ ] 10. Backend: Document Processing Services
  - [~] 10.1 Create `PDFReader` service in `backend/app/services/pdf_reader.py`
    - Implement text extraction from PDF files using PyMuPDF (fitz)
    - Handle encrypted/unreadable PDF files gracefully
    - Implement timeout mechanism (30 seconds)
    - _Requirements: 3.2.1, 3.2.4, 3.2.6_

  - [~] 10.2 Create `OCRProcessor` service in `backend/app/services/ocr_processor.py`
    - Implement OCR text extraction from images (JPEG, PNG, WebP)
    - Use pytesseract for OCR processing
    - Handle empty OCR results gracefully
    - Implement timeout mechanism (30 seconds)
    - _Requirements: 3.2.2, 3.2.5, 3.2.6_

  - [~] 10.3 Create `DocumentProcessor` service in `backend/app/services/document_processor.py`
    - Implement `extract_text()` method that routes to appropriate service
    - Handle MIME type detection and routing
    - Manage extraction timeouts and error handling
    - Return structured `DocumentExtractionResult`
    - _Requirements: 3.2.1, 3.2.2, 3.2.3, 3.2.4, 3.2.5, 3.2.6_

  - [ ]\* 10.4 Write unit tests for document processing services
    - Test PDF text extraction with sample PDFs
    - Test OCR extraction with sample images
    - Test timeout handling for large files
    - Test error handling for unreadable files
    - _Requirements: 3.2.4, 3.2.5, 3.2.6_

- [ ] 11. Backend: Query API Enhancement for Document Upload
  - [~] 11.1 Update query API endpoint for multipart upload in `backend/app/api/v1/query.py`
    - Accept `multipart/form-data` with optional `document` file field
    - Accept optional `folder_id` for authenticated users
    - Extract text from uploaded document using `DocumentProcessor`
    - Add extracted text to workflow state as `document_context`
    - Store document in wallet for authenticated users with `folder_id`
    - _Requirements: 3.1.6, 3.2.3, 3.3.4_

  - [~] 11.2 Update `PolicyPilotState` in `backend/app/graph/state.py`
    - Add `document_context: str` field to state
    - Add `selected_person_folder_id: str | None` field to state
    - Ensure backward compatibility with existing state structure
    - _Requirements: 3.2.3, 3.3.2_

  - [~] 11.3 Update `EligibilityAgent` to use document context
    - Modify agent to read `document_context` from state
    - Implement logic to merge document-derived info into user_profile
    - Document values only fill gaps in user_profile (don't override)
    - _Requirements: 3.4.1, 3.4.2, 3.4.3_

  - [~] 11.4 Create `PersonSelectionService` in `backend/app/services/person_selection_service.py`
    - Implement logic to determine when to prompt for person selection
    - Check if user has folders and query is `eligibility_check`
    - Return list of person folders for selection prompt
    - _Requirements: 3.3.1, 3.3.2, 3.3.6_

  - [ ]\* 11.5 Write property test for document text round-trip
    - **Property 1: Document Text Round-Trip**
    - **Validates: Requirements 3.2.7**
    - Test that parsing text into document_context and serializing back produces equivalent string

  - [ ]\* 11.6 Write integration tests for document upload flow
    - Test query with PDF document attachment
    - Test query with image document attachment
    - Test person selection flow for authenticated users
    - Test anonymous user document upload (no persistence)
    - _Requirements: 3.1.4, 3.1.5, 3.2.1, 3.2.2, 3.3.5_

- [ ] 12. Frontend: Chat Input Enhancement
  - [~] 12.1 Update `ChatInput` component in `frontend/src/components/ChatInput.jsx`
    - Add file attachment button with icon
    - Implement file selection with validation (MIME types, size limit)
    - Display file preview chip with filename and size
    - Implement file removal functionality
    - _Requirements: 3.1.1, 3.1.2, 3.1.3, 3.1.4, 3.1.5_

  - [~] 12.2 Create `FilePreviewChip` component in `frontend/src/components/FilePreviewChip.jsx`
    - Display filename and formatted file size
    - Show file type icon based on MIME type
    - Implement dismiss button to remove attached file
    - _Requirements: 3.1.2, 3.1.3_

  - [~] 12.3 Create `PersonSelectionModal` component in `frontend/src/components/PersonSelectionModal.jsx`
    - Display "For whom?" prompt with list of person folders
    - Implement folder selection buttons
    - Implement skip option for anonymous users or users without folders
    - _Requirements: 3.3.1, 3.3.2, 3.3.6_

  - [~] 12.4 Update `useQuery` hook for document handling
    - Modify `runQuery()` to handle file attachments
    - Implement form data construction with multipart support
    - Integrate person selection modal logic
    - Handle `folder_id` parameter for authenticated users
    - _Requirements: 3.1.6, 3.3.1, 3.3.2, 3.3.3_

  - [ ]\* 12.5 Write unit tests for frontend document upload components
    - Test file validation logic in ChatInput
    - Test file preview chip display and removal
    - Test person selection modal display logic
    - Test form data construction for multipart upload
    - _Requirements: 3.1.4, 3.1.5, 3.3.1_

- [~] 13. Phase 3 Completion Checkpoint
  - Ensure all tests pass for Phase 3 implementation
  - Verify document upload works in chat interface
  - Test text extraction from PDF and image files
  - Test person selection flow for eligibility checks
  - Verify document context is used in eligibility evaluations
  - _Requirements: All Phase 3 requirements_

---

### Phase 4: Login Page (Email Authentication)

**Objective:** Add email-based login flow so every user has a persistent identity used across the entire app.

- [ ] 14. Backend: Authentication Service
  - [~] 14.1 Create `AuthService` class in `backend/app/services/auth_service.py`
    - Implement RFC 5322 email validation
    - Implement `find_or_create_user(email)` method
    - Implement JWT token generation with 7-day expiration
    - Implement JWT token validation and decoding
    - _Requirements: 4.1.1, 4.1.2, 4.1.3, 4.1.4_

  - [~] 14.2 Create auth API endpoints in `backend/app/api/v1/auth.py`
    - Implement `POST /auth/login` endpoint for email-based login
    - Implement `GET /auth/me` endpoint for current user info
    - Define request/response schemas with validation
    - _Requirements: 4.1.7, 4.1.8, 4.2.7, 4.2.8_

  - [~] 14.3 Create authentication dependencies in `backend/app/api/deps.py`
    - Implement `get_current_user()` dependency for protected endpoints
    - Implement `get_optional_user()` dependency for optional auth
    - Handle HTTP 401 responses for invalid/expired tokens
    - _Requirements: 4.2.6, 5.2.1, 5.2.2_

  - [ ]\* 14.4 Write property test for JWT token round-trip
    - **Property 2: JWT Token Round-Trip**
    - **Validates: Requirements 4.1.2, 4.1.4**
    - Test that creating JWT from user and validating returns same user identity

  - [ ]\* 14.5 Write unit tests for authentication service
    - Test email validation with RFC 5322 format
    - Test JWT token creation and validation
    - Test token expiration handling
    - Test user creation on first login
    - _Requirements: 4.1.3, 4.1.4, 4.2.6_

- [ ] 15. Backend: Query API Authentication Integration
  - [~] 15.1 Update query API to support optional authentication
    - Use `get_optional_user()` dependency for query endpoint
    - Include `user_id` in query payload for authenticated users
    - Associate conversations with user_id for authenticated users
    - Maintain guest mode support for anonymous users
    - _Requirements: 4.2.1, 4.2.2, 4.3.1, 4.3.2, 5.2.4_

  - [~] 15.2 Update wallet API to require authentication
    - Use `get_current_user()` dependency for all wallet endpoints
    - Return HTTP 401 for unauthenticated access to wallet
    - _Requirements: 5.2.1, 5.2.3_

  - [ ]\* 15.3 Write integration tests for authentication flow
    - Test login with new email creates user
    - Test login with existing email returns user
    - Test protected endpoints return 401 without token
    - Test guest mode continues to work for query endpoint
    - _Requirements: 4.1.2, 4.1.3, 4.2.6, 4.3.1_

- [ ] 16. Frontend: Authentication Components
  - [~] 16.1 Create `LoginPage` component in `frontend/src/pages/LoginPage.jsx`
    - Implement email input form with validation
    - Handle login API call and token storage
    - Redirect to main app on successful login
    - Show guest mode option to continue without login
    - _Requirements: 4.1.1, 4.1.4, 4.1.5, 4.3.5_

  - [~] 16.2 Create `AuthContext` provider in `frontend/src/contexts/AuthContext.jsx`
    - Manage authentication state (user, loading, isAuthenticated)
    - Implement `login(email)`, `logout()`, and `checkAuth()` methods
    - Store JWT token in localStorage
    - Handle token expiration and auto-logout
    - _Requirements: 4.1.4, 4.1.5, 4.1.6, 4.2.5_

  - [~] 16.3 Create `ProtectedRoute` component in `frontend/src/components/ProtectedRoute.jsx`
    - Implement route protection for authenticated-only pages
    - Redirect to login page for unauthenticated users
    - Show loading spinner during auth check
    - _Requirements: 2.1.4, 4.2.3_

  - [~] 16.4 Create `AnonymousBanner` component in `frontend/src/components/AnonymousBanner.jsx`
    - Display non-blocking banner for anonymous users
    - Explain benefits of login (conversation history, document wallet)
    - Provide link to login page
    - _Requirements: 4.3.5_

  - [~] 16.5 Update API client with auth interceptors
    - Add JWT token to all requests from localStorage
    - Handle 401 responses by clearing token and redirecting to login
    - _Requirements: 4.1.4, 4.2.6_

  - [~] 16.6 Update app routing in `frontend/src/App.jsx`
    - Add routes for `/login` and `/dashboard`
    - Protect `/dashboard` route with `ProtectedRoute`
    - Set login page as entry point for users without active session
    - _Requirements: 4.1.1, 4.1.5, 2.1.1_

  - [ ]\* 16.7 Write unit tests for frontend authentication components
    - Test login form validation and submission
    - Test auth context state management
    - Test protected route redirection logic
    - Test API client token handling
    - _Requirements: 4.1.3, 4.1.5, 4.1.6_

- [~] 17. Phase 4 Completion Checkpoint
  - Ensure all tests pass for Phase 4 implementation
  - Verify login flow works end-to-end
  - Test guest mode continues to function
  - Verify authenticated users can access dashboard and wallet
  - Confirm anonymous users are redirected when accessing protected resources
  - _Requirements: All Phase 4 requirements_

- [~] 18. Final Integration Checkpoint
  - Run all tests across all four phases
  - Verify backward compatibility with existing functionality
  - Test complete user journey: login → dashboard → document upload → chat with documents
  - Ensure error handling works consistently across all components
  - Confirm all requirements from all phases are satisfied
  - _Requirements: All requirements_

## Notes

- **Sequential Approval**: Each phase (Phase 1-4) should be completed and approved by the user before moving to the next phase, as requested.
- **Optional Tests**: Tasks marked with `*` are optional test tasks that can be skipped for faster MVP development.
- **Backend-First**: Within each phase, backend tasks should be completed before corresponding frontend tasks.
- **Property Tests**: Four property-based tests are included based on the design's correctness properties section.
- **Dependencies**: Tasks within the same phase can often run in parallel, but cross-phase dependencies must be respected (Phase 2 depends on Phase 1 completion, etc.).
- **Testing Strategy**: Each implementation task includes corresponding testing tasks to ensure quality and correctness.
- **Error Handling**: Comprehensive error handling is built into each component as specified in the design document.
- **Backward Compatibility**: All changes maintain compatibility with existing anonymous user functionality.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.3", "5.1", "5.2", "5.3", "5.5"] },
    {
      "id": 1,
      "tasks": [
        "1.2",
        "1.4",
        "2.1",
        "5.4",
        "6.1",
        "10.1",
        "10.2",
        "10.3",
        "14.1"
      ]
    },
    {
      "id": 2,
      "tasks": [
        "2.2",
        "3.1",
        "6.2",
        "7.1",
        "7.2",
        "10.4",
        "11.1",
        "11.2",
        "11.3",
        "11.4",
        "14.2",
        "14.3"
      ]
    },
    {
      "id": 3,
      "tasks": [
        "3.2",
        "7.3",
        "8.1",
        "8.2",
        "8.3",
        "8.4",
        "11.5",
        "11.6",
        "14.4",
        "14.5",
        "15.1",
        "15.2"
      ]
    },
    {
      "id": 4,
      "tasks": [
        "8.5",
        "12.1",
        "12.2",
        "12.3",
        "12.4",
        "15.3",
        "16.1",
        "16.2",
        "16.3",
        "16.4",
        "16.5",
        "16.6"
      ]
    },
    { "id": 5, "tasks": ["12.5", "16.7"] }
  ]
}
```

### Dependency Graph Notes:

- **Wave 0**: Core foundation tasks (services, models, migrations)
- **Wave 1**: Supporting services and basic implementations
- **Wave 2**: API endpoints and integration logic
- **Wave 3**: Frontend components and property tests
- **Wave 4**: Frontend integration and authentication setup
- **Wave 5**: Final test implementations

The graph ensures that:

1. Backend services are created before APIs that use them
2. Database models and migrations are ready before services that depend on them
3. Frontend components are built after corresponding backend APIs
4. Tests are written after the code they test
5. Property tests are placed close to the implementations they validate
