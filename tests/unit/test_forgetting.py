"""Tests for the 5 forgetting modes."""

from memory_system.core.forgetting import ForgettingEngine


class TestInterference:
    def test_high_similarity_applies_penalty(self) -> None:
        engine = ForgettingEngine()
        similar = [{"id": "mem1", "activation": 1.0}]
        similarities = [0.9]
        updates = engine.compute_interference(1.0, similar, similarities)
        assert len(updates) == 1
        assert updates[0][1] < 1.0

    def test_low_similarity_no_penalty(self) -> None:
        engine = ForgettingEngine()
        similar = [{"id": "mem1", "activation": 1.0}]
        similarities = [0.5]  # below 0.8 threshold
        updates = engine.compute_interference(1.0, similar, similarities)
        assert len(updates) == 0


class TestRIF:
    def test_competitors_suppressed(self) -> None:
        engine = ForgettingEngine()
        updates = engine.compute_rif(
            retrieved_ids=["a"],
            competitor_ids=["a", "b", "c"],
            competitor_activations={"a": 1.0, "b": 0.8, "c": 0.6},
        )
        # b and c should be suppressed, not a
        ids = [u[0] for u in updates]
        assert "a" not in ids
        assert "b" in ids
        assert "c" in ids

    def test_all_retrieved_no_rif(self) -> None:
        engine = ForgettingEngine()
        updates = engine.compute_rif(
            retrieved_ids=["a", "b"],
            competitor_ids=["a", "b"],
            competitor_activations={"a": 1.0, "b": 0.8},
        )
        assert len(updates) == 0


class TestStrategicPrune:
    def test_irrelevant_memories_weakened(self) -> None:
        engine = ForgettingEngine()
        memories = [
            {"id": "1", "content": "Python programming tips", "activation": 0.8},
            {"id": "2", "content": "Cooking recipes for dinner", "activation": 0.8},
        ]
        updates = engine.compute_strategic_prune(memories, ["Python", "programming"])
        # Only cooking should be pruned
        pruned_ids = [u[0] for u in updates]
        assert "2" in pruned_ids
        assert "1" not in pruned_ids

    def test_no_goals_no_prune(self) -> None:
        engine = ForgettingEngine()
        memories = [{"id": "1", "content": "test", "activation": 0.8}]
        updates = engine.compute_strategic_prune(memories, [])
        assert len(updates) == 0


class TestCapacityOverflow:
    def test_under_capacity_no_eviction(self) -> None:
        engine = ForgettingEngine(max_capacity=10)
        memories = [{"id": str(i), "activation": float(i)} for i in range(5)]
        result = engine.compute_capacity_overflow(memories)
        assert len(result) == 0

    def test_over_capacity_evicts_weakest(self) -> None:
        engine = ForgettingEngine(max_capacity=3)
        memories = [{"id": str(i), "activation": float(i)} for i in range(5)]
        result = engine.compute_capacity_overflow(memories)
        assert len(result) == 2
        # Should evict IDs "0" and "1" (lowest activation)
        assert "0" in result
        assert "1" in result
