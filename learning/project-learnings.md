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

### RAG and retrieval decisions
- Retrieval is verse-based, not arbitrary token chunking.
- Each knowledge chunk should preserve a full philosophical unit:
  - chapter
  - verse
  - translation
  - meaning
  - themes
  - emotions
- Retrieval should not rely only on raw semantic similarity.
- Current retriever uses a hybrid score across:
  - semantic text similarity
  - lexical overlap
  - theme overlap
  - emotion overlap
- Retrieval now uses a persistent ChromaDB candidate store and reranks candidate results with the hybrid score.
- Prompt construction now includes retrieved verse translation, meaning, themes, and emotions.
- Context is trimmed by a token budget so retrieved material remains bounded before generation.
- Current generated dataset path for the active Bhagavad Gita book is `data/books/bhagavad_gita_as_it_is/dataset.json`.
- Ingestion now has a book-specific structured source at `data-resources/hindu/bhagavad_gita_as_it_is.seed.json`.
- Generated outputs live under `data/books/<book_slug>/`, which allows rerunning one book without touching others.
- The vector index now persists at `data/vector_store/`.
- Embeddings are provider-based:
  - deterministic mode for lightweight local execution
  - sentence-transformers mode for richer semantic retrieval
- `.env` now uses sentence-transformers embeddings and an active source slug for the live setup.
- `.env.example` mirrors the same source-driven retrieval contract.

### Ingestion design decisions
- Ingestion is exposed through API endpoints, not a CLI.
- Configured books can be listed through `/ingestion/books`.
- A specific book can be rerun through `/ingestion/run`.
- The ingestion pipeline is generic at the registry and book-adapter level:
  - each book has a registry definition
  - each book can have its own ingestor implementation
  - each book writes to its own dataset and metadata paths
- When an ingested book is marked as active for retrieval, rerunning ingestion also refreshes the in-memory retrieval index.
- The Bhagavad Gita ingestor now parses the PDF directly using chapter page boundaries and verse block detection.
- JSON overrides are applied after parsing so data quality improvements can be made for specific verses without replacing the parser.
- Combined verse blocks such as `TEXTS 1-2` are preserved as a single chunk with `verse_label`.

### Process learnings
- `pypdf` had to be installed locally to extract the PRD and source PDF text.
- Requirement from user: do not assume details not stated in the PRD; ask when unclear.
- Requirement from user: changes should be approved before implementation.
- Initial nested `ai_service/` package layout was rejected because the repo itself should be the AI service, not a wrapper project containing one.
- IDE/runtime errors around `fastapi` were caused by the wrong interpreter selection, not by the code itself.
- The AI service should stay scoped to AI responsibilities only: ingestion, retrieval, prompt construction, and model generation. Backend persistence and application workflow ownership should remain outside this repo.
- The active knowledge source should be selected by `ACTIVE_BOOK_SLUG`, not by a hardcoded dataset path.
- The core retrieval model should be generic (`KnowledgeSource`, `KnowledgeChunk`) so new books can be added without renaming the service domain model each time.
- Source-specific parsers can still exist, but they should emit the same generic chunk model.
- Prompt tone needs to be explicitly constrained. A calm product voice does not emerge automatically from RAG; it has to be enforced in the system prompt and fallback responses.
- Useful tone constraints for this product:
  - calm and respectful
  - modern language, not devotional language
  - reflective, not preachy
  - short and readable
  - end with one gentle next step or question
- The model should reference teachings naturally rather than sounding like it is reciting scripture verbatim.
- Ollama generation is part of the AI service boundary, but it needs a safe fallback path so `/ai/chat` continues working when the local model runtime is unavailable.
- Retrieval quality improves when noisy user input is rewritten before embedding.
- Query rewrite should happen before retrieval, not before final answer generation.
- The rewritten query should preserve meaning and emotional signal, but the final model should still answer the original user message.
- Query rewrite should be optional and config-driven so it can be disabled if it starts over-normalizing user intent.
- Splitting rewrite and generation models is useful for latency control. A smaller model can clean the query while a stronger model handles the final mentor response.
- Streaming matters even when total generation time is still noticeable. Returning token chunks through SSE makes the product feel much faster and closer to a ChatGPT-style experience.
- `OLLAMA_KEEP_ALIVE` helps reduce repeated cold-start latency for local model inference.
