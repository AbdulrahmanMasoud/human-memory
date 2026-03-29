# Implementation Plan: Semantic Memory + Consolidation Engine

**Branch**: `002-semantic-memory-consolidation` | **Date**: 2026-03-28 | **Spec**: [spec.md](./spec.md)

## Summary

Add Neo4j knowledge graph for semantic memory with spreading activation, and a 4-phase consolidation engine. This completes the ACT-R S_i component and enables episodic→semantic knowledge transfer.

## Technical Context

**New Dependencies**: `neo4j>=5.27.0` (async driver), `httpx` (already present for LLM API)
**New Service**: Neo4j (`neo4j:5-community`) in docker-compose
**New Files**:
- `src/memory_system/stores/neo4j_store.py`
- `src/memory_system/core/consolidation.py`
- `src/memory_system/core/clustering.py`
- `src/memory_system/tasks/consolidation.py`
- `src/memory_system/api/graph.py`
- `src/memory_system/models/graph.py`

## Neo4j Schema

**Nodes**: `Concept(name, type, activation, created_at)`, `Entity(name, type, activation)`
**Relationships**: `IS_A`, `USED_FOR`, `WORKS_WITH`, `RELATED_TO`, `EXTRACTED_FROM` — all with `weight` property

## Spreading Activation Query

```cypher
UNWIND $active_concepts AS source_name
MATCH (source:Concept {name: source_name})-[r]-(target:Concept)
WITH target, sum(r.weight * (1.0 / $context_size)) AS spreading
RETURN target.name, spreading
ORDER BY spreading DESC LIMIT 10
```

## Consolidation Phases

1. **Replay**: Recent episodes with salience > 0.6 get activation += REPLAY_BOOST (0.3)
2. **Extract**: Cluster episodes by embedding similarity (threshold 0.7), LLM extracts facts from clusters of 3+
3. **Prune**: All activations *= DOWNSCALE_FACTOR (0.9), archive below threshold
4. **Compile**: No-op (V4)
