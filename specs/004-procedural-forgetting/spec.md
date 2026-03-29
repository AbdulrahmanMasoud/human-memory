# Feature Specification: Procedural Memory + Strategic Forgetting

**Feature Branch**: `004-procedural-forgetting`
**Created**: 2026-03-28
**Status**: Draft

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Five Forgetting Modes (Priority: P1)

The system implements 5 distinct forgetting mechanisms: temporal decay (existing), interference, retrieval-induced forgetting, strategic prune, and capacity overflow.

**Acceptance Scenarios**:
1. **Given** a new similar memory stored, **When** interference runs, **Then** older similar memories lose activation.
2. **Given** memory A retrieved while B and C compete, **When** RIF runs, **Then** B and C lose activation.
3. **Given** current goals, **When** strategic prune runs, **Then** irrelevant memories lose activation.
4. **Given** store exceeds capacity, **When** overflow runs, **Then** weakest memories are archived.

---

### User Story 2 - Procedural Memory Store (Priority: P1)

Compiled skills are stored as action patterns with preconditions, success rates, and execution counts. Skills are created when patterns repeat 3+ times with >80% success.

**Acceptance Scenarios**:
1. **Given** a compiled skill, **When** queried, **Then** it returns preconditions, action pattern, and success rate.
2. **Given** a new skill stored, **When** the same pattern is seen again, **Then** the existing skill's execution count increments.

---

### User Story 3 - Consolidation Phase 4 Active (Priority: P2)

The consolidation compile phase now detects repeated successful action patterns and compiles them into procedural memory.

---

### User Story 4 - Forgetting API (Priority: P2)

API endpoint to manually apply a specific forgetting strategy with parameters.

## Requirements

- **FR-001**: System MUST implement 5 forgetting modes.
- **FR-002**: System MUST store procedural skills with preconditions, patterns, success rates.
- **FR-003**: Consolidation Phase 4 MUST compile repeated patterns into skills.
- **FR-004**: System MUST expose forgetting strategy API.

## Assumptions

- Procedural skills stored in PostgreSQL with JSONB columns.
- Interference detection uses cosine similarity threshold of 0.8.
- RIF penalty applied after each retrieval to non-returned competitors.
