# Feature Specification: Frontend Dashboard + Benchmark Tool

**Feature Branch**: `005-frontend-benchmark`
**Created**: 2026-03-29
**Status**: Draft

## User Scenarios & Testing *(mandatory)*

### User Story 1 - System Overview Dashboard (Priority: P1)

A developer opens http://localhost:8000/ and sees a real-time dashboard showing memory system stats: total/active/decayed/deleted counts and average activation. Stats auto-refresh every 5 seconds.

**Acceptance Scenarios**:
1. **Given** the system is running, **When** the user opens /, **Then** they see stat cards with current memory counts.
2. **Given** memories are being stored, **When** 5 seconds pass, **Then** the stats update automatically.

---

### User Story 2 - Knowledge Graph Visualization (Priority: P1)

The dashboard has a Knowledge Graph tab showing an interactive force-directed graph. Concepts are nodes (sized by activation, colored by type), relationships are edges (labeled, thickness by weight). Clicking a node shows details and spreading activation results.

**Acceptance Scenarios**:
1. **Given** concepts and relations exist in Neo4j, **When** the Graph tab is opened, **Then** a D3 force-directed graph renders with all concepts and relations.
2. **Given** the graph is displayed, **When** a user clicks a node, **Then** a detail panel shows the concept's relationships and spreading activation results.

---

### User Story 3 - Memory Explorer (Priority: P1)

The dashboard has a Memory Explorer tab listing all memories with activation bars, status badges (green/red/gray), and access counts. Users can search memories and click to inspect full metadata.

**Acceptance Scenarios**:
1. **Given** memories exist, **When** the Explorer tab is opened, **Then** all memories are listed with activation bars and status badges.
2. **Given** the explorer is open, **When** the user types a search query, **Then** results update via semantic search.
3. **Given** a memory in the list, **When** clicked, **Then** full metadata and access history are shown.

---

### User Story 4 - Decay & Consolidation Controls (Priority: P2)

The dashboard has controls to trigger decay, consolidation, and forgetting strategies manually. Results display inline.

**Acceptance Scenarios**:
1. **Given** the controls tab, **When** "Run Decay" is clicked, **Then** decay runs and the result (processed/decayed counts) is shown.
2. **Given** the controls tab, **When** "Run Consolidation" is clicked, **Then** the consolidation report is shown.

---

### User Story 5 - Benchmark with Live Progress (Priority: P1)

The dashboard has a Benchmark tab where the user can run a load test storing 10k+ memories. A live progress bar shows progress, and latency charts (p50/p95/p99) update in real-time. The user can watch stats change on the Overview tab while the benchmark runs.

**Acceptance Scenarios**:
1. **Given** the benchmark tab, **When** "Run Benchmark" is clicked with count=10000, **Then** a progress bar fills as memories are stored.
2. **Given** the benchmark is running, **When** each batch completes, **Then** latency charts update with p50/p95/p99.
3. **Given** the benchmark is running, **When** the user switches to Overview, **Then** stats are updating in real-time.
4. **Given** the benchmark completes, **Then** a summary with total time and latency percentiles is shown.

---

### User Story 6 - Standalone Benchmark CLI (Priority: P3)

A standalone Python script can run the benchmark from the command line without the dashboard.

**Acceptance Scenarios**:
1. **Given** the system is running, **When** `python scripts/benchmark.py --count 1000` is run, **Then** it stores memories, runs searches, and prints p50/p95/p99.

---

### Edge Cases

- What if Neo4j is not available? The graph tab shows "Neo4j not connected" message.
- What if the embedding API rate-limits during benchmark? Batches slow down with backoff, progress bar reflects the actual pace.
- What if the graph has 500+ nodes? Limit to 200 nodes with a warning.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST serve a single-page dashboard at GET /.
- **FR-002**: Dashboard MUST show real-time stats with auto-refresh.
- **FR-003**: Dashboard MUST render an interactive D3 force-directed knowledge graph.
- **FR-004**: Dashboard MUST list all memories with status, activation, and search.
- **FR-005**: Dashboard MUST provide manual decay, consolidation, and forgetting controls.
- **FR-006**: System MUST provide a benchmark endpoint that streams progress via SSE.
- **FR-007**: Dashboard MUST show live progress bar and latency charts during benchmark.
- **FR-008**: System MUST provide a GET endpoint to export full graph data for D3.
- **FR-009**: System MUST provide a GET endpoint to list all memories (paginated, all statuses).
- **FR-010**: System MUST include a standalone CLI benchmark script.

### Key Entities

- **Dashboard**: Single HTML file with inline CSS/JS, served by FastAPI.
- **Graph Export**: Bulk export of all concepts and relationships for visualization.
- **Benchmark Run**: A streaming process that stores N memories and measures latency.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Dashboard loads and shows stats within 2 seconds of opening.
- **SC-002**: Knowledge graph renders with all existing concepts and relationships.
- **SC-003**: Benchmark can store 10,000 memories and report latency percentiles.
- **SC-004**: Live progress bar updates during benchmark run.
- **SC-005**: Memory explorer search returns results within 1 second.

## Assumptions

- Single HTML file with CDN dependencies (D3.js, Chart.js) — no build tools.
- Dark theme matching the existing system-overview.html style.
- No new Python dependencies needed.
- Benchmark uses existing embedding API (may be rate-limited by OpenAI).
