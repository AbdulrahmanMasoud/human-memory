# Implementation Plan: Frontend Dashboard + Benchmark Tool

**Branch**: `005-frontend-benchmark` | **Date**: 2026-03-29 | **Spec**: [spec.md](./spec.md)

## Summary

Add a single-file frontend dashboard served by FastAPI at GET / with 5 tabs (overview, graph, explorer, controls, benchmark), plus a streaming benchmark endpoint and a CLI benchmark script. No new Python dependencies.

## Technical Context

**Frontend**: Single HTML file with inline CSS/JS, D3.js + Chart.js from CDN
**Backend additions**: 3 new endpoints, 2 new store methods
**Streaming**: FastAPI `StreamingResponse` for SSE benchmark progress
**Theme**: Dark (#0f172a), matching existing system-overview.html

## New Files
- `src/memory_system/api/dashboard.py` — GET /v1/memories (list), GET /v1/graph/export
- `src/memory_system/api/benchmark.py` — POST /v1/benchmark/run (SSE)
- `src/memory_system/dashboard.html` — single-file frontend
- `scripts/benchmark.py` — CLI benchmark tool

## Modified Files
- `src/memory_system/stores/neo4j_store.py` — add `get_full_graph(limit=200)`
- `src/memory_system/stores/postgres_store.py` — add `get_all_memories(offset, limit)`
- `src/memory_system/main.py` — register routers, serve dashboard, add CORS

## API Additions

| Method | Path | Description |
|--------|------|-------------|
| GET | / | Serve dashboard.html |
| GET | /v1/memories | List all memories (paginated, all statuses) |
| GET | /v1/graph/export | Full graph data for D3 {nodes, edges} |
| POST | /v1/benchmark/run | SSE stream of benchmark progress |

## Dashboard Tabs

1. **Overview**: 4 stat cards + avg activation, auto-refresh 5s
2. **Knowledge Graph**: D3 force graph, click for details + spreading activation
3. **Memory Explorer**: Table with activation bars, search, click to inspect
4. **Controls**: Decay/consolidation/forgetting buttons with inline results
5. **Benchmark**: Count input, progress bar, Chart.js latency charts (p50/p95/p99)

## Benchmark SSE Events

```json
{"phase":"store","progress":0.15,"batch_p50":45.2,"batch_p95":89.1,"total_stored":150}
{"phase":"retrieve","progress":0.5,"batch_p50":32.1,"batch_p95":78.4,"total_searched":50}
{"phase":"complete","store":{"p50":44,"p95":88,"p99":120,"total_ms":45000},"retrieve":{"p50":31,"p95":76,"p99":105,"total_ms":3200},"total_memories":1000}
```
