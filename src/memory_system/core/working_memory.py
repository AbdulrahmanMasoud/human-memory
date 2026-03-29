"""Working memory with capacity limit (Baddeley's model).

Working memory capacity is 7±2 items. The highest-activation
items are retained; others are dropped from the active context.
"""


class WorkingMemory:
    """Capacity-limited working memory buffer."""

    def __init__(self, capacity: int = 7) -> None:
        self.capacity = capacity
        self._items: list[dict[str, object]] = []

    def filter_by_capacity(
        self, items: list[dict[str, object]], activation_key: str = "activation"
    ) -> list[dict[str, object]]:
        """Keep only the top-capacity items by activation.

        Items must have an activation_key field (float).
        Returns items sorted by activation descending, capped at capacity.
        """
        sorted_items = sorted(
            items,
            key=lambda x: float(x.get(activation_key, 0.0)),  # type: ignore[arg-type]
            reverse=True,
        )
        return sorted_items[: self.capacity]

    def update(self, items: list[dict[str, object]]) -> None:
        """Update the working memory buffer with new items."""
        self._items = self.filter_by_capacity(items)

    def get_active(self) -> list[dict[str, object]]:
        """Get current working memory contents."""
        return list(self._items)

    def clear(self) -> None:
        """Clear working memory."""
        self._items = []
