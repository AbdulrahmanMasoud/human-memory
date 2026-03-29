"""Shared test fixtures."""

import pytest


@pytest.fixture
def actr_default_params() -> dict[str, float]:
    """Default ACT-R parameters for testing."""
    return {
        "decay": 0.5,
        "noise_std": 0.25,
        "threshold": -1.0,
    }
