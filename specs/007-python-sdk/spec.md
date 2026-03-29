# Feature Specification: Python SDK — `human-memory`

**Feature Branch**: `007-python-sdk`
**Created**: 2026-03-29
**Status**: Draft

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Store and Search Memories (Priority: P1)

A developer installs the SDK via `pip install human-memory` and uses it to store and search memories with 3 lines of code.

**Acceptance Scenarios**:
1. **Given** the SDK is installed, **When** `memory.store("some text")` is called, **Then** a memory ID is returned.
2. **Given** memories exist, **When** `memory.search("query")` is called, **Then** results are returned ranked by ACT-R activation.
3. **Given** a memory ID, **When** `memory.recall(id)` is called, **Then** the full memory is returned and access is tracked.

---

### User Story 2 — Knowledge Graph Operations (Priority: P1)

A developer builds a knowledge graph using `memory.add_concept()` and `memory.add_relation()`, then queries it with spreading activation.

**Acceptance Scenarios**:
1. **Given** concepts exist, **When** `memory.spread(["Python"])` is called, **Then** related concepts are returned with activation weights.

---

### User Story 3 — Async Support (Priority: P1)

The SDK provides an `AsyncMemory` class for async/await usage in FastAPI, LangChain, etc.

**Acceptance Scenarios**:
1. **Given** `AsyncMemory`, **When** `await memory.search("query")` is called, **Then** results are returned.

---

### User Story 4 — System Operations (Priority: P2)

A developer triggers decay, consolidation, and forgetting via the SDK.

**Acceptance Scenarios**:
1. **Given** the SDK, **When** `memory.decay()` is called, **Then** a decay report is returned.
2. **Given** the SDK, **When** `memory.consolidate()` is called, **Then** a consolidation report is returned.
3. **Given** the SDK, **When** `memory.forget_strategy("strategic_prune", goals=["Python"])` is called, **Then** affected count is returned.

---

### User Story 5 — Publishable Package (Priority: P1)

The SDK is a standalone Python package with its own `pyproject.toml`, publishable to PyPI.

**Acceptance Scenarios**:
1. **Given** the SDK directory, **When** `pip install ./sdk` is run, **Then** `from human_memory import Memory` works.
2. **Given** the SDK, **When** `pip install human-memory` is run from PyPI, **Then** it installs with only `httpx` and `pydantic` as dependencies.

---

### User Story 6 — Comprehensive Tests (Priority: P1)

The SDK has unit tests (mocked HTTP) and integration tests (against running API).

**Acceptance Scenarios**:
1. **Given** no running server, **When** unit tests run, **Then** all pass using mocked responses.
2. **Given** a running server, **When** integration tests run, **Then** all pass against real API.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: SDK MUST provide `Memory` (sync) and `AsyncMemory` (async) classes.
- **FR-002**: SDK MUST wrap all 12 API endpoints with typed methods.
- **FR-003**: SDK MUST use Pydantic models for all return types.
- **FR-004**: SDK MUST have only `httpx` and `pydantic` as dependencies (lightweight).
- **FR-005**: SDK MUST be a standalone package in `sdk/` directory with its own `pyproject.toml`.
- **FR-006**: SDK MUST include comprehensive docstrings and type hints.
- **FR-007**: SDK MUST handle errors gracefully (raise typed exceptions).
- **FR-008**: SDK MUST include unit tests with mocked HTTP.
- **FR-009**: SDK MUST include integration tests against real API.
- **FR-010**: SDK MUST be publishable to PyPI as `human-memory`.

### Key Entities

- **Memory** — sync client class
- **AsyncMemory** — async client class
- **MemoryResult** — search result model
- **MemoryDetail** — full metadata model
- **Stats** — system statistics model
- **Concept** — knowledge graph concept model
- **ConsolidationReport** — consolidation result model

## Success Criteria

- **SC-001**: `from human_memory import Memory; m = Memory(); m.store("test")` works.
- **SC-002**: All sync and async methods return typed Pydantic models.
- **SC-003**: SDK has < 3 dependencies (httpx, pydantic).
- **SC-004**: Unit tests pass without a running server.
- **SC-005**: Integration tests pass against the Docker deployment.

## Assumptions

- SDK lives in `sdk/` directory at project root, separate from the server code.
- Published to PyPI as `human-memory`.
- Minimal dependencies — only `httpx` and `pydantic`.
- Python 3.12+ required (matches server).
