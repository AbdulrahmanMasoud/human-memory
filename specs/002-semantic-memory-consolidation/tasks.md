# Tasks: Semantic Memory + Consolidation Engine

## Phase 1: Neo4j Integration

- [ ] T001 Add neo4j dependency to pyproject.toml, uncomment neo4j in docker-compose.yml
- [ ] T002 Write `src/memory_system/models/graph.py` — Pydantic models: ConceptCreate, ConceptResponse, RelationCreate, GraphSearchResult, ConsolidationReport
- [ ] T003 Write `src/memory_system/stores/neo4j_store.py` — Neo4jStore: create_concept, create_relation, get_concept, spreading_activation_query, search_graph
- [ ] T004 Write `src/memory_system/api/graph.py` — FastAPI router: POST/GET /v1/graph/concepts, POST /v1/graph/relations, POST /v1/graph/search

## Phase 2: Spreading Activation

- [ ] T005 Update `src/memory_system/core/memory_service.py` — Wire S_i into retrieval pipeline using Neo4jStore.spreading_activation_query
- [ ] T006 Update `src/memory_system/main.py` — Initialize Neo4jStore in lifespan, register graph router

## Phase 3: Consolidation Engine

- [ ] T007 Write `src/memory_system/core/clustering.py` — cluster_episodes() using cosine similarity on embeddings
- [ ] T008 Write `src/memory_system/core/consolidation.py` — ConsolidationEngine with 4 phases: replay, extract, prune, compile (no-op)
- [ ] T009 Write `src/memory_system/tasks/consolidation.py` — Celery task for 6-hour consolidation cycle
- [ ] T010 Update `src/memory_system/celery_app.py` — Add consolidation-cycle to beat schedule
- [ ] T011 Update `src/memory_system/api/memories.py` — Add POST /v1/consolidate endpoint

## Phase 4: Verification

- [ ] T012 Docker compose up with Neo4j, verify all services healthy
- [ ] T013 Smoke test: create concepts + relations, verify spreading activation improves retrieval
