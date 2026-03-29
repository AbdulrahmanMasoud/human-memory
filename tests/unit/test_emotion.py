"""Tests for emotional salience scoring."""

import pytest

from memory_system.core.emotion import EmotionalSalience


@pytest.fixture
def salience() -> EmotionalSalience:
    return EmotionalSalience()


class TestComputeSalience:
    def test_neutral_low_salience(self, salience: EmotionalSalience) -> None:
        s = salience.compute_salience(valence=0.0, arousal=0.2)
        assert s < 0.3

    def test_high_emotion_high_salience(self, salience: EmotionalSalience) -> None:
        s = salience.compute_salience(valence=-0.8, arousal=0.9)
        assert s > 0.5

    def test_novelty_boosts(self, salience: EmotionalSalience) -> None:
        s_no = salience.compute_salience(valence=0.0, arousal=0.2, is_novel=False)
        s_yes = salience.compute_salience(valence=0.0, arousal=0.2, is_novel=True)
        assert s_yes > s_no

    def test_capped_at_one(self, salience: EmotionalSalience) -> None:
        s = salience.compute_salience(valence=1.0, arousal=1.0, goal_relevance=1.0, is_novel=True)
        assert s == 1.0


class TestModifyDecayRate:
    def test_high_salience_slower_decay(self, salience: EmotionalSalience) -> None:
        slow = salience.modify_decay_rate(0.5, salience=0.9)
        fast = salience.modify_decay_rate(0.5, salience=0.1)
        assert slow < fast

    def test_zero_salience_unchanged(self, salience: EmotionalSalience) -> None:
        rate = salience.modify_decay_rate(0.5, salience=0.0)
        assert rate == pytest.approx(0.5, abs=0.01)


class TestRetrievalBoost:
    def test_high_salience_bigger_boost(self, salience: EmotionalSalience) -> None:
        big = salience.retrieval_boost(0.9)
        small = salience.retrieval_boost(0.1)
        assert big > small

    def test_zero_salience_no_boost(self, salience: EmotionalSalience) -> None:
        assert salience.retrieval_boost(0.0) == 0.0
