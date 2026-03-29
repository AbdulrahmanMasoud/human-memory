"""ACT-R Cognitive Architecture — Memory Activation Mathematics.

Implements the core ACT-R equations for memory retrieval:
    A_i = B_i + S_i + P_i + ε

Where:
    B_i = Base-level activation (recency and frequency)
    S_i = Spreading activation from context (V2+)
    P_i = Partial matching penalty/bonus (V2+)
    ε   = Stochastic noise
"""

import math
import random


class ACTRMemory:
    """Computes ACT-R activation levels for memory chunks."""

    def __init__(
        self,
        decay: float = 0.5,
        noise_std: float = 0.25,
        threshold: float = -1.0,
        latency_factor: float = 1.0,
    ) -> None:
        self.decay = decay
        self.noise_std = noise_std
        self.threshold = threshold
        self.latency_factor = latency_factor

    def base_level_activation(self, access_times: list[float], current_time: float) -> float:
        """Compute B_i = ln(Σ t_j^(-d)).

        Args:
            access_times: List of timestamps (seconds) when the chunk was accessed.
            current_time: Current time in seconds.

        Returns:
            Base-level activation value. Returns -inf if no access history.
        """
        if not access_times:
            return float("-inf")

        total = 0.0
        for t in access_times:
            age = current_time - t
            if age <= 0:
                age = 0.001  # avoid division by zero for concurrent access
            total += age ** (-self.decay)

        if total <= 0:
            return float("-inf")

        return math.log(total)

    def spreading_activation(
        self,
        chunk_id: str,
        context_chunk_ids: list[str],
        association_strengths: dict[tuple[str, str], float],
    ) -> float:
        """Compute S_i = Σ W_k × S_ki.

        V1: Returns 0.0 (no spreading activation yet).
        V2+: Will compute real spreading activation from context.
        """
        if not context_chunk_ids:
            return 0.0

        n = len(context_chunk_ids)
        w = 1.0 / n  # equal attention weight across context sources
        total = 0.0
        for ctx_id in context_chunk_ids:
            s_ki = association_strengths.get((ctx_id, chunk_id), 0.0)
            total += w * s_ki
        return total

    def partial_match(
        self,
        desired: dict[str, str],
        actual: dict[str, str],
        mismatch_penalty: float = -1.0,
    ) -> float:
        """Compute P_i = Σ P × Match(desired_l, actual_l).

        V1: Returns 0.0 (no partial matching yet).
        V2+: Will compute similarity-based matching penalty.
        """
        if not desired or not actual:
            return 0.0

        total = 0.0
        for key, desired_val in desired.items():
            actual_val = actual.get(key)
            if actual_val is None:
                total += mismatch_penalty
            elif actual_val != desired_val:
                total += mismatch_penalty * 0.5  # partial mismatch
            # perfect match contributes 0
        return total

    def noise(self) -> float:
        """Generate stochastic noise ε ~ N(0, noise_std)."""
        if self.noise_std <= 0:
            return 0.0
        return random.gauss(0, self.noise_std)

    def total_activation(
        self,
        access_times: list[float],
        current_time: float,
        context_chunk_ids: list[str] | None = None,
        association_strengths: dict[tuple[str, str], float] | None = None,
        chunk_id: str = "",
        desired: dict[str, str] | None = None,
        actual: dict[str, str] | None = None,
        include_noise: bool = True,
    ) -> float:
        """Compute total activation A_i = B_i + S_i + P_i + ε."""
        b_i = self.base_level_activation(access_times, current_time)
        if b_i == float("-inf"):
            return float("-inf")

        s_i = self.spreading_activation(
            chunk_id,
            context_chunk_ids or [],
            association_strengths or {},
        )
        p_i = self.partial_match(desired or {}, actual or {})
        epsilon = self.noise() if include_noise else 0.0

        return b_i + s_i + p_i + epsilon

    def can_retrieve(self, activation: float) -> bool:
        """Check if activation exceeds retrieval threshold τ."""
        return activation > self.threshold

    def retrieval_latency(self, activation: float) -> float:
        """Compute retrieval time T_i = F × e^(-A_i).

        Higher activation → faster retrieval.
        """
        if activation == float("-inf"):
            return float("inf")
        return self.latency_factor * math.exp(-activation)

    def retrieval_probability(self, activation: float, scale: float = 1.0) -> float:
        """Compute P(retrieve) = 1 / (1 + e^(-(A_i - τ)/s))."""
        exponent = -(activation - self.threshold) / max(scale, 0.001)
        try:
            return 1.0 / (1.0 + math.exp(exponent))
        except OverflowError:
            return 0.0 if exponent > 0 else 1.0
