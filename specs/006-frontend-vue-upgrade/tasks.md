# Tasks: Frontend Dashboard Upgrade — Vue 3

## Phase 1: Scaffolding

- [ ] T001 Create `frontend/` with Vite + Vue 3 + TypeScript + Tailwind CSS
- [ ] T002 Configure `vite.config.ts` with API proxy to localhost:8000
- [ ] T003 Set up Tailwind with dark theme (matching current palette)

## Phase 2: API Layer

- [ ] T004 Write `frontend/src/api/types.ts` — TypeScript interfaces for all Pydantic models
- [ ] T005 Write `frontend/src/api/client.ts` — fetch wrapper with base URL
- [ ] T006 Write API modules: `stats.ts`, `memories.ts`, `graph.ts`, `benchmark.ts`

## Phase 3: Composables

- [ ] T007 Write `useStats.ts` — reactive stats with auto-refresh (polling → WebSocket)
- [ ] T008 Write `useMemories.ts` — pagination, search, inspect state
- [ ] T009 Write `useGraph.ts` — graph data loading + spreading activation
- [ ] T010 Write `useBenchmark.ts` — SSE stream handling + progress state
- [ ] T011 Write `useToast.ts` — toast notification queue
- [ ] T012 Write `useTheme.ts` — dark/light toggle with localStorage

## Phase 4: Port Existing Tabs

- [ ] T013 Build `AppNav.vue` — tab navigation with keyboard shortcuts (1-5)
- [ ] T014 Build `OverviewPanel.vue` — stat cards + readiness checks
- [ ] T015 Build `GraphPanel.vue` + `ForceGraph.vue` — D3 force-directed graph
- [ ] T016 Build `ExplorerPanel.vue` + `MemoryTable.vue` + `MemoryDetailDrawer.vue`
- [ ] T017 Build `ControlsPanel.vue` — decay, consolidation, forgetting cards
- [ ] T018 Build `BenchmarkPanel.vue` — form, progress bar, latency charts
- [ ] T019 Build `App.vue` + `main.ts` — wire everything together

## Phase 5: New Visualizations

- [ ] T020 Build `ActivationDecayCurve.vue` — line chart (Chart.js)
- [ ] T021 Build `MemoryTypeBreakdown.vue` — donut chart (Chart.js)
- [ ] T022 Build `AccessHeatmap.vue` — calendar heatmap (D3)
- [ ] T023 Build `ConsolidationFlow.vue` — Sankey flow diagram (D3)

## Phase 6: UX Enhancements

- [ ] T024 Build `AppToast.vue` — toast notifications with transitions
- [ ] T025 Add loading skeletons and error states to all panels
- [ ] T026 Add responsive breakpoints (tablet + mobile)
- [ ] T027 Add keyboard shortcuts (/, r, Esc)

## Phase 7: WebSocket + Backend

- [ ] T028 Add WebSocket `/ws/stats` endpoint to `main.py`
- [ ] T029 Update `useStats.ts` — WebSocket with polling fallback

## Phase 8: Docker Integration

- [ ] T030 Update `Dockerfile` — add node:22-alpine build stage
- [ ] T031 Update `main.py` — replace FileResponse with StaticFiles mount
- [ ] T032 Remove old `dashboard.html`

## Phase 9: Verification

- [ ] T033 Docker build + compose up — verify dashboard loads at /
- [ ] T034 Test all 5 tabs with real data
- [ ] T035 Test new visualizations render correctly
- [ ] T036 Test WebSocket real-time updates
- [ ] T037 Run existing test suites (unit + e2e + memory logic)
