# Feature Specification: Emotional Salience + Working Memory

**Feature Branch**: `003-emotion-working-memory`
**Created**: 2026-03-28
**Status**: Draft

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Auto-Detect Emotion on Store (Priority: P1)

When storing a memory, the system detects emotion via an LLM and computes valence/arousal scores. These feed into the emotional salience calculation.

**Acceptance Scenarios**:
1. **Given** content with strong emotion (e.g., anger, joy), **When** stored, **Then** valence and arousal are set to non-default values.
2. **Given** neutral content, **When** stored, **Then** valence ≈ 0, arousal ≈ 0.2.

---

### User Story 2 - Salience Scoring (Priority: P1)

Salience is computed as: `Sal = 0.4|val| + 0.3·aro + 0.2·rel + 0.1·nov`. High-salience memories decay slower and get retrieval boosts.

**Acceptance Scenarios**:
1. **Given** a high-emotion memory (salience > 0.7), **When** decay runs, **Then** it decays slower than a neutral memory of the same age.
2. **Given** retrieval, **When** a high-salience memory competes with a low-salience one, **Then** salience provides an activation boost.

---

### User Story 3 - Working Memory Capacity (Priority: P2)

Retrieval results are capped at 7±2 items (configurable). The capacity-limited set represents the agent's active context.

**Acceptance Scenarios**:
1. **Given** 20 candidate memories, **When** retrieval completes, **Then** at most `working_memory_capacity` results are returned.

---

### User Story 4 - Emotion-Modified Decay (Priority: P2)

Decay rate is modified by salience: `modified_rate = base_decay / (1.0 + salience * 2.0)`.

**Acceptance Scenarios**:
1. **Given** two memories of same age, one with salience=0.9 and one with salience=0.1, **When** decay runs, **Then** the high-salience memory has higher activation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST detect emotion (valence + arousal) when storing memories, using an LLM API.
- **FR-002**: System MUST compute salience: `Sal = α|val| + β·aro + γ·rel + δ·nov`.
- **FR-003**: System MUST modify decay rate based on salience.
- **FR-004**: System MUST cap retrieval results at working memory capacity (default 7).
- **FR-005**: System MUST boost activation by salience during retrieval.

## Success Criteria

- **SC-001**: High-emotion memories persist measurably longer after decay cycles.
- **SC-002**: Retrieval never returns more than working memory capacity items.

## Assumptions

- Emotion detection uses the same LLM API as consolidation extraction (OpenAI-compatible).
- Default salience weights: α=0.4, β=0.3, γ=0.2, δ=0.1.
- Working memory capacity defaults to 7, configurable via env var.
