# Tasks: Frontend Dashboard + Benchmark Tool

## Phase 1: Backend API Additions

- [ ] T001 Add `get_full_graph(limit=200)` to `src/memory_system/stores/neo4j_store.py`
- [ ] T002 Add `get_all_memories(offset, limit)` to `src/memory_system/stores/postgres_store.py`
- [ ] T003 Write `src/memory_system/api/dashboard.py` — GET /v1/memories, GET /v1/graph/export
- [ ] T004 Write `src/memory_system/api/benchmark.py` — POST /v1/benchmark/run (SSE streaming)
- [ ] T005 Update `src/memory_system/main.py` — register routers, serve dashboard, CORS middleware

## Phase 2: Frontend Dashboard

- [ ] T006 Write `src/memory_system/dashboard.html` — Tab A: Overview (stat cards, auto-refresh)
- [ ] T007 Dashboard Tab B: Knowledge Graph (D3 force-directed, click for details)
- [ ] T008 Dashboard Tab C: Memory Explorer (table, search, inspect panel)
- [ ] T009 Dashboard Tab D: Decay & Controls (decay, consolidation, forgetting buttons)
- [ ] T010 Dashboard Tab E: Benchmark (progress bar, Chart.js latency charts)

## Phase 3: CLI Benchmark

- [ ] T011 Write `scripts/benchmark.py` — standalone CLI benchmark tool

## Phase 4: Verification

- [ ] T012 Docker build + compose up, verify dashboard loads at /
- [ ] T013 Test all 5 tabs work with real data
- [ ] T014 Run benchmark from dashboard, verify live progress and charts
