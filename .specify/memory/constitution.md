<!--
  Sync Impact Report
  Version change: 0.0.0 → 1.0.0 (initial ratification)
  Added principles:
    - I. ACT-R Mathematical Fidelity
    - II. Test-Driven Development (NON-NEGOTIABLE)
    - III. Tech Stack Lock
    - IV. Alpine Docker
    - V. Performance Contracts
    - VI. Incremental Delivery
    - VII. Separation of Concerns
    - VIII. Type Safety
  Added sections:
    - Technology Stack
    - Development Workflow
    - Governance
  Templates requiring updates:
    - .specify/templates/plan-template.md ✅ (no changes needed, Constitution Check section exists)
    - .specify/templates/spec-template.md ✅ (no changes needed, priority structure compatible)
    - .specify/templates/tasks-template.md ✅ (no changes needed)
  Follow-up TODOs: None
-->

# Human-Like Memory System Constitution

## Core Principles

### I. ACT-R Mathematical Fidelity (NON-NEGOTIABLE)

The ACT-R cognitive architecture equations are the mathematical foundation of this system. All memory retrieval MUST flow through these equations:

- **Total Activation**: `A_i = B_i + S_i + P_i + ε`
- **Base-Level Activation**: `B_i = ln(Σ t_j^(-d))` where d = 0.5 (decay rate)
- **Spreading Activation**: `S_i = Σ W_k × S_ki`
- **Retrieval Threshold**: Memories MUST only be retrieved when `A_i > τ`

No shortcut, heuristic, or approximation may replace these equations in the retrieval pipeline. Cosine similarity is a pre-filter only — final ranking MUST use ACT-R activation.

### II. Test-Driven Development (NON-NEGOTIABLE)

TDD is mandatory for every component:

- Tests MUST be written before implementation (Red-Green-Refactor)
- Unit tests for all core math (ACT-R equations, forgetting, salience)
- Integration tests for all store adapters (Qdrant, PostgreSQL, Neo4j)
- End-to-end tests for all API endpoints via `httpx.AsyncClient`
- No code merges without passing test suite

### III. Tech Stack Lock

The following stack is fixed. Substitutions require a constitution amendment:

- **Language**: Python 3.12+
- **Web Framework**: FastAPI with async
- **Vector DB**: Qdrant
- **Graph DB**: Neo4j (V2+)
- **Relational DB**: PostgreSQL with asyncpg
- **Cache/Broker**: Redis
- **Task Queue**: Celery with Redis broker
- **Embeddings**: ONNX Runtime with sentence-transformers models
- **Migrations**: Alembic

### IV. Alpine Docker (NON-NEGOTIABLE)

All custom Docker images MUST use `python:3.13-alpine` as the base image. Third-party service images MUST use Alpine variants where available:

- `postgres:17-alpine`
- `redis:7-alpine`
- `qdrant/qdrant:latest` (Alpine-based)
- `neo4j:5-community` (exception: no Alpine variant exists due to JVM)

ONNX Runtime MUST be used instead of PyTorch for model inference to maintain Alpine/musl compatibility.

### V. Performance Contracts

All components MUST meet these latency targets:

- **Retrieval**: < 100ms at p95
- **Storage**: < 50ms at p95
- **Consolidation**: Background-only, zero impact on retrieval latency
- **Decay updates**: Batch processing, MUST NOT block API requests

Embedding and emotion models MUST be loaded once at application startup, not per-request.

### VI. Incremental Delivery

The system is delivered in four independently deployable versions:

- **V1**: Episodic Memory + ACT-R Temporal Decay (MVP)
- **V2**: + Semantic Memory + Consolidation Engine
- **V3**: + Emotional Salience + Working Memory
- **V4**: + Procedural Memory + Strategic Forgetting

Each version MUST be a complete, working, deployable system. No version may depend on features planned for a future version.

### VII. Separation of Concerns

Architecture MUST follow strict layer separation:

- **Core** (`core/`): Pure Python with no framework dependencies. Contains ACT-R math, forgetting logic, consolidation, emotion scoring. MUST be independently testable without any infrastructure.
- **Stores** (`stores/`): Thin adapter wrappers around databases. One store per database. No business logic.
- **API** (`api/`): FastAPI routers for HTTP routing and serialization only. No business logic. Delegates to core services.
- **Tasks** (`tasks/`): Celery task definitions. Thin wrappers calling core logic.

### VIII. Type Safety

- All public interfaces MUST use Pydantic models for request/response validation
- All function signatures MUST include type hints
- `mypy --strict` MUST pass on the entire codebase
- No use of `Any` type without explicit justification

## Technology Stack

| Component | Technology | Version | Docker Image |
|-----------|-----------|---------|-------------|
| Application | Python + FastAPI | 3.12+ | `python:3.13-alpine` |
| Vector Search | Qdrant | latest | `qdrant/qdrant:latest` |
| Metadata Store | PostgreSQL | 17 | `postgres:17-alpine` |
| Graph Database | Neo4j | 5 | `neo4j:5-community` |
| Cache & Broker | Redis | 7 | `redis:7-alpine` |
| Task Queue | Celery | 5.4+ | (same as app image) |
| Embeddings | ONNX Runtime | 1.21+ | (same as app image) |
| Migrations | Alembic | 1.15+ | (same as app image) |

## Development Workflow

1. **Spec-Driven Development**: All features MUST go through the spec-kit workflow:
   `/speckit.specify` → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`

2. **Branch Strategy**: One feature branch per spec (e.g., `001-episodic-memory-mvp`)

3. **Quality Gates**:
   - All tests pass (`pytest`)
   - Type checks pass (`mypy --strict`)
   - Linting passes (`ruff check`)
   - Docker build succeeds
   - API health check responds 200

4. **Commit Messages**: Conventional commits format (`feat:`, `fix:`, `test:`, `docs:`, `refactor:`)

## Governance

- This constitution supersedes all other development practices in this project
- Amendments require:
  1. Written justification documenting the reason for change
  2. Version bump following semantic versioning (MAJOR for principle removal/redefinition, MINOR for additions, PATCH for clarifications)
  3. Update to all dependent templates and artifacts
- All code reviews MUST verify compliance with these principles
- Complexity MUST be justified — prefer simple, correct implementations over clever ones

**Version**: 1.0.0 | **Ratified**: 2026-03-28 | **Last Amended**: 2026-03-28
