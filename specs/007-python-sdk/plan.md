# Implementation Plan: Python SDK — `human-memory`

**Branch**: `007-python-sdk` | **Date**: 2026-03-29 | **Spec**: [spec.md](./spec.md)

## Summary

Create a lightweight Python SDK (`pip install human-memory`) that wraps the memory system API. Provides `Memory` (sync) and `AsyncMemory` (async) classes with typed methods for all 12 endpoints. Only depends on `httpx` and `pydantic`.

## Project Structure

```
sdk/
  pyproject.toml
  README.md
  src/
    human_memory/
      __init__.py          # Exports Memory, AsyncMemory
      client.py            # Memory (sync) class
      async_client.py      # AsyncMemory (async) class
      models.py            # Pydantic models (mirrors server models)
      exceptions.py        # MemoryNotFound, ServiceUnavailable, etc.
  tests/
    __init__.py
    test_client.py         # Unit tests with mocked HTTP
    test_async_client.py   # Async unit tests with mocked HTTP
    test_integration.py    # Integration tests against real API
```

## SDK API Design

### Memory (sync)

```python
class Memory:
    def __init__(self, base_url: str = "http://localhost:8000") -> None

    # Core
    def store(self, content: str, memory_type: str = "episodic", context: str | None = None) -> MemoryCreated
    def search(self, query: str, top_k: int = 7, min_activation: float | None = None) -> list[SearchResult]
    def recall(self, memory_id: str) -> MemoryInfo
    def forget(self, memory_id: str) -> bool
    def inspect(self, memory_id: str) -> MemoryDetail
    def list(self, offset: int = 0, limit: int = 50) -> list[MemoryItem]

    # Knowledge Graph
    def add_concept(self, name: str, type: str = "concept", activation: float = 0.8) -> Concept
    def get_concept(self, name: str) -> Concept
    def add_relation(self, source: str, target: str, relation_type: str, weight: float = 1.0) -> Relation
    def spread(self, concepts: list[str], depth: int = 2, limit: int = 10) -> list[SpreadResult]

    # Operations
    def decay(self) -> DecayReport
    def consolidate(self) -> ConsolidationReport
    def forget_strategy(self, strategy: str, **params) -> ForgetReport
    def stats(self) -> Stats
    def ready(self) -> dict[str, str]

    # Cleanup
    def close(self) -> None
```

### AsyncMemory (async)

Same methods but all `async def` and uses `httpx.AsyncClient`.

## Pydantic Models (sdk/src/human_memory/models.py)

```python
class MemoryCreated(BaseModel):
    memory_id: str
    activation: float
    created_at: str

class SearchResult(BaseModel):
    memory_id: str
    content: str
    activation: float
    similarity: float
    last_accessed: str
    access_count: int

class MemoryInfo(BaseModel):
    memory_id: str
    content: str
    activation: float
    memory_type: str
    created_at: str
    last_accessed: str
    access_count: int

class MemoryDetail(BaseModel):
    # ... all fields including emotion, salience, access_history

class MemoryItem(BaseModel):
    # ... list item fields

class Stats(BaseModel):
    total: int
    active: int
    decayed: int
    deleted: int
    avg_activation: float

class Concept(BaseModel):
    name: str
    type: str
    activation: float
    relationships: list[Relation] = []

class Relation(BaseModel):
    source: str
    target: str
    relation_type: str
    weight: float

class SpreadResult(BaseModel):
    name: str
    activation: float
    path_weight: float

class DecayReport(BaseModel):
    memories_processed: int
    memories_decayed: int

class ConsolidationReport(BaseModel):
    episodes_replayed: int
    facts_extracted: int
    memories_pruned: int
    memories_downscaled: int

class ForgetReport(BaseModel):
    strategy: str
    memories_affected: int
```

## Exceptions

```python
class HumanMemoryError(Exception): ...
class MemoryNotFound(HumanMemoryError): ...     # 404
class ServiceUnavailable(HumanMemoryError): ...  # 503
class ValidationError(HumanMemoryError): ...     # 422
```

## pyproject.toml

```toml
[project]
name = "human-memory"
version = "0.1.0"
description = "Python SDK for the Human-Like Memory System"
requires-python = ">=3.12"
dependencies = ["httpx>=0.28.0", "pydantic>=2.10.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-asyncio>=0.25", "pytest-httpx>=0.30", "ruff>=0.9"]
```

## Context Manager Support

```python
# Sync
with Memory("http://localhost:8000") as memory:
    memory.store("hello")

# Async
async with AsyncMemory("http://localhost:8000") as memory:
    await memory.store("hello")
```
