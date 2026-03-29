# Feature Specification: Frontend Dashboard Upgrade — Vue 3

**Feature Branch**: `006-frontend-vue-upgrade`
**Created**: 2026-03-29
**Status**: Draft

## Why Vue 3

Vue is the better choice over React for this project:
- **Dashboard-native** — built-in reactivity maps perfectly to real-time data
- **Single-File Components** — current dashboard is already template+style+script, so migration is natural
- **Lighter** — 33KB vs React's 45KB+, faster cold loads
- **No JSX** — templates are closer to the existing vanilla HTML
- **Built-in transitions** — smooth animations without extra libraries
- **Composition API** — clean composables for API state management

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Port All 5 Tabs (Priority: P1)

All existing dashboard functionality must work in the new Vue frontend: overview stats, knowledge graph, memory explorer, controls, and benchmark.

**Acceptance Scenarios**:
1. **Given** the Vue dashboard loads at /, **Then** all 5 tabs are present and functional.
2. **Given** the user switches tabs, **Then** content loads without page reload.

---

### User Story 2 — New Visualizations (Priority: P1)

Add new charts and visualizations not in the current dashboard:

- **Activation Decay Curve**: line chart showing how activation decreases over time per memory
- **Memory Type Breakdown**: donut chart showing episodic/semantic/procedural distribution
- **Access Frequency Heatmap**: calendar-style heatmap of memory access patterns (like GitHub contributions)
- **Consolidation Flow**: Sankey/flow diagram showing replay → extract → prune → compile pipeline

**Acceptance Scenarios**:
1. **Given** memories exist, **When** Overview tab loads, **Then** decay curve and type breakdown charts render.
2. **Given** access history exists, **When** Explorer tab loads, **Then** heatmap is visible.

---

### User Story 3 — Real-Time WebSocket Updates (Priority: P2)

Replace the 5-second polling with WebSocket push for live stats updates.

**Acceptance Scenarios**:
1. **Given** the dashboard is open, **When** a memory is stored via API, **Then** stats update within 2 seconds without page refresh.
2. **Given** WebSocket disconnects, **Then** the dashboard falls back to polling gracefully.

---

### User Story 4 — UX Polish (Priority: P2)

- Toast notifications for all operations (decay, consolidation, forgetting)
- Loading skeletons while data fetches
- Error states with retry buttons
- Responsive layout (works on tablet/mobile)
- Dark/light theme toggle (localStorage persisted)
- Keyboard shortcuts (1-5 for tabs, / for search, r for refresh, Esc to close)

---

### User Story 5 — Docker Integration (Priority: P1)

Frontend builds inside Docker multi-stage (node:22-alpine). Build output served by FastAPI via StaticFiles. Single `docker compose up -d` starts everything.

**Acceptance Scenarios**:
1. **Given** `docker compose up -d`, **When** user opens http://localhost:8000/, **Then** the Vue dashboard loads.
2. **Given** no Node.js in runtime image, **Then** Docker image stays Alpine-based and small.

---

### Edge Cases

- What if Neo4j is unavailable? Graph tab shows "Neo4j not connected" with a retry button.
- What if embedding API is down? Search shows an error toast, other tabs work fine.
- What if WebSocket fails? Falls back to 5-second polling automatically.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Frontend MUST be built with Vue 3 + Composition API + TypeScript.
- **FR-002**: Frontend MUST use Vite for build tooling.
- **FR-003**: Frontend MUST use Tailwind CSS for styling.
- **FR-004**: Frontend MUST port all 5 existing tabs with identical functionality.
- **FR-005**: Frontend MUST add 4 new visualizations (decay curve, type breakdown, heatmap, consolidation flow).
- **FR-006**: Frontend MUST support real-time updates via WebSocket with polling fallback.
- **FR-007**: Frontend MUST build in Docker (node:22-alpine stage) and be served by FastAPI StaticFiles.
- **FR-008**: Frontend MUST include toast notifications, loading states, and error handling.
- **FR-009**: Frontend MUST be responsive (desktop + tablet).
- **FR-010**: Frontend MUST support dark/light theme toggle.

## Success Criteria

- **SC-001**: Dashboard loads in under 2 seconds (built assets < 500KB gzipped).
- **SC-002**: All existing e2e tests still pass.
- **SC-003**: All 5 tabs work with real data.
- **SC-004**: New visualizations render with existing API data.
- **SC-005**: Single `docker compose up -d` starts everything, no manual steps.

## Assumptions

- D3.js used for force graph and heatmap; Chart.js (via vue-chartjs) for bar/line/donut charts.
- @vueuse/core for utilities (localStorage, keyboard shortcuts, debounce).
- No Vue Router needed — tab switching via reactive state.
- Old `dashboard.html` removed after migration complete.
