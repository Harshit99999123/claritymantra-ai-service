## Clarity Mantra AI Service — API Reference

Each endpoint below lists the intent, request payload, and the canonical response schema so the Java backend and frontend can integrate cleanly.

### `/health`
- **Intent:** quick uptime check.
- **Request:** `GET /health`
- **Response:**
  ```json
  {
    "status": "ok",
    "service": "ai-service"
  }
  ```

### `/ai/chat`
- **Intent:** generate a Bhagavad Gita grounded reflection.
- **Request:** `POST /ai/chat`
  ```json
  {
    "message": "I am dealing with heartache and I do not know how to move forward.",
    "context": [
      {
        "role": "user",
        "message": "I feel the same sadness again."
      }
    ]
  }
  ```
- **Response (production schema):**
  ```json
  {
    "reflection": "Acknowledges emotion, references Bhagavad Gita 2.8, interprets it in modern language.",
    "reflection_question": "What small step could help you move forward today?",
    "verses": [
      {
        "reference": "2.8",
        "translation": "I can find no means to drive away this grief ...",
        "themes": ["grief", "detachment"]
      }
    ]
  }
  ```
- **Notes:** `reflection_question` is extracted from the LLM output; verses are limited to top 2 entries; debug fields (scores, chunk IDs, retrieval_query) are not exposed.

### `/ai/chat/stream`
- **Intent:** stream tokens for a ChatGPT-style UI.
- **Request:** `POST /ai/chat/stream` same payload as `/ai/chat`.
- **Response:** SSE (`text/event-stream`)
  1. `event: meta` contains brief references:
     ```json
     {"references":[{"source":"Bhagavad Gita As It Is","reference":"2.8"}]}
     ```
  2. `event: token` delivers incremental text chunks (`{"text":"..."}`).
  3. `event: done` signals completion.
- **Notes:** meta no longer emits `retrieval_query`; backend should proxy the stream unchanged to the frontend.

### `/ai/retrieve`
- **Intent:** expose retrieval-only data for diagnostics or insight purposes.
- **Request:**
  ```json
  {
    "query": "I feel stuck in my career and uncertain about my future."
  }
  ```
- **Response:**
  ```json
  {
    "results": [
      {
        "chunk_id": "2_8",
        "source": {"slug":"bhagavad_gita_as_it_is","title":"Bhagavad Gita As It Is","kind":"book"},
        "reference": "2.8",
        "translation": "...",
        "interpretation": "...",
        "themes": ["career"],
        "emotions": ["confusion"],
        "retrieval_score": 1.0092,
        "retrieval_reason": "theme match, semantic overlap"
      }
    ],
    "retrieval_query": "cleaned query used for retrieval"
  }
  ```
- **Notes:** This is the only endpoint that still returns `retrieval_query` and debug fields; keep it for troubleshooting.

### `/ai/insight`
- **Intent:** produce a concise insight card referencing a single verse.
- **Request:**
  ```json
  {
    "conversation": [
      {"role": "user","message": "I feel stuck and uncertain about results."}
    ]
  }
  ```
- **Response:**
  ```json
  {
    "quote": "Abandon all varieties of religion and just surrender unto Me...",
    "meaning": "You can let go of rigid dogma and rest in clarity.",
    "reflection": "What part of this teaching feels most useful for your next step?",
    "shloka": "sarva-dharmän parityajya mäm ekaà çaraëaà vraja" // optional
  }
  ```
- **Notes:** Shloka text appears only when the chunk has clean source text; output is neutralized to avoid divine names.

### `/ingestion/books`
- **Intent:** list available books/parsers.
- **Request:** `GET /ingestion/books`
- **Response:** list of book definitions (`slug`, `title`, paths, `active_for_retrieval` flag).

### `/ingestion/run`
- **Intent:** rebuild dataset + index for a book (used after parser updates or new book data).
- **Request:**
  ```json
  {
    "book_slug": "bhagavad_gita_as_it_is",
    "refresh_active_index": true
  }
  ```
- **Response:**
  ```json
  {
    "book_slug": "...",
    "title": "...",
    "output_dataset_path": "...",
    "records_written": 653,
    "refreshed_active_index": true
  }
  ```
- **Notes:** When `refresh_active_index` is `true` and the book is active (`ACTIVE_BOOK_SLUG`), the Chroma index is rebuilt and cached manifest updated.

### Integration tips
- Use `.env`/`.env.example` to align token limits and models (`CHAT_MAX_TOKENS`, `ACTIVE_BOOK_SLUG`, etc.).
- The Java backend should call `/ai/chat` for the reflection card and `/ai/chat/stream` if streaming is required; both endpoints share the same verse pool and prompt logic.
- For logging/debug, call `/ai/retrieve` to inspect raw retrieval metadata.
- Ingestion runs should be triggered whenever book PDFs change or parser logic is modified; the backend should wait for `refreshed_active_index` before serving the new vectors.
