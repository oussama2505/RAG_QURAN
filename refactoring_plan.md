# Project Refactoring Plan

## Current Structure Issues

The current project structure has several issues that make it confusing:

1. Two separate `src` directories (one in root for RAG system, one in frontend for Svelte)
2. Backend API implementation in `app/api.py` that imports from the root `src` directory
3. References to Streamlit in Docker and configuration files despite migration to Svelte
4. Unclear separation between frontend and backend components

## Proposed New Structure

```
RAG_QURAN/
├── backend/              # All backend code
│   ├── api/              # API implementation
│   │   ├── __init__.py
│   │   └── routes.py     # (renamed from api.py)
│   ├── core/             # Core RAG implementation (moved from src/)
│   │   ├── __init__.py
│   │   ├── api_key_manager.py
│   │   ├── config.py
│   │   ├── data_processing.py
│   │   ├── direct_openai.py
│   │   ├── embeddings.py
│   │   ├── generator.py
│   │   ├── llm_client.py
│   │   ├── main.py
│   │   ├── retriever.py
│   │   └── utils.py
│   └── __init__.py
├── frontend/            # Svelte frontend (unchanged)
├── data/                # Data directory (unchanged)
├── vector_db/           # Vector database (unchanged)
├── utils/               # Utility scripts (unchanged)
├── .github/             # GitHub workflows
├── Dockerfile           # Updated for new structure
├── docker-compose.yml   # Updated for new structure
├── requirements.txt     # Backend dependencies
└── README.md           # Updated documentation
```

## Implementation Steps

1. Create the new directory structure
2. Move files from `src/` to `backend/core/`
3. Move files from `app/` to `backend/api/`
4. Update import paths in all files
5. Update Dockerfile and docker-compose.yml
6. Update GitHub workflow
7. Remove Streamlit references
8. Update README.md to reflect new structure

## Import Path Changes

Current imports like:
```python
from src.config import VECTOR_DB_PATH
from src.embeddings import get_embedding_model
```

Will become:
```python
from backend.core.config import VECTOR_DB_PATH
from backend.core.embeddings import get_embedding_model
```

## Docker Changes

The Dockerfile and docker-compose.yml will need to be updated to reflect the new directory structure and remove Streamlit references.

## GitHub Workflow Changes

The GitHub workflow will need to be updated to reflect the new directory structure.

## README Updates

The README.md will need to be updated to reflect the new directory structure and provide clear documentation on the project organization.