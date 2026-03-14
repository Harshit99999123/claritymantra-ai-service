# ClarityMantra AI Service

FastAPI service scaffold for the ClarityMantra AI layer described in the PRD.

## Python Version
This repo is standardized on Python `3.11`.

## Scope
This repo is only the AI service. It is responsible for:
- source ingestion
- retrieval
- prompt construction
- local model generation
- AI-facing APIs

It is not the Java backend or the React UI.

## Included
- FastAPI application factory
- Health, chat, insight, retrieve, and speech routes
- Ingestion endpoints for listing configured books and rerunning a single book
- Centralized settings
- Request-aware logging middleware
- Generic knowledge-chunk dataset loading
- Hybrid retrieval using semantic text plus themes and emotions
- Per-book ingestion registry with book-specific parsers
- Persistent ChromaDB vector index
- Embedding provider abstraction with deterministic and sentence-transformers modes
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

## Start Local Models
Start Ollama in a separate terminal:
```bash
ollama serve
```

Check installed models:
```bash
ollama list
```

Recommended local models for the current config:
```bash
ollama pull llama3:8b
ollama pull llama3.2:latest
```

## Test
```bash
pytest
```

## API Overview
- `GET /health`
- `POST /ai/retrieve`
- `POST /ai/chat`
- `POST /ai/chat/stream`
- `POST /ai/insight`
- `GET /ingestion/books`
- `POST /ingestion/run`

## Chat Examples
Standard chat:
```bash
curl -X POST http://127.0.0.1:8000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I feel stuck and uncertain about results",
    "context": []
  }'
```

Streaming chat with SSE:
```bash
curl -N -X POST http://127.0.0.1:8000/ai/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I feel stuck and uncertain about results",
    "context": []
  }'
```

Retrieve only:
```bash
curl -X POST http://127.0.0.1:8000/ai/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I feel anxious about my future"
  }'
```

## Ingestion
List configured books:
```bash
curl http://127.0.0.1:8000/ingestion/books
```

Rerun ingestion for one book:
```bash
curl -X POST http://127.0.0.1:8000/ingestion/run \
  -H "Content-Type: application/json" \
  -d '{"book_slug":"bhagavad_gita_as_it_is","refresh_active_index":true}'
```

### Ingestion design
- Each book has a registry entry and its own ingestor implementation.
- The active example book is the Bhagavad Gita, parsed from the source PDF directly.
- Optional JSON overrides can refine specific verses without changing the parser.
- Generated outputs are written under `data/books/<book_slug>/`.
- Active retrieval source selection is config-driven through `ACTIVE_BOOK_SLUG`.

### Add a new book
1. Put the source file under a suitable location in `data-resources/`.
2. Add a book definition in [ingestion/registry.py](/Users/harshit/PycharmProjects/clarity_mantra/ingestion/registry.py) with:
   - `slug`
   - `title`
   - `source_kind`
   - `source_document_path`
   - `structured_source_path`
   - `output_dataset_path`
   - `output_metadata_path`
   - `ingestor_key`
3. Create a parser or ingestor under [ingestion/books](/Users/harshit/PycharmProjects/clarity_mantra/ingestion/books).
4. Register the ingestor selection in [ingestion/factory.py](/Users/harshit/PycharmProjects/clarity_mantra/ingestion/factory.py).
5. Make sure the ingestor emits the generic `KnowledgeChunk` model.
6. Optionally add a structured override file for manual fixes.
7. Run ingestion for that specific book:
```bash
curl -X POST http://127.0.0.1:8000/ingestion/run \
  -H "Content-Type: application/json" \
  -d '{"book_slug":"your_new_book_slug","refresh_active_index":false}'
```
8. If you want that book to drive retrieval, update `ACTIVE_BOOK_SLUG` in `.env`.
9. Re-run ingestion with `refresh_active_index=true` for the active book.

### Update an existing book
- update the parser logic, or
- update the structured override JSON for targeted fixes

Then rerun ingestion for only that book:
```bash
curl -X POST http://127.0.0.1:8000/ingestion/run \
  -H "Content-Type: application/json" \
  -d '{"book_slug":"bhagavad_gita_as_it_is","refresh_active_index":true}'
```

### Generated files
- source outputs live under `data/books/<book_slug>/`
- vector index lives under `data/vector_store/`

## RAG Runtime
- Default local setup uses `VECTOR_STORE_PROVIDER=chroma`.
- Current `.env` uses `EMBEDDING_PROVIDER=sentence-transformers`.
- If the model already exists in the local Hugging Face cache, the service loads it offline from the cached snapshot.
- The vector index is automatically rebuilt when the embedding provider, model, or dataset record count changes.
- The vector index persists under `data/vector_store/`.

## Response Style
- Chat responses are tuned to sound calm, polite, modern, and reflective.
- The mentor acknowledges emotion, introduces a grounded perspective, connects it to a retrieved teaching, explains it briefly, and ends with a gentle reflection question.
- The model is explicitly instructed not to preach, moralize, impersonate Krishna, or sound like a raw scripture recitation.
- Retrieved teachings are interpreted in contemporary language rather than copied literally for long stretches.

## Response Format
- `/ai/chat` now returns a structured payload that separates the reflection, the reflection question, and the top 2 verses.
- Example:
```json
{
  "reflection": "Arjuna once felt the same longing ...",
  "reflection_question": "What small step could help you move forward today?",
  "verses": [
    {
      "reference": "2.8",
      "translation": "I can find no means to drive away this grief...",
      "themes": ["grief", "detachment"]
    }
  ]
}
```
This makes the frontend rendering simpler and avoids parsing metadata out of the text.

## Query Rewrite
- Before retrieval, the AI service rewrites messy or error-filled user input into a cleaner retrieval query.
- The rewritten query is used only for similarity search; the final reflection still answers the original user message.
- This helps when user input contains spelling mistakes, fragmented phrasing, or shorthand.
- The feature is controlled by:
  - `ENABLE_QUERY_REWRITE`
  - `QUERY_REWRITE_MODEL`

Example:
- user message: `i dnt knw wht to do in my life evrything is mess`
- retrieval query: cleaned version used for embeddings and retrieval
- final answer: still responds to the original user message

## Local Model Runtime
- The AI service uses Ollama for live generation when `OLLAMA_BASE_URL` is reachable.
- Current `.env` expects `OLLAMA_MODEL=llama3:8b`.
- Current `.env` uses `QUERY_REWRITE_MODEL=llama3.2:latest` to keep rewrite latency lower than main generation.
- If Ollama is not running, the service falls back to a local grounded response so the API remains usable.
- Start Ollama with:
```bash
ollama serve
```
- Check available models with:
```bash
ollama list
```

## Streaming
- `/ai/chat/stream` uses Server-Sent Events (`text/event-stream`)
- event types:
  - `meta`
  - `token`
  - `done`

The `meta` event includes only:
  - retrieved verse references

The `token` event includes incremental text chunks, which allows a ChatGPT-like streaming UX.

## Performance Tuning
If response time feels slow, start with these:
- keep `QUERY_REWRITE_MODEL` on a smaller model such as `llama3.2:latest`
- keep `OLLAMA_MODEL` on the main generation model you want for quality
- reduce `CHAT_MAX_TOKENS`
- keep `OLLAMA_KEEP_ALIVE` enabled so the model stays warm between requests
- prefer streaming in the UI so users see tokens immediately instead of waiting for full completion

Current latency-related env vars:
- `OLLAMA_MODEL`
- `OLLAMA_KEEP_ALIVE`
- `CHAT_TEMPERATURE`
- `CHAT_MAX_TOKENS`
- `QUERY_REWRITE_MODEL`
- `QUERY_REWRITE_MAX_TOKENS`

## Notes
- Chat and insight generation call Ollama when it is available and fall back to local grounded responses when it is not.
- Retrieval is grounded in a source-aware chunk dataset with hybrid ranking across Chroma candidates, translation, interpretation, themes, and emotions.
- The current embedding implementation can run in deterministic mode or sentence-transformers mode without changing the retrieval architecture.
- `.env` is required. The app is configured to fail fast if required environment variables are missing.
