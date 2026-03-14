# Project Learnings

## 2026-03-15

### Product scope from PRD
- Product: AI philosophical reflection mentor inspired by the Bhagavad Gita.
- Product posture: calm, reflective, thoughtful, non-judgmental.
- Must not behave like a generic chatbot, a preaching tool, a scripture reader, or an impersonation of Krishna.
- Mentor representation must be a neutral monk-like guide and must not resemble Krishna.

### Full product vision
- Guided reflection experience grounded in philosophical teachings.
- Users can engage through voice primarily, with text as an optional mode.
- Responses should follow a structured reflection model:
  1. understand the concern
  2. acknowledge emotion
  3. identify philosophical conflict
  4. introduce a relevant principle
  5. reference Bhagavad Gita teaching
  6. interpret it in modern language
  7. apply it to the user's situation
  8. encourage reflection or action

### MVP scope from PRD
- Landing page
- Authentication
- Mentor environment
- Conversation system
- Bhagavad Gita knowledge grounding
- Voice responses
- On-screen transcript
- Conversation history
- Shareable insight cards
- Feedback system

### Explicitly excluded from MVP
- Habit tracker
- Journaling system
- Poster marketplace
- Advanced analytics
- Multi-philosophy knowledge base

### Architecture from PRD
- Frontend: React + TypeScript + TailwindCSS
- Backend API: Spring Boot
- AI service: Python + FastAPI
- RAG stack: sentence-transformers + ChromaDB
- LLM runtime: Ollama with Llama-family model
- Database: PostgreSQL

### Source data
- Primary source text available locally at `data-resources/hindu/Bhagavad-gita-As-It-Is.pdf`.
- This edition includes Sanskrit text, transliteration, English translation, and commentary/purports.
- The source has strong devotional commentary, so grounding logic will need deliberate handling to keep the product aligned with the PRD's non-preaching and non-impersonation constraints.

### Current repository state
- Repository is now a standalone Python AI service project.
- This repo is only for the FastAPI AI service.
- Java backend and React frontend will live in separate projects.

### Finalized project structure
- `main.py`: FastAPI application entrypoint and app factory.
- `dependencies.py`: service container wiring.
- `api/`: HTTP routing layer.
- `core/`: config, logging, middleware.
- `models/`: request and response schemas.
- `services/`: orchestration and business logic.
- `rag/`: retrieval, embeddings, vector store abstractions.
- `llm/`: prompt building and LLM client integration points.
- `utils/`: shared helper utilities.
- `tests/`: endpoint and service tests.
- `data-resources/`: source PDFs and reference documents.
- `learning/`: running project learnings and decisions.

### Runtime standard
- The repo is standardized on Python `3.11`.
- Local project interpreter should be `.venv/bin/python`.
- The machine default `python3` may point to Python `3.14`, which does not currently work for this pinned FastAPI stack in this environment.
- The application should be run with:
  - `source .venv/bin/activate`
  - `uvicorn main:app --reload`

### Process learnings
- `pypdf` had to be installed locally to extract the PRD and source PDF text.
- Requirement from user: do not assume details not stated in the PRD; ask when unclear.
- Requirement from user: changes should be approved before implementation.
- Initial nested `ai_service/` package layout was rejected because the repo itself should be the AI service, not a wrapper project containing one.
- IDE/runtime errors around `fastapi` were caused by the wrong interpreter selection, not by the code itself.
