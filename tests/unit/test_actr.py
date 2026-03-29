"""Tests for ACT-R activation mathematics."""

import math

import pytest

from memory_system.core.actr import ACTRMemory


@pytest.fixture
def actr() -> ACTRMemory:
    return ACTRMemory(decay=0.5, noise_std=0.0, threshold=-1.0)


class TestBaseLevelActivation:
    def test_empty_access_times_returns_neg_inf(self, actr: ACTRMemory) -> None:
        result = actr.base_level_activation([], 1000.0)
        assert result == float("-inf")

    def test_single_recent_access_high_activation(self, actr: ACTRMemory) -> None:
        current = 100.0
        access_times = [99.0]  # 1 second ago
        result = actr.base_level_activation(access_times, current)
        # B_i = ln(1^(-0.5)) = ln(1) = 0
        assert result == pytest.approx(0.0, abs=0.01)

    def test_single_old_access_lower_activation(self, actr: ACTRMemory) -> None:
        current = 1000.0
        recent = actr.base_level_activation([999.0], current)  # 1 sec ago
        old = actr.base_level_activation([0.0], current)  # 1000 sec ago
        assert recent > old

    def test_more_accesses_higher_activation(self, actr: ACTRMemory) -> None:
        current = 1000.0
        few = actr.base_level_activation([900.0], current)
        many = actr.base_level_activation([900.0, 800.0, 700.0, 600.0, 500.0], current)
        assert many > few

    def test_power_law_decay(self, actr: ACTRMemory) -> None:
        """Verify activation follows power law: rapid initial drop, then slower."""
        current = 10000.0
        a_1h = actr.base_level_activation([current - 3600], current)
        a_1d = actr.base_level_activation([current - 86400], current)
        a_1w = actr.base_level_activation([current - 604800], current)

        # Each should be lower than the previous
        assert a_1h > a_1d > a_1w

        # The drop from 1h to 1d should be larger than 1d to 1w (power law)
        drop_1 = a_1h - a_1d
        drop_2 = a_1d - a_1w
        assert drop_1 > drop_2

    def test_concurrent_access_handled(self, actr: ACTRMemory) -> None:
        """Access at current_time should not cause errors."""
        result = actr.base_level_activation([100.0], 100.0)
        assert math.isfinite(result)

    def test_known_values(self, actr: ACTRMemory) -> None:
        """Verify against hand-calculated values."""
        # Single access 100 seconds ago: B = ln(100^(-0.5)) = ln(0.1) ≈ -2.302
        result = actr.base_level_activation([0.0], 100.0)
        expected = math.log(100.0 ** (-0.5))
        assert result == pytest.approx(expected, abs=0.01)


class TestTotalActivation:
    def test_v1_only_base_level_active(self, actr: ACTRMemory) -> None:
        """In V1, S_i and P_i should contribute 0."""
        current = 1000.0
        access_times = [999.0, 998.0, 997.0]

        b_i = actr.base_level_activation(access_times, current)
        a_i = actr.total_activation(
            access_times, current, include_noise=False
        )
        assert a_i == pytest.approx(b_i, abs=0.001)

    def test_no_access_returns_neg_inf(self, actr: ACTRMemory) -> None:
        result = actr.total_activation([], 1000.0, include_noise=False)
        assert result == float("-inf")


class TestCanRetrieve:
    def test_above_threshold(self, actr: ACTRMemory) -> None:
        assert actr.can_retrieve(0.0) is True
        assert actr.can_retrieve(-0.5) is True

    def test_below_threshold(self, actr: ACTRMemory) -> None:
        assert actr.can_retrieve(-1.0) is False
        assert actr.can_retrieve(-2.0) is False
        assert actr.can_retrieve(float("-inf")) is False

    def test_custom_threshold(self) -> None:
        actr = ACTRMemory(threshold=0.5, noise_std=0.0)
        assert actr.can_retrieve(0.6) is True
        assert actr.can_retrieve(0.4) is False


class TestRetrievalLatency:
    def test_higher_activation_faster(self, actr: ACTRMemory) -> None:
        fast = actr.retrieval_latency(2.0)
        slow = actr.retrieval_latency(0.0)
        assert fast < slow

    def test_neg_inf_returns_inf(self, actr: ACTRMemory) -> None:
        assert actr.retrieval_latency(float("-inf")) == float("inf")


class TestRetrievalProbability:
    def test_high_activation_near_one(self, actr: ACTRMemory) -> None:
        prob = actr.retrieval_probability(5.0)
        assert prob > 0.99

    def test_low_activation_near_zero(self, actr: ACTRMemory) -> None:
        prob = actr.retrieval_probability(-10.0)
        assert prob < 0.01

    def test_at_threshold_is_half(self, actr: ACTRMemory) -> None:
        prob = actr.retrieval_probability(-1.0)
        assert prob == pytest.approx(0.5, abs=0.01)


class TestNoise:
    def test_noise_disabled_when_std_zero(self) -> None:
        actr = ACTRMemory(noise_std=0.0)
        for _ in range(100):
            assert actr.noise() == 0.0

    def test_noise_has_variance(self) -> None:
        actr = ACTRMemory(noise_std=0.5)
        values = [actr.noise() for _ in range(1000)]
        assert max(values) != min(values)
        # Mean should be near 0
        mean = sum(values) / len(values)
        assert abs(mean) < 0.1


class TestSpreadingActivation:
    def test_no_context_returns_zero(self, actr: ACTRMemory) -> None:
        result = actr.spreading_activation("chunk1", [], {})
        assert result == 0.0

    def test_with_associations(self, actr: ACTRMemory) -> None:
        associations = {
            ("ctx1", "chunk1"): 2.0,
            ("ctx2", "chunk1"): 1.0,
        }
        result = actr.spreading_activation(
            "chunk1", ["ctx1", "ctx2"], associations
        )
        # W = 1/2 for each, S = 0.5*2.0 + 0.5*1.0 = 1.5
        assert result == pytest.approx(1.5, abs=0.01)


class TestPartialMatch:
    def test_empty_returns_zero(self, actr: ACTRMemory) -> None:
        assert actr.partial_match({}, {}) == 0.0

    def test_perfect_match_returns_zero(self, actr: ACTRMemory) -> None:
        desired = {"color": "red", "size": "large"}
        actual = {"color": "red", "size": "large"}
        assert actr.partial_match(desired, actual) == 0.0

    def test_mismatch_returns_penalty(self, actr: ACTRMemory) -> None:
        desired = {"color": "red"}
        actual = {"color": "blue"}
        result = actr.partial_match(desired, actual)
        assert result < 0.0
