# Implementation Plan: Frontend Dashboard Upgrade — Vue 3

**Branch**: `006-frontend-vue-upgrade` | **Date**: 2026-03-29 | **Spec**: [spec.md](./spec.md)

## Summary

Replace the 540-line single HTML dashboard with a Vue 3 + TypeScript + Tailwind CSS + Vite frontend. Add 4 new visualizations, WebSocket real-time updates, and full UX polish. Built in Docker, served by FastAPI.

## Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Vue 3 | ^3.5 | UI framework (Composition API) |
| TypeScript | ^5.7 | Type safety |
| Vite | ^6 | Build + dev server |
| Tailwind CSS | ^4 | Styling |
| Chart.js + vue-chartjs | ^4 / ^5 | Bar, line, donut charts |
| D3.js | ^7 | Force graph, heatmap |
| @vueuse/core | latest | Utilities (localStorage, keyboard, debounce) |

## Project Structure

```
frontend/
  index.html
  package.json
  vite.config.ts
  tsconfig.json
  tailwind.config.ts
  postcss.config.js
  src/
    main.ts
    App.vue
    api/
      client.ts              # fetch wrapper
      types.ts               # TS interfaces matching Pydantic models
      stats.ts               # GET /v1/stats, /ready
      memories.ts            # /v1/memories/*, search, decay
      graph.ts               # /v1/graph/*
      benchmark.ts           # /v1/benchmark/run (SSE)
    composables/
      useStats.ts            # Auto-refresh stats (WebSocket → polling fallback)
      useMemories.ts         # Pagination, search, inspect
      useGraph.ts            # Graph data + spreading activation
      useBenchmark.ts        # SSE stream + progress
      useToast.ts            # Notification queue
      useTheme.ts            # Dark/light toggle
    components/
      layout/
        AppNav.vue           # Tab navigation
        AppToast.vue         # Toast notifications
      shared/
        StatCard.vue
        Badge.vue
        ActivationBar.vue
        LoadingSpinner.vue
        ProgressBar.vue
      overview/
        OverviewPanel.vue
        ActivationDecayCurve.vue    # NEW: line chart
        MemoryTypeBreakdown.vue     # NEW: donut chart
      graph/
        GraphPanel.vue
        ForceGraph.vue              # D3 force-directed
        GraphDetailSidebar.vue
        ConsolidationFlow.vue       # NEW: Sankey flow
      explorer/
        ExplorerPanel.vue
        MemoryTable.vue
        MemoryDetailDrawer.vue
        AccessHeatmap.vue           # NEW: calendar heatmap
      controls/
        ControlsPanel.vue
        DecayCard.vue
        ConsolidationCard.vue
        ForgettingCard.vue
      benchmark/
        BenchmarkPanel.vue
        BenchmarkForm.vue
        LatencyChart.vue
        BenchmarkResults.vue
    assets/
      main.css               # Tailwind directives + theme
```

## Backend Changes

### 1. WebSocket endpoint (main.py)
```python
@app.websocket("/ws/stats")
async def ws_stats(websocket: WebSocket):
    await websocket.accept()
    while True:
        stats = await memory_service.stats()
        await websocket.send_json(stats.model_dump())
        await asyncio.sleep(2)
```

### 2. Replace FileResponse with StaticFiles (main.py)
```python
from fastapi.staticfiles import StaticFiles
FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
```

### 3. Dockerfile — add frontend build stage
```dockerfile
FROM node:22-alpine AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# ... existing builder + runtime stages ...
COPY --from=frontend /frontend/dist /app/frontend/dist
```

## Vite Config

```typescript
export default defineConfig({
  plugins: [vue(), tailwindcss()],
  server: {
    proxy: {
      '/v1': 'http://localhost:8000',
      '/ws': { target: 'ws://localhost:8000', ws: true },
      '/health': 'http://localhost:8000',
      '/ready': 'http://localhost:8000',
    }
  }
})
```

## New Visualizations Detail

1. **Activation Decay Curve** — Chart.js line chart, plots `B_i = ln(Σ t_j^(-d))` curve using memory's `decay_rate` and `access_count`
2. **Memory Type Breakdown** — Chart.js doughnut, aggregates from `/v1/memories` list
3. **Access Heatmap** — D3 rect grid (calendar view), aggregates from access_history timestamps
4. **Consolidation Flow** — D3 Sankey showing episodes → replayed → extracted → pruned → compiled
