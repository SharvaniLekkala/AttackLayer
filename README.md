# AttackLayer - Semantic Security Firewall for LLM Agent Memory

## Project Overview

AttackLayer is an advanced security framework designed to protect Long-Term Memory systems in Large Language Model (LLM) agents from sophisticated attacks. It serves as a semantic security firewall that comprehensively evaluates, validates, and monitors all memory interactions within an AI agent system. The system combines machine learning-based threat detection, semantic analysis, policy enforcement, and audit logging to create a multi-layered defense mechanism against various attack vectors including prompt injection, memory poisoning, credential theft, personally identifiable information (PII) exposure, and tool manipulation attacks.

The architecture is built with a full-stack approach combining a FastAPI backend with comprehensive security modules and a React-based frontend dashboard that provides real-time visualization of memory security events, threats, and system health.

## Architecture Overview

The system follows a layered architecture pattern with clear separation of concerns:

Layer 1 - Frontend Presentation Layer
Layer 2 - API Layer (FastAPI)
Layer 3 - Security Processing Layer
Layer 4 - Memory Management Layer
Layer 5 - Persistence Layer (SQLite Database + Vector Database)

Data flow in the system:
User Input -> Frontend -> Chat API -> Security Gateway -> Memory Management -> Database Storage
Response -> LLM Service -> Response Validation -> Security Audit -> Frontend

## Directory Structure and File Explanations

### Root Level Files

README.md - Original project documentation and quick start guide
.gitignore - Git configuration to exclude cache, environment files, and database files
DETAILED_README.md - This comprehensive documentation file

### Backend Directory Structure

backend/
  app/
    main.py - FastAPI application entry point and routing configuration
    __init__.py - Backend package initialization
    requirements.txt - Python dependencies and version specifications

backend/app/
 main.py
 __init__.py
 memory/
 security/
 llm/
 api/
 database/
 audit/
 memory_security/
 research/
 learning/
 evaluation/
 schemas/
 utils/
 attacklayer.db (SQLite database file)
 chroma_db/ (Vector database directory)

### Frontend Directory Structure

frontend/
 src/
    main.jsx - Entry point for React application
    App.jsx - Root React component with routing configuration
    App.css - Root application styles
    index.css - Global CSS styles
    components/ - Reusable React components
    pages/ - Page-level components
    api/ - API communication services
    services/ - Business logic services
    utils/ - Utility functions
    styles/ - CSS stylesheets for pages and components
    assets/ - Static assets (images, SVGs)
    public/ - Public static files
 index.html - HTML entry point
 package.json - Node.js dependencies and scripts
 package-lock.json - Locked dependency versions
 eslint.config.js - ESLint configuration for code quality
 vite.config.js - Vite build configuration
 .gitignore - Frontend-specific git ignore rules

## Detailed Component Analysis

### Backend Components

#### 1. Main Application Entry Point (backend/app/main.py)

What it does:
- Initializes the FastAPI application with title "AttackLayer"
- Configures CORS (Cross-Origin Resource Sharing) middleware to allow all origins
- Creates database tables using SQLAlchemy ORM
- Runs database migrations
- Registers all API routers

Why it's necessary:
- Serves as the server initialization point
- Enables cross-origin requests so the frontend can communicate with the backend
- Ensures database schema is created before the app starts
- Routes incoming requests to appropriate handlers

Dependencies:
- FastAPI: Web framework for building APIs
- SQLAlchemy: ORM for database operations
- All API routers from api/ directory

#### 2. Memory Management System (backend/app/memory/)

Location: backend/app/memory/

Files and their purposes:

a) vault.py - Core Memory Vault Implementation
What it does:
- Manages memory creation through the create_memory() function
- Integrates security evaluation at memory entry point
- Handles memory normalization and worthiness checking
- Manages memory quarantine for suspicious memories
- Logs events for compliance and auditing

Why it's necessary:
- Central point for all memory write operations
- Ensures security policies are evaluated before memory storage
- Prevents unworthy or malicious memories from being stored
- Provides audit trail of all memory decisions

Key process:
1. Input arrives at create_memory()
2. Security evaluation runs through evaluate_security()
3. If BLOCK decision: memory is rejected with reason
4. If ALLOW or ALLOW_WITH_WARNING: memory continues
5. Memory is normalized and worthiness checked
6. If worthy: stored in database and vector store
7. If quarantined: sent for manual review
8. Events are logged for audit trail

b) embedding_service.py - Embedding Generation
What it does:
- Generates semantic embeddings using the Ollama service
- Uses nomic-embed-text model for text vectorization
- Converts text into numerical vectors for semantic comparison

Why it's necessary:
- Enables semantic search and similarity detection
- Allows the system to understand meaning, not just keywords
- Required for memory retrieval and threat detection
- Enables duplicate detection and conflict analysis

Model used: nomic-embed-text (lightweight, efficient)

c) vector_storage.py - ChromaDB Vector Store Management
What it does:
- Manages persistent vector database using ChromaDB
- Stores embeddings and associated memories
- Provides semantic search capabilities
- Handles memory deletion from vector store

Why it's necessary:
- Enables fast semantic searches for memory retrieval
- Maintains embeddings separately from relational database
- Supports similarity queries for context building

Key functions:
- add_memory_embedding(): Stores embedding in vector DB
- remove_memory_embedding(): Deletes embedding from vector DB
- semantic_search(): Searches for similar memories (top k results)
- reset_memory_collection(): Clears all vector data (used in admin reset)

d) retrieval.py - Memory Retrieval System
What it does:
- Retrieves relevant memories based on user queries
- Performs semantic search using embeddings
- Filters memories by category and user
- Returns ranked list of relevant memories for context

Why it's necessary:
- Enables the LLM to access relevant past context
- Reduces hallucination by providing factual memory references
- Allows personalized responses based on user history

e) memory_normalizer.py - Memory Standardization
What it does:
- Normalizes memory text to standard format
- Removes redundancy and improves clarity
- Standardizes factual statements

Why it's necessary:
- Prevents storing duplicate memories in different formats
- Improves memory quality and retrieval accuracy
- Enables better conflict detection

f) versioning.py - Memory Version Control
What it does:
- Tracks memory versions and revisions
- Maintains parent-child relationships for updated memories
- Enables memory history tracking

Why it's necessary:
- Supports memory updates while preserving history
- Enables rollback to previous memory states
- Provides accountability for memory changes

#### 3. Security Framework (backend/app/security/)

This is the most critical component with multiple specialized modules.

a) security_gateway.py - Central Security Orchestrator
What it does:
- Acts as the main entry point for all security evaluations
- Orchestrates multiple security classifiers
- Makes final ALLOW/BLOCK/ALLOW_WITH_WARNING decisions
- Builds comprehensive security explanations

Function: evaluate_security(text, db=None, user_id=None)

Process flow:
1. Classifies user intent (what operation they're attempting)
2. Runs security classification (detects attacks)
3. Detects sensitive data (PII, credentials)
4. Classifies memory semantically
5. Determines final decision based on results
6. Builds explanation for traceability

Why it's necessary:
- Single point of control for security decisions
- Ensures consistent security policy application
- Provides traceability and explanations for all decisions

b) threat_detector.py - Attack Pattern Recognition
What it does:
- Contains threat examples for known attack types
- Uses semantic similarity to detect variations of attacks
- Identifies patterns like prompt injection, role override, credential theft

Threat types detected:
- PROMPT_INJECTION: Attempts to override system instructions
- MEMORY_POISONING: Attempts to store false or malicious facts
- ROLE_OVERRIDE: Attempts to change system role/permissions
- RETRIEVAL_ABUSE: Attempts to access unauthorized memories
- CREDENTIAL_STORAGE: Attempts to store passwords/API keys
- PII_STORAGE: Attempts to store personally identifiable information

Why it's necessary:
- Pattern-based detection complements behavioral analysis
- Identifies known attack variations through semantic similarity
- Provides specific threat classification for audit and response

c) sensitive_detector.py - PII and Sensitive Data Detection
What it does:
- Identifies personally identifiable information (SSN, credit cards, phone numbers)
- Detects credential-like patterns (passwords, API keys, tokens)
- Blocks storage of sensitive information

Why it's necessary:
- Protects user privacy
- Prevents credential theft through memory manipulation
- Complies with data protection regulations

d) intent_classifier.py - User Intent Classification
What it does:
- Determines what the user is trying to do (operation type)
- Classifies intent categories (chat, memory store, settings, etc.)
- Calculates confidence scores for classifications

Why it's necessary:
- Different operations have different security requirements
- Enables context-aware security policy application
- Helps detect abusive behavior patterns

e) semantic_classifier.py - Memory Category Classification
What it does:
- Classifies stored memories into semantic categories
- Examples: PERSONAL, PREFERENCES, FACTS, INSTRUCTIONS
- Uses embedding-based similarity to categories

Why it's necessary:
- Enables category-specific security policies
- Allows retrieval filtering by memory type
- Supports different trust levels for different categories

f) semantic_engine.py - Embedding Utilities
What it does:
- Provides helper functions for embedding operations
- Calculates cosine similarity between embeddings
- Computes mean embeddings for groups of texts

Why it's necessary:
- Core utilities for semantic similarity calculations
- Used by threat detection and memory retrieval
- Enables efficient vector operations

g) memory_conflict_engine.py - Conflict Detection
What it does:
- Detects contradictions between new and existing memories
- Calculates conflict scores
- Flags memories that contradict user's known facts

Why it's necessary:
- Prevents memory poisoning through contradictory facts
- Alerts user when memories conflict
- Enables learning from corrections

h) trust_engine.py - Memory Trust Calculation
What it does:
- Calculates trust scores for memories
- Considers source, verification count, verification_count
- Updates trust based on user interactions

Why it's necessary:
- Enables ranking of memories by reliability
- Supports weighted memory usage
- Prevents over-reliance on untrusted memories

i) memory_verification.py - Fact Verification
What it does:
- Verifies stored memories against known facts
- Tracks verification attempts
- Updates verification counts

Why it's necessary:
- Ensures memory accuracy
- Detects gradually poisoned memories
- Supports continuous improvement

j) memory_poison_detector.py - Poisoning Detection
What it does:
- Detects characteristics of poisoned memories
- Identifies gradualized poisoning attempts
- Calculates poison probability scores

Why it's necessary:
- Detects sophisticated memory poisoning attacks
- Flags gradually corrupted memories
- Prevents long-term system degradation

k) policy_engine.py - Policy Evaluation
What it does:
- Evaluates security policies against user input
- Applies configurable rules
- Supports policy-based filtering

Why it's necessary:
- Enables flexible security policy configuration
- Allows administrators to define custom rules
- Supports different security levels for different users

l) response_validator.py - Output Security Validation
What it does:
- Validates LLM responses before sending to user
- Checks for policy violations in generated text
- Detects if model violates memory constraints

Why it's necessary:
- Prevents model from leaking memories inappropriately
- Ensures responses comply with security policies
- Catches model attempts to bypass memory restrictions

m) request_analyzer.py - Request Analysis
What it does:
- Analyzes incoming requests for anomalies
- Detects attack patterns in request stream
- Identifies suspicious user behavior

Why it's necessary:
- Provides behavioral analysis capabilities
- Detects patterns indicating compromise
- Enables rate limiting and abuse prevention

n) instruction_detector.py - Instruction Injection Detection
What it does:
- Detects attempts to inject new instructions
- Identifies role-playing and jailbreak attempts
- Flags instruction-like content

Why it's necessary:
- Prevents model behavior modification
- Detects attempts to override system instructions
- Protects system integrity

o) self_reflection.py - System Reflection
What it does:
- Generates reflection logs on system decisions
- Records reasoning for security decisions
- Supports debugging and transparency

Why it's necessary:
- Provides explainability for security decisions
- Enables debugging of false positives/negatives
- Supports model improvement

p) context_builder.py - Secure Context Construction
What it does:
- Builds LLM context from retrieved memories
- Filters memories based on security policies
- Constructs appropriate context for safe responses

Why it's necessary:
- Ensures LLM only receives appropriate memories
- Prevents leaking sensitive memories in responses
- Supports context-aware secure responses

q) explainability.py - Explanation Generation
What it does:
- Generates human-readable explanations for decisions
- Records reasoning chain
- Supports audit and transparency requirements

Why it's necessary:
- Provides transparency to users and administrators
- Enables debugging of security decisions
- Supports compliance and accountability

#### 4. LLM Integration (backend/app/llm/)

a) service.py - LLM Response Generation
What it does:
- Calls LLM service to generate responses
- Handles LLM API communication
- Manages model configuration

Why it's necessary:
- Generates intelligent responses to user queries
- Integrates with external LLM services
- Handles model-specific configurations

b) orchestrator.py - Request/Response Orchestration
What it does:
- Coordinates entire request-response flow
- Retrieves context from memory
- Validates responses before returning
- Handles memory storage for user statements

Process flow:
1. Receives user message and user_id
2. Determines if message requests memory storage
3. Retrieves relevant memories using semantic search
4. Builds secure context from retrieved memories
5. Calls LLM service to generate response
6. Validates response against policies
7. Processes memory storage if requested
8. Logs security events
9. Returns response with metadata

Why it's necessary:
- Central coordinator for all request processing
- Ensures consistent security evaluation
- Manages complex multi-step operations

#### 5. API Layer (backend/app/api/)

The API layer provides REST endpoints for all system functionality.

a) main.py - FastAPI initialization and endpoint registration
b) chat.py - Chat messaging endpoints
   Endpoint: POST /chat/ with user_id and message
   Purpose: Main user interaction endpoint

c) memory.py - Memory management endpoints
   - GET /memory/: Retrieve all memories
   - POST /memory/: Create new memory
   - DELETE /memory/{id}: Delete memory
   - GET /memory/search: Search memories

d) security.py - Security evaluation endpoints
   - POST /security/evaluate: Evaluate text for threats
   - GET /security/status: Get security system status

e) threat.py - Threat analysis endpoints
   - GET /threats/: Get detected threats
   - POST /threats/analyze: Analyze for threats

f) audit.py - Audit log endpoints
   - GET /audit/events: Retrieve audit events
   - GET /audit/summary: Get audit summary
   - POST /audit/export: Export audit logs

g) classifier.py - Classification endpoints
   - POST /classify/intent: Classify user intent
   - POST /classify/memory: Classify memory category
   - POST /classify/threat: Classify threat type

h) export.py - Data export endpoints
   - GET /export/excel: Export data to Excel format

i) research.py - Research and experimentation endpoints
   - Used for testing attack scenarios
   - Supports research on security effectiveness

j) tool_policy.py - Tool usage policy endpoints
   - Manages which tools can be accessed
   - Enforces tool usage restrictions

k) propagation.py - Poison propagation analysis
   - Tracks how poisoned memories spread
   - Analyzes infection patterns

l) evaluation.py - System evaluation endpoints
   - Metrics and performance evaluation
   - Security effectiveness metrics

m) admin.py - Administrative endpoints
   DELETE /admin/databases - Clear all data (for testing)

#### 6. Database Layer (backend/app/database/)

a) session.py - Database Connection Management
What it does:
- Creates SQLAlchemy engine for database connection
- Provides session factory for database operations
- Dependency injection for database sessions in endpoints

Why it's necessary:
- Manages database connection lifecycle
- Enables efficient connection pooling
- Provides clean session management

b) models.py - Database Schema Definition
What it does:
- Defines all database tables using SQLAlchemy ORM
- Specifies relationships between tables
- Includes complete schema for memory system

Key models:
- Memory: Stores facts with security metadata
- MemoryHistory: Tracks memory changes over time
- AuditEvent: Logs all security decisions
- PoisonEvent: Tracks poisoning detection
- PreferenceEvent: Tracks preference-related events
- ToolPolicyEvent: Tracks tool policy violations
- PropagationEvent: Tracks poison propagation
- ClassificationStat: Tracks classification accuracy
- QuarantineMemory: Stores quarantined memories
- ReflectionLog: Stores system reflections

c) migrate.py - Database Migration System
What it does:
- Handles schema updates and migrations
- Runs migrations on application startup
- Supports schema evolution

Why it's necessary:
- Allows safe database schema changes
- Enables backward compatibility
- Supports version upgrades

#### 7. Audit and Logging (backend/app/audit/)

a) logger.py - Security Event Logging
What it does:
- Logs all security decisions and events
- Records decision reasoning
- Stores event metadata

Why it's necessary:
- Provides complete audit trail
- Enables compliance reporting
- Supports forensics and debugging

b) history_logger.py - Memory History Logging
What it does:
- Tracks all changes to memories
- Records who changed what and when
- Maintains revision history

Why it's necessary:
- Enables memory rollback
- Provides accountability
- Supports compliance requirements

c) dashboard.py - Dashboard Data Aggregation
What it does:
- Aggregates audit data for dashboard visualization
- Provides summary statistics
- Calculates trends and metrics

Why it's necessary:
- Provides real-time system monitoring
- Visualizes security events
- Supports threat analysis

d) events.py - Event Type Definitions
What it does:
- Defines event types and structures
- Provides event categorization

e) research_metrics.py - Research-Specific Metrics
What it does:
- Calculates metrics for security research
- Tracks attack success rates
- Measures detection accuracy

#### 8. Memory Security Framework (backend/app/memory_security/)

a) tool_policy_config.py - Tool Usage Policy Configuration
What it does:
- Defines which tools can be accessed
- Specifies restrictions per tool
- Manages tool usage policies

Why it's necessary:
- Prevents unauthorized tool access
- Implements principle of least privilege
- Restricts dangerous operations

b) constants.py - Security Constants
What it does:
- Defines threshold values for security decisions
- Stores policy constants
- Contains configuration values

Subdirectory: quarantine/
  quarantine_manager.py - Manages memory quarantine
  What it does:
  - Quarantines suspicious memories
  - Manages quarantine workflow
  - Supports review and release processes

Subdirectory: services/
  memory_security_pipeline.py - Main security pipeline orchestrator
  What it does:
  - Coordinates all security operations
  - Manages security workflow
  - Ensures all security checks execute

  poison_event_logger.py - Tracks poisoning events
  preference_event_logger.py - Tracks preference changes
  tool_policy_event_logger.py - Tracks policy violations
  propagation_event_logger.py - Tracks poison spreading

Subdirectory: engines/
  decision_engine.py - Makes quarantine decisions
  poison_propagation_engine.py - Models poison spreading

Subdirectory: detectors/
  preference_manipulation_detector.py - Detects preference tampering
  false_fact_detector.py - Detects false memories
  tool_policy_validator.py - Validates tool policies

#### 9. Learning and Classification (backend/app/learning/)

a) classification_tracker.py - Classification Statistics
What it does:
- Tracks classification accuracy
- Records false positives and false negatives
- Supports continuous improvement

Why it's necessary:
- Measures system effectiveness
- Identifies areas needing improvement
- Supports model retraining decisions

#### 10. Evaluation (backend/app/evaluation/)

a) metrics.py - Performance Metrics Calculation
What it does:
- Calculates security metrics
- Measures detection rates
- Evaluates system performance

Why it's necessary:
- Provides objective system evaluation
- Supports benchmarking
- Identifies optimization opportunities

#### 11. Schemas (backend/app/schemas/)

Pydantic models for data validation:

a) threat.py - Threat data structures
b) memory_security.py - Security decision structures
c) memory.py - Memory data structures
d) audit.py - Audit event structures

Why they exist:
- Provides input/output validation
- Enables API documentation
- Prevents invalid data from entering system

#### 12. Utilities (backend/app/utils/)

a) config.py - Configuration management
b) constants.py - Application constants
c) helpers.py - Helper functions

### Frontend Components

#### 1. React Application Structure

a) main.jsx - React application entry point
What it does:
- Initializes React with ReactDOM
- Mounts App component to DOM

b) App.jsx - Root Component with Routing
What it does:
- Defines application routes using React Router
- Routes to /chat (ChatPage)
- Routes to /dashboard (DashboardPage)
- Default redirect to /chat

Why it's necessary:
- Enables multi-page navigation
- Provides structure for application

#### 2. Pages (frontend/src/pages/)

a) ChatPage.jsx - Chat Interface
What it does:
- Displays chat interface for user interaction
- Manages conversation history
- Handles message sending and receiving
- Manages session state (local storage)
- Provides session sidebar for conversation management

Key features:
- New chat creation
- Chat session management
- Message persistence in localStorage
- Real-time message updates
- Auto-scroll to latest message

Functions:
- selectSession(): Switch active chat
- handleNewChat(): Create new conversation
- handleDelete(): Remove conversation
- send(): Send message to backend

Why it's necessary:
- Primary user interface for interaction
- Manages conversation state
- Provides persistent session storage

b) DashboardPage.jsx - Monitoring Dashboard
What it does:
- Displays real-time security monitoring
- Shows memory vault contents
- Displays audit events
- Provides system control functions

Features:
- Real-time memory table with updates every 5 seconds
- Audit event logging view
- Database reset capability (for testing)
- Excel export functionality

Why it's necessary:
- Provides security monitoring interface
- Enables system administration
- Supports debugging and analysis

#### 3. Components (frontend/src/components/)

a) Layout.jsx - Common Page Layout
What it does:
- Provides consistent layout for dashboard pages
- Includes header and navigation

b) dashboard/ directory:
  - Sidebar.jsx: Navigation sidebar for dashboard
  - MemoryTable.jsx: Table displaying stored memories with security details
  - AuditTable.jsx: Table displaying security audit events
  - ThreatTable.jsx: Table displaying detected threats
  - ConflictTable.jsx: Table displaying memory conflicts
  - ExportPanel.jsx: Export functionality UI

c) chat/ directory:
  - ChatSidebar.jsx: Sidebar for chat sessions
  - MessageBubble.jsx: Individual message display component

#### 4. API Services (frontend/src/api/)

a) attacklayer.js - Main API Service
What it does:
- Provides functions for API communication
- Handles HTTP requests using Axios
- Implements error handling

Key functions:
- sendChatMessage(userId, message): Send chat message
- getAllMemories(): Fetch all stored memories
- getAuditEvents(): Fetch audit logs
- downloadExcel(): Export data
- clearDatabases(): Admin function to clear data

Why it's necessary:
- Centralizes API communication
- Provides consistent error handling
- Abstracts backend API details

#### 5. Utilities (frontend/src/utils/)

a) chatSessions.js - Session Management
What it does:
- Manages chat session state in localStorage
- Functions: getSessions, createSession, getSession, updateSession, deleteSession
- Generates titles from messages
- Bootstrap initial state

Why it's necessary:
- Persists conversation history
- Provides offline-first approach
- Enables session recovery

#### 6. Styling (frontend/src/styles/)

a) dashboard.css - Dashboard styling
b) chat.css - Chat interface styling
c) App.css - Global application styles
d) index.css - Base CSS styles

## Data Flow and Request Processing

### Chat Message Processing Flow

1. User enters message in ChatPage frontend
2. Message sent to /chat endpoint with user_id
3. Backend orchestrator receives request
4. Security gateway evaluates message for threats
5. If threat detected: response with security warning
6. If safe:
   a. Determines if message is memory store request
   b. Retrieves relevant memories using semantic search
   c. Builds LLM context from safe memories
   d. Calls LLM service to generate response
   e. Validates response against policies
   f. Stores user statement if appropriate
   g. Logs security event with full metadata
7. Response returned to frontend with metadata
8. Frontend displays response and updates session

### Memory Creation Flow

1. User provides statement like "Remember that I prefer coffee"
2. Memory detection logic identifies memory store intent
3. Security gateway evaluates statement
4. If blocked:
   - Memory rejected with reason
   - Event logged with attack type
   - User receives security warning
5. If allowed:
   a. Memory normalized to standard format
   b. Worthiness evaluated (is it worth storing?)
   c. If worthy:
      - Embedding generated using Ollama
      - Embedding added to ChromaDB vector store
      - Memory stored in SQLite database
      - History logged in MemoryHistory table
   d. If suspicious:
      - Memory quarantined for review
      - Marked as pending verification
      - Admin notified
   e. Conflict detection runs against existing memories
   f. Trust score calculated
   g. Audit event logged

### Security Decision Process

1. Input text received
2. Intent classification: What is user trying to do?
3. Security classification: Is this a known attack pattern?
4. Sensitive data detection: Does it contain PII/credentials?
5. Semantic classification: What category is this memory?
6. Final decision logic:
   - If sensitive data detected: BLOCK
   - Else if attack pattern detected: BLOCK
   - Else if policy violation: BLOCK
   - Else if high risk score: ALLOW_WITH_WARNING
   - Else: ALLOW
7. Explanation generated for traceability
8. Complete result returned with all metadata

## Database Schema Overview

### Core Tables

Memory Table:
- id: Primary key
- user_id: User identifier
- fact: The memory content
- category: Semantic category
- trust_score: 0-1 trustworthiness
- confidence_score: Classifier confidence
- conflict_score: Contradiction level
- poison_score: Poisoning probability
- risk_score: Overall risk assessment
- poison_flag: Manual poison marker
- verified: Verification status
- attack_type: Type of attack detected
- sensitivity_level: PII classification level
- source: Where memory came from
- final_decision: ALLOW/BLOCK/ALLOW_WITH_WARNING
- memory_version: Version number
- parent_memory_id: For versioning
- active: Is this memory active?
- preference_stability_score: Preference change tracking
- preference_drift_score: Behavior drift tracking
- importance_score: Memory importance

AuditEvent Table:
- Stores all security decisions
- Records complete decision context
- Contains threat type, confidence, risk level
- Includes full payload for replay/analysis
- Tracks execution time and metadata

## Technology Stack

Backend:
- Python 3.12
- FastAPI: Web framework
- SQLAlchemy: ORM for database
- Pydantic: Data validation
- Ollama: Embedding generation
- ChromaDB: Vector database
- Httpx/Requests: HTTP client

Frontend:
- React 19: UI framework
- React Router 7: Client-side routing
- Axios: HTTP client
- Vite: Build tool
- ESLint: Code quality
- CSS3: Styling

Databases:
- SQLite: Relational database
- ChromaDB: Vector database for embeddings

## Security Mechanisms

1. Multi-Layer Security:
   - Intent-based classification
   - Pattern-based threat detection
   - Sensitive data detection
   - Semantic analysis
   - Policy enforcement

2. Memory Protection:
   - Semantic conflict detection
   - Poisoning detection
   - Trust scoring
   - Version tracking
   - Quarantine system

3. Audit and Compliance:
   - Complete event logging
   - Decision reasoning
   - Execution metrics
   - Compliance reporting

4. Attack Prevention:
   - Prompt injection detection
   - Memory poisoning prevention
   - Credential protection
   - PII safeguarding
   - Tool policy enforcement

## Running the Application

Backend:
pip install -r backend/requirements.txt
uvicorn app.main:app --reload

Frontend:
cd frontend
npm install
npm run dev

Access:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Summary

AttackLayer is a comprehensive security framework for LLM agent memory systems. It implements defense-in-depth with multiple security layers, comprehensive threat detection, sophisticated memory management, and complete audit trails. The architecture separates concerns effectively with specialized modules for each security function, enabling maintainability and extensibility while providing state-of-the-art protection against modern LLM attack vectors.
