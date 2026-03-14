# ClarityMantra AI Service

FastAPI service scaffold for the ClarityMantra AI layer described in the PRD.

## Python Version
This repo is standardized on Python `3.11`.

## Included
- FastAPI application factory
- Health, chat, insight, retrieve, and speech routes
- Centralized settings
- Request-aware logging middleware
- Service, LLM, and RAG package boundaries
- Basic tests

## Run
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

## Test
```bash
pytest
```

## Notes
- External integrations are scaffolded, not fully implemented yet.
- Current LLM and retrieval behavior uses placeholder logic to preserve clean interfaces while the real RAG pipeline is built.
- `.env` is required. The app is configured to fail fast if required environment variables are missing.
