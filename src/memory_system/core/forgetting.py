"""Forgetting engine — 5 forgetting mechanisms.

1. Temporal decay (handled by decay task — existing)
2. Interference: new similar memories weaken old ones
3. Retrieval-induced forgetting (RIF): retrieving A suppresses B, C
4. Strategic prune: goal-directed forgetting
5. Capacity overflow: weakest evicted when full
"""

import logging

logger = logging.getLogger(__name__)

INTERFERENCE_PENALTY = 0.2
RIF_PENALTY = 0.15
PRUNE_FACTOR = 0.5
DEFAULT_MAX_CAPACITY = 10000


class ForgettingEngine:
    """Implements 5 forgetting modes from cognitive science."""

    def __init__(
        self,
        interference_penalty: float = INTERFERENCE_PENALTY,
        rif_penalty: float = RIF_PENALTY,
        prune_factor: float = PRUNE_FACTOR,
        max_capacity: int = DEFAULT_MAX_CAPACITY,
    ) -> None:
        self.interference_penalty = interference_penalty
        self.rif_penalty = rif_penalty
        self.prune_factor = prune_factor
        self.max_capacity = max_capacity

    def compute_interference(
        self,
        new_memory_activation: float,
        similar_memories: list[dict[str, object]],
        similarities: list[float],
    ) -> list[tuple[str, float]]:
        """Compute interference penalties for similar existing memories.

        Returns list of (memory_id, new_activation) pairs.
        """
        updates: list[tuple[str, float]] = []
        for mem, sim in zip(similar_memories, similarities):
            if sim > 0.8:
                old_activation = float(mem.get("activation", 0.0))  # type: ignore[arg-type]
                penalty = sim * self.interference_penalty
                new_activation = old_activation - penalty
                updates.append((str(mem["id"]), new_activation))
        return updates

    def compute_rif(
        self,
        retrieved_ids: list[str],
        competitor_ids: list[str],
        competitor_activations: dict[str, float],
    ) -> list[tuple[str, float]]:
        """Compute retrieval-induced forgetting penalties.

        Competitors that were NOT retrieved get suppressed.
        """
        updates: list[tuple[str, float]] = []
        for comp_id in competitor_ids:
            if comp_id not in retrieved_ids:
                old = competitor_activations.get(comp_id, 0.0)
                updates.append((comp_id, old - self.rif_penalty))
        return updates

    def compute_strategic_prune(
        self,
        memories: list[dict[str, object]],
        current_goals: list[str],
    ) -> list[tuple[str, float]]:
        """Goal-directed forgetting — reduce activation of irrelevant memories.

        Memories whose content doesn't relate to current goals get weakened.
        Simple keyword matching for now; V5+ could use semantic similarity.
        """
        updates: list[tuple[str, float]] = []
        goal_text = " ".join(current_goals).lower()
        goal_words = [w for w in goal_text.split() if len(w) > 3]

        if not goal_words:
            return updates

        for mem in memories:
            content = str(mem.get("content", "")).lower()
            # Simple relevance: any goal keyword in content
            relevant = any(word in content for word in goal_words)
            if not relevant:
                old = float(mem.get("activation", 0.0))  # type: ignore[arg-type]
                updates.append((str(mem["id"]), old * self.prune_factor))

        return updates

    def compute_capacity_overflow(
        self,
        memories: list[dict[str, object]],
    ) -> list[str]:
        """When store exceeds capacity, return IDs of weakest memories to archive.

        Returns list of memory_ids to archive.
        """
        if len(memories) <= self.max_capacity:
            return []

        sorted_mems = sorted(
            memories,
            key=lambda m: float(m.get("activation", 0.0)),  # type: ignore[arg-type]
        )
        overflow = len(memories) - self.max_capacity
        return [str(m["id"]) for m in sorted_mems[:overflow]]
