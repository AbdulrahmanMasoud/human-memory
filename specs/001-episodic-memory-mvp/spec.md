# Feature Specification: Episodic Memory Store with ACT-R Temporal Decay

**Feature Branch**: `001-episodic-memory-mvp`
**Created**: 2026-03-28
**Status**: Draft
**Input**: User description: "Episodic Memory Store with ACT-R Temporal Decay - MVP"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Store an Episodic Memory (Priority: P1)

An AI agent processes a user interaction and needs to persist it as an episodic memory for future recall. The agent sends the text content of the interaction, and the system stores it with a semantic embedding, metadata (timestamps, initial activation level), and a unique identifier.

**Why this priority**: Without the ability to store memories, no other feature can function. This is the foundational capability.

**Independent Test**: Can be fully tested by sending content to the store endpoint and verifying the memory is persisted with correct metadata, embedding, and a retrievable ID.

**Acceptance Scenarios**:

1. **Given** the system is running, **When** the agent sends text content to the store endpoint, **Then** the system returns a unique memory ID, stores a semantic embedding alongside the content, and initializes metadata with creation timestamp, default activation level (1.0), and access count of 1.
2. **Given** the system is running, **When** the agent sends empty content, **Then** the system rejects the request with a validation error.
3. **Given** the system is running, **When** the agent stores a memory with optional metadata (memory type, context), **Then** the additional metadata is persisted alongside the memory.

---

### User Story 2 - Retrieve Memories by Semantic Query (Priority: P1)

An AI agent needs to find relevant past memories given a natural language query. The system retrieves candidates by semantic similarity, then ranks them using the ACT-R activation equation — factoring in recency, frequency of access, and context relevance — not just embedding distance.

**Why this priority**: Retrieval is the primary value proposition. The system must return contextually relevant memories ranked by cognitive plausibility (ACT-R activation), not just cosine similarity.

**Independent Test**: Store several memories with varying ages and access counts, then query. Verify that results are ordered by ACT-R activation (a recently and frequently accessed memory ranks higher than an older, less-accessed one with similar semantic similarity).

**Acceptance Scenarios**:

1. **Given** 10 stored memories spanning different topics and ages, **When** the agent queries with a topic-related phrase, **Then** the system returns semantically relevant memories ordered by ACT-R activation (not purely by embedding distance).
2. **Given** two memories with identical semantic similarity to the query but different access histories, **When** the agent queries, **Then** the more recently and frequently accessed memory ranks higher.
3. **Given** a query with no semantically relevant memories above the retrieval threshold, **When** the agent queries, **Then** the system returns an empty list (retrieval failure, not an error).
4. **Given** a query, **When** the system returns results, **Then** each result includes the memory content, activation score, last accessed timestamp, and access count.

---

### User Story 3 - Temporal Decay Reduces Activation Over Time (Priority: P2)

Memories that are not accessed should gradually lose activation, following the ACT-R power-law decay curve. A background process periodically recalculates activation levels for all active memories. Memories whose activation drops below a threshold become inaccessible (decayed).

**Why this priority**: Decay is what makes this system cognitively plausible rather than a simple vector database. Without it, old irrelevant memories would clutter retrieval indefinitely.

**Independent Test**: Store a memory, wait for a decay cycle, and verify its activation has decreased according to the power-law formula. Store another memory and access it multiple times — verify it decays more slowly due to higher base-level activation.

**Acceptance Scenarios**:

1. **Given** a memory stored 24 hours ago with no subsequent access, **When** the decay process runs, **Then** the memory's activation is recalculated using the base-level activation equation and is lower than its initial activation.
2. **Given** a memory accessed 10 times in the last hour, **When** the decay process runs, **Then** its activation remains high because frequent recent access produces a large summation in the base-level equation.
3. **Given** a memory whose recalculated activation falls below the retrieval threshold, **When** the decay process runs, **Then** the memory is marked as "decayed" and excluded from future retrieval queries.
4. **Given** the decay process is running, **When** a retrieval query arrives simultaneously, **Then** the retrieval is not blocked or delayed by the decay computation.

---

### User Story 4 - Access Tracking Strengthens Memory (Priority: P2)

Every time a memory is retrieved (via search or direct recall), the system records the access event. This access history directly feeds the ACT-R activation equation — memories that are retrieved more often maintain higher activation and resist decay.

**Why this priority**: This creates the positive feedback loop central to ACT-R — useful memories get stronger, unused ones fade. Without this, the decay process would uniformly weaken all memories.

**Independent Test**: Retrieve the same memory multiple times, then check that its activation is higher than an equally old but never-retrieved memory.

**Acceptance Scenarios**:

1. **Given** a stored memory, **When** the agent retrieves it via search or recall, **Then** the system records the current timestamp in the access history, increments the access count, and updates the last-accessed timestamp.
2. **Given** two memories stored at the same time, one retrieved 5 times and one never retrieved, **When** activation is recalculated, **Then** the frequently retrieved memory has significantly higher activation.

---

### User Story 5 - Direct Recall by ID (Priority: P3)

An AI agent already knows the ID of a specific memory (e.g., from a previous retrieval) and wants to access it directly. This also counts as an access event, strengthening the memory.

**Why this priority**: Complements search-based retrieval for cases where the agent has a specific memory reference.

**Independent Test**: Store a memory, note its ID, recall it by ID, and verify the full content and metadata are returned and an access event is recorded.

**Acceptance Scenarios**:

1. **Given** a stored memory with a known ID, **When** the agent requests recall by that ID, **Then** the system returns the full memory content, metadata, and activation score, and records an access event.
2. **Given** a non-existent memory ID, **When** the agent requests recall, **Then** the system returns a not-found error.
3. **Given** a decayed memory ID, **When** the agent requests recall, **Then** the system returns a not-found error (decayed memories are inaccessible).

---

### User Story 6 - System Inspection and Statistics (Priority: P3)

A system operator or the agent itself needs visibility into the memory system's state — total memory count, active vs. decayed counts, average activation levels, and the ability to inspect a specific memory's full metadata.

**Why this priority**: Observability is essential for debugging and monitoring, but not core functionality.

**Independent Test**: Store several memories, let some decay, then call the stats endpoint and verify counts match. Inspect a specific memory and verify all metadata fields are present.

**Acceptance Scenarios**:

1. **Given** 20 stored memories (15 active, 5 decayed), **When** the operator requests system stats, **Then** the system returns total count (20), active count (15), decayed count (5), and average activation of active memories.
2. **Given** a stored memory, **When** the operator requests inspection by ID, **Then** the system returns all metadata: content, creation time, last accessed time, access count, full access history, activation score, salience, emotion scores, decay rate, and status.

---

### Edge Cases

- What happens when the vector database is unavailable during a store operation? The system returns a service-unavailable error without partial writes.
- What happens when a memory has thousands of access history entries? The activation calculation caps at the most recent 1000 entries to bound computation time.
- What happens when two decay cycles overlap? The system uses locking to prevent concurrent decay runs on the same memory.
- What happens when a memory is retrieved during a decay update? Retrieval reads the current activation value; the next decay cycle will incorporate the new access.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST store text content as episodic memories with semantic embeddings (384 dimensions) and structured metadata.
- **FR-002**: System MUST retrieve memories using semantic similarity as a pre-filter, then rank by ACT-R activation score: `A_i = B_i + S_i + P_i + ε`.
- **FR-003**: System MUST compute base-level activation using the ACT-R equation: `B_i = ln(Σ t_j^(-d))` where d=0.5 and t_j is time since each access.
- **FR-004**: System MUST run a periodic background decay process (every 30 minutes) that recalculates activation for all active memories.
- **FR-005**: System MUST mark memories as "decayed" when activation falls below the retrieval threshold (τ = -1.0).
- **FR-006**: System MUST record every retrieval as an access event (timestamp + context) that strengthens the memory's future activation.
- **FR-007**: System MUST support direct recall by memory ID, which also counts as an access event.
- **FR-008**: System MUST support soft deletion (forget) of individual memories.
- **FR-009**: System MUST provide system-wide statistics (counts by status, average activation).
- **FR-010**: System MUST provide detailed inspection of individual memory metadata.
- **FR-011**: System MUST cap access history to 1000 most recent entries per memory to bound activation computation.
- **FR-012**: System MUST support manual triggering of the decay process for testing and operational use.

### Key Entities

- **Memory**: The core entity — text content with a semantic embedding, metadata (timestamps, activation, salience, emotion scores), and a unique ID. Has a status lifecycle: active → decayed.
- **Access Record**: A timestamped log entry recording when and in what context a memory was retrieved. Linked to a memory by ID.
- **Memory Statistics**: An aggregate view of system state — total/active/decayed counts, average activation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Memories can be stored and are immediately retrievable within 50ms.
- **SC-002**: Retrieval returns results within 100ms, ordered by ACT-R activation (not just semantic similarity).
- **SC-003**: After 24 hours without access, a single-access memory's activation is measurably lower than at creation time.
- **SC-004**: A memory accessed 10 times in the last hour has higher activation than a memory accessed once 24 hours ago, given similar semantic relevance.
- **SC-005**: Memories below the retrieval threshold are excluded from search results with 100% consistency.
- **SC-006**: The decay background process completes without impacting concurrent retrieval latency.
- **SC-007**: System correctly reports memory counts and status breakdowns via the statistics endpoint.

## Assumptions

- The system operates as a backend service consumed by AI agents via HTTP API, not directly by end users.
- Embedding model is loaded once at startup; model download/management is handled outside the runtime (pre-downloaded in Docker image or volume mount).
- V1 does not include spreading activation (S_i returns 0) or partial matching (P_i returns 0) — these are V2+ features. The ACT-R equation framework is present but only B_i and ε are active.
- V1 does not include emotional salience scoring — emotion fields exist in metadata with default values but are not computed. This is a V3 feature.
- The decay rate parameter (d=0.5) and retrieval threshold (τ=-1.0) are configurable via environment variables.
- The system targets a single-node deployment for V1; horizontal scaling is a future concern.
