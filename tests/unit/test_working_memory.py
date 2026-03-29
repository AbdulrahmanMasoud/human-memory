"""Tests for working memory capacity management."""

from memory_system.core.working_memory import WorkingMemory


class TestWorkingMemory:
    def test_default_capacity(self) -> None:
        wm = WorkingMemory()
        assert wm.capacity == 7

    def test_filter_caps_at_capacity(self) -> None:
        wm = WorkingMemory(capacity=3)
        items = [{"id": i, "activation": float(i)} for i in range(10)]
        result = wm.filter_by_capacity(items)
        assert len(result) == 3

    def test_filter_keeps_highest_activation(self) -> None:
        wm = WorkingMemory(capacity=2)
        items = [
            {"id": "low", "activation": 0.1},
            {"id": "high", "activation": 0.9},
            {"id": "mid", "activation": 0.5},
        ]
        result = wm.filter_by_capacity(items)
        assert len(result) == 2
        assert result[0]["id"] == "high"
        assert result[1]["id"] == "mid"

    def test_fewer_items_than_capacity(self) -> None:
        wm = WorkingMemory(capacity=10)
        items = [{"id": 1, "activation": 0.5}]
        result = wm.filter_by_capacity(items)
        assert len(result) == 1

    def test_update_and_get(self) -> None:
        wm = WorkingMemory(capacity=2)
        items = [{"id": i, "activation": float(i)} for i in range(5)]
        wm.update(items)
        active = wm.get_active()
        assert len(active) == 2
        assert active[0]["activation"] == 4.0

    def test_clear(self) -> None:
        wm = WorkingMemory(capacity=5)
        wm.update([{"id": 1, "activation": 1.0}])
        wm.clear()
        assert len(wm.get_active()) == 0
