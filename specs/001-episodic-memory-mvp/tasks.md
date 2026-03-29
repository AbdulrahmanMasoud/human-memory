# Tasks: Episodic Memory Store with ACT-R Temporal Decay

**Input**: Design documents from `specs/001-episodic-memory-mvp/`
**Prerequisites**: plan.md, spec.md, data-model in plan.md

## Phase 1: Foundation (Pure Python — No External Services)

- [x] T001 [P] Write `src/memory_system/core/actr.py` — ACTRMemory class with `base_level_activation()`, `total_activation()`, `can_retrieve()`, `retrieval_latency()`
- [x] T002 [P] Write `tests/unit/test_actr.py` — Test power-law decay, threshold filtering, noise, known-input verification (21 tests passing)
- [x] T003 [P] Write `src/memory_system/models/memory.py` — Pydantic models: MemoryCreate, MemoryResponse, MemorySearchRequest, MemorySearchResult, MemoryDetail, MemoryStats
- [x] T004 [P] Write `tests/unit/test_models.py` — Test validation, defaults, serialization (13 tests passing)
- [x] T005 [P] Write `src/memory_system/core/embeddings.py` — EmbeddingService using ONNX Runtime + tokenizers for all-MiniLM-L6-v2
- [ ] T006 [P] Write `tests/unit/test_embeddings.py` — Test embed() returns 384-dim vector, deterministic output (requires model download)

## Phase 2: Storage Layer (Requires Docker Services)

- [x] T007 Write `src/memory_system/models/database.py` — SQLAlchemy async models: MemoryMetadata, AccessHistory with Base
- [x] T008 Write Alembic migration `alembic/versions/001_initial_schema.py` — Create memory_metadata and access_history tables with indexes
- [x] T009 Write `src/memory_system/stores/postgres_store.py` — PostgresMetadataStore: create_memory, get_memory, update_activation, record_access, get_access_history, get_active_memories, mark_decayed, get_stats, delete_memory
- [ ] T010 Write `tests/integration/test_postgres_store.py` — Integration tests against real PostgreSQL
- [x] T011 Write `src/memory_system/stores/qdrant_store.py` — QdrantMemoryStore: ensure_collection, upsert_memory, search, update_payload, delete
- [ ] T012 Write `tests/integration/test_qdrant_store.py` — Integration tests against real Qdrant

## Phase 3: Service Layer (US1 + US2 Core)

- [x] T013 Write `src/memory_system/core/memory_service.py` — MemoryService: store(), retrieve(), recall(), forget(), inspect(), stats(), run_decay()
- [ ] T014 Write `tests/unit/test_memory_service.py` — Test retrieval pipeline with mocked stores, verify ACT-R ordering

## Phase 4: API + Background Tasks (US1-US6)

- [x] T015 Write `src/memory_system/api/memories.py` — FastAPI router: POST /v1/memories, POST /v1/memories/search, GET /v1/memories/{id}, DELETE /v1/memories/{id}, POST /v1/memories/decay
- [x] T016 Write `src/memory_system/api/stats.py` — FastAPI router: GET /v1/stats, GET /v1/memories/{id}/inspect
- [x] T017 Update `src/memory_system/main.py` — Register routers, implement lifespan (init Qdrant collection, verify Postgres, load embedding model)
- [x] T018 Write `src/memory_system/tasks/decay.py` — Celery task `batch_update_decay`: fetch all active memories, recalculate B_i, update activation, mark decayed
- [ ] T019 Write `tests/integration/test_api_memories.py` — End-to-end tests: store → retrieve → recall → forget → stats
- [ ] T020 Write `tests/integration/test_decay_task.py` — Test decay reduces activation, marks memories below threshold

## Phase 5: Docker Verification

- [ ] T021 Build Docker image and run `docker compose up` — verify all services start healthy
- [ ] T022 Smoke test: store 10 memories via API, retrieve by query, verify ACT-R ordering, trigger decay, verify activation decreased
