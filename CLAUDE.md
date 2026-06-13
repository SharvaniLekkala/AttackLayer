# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

AttackLayer is a semantic security firewall for LLM agent memory systems. It consists of a FastAPI backend and a React frontend, designed to protect against prompt injection, memory poisoning, and other LLM-specific attacks.

## Directory Structure

```
AttackLayer/
├── backend/                 # Python/FastAPI backend
│   ├── app/                 # Main application code
│   │   ├── api/             # REST API endpoints
│   │   ├── memory/          # Memory management (vault, embeddings, retrieval)
│   │   ├── security/        # Security framework (threat detection, policy enforcement)
│   │   ├── llm/             # LLM integration and orchestration
│   │   ├── database/        # SQLAlchemy models and migrations
│   │   ├── audit/           # Logging and audit trails
│   │   ├── memory_security/ # Advanced memory security components
│   │   ├── learning/        # Classification tracking
│   │   ├── evaluation/      # Performance metrics
│   │   ├── schemas/         # Pydantic models
│   │   └── utils/           # Helper functions
│   ├── tests/               # Unit tests (using unittest)
│   └── requirements.txt     # Python dependencies
├── frontend/                # React/Vite frontend
│   ├── src/                 # Source code
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page components (ChatPage, DashboardPage, MemoryVaultPage, HITLPage, ThreatAnalysisPage)
│   │   ├── api/             # API service layer
│   │   ├── services/        # Business logic services
│   │   ├── utils/           # Utility functions (session management)
│   │   └── styles/          # CSS stylesheets
│   ├── public/              # Static assets
│   ├── package.json         # Node.js dependencies and scripts
│   └── vite.config.js       # Vite configuration
└── README.md                # Project documentation
```

## Development Commands

### Backend (Python)

1. **Install dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

2. **Run the development server**:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```
   - API will be available at http://localhost:8000
   - API documentation at http://localhost:8000/docs

3. **Run tests**:
   ```bash
   # From the backend directory
   python -m unittest discover -s tests -p "test_*.py"
   ```
   - To run a specific test file: `python -m unittest tests/test_admin_reset.py`

4. **Linting**:
   - No formal linting configuration is present in the backend. However, you can use standard Python linters like `flake8` or `pylint` if needed.

### Frontend (Node.js)

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Run the development server**:
   ```bash
   npm run dev
   ```
   - Frontend will be available at http://localhost:5173

3. **Build for production**:
   ```bash
   npm run build
   ```

4. **Lint the code**:
   ```bash
   npm run lint
   ```
   - Uses ESLint with React plugins

5. **Preview production build**:
   ```bash
   npm run preview
   ```

## Architecture Highlights

### Layered Architecture
1. **Frontend Presentation Layer** (React/Vite) - User interface
2. **API Layer** (FastAPI) - REST endpoints for all operations
3. **Security Processing Layer** - Threat detection, policy enforcement, semantic analysis
4. **Memory Management Layer** - Memory creation, storage, retrieval, versioning
5. **Persistence Layer** - SQLite (relational) + ChromaDB (vector) databases

### Key Data Flow
1. User input → Frontend → `/chat` endpoint
2. Backend orchestrator receives request
3. Security gateway evaluates input for threats
4. If safe, retrieves relevant memories via semantic search
5. Builds LLM context from safe memories
6. Calls LLM service to generate response
7. Validates response against policies
8. Stores user statement if appropriate
9. Logs security event with full metadata
10. Returns response to frontend

### Security Components
- **Intent Classification**: Determines user operation type
- **Threat Detection**: Identifies attack patterns (prompt injection, etc.)
- **Sensitive Data Detection**: Blocks PII/credentials
- **Semantic Analysis**: Categorizes memory content
- **Policy Engine**: Applies configurable security rules
- **Response Validation**: Ensures LLM responses comply with policies
- **Audit Logging**: Complete traceability of all decisions

## Important Notes
- The backend requires Ollama running for embedding generation (uses `nomic-embed-text` model)
- The frontend uses Vite for fast development builds
- Tests are written using Python's unittest framework
- API endpoints are organized by feature in `backend/app/api/`
- Memory security involves multiple layers: detection, quarantine, conflict analysis, trust scoring

For more detailed information, refer to the README.md and the inline code comments throughout the repository.