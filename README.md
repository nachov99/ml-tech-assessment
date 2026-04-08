# ml-tech-assessment

## Quick Start (Docker)

1. Create a `.env` file in the root directory:
   ```
   OPENAI_API_KEY=your_api_key_here
   OPENAI_MODEL=gpt-4o-2024-08-06
   ```

2. Build and run:
   ```bash
   docker build -t ml-tech-assessment .
   docker run --env-file .env -p 8000:8000 ml-tech-assessment
   ```

3. Open Swagger docs at http://localhost:8000/docs

## Local Setup (Conda + Poetry)

1. Create and activate a conda environment:
   ```bash
   conda create -n ml-assessment python=3.12
   conda activate ml-assessment
   ```

2. Install Poetry and project dependencies:
   ```bash
   pip install poetry
   poetry install
   ```

3. Create a `.env` file with your OpenAI credentials (see above).

4. Run the API:
   ```bash
   uvicorn app.main:app --reload
   ```

## Running Tests

```bash
# All tests except OpenAI integration (no API key needed)
pytest tests/adapters/test_in_memory_repository.py tests/services/ tests/api/ -v

# Full suite (requires valid OPENAI_API_KEY in .env)
pytest -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/transcripts/analyze?transcript=...` | Analyze a single transcript |
| GET | `/transcripts/{id}` | Get analysis by ID |
| GET | `/transcripts/` | List all analyses |
| POST | `/transcripts/analyze-batch` | Analyze multiple transcripts concurrently |

## Architecture

```
API Layer (FastAPI routes + schemas)
    ↓
Service Layer (TranscriptService)
    ↓
Ports (LLm, TranscriptRepository — abstract interfaces)
    ↓
Adapters (OpenAIAdapter, InMemoryTranscriptRepository)
    ↓
Domain (TranscriptAnalysis — plain dataclass)
```

The project follows hexagonal (ports & adapters) architecture with clear layer separation:

- **Domain model as dataclass**, not Pydantic — keeps the domain layer framework-agnostic and decoupled from infrastructure.
- **LLM response DTO separate from domain model** — `TranscriptAnalysisDTO` (Pydantic) is the structured output contract with OpenAI. `TranscriptAnalysis` (dataclass) is the business entity. If the LLM response shape changes, the domain stays untouched.
- **Repository port** — abstracts storage behind an interface. Currently backed by an in-memory dict, but swappable to Redis, PostgreSQL, etc. without changing the service layer.

## Design Decisions

### GET vs POST for Analyze

The assessment specifies a GET request. I chose `GET /transcripts/analyze?transcript=...` with the transcript as a query parameter, which makes the endpoint fully testable from Swagger UI.

**Trade-off:** query parameters have practical size limits (~8KB depending on the server/browser). For production use with long transcripts, POST with a JSON body would be more appropriate. The switch is a one-line change (decorator + parameter type).

### Async Batch Processing

The batch endpoint uses `asyncio.gather()` to fire all LLM calls concurrently via the adapter's `run_completion_async` method. This means N transcripts are processed in roughly the time of 1, rather than sequentially.

### Error Handling

- **400** — validation errors (empty transcript)
- **404** — transcript ID not found
- **502** — upstream LLM failure or invalid LLM output (empty summary, no action items)

### Output Guardrails

The service validates LLM responses before storing — if the model returns an empty summary or no action items, the request fails with a 502 rather than saving bad data.

### Dependency Injection

Routes receive the `TranscriptService` via FastAPI's `Depends()` system. This enables clean test isolation — tests inject mocks without touching production wiring.

### Testing Strategy

- **Service tests** — mock both ports (LLm, TranscriptRepository), test business logic in isolation
- **Repository tests** — test the in-memory adapter directly
- **API tests** — mock the service, test HTTP status codes and response shapes via `TestClient`
