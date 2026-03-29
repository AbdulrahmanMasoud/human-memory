# Feature Specification: Semantic Memory + Consolidation Engine

**Feature Branch**: `002-semantic-memory-consolidation`
**Created**: 2026-03-28
**Status**: Draft

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Store Semantic Facts in Knowledge Graph (Priority: P1)

The system stores general knowledge as concepts and relationships in a graph database. An AI agent or the consolidation engine can add facts like "Python is a programming language" or "User prefers dark mode" as typed graph relationships.

**Why this priority**: The knowledge graph is the foundation for semantic memory — without it, there is no semantic store.

**Independent Test**: Add concepts and relationships via API, query them back, verify graph structure.

**Acceptance Scenarios**:

1. **Given** the system is running, **When** a concept is created with name and type, **Then** it is stored in the graph with default activation and is queryable.
2. **Given** existing concepts, **When** a typed relationship is created between them, **Then** the relationship is stored with a weight and is traversable.
3. **Given** a concept exists, **When** queried by name, **Then** the system returns the concept with all its relationships.

---

### User Story 2 - Spreading Activation Retrieval (Priority: P1)

When retrieving memories, the system now computes spreading activation (S_i) from the knowledge graph. Concepts currently in the working context "spread" activation to related concepts, boosting memories associated with those concepts.

**Why this priority**: This makes the ACT-R equation complete (S_i was returning 0 in V1). Retrieval becomes context-aware.

**Independent Test**: Create a graph with connected concepts, set some as active context, verify that memories related to connected concepts get higher activation than unconnected ones.

**Acceptance Scenarios**:

1. **Given** concepts A→B→C in the graph with weighted relationships, **When** A is in the active context and retrieval is performed, **Then** memories tagged with B get a spreading activation boost proportional to the A→B weight.
2. **Given** multiple active context concepts, **When** retrieval runs, **Then** spreading activation is distributed with equal attention weight (W = 1/N) across context sources.

---

### User Story 3 - Consolidation Cycle (Priority: P2)

A periodic background process (every 6 hours) runs a 4-phase consolidation cycle inspired by sleep consolidation: replay high-salience memories, extract semantic knowledge from episode clusters, prune by global downscaling, and compile (placeholder for V4).

**Why this priority**: Consolidation transforms raw episodic memories into structured semantic knowledge and manages memory lifecycle.

**Independent Test**: Store 20+ related episodic memories, trigger consolidation manually, verify semantic facts are extracted into the graph and low-activation memories are pruned.

**Acceptance Scenarios**:

1. **Given** recent high-salience episodic memories, **When** consolidation Phase 1 (Replay) runs, **Then** their activation is boosted by a configurable replay factor.
2. **Given** a cluster of 3+ similar episodic memories, **When** consolidation Phase 2 (Extract) runs, **Then** the system uses an LLM to extract general facts and stores them as graph nodes linked to source episodes.
3. **Given** all active memories, **When** consolidation Phase 3 (Prune) runs, **Then** every memory's activation is scaled down by a configurable factor (e.g., 0.9) and memories below threshold are archived.
4. **Given** the decay and consolidation tasks, **When** both are scheduled, **Then** they do not interfere with each other or block retrieval.

---

### User Story 4 - LLM-Based Knowledge Extraction (Priority: P2)

During consolidation, clusters of similar episodic memories are analyzed by an LLM to extract general facts, patterns, and user preferences. These become semantic memory nodes in the knowledge graph.

**Why this priority**: This is the bridge between episodic and semantic memory — the system learns general knowledge from specific experiences.

**Independent Test**: Provide a cluster of related episodes to the extraction endpoint, verify JSON facts are returned with confidence scores.

**Acceptance Scenarios**:

1. **Given** 5 episodic memories about the same topic, **When** the extraction process runs, **Then** it returns general facts with confidence scores as JSON.
2. **Given** extracted facts, **When** they are stored in the graph, **Then** each fact node is linked to its source episodes via EXTRACTED_FROM relationships.

---

### Edge Cases

- What happens when Neo4j is unavailable? The system falls back to V1 behavior (S_i = 0) and logs a warning.
- What happens when the LLM API is unavailable during consolidation? The extract phase is skipped with a warning; other phases proceed.
- What happens when no episode clusters are found? Phase 2 completes with zero extractions.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST store concepts and typed relationships in a graph database.
- **FR-002**: System MUST compute spreading activation S_i = Σ W_k × S_ki using graph relationships during retrieval.
- **FR-003**: System MUST run a 4-phase consolidation cycle: replay, extract, prune, compile (placeholder).
- **FR-004**: System MUST schedule consolidation every 6 hours via background task.
- **FR-005**: System MUST support manual triggering of consolidation.
- **FR-006**: System MUST cluster similar episodic memories using embedding similarity.
- **FR-007**: System MUST use an LLM to extract semantic facts from episode clusters.
- **FR-008**: System MUST link extracted facts to source episodes in the graph.
- **FR-009**: System MUST apply global activation downscaling during prune phase.
- **FR-010**: System MUST expose graph search API for concept traversal.

### Key Entities

- **Concept**: A node in the knowledge graph with name, type, and activation level.
- **Relationship**: A typed, weighted edge between concepts (IS_A, USED_FOR, WORKS_WITH, EXTRACTED_FROM, etc.).
- **ConsolidationReport**: Summary of a consolidation cycle (episodes replayed, facts extracted, memories pruned).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Spreading activation measurably improves retrieval relevance compared to V1 (base-level only).
- **SC-002**: Consolidation extracts at least 1 semantic fact per cluster of 3+ related episodes.
- **SC-003**: After prune phase, average activation across all memories is reduced by the configured factor.
- **SC-004**: Consolidation completes without impacting concurrent retrieval latency.

## Assumptions

- Neo4j is available as a Docker service (neo4j:5-community, non-Alpine exception).
- LLM API is OpenAI-compatible (same pattern as embedding API).
- Episode clustering uses cosine similarity on existing embeddings stored in Qdrant.
- Consolidation Phase 4 (Compile) is a no-op placeholder — procedural compilation is V4.
