# Tasks: Python SDK — `human-memory`

## Phase 1: Package Scaffold

- [ ] T001 Create `sdk/` directory with `pyproject.toml`, `README.md`, package structure
- [ ] T002 Write `sdk/src/human_memory/models.py` — all Pydantic response models
- [ ] T003 Write `sdk/src/human_memory/exceptions.py` — typed exceptions

## Phase 2: Sync Client

- [ ] T004 Write `sdk/src/human_memory/client.py` — `Memory` class with all methods
- [ ] T005 Write `sdk/src/human_memory/__init__.py` — exports Memory, AsyncMemory, models

## Phase 3: Async Client

- [ ] T006 Write `sdk/src/human_memory/async_client.py` — `AsyncMemory` class

## Phase 4: Tests

- [ ] T007 Write `sdk/tests/test_client.py` — unit tests with mocked HTTP (pytest-httpx)
- [ ] T008 Write `sdk/tests/test_async_client.py` — async unit tests
- [ ] T009 Write `sdk/tests/test_integration.py` — integration tests against real API

## Phase 5: Documentation

- [ ] T010 Write `sdk/README.md` — installation, usage examples, API reference

## Phase 6: Verification

- [ ] T011 Install SDK locally (`pip install ./sdk`) and verify imports work
- [ ] T012 Run unit tests — all pass without server
- [ ] T013 Run integration tests — all pass against Docker deployment
