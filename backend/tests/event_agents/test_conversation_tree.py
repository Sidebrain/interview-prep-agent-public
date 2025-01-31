import random

import pytest

from app.event_agents.questions.types import (
    ProbeDirection,
    choose_probe_direction,
    normalize_probabilities,
)


def test_normalize_probabilities() -> None:
    assert normalize_probabilities(1.0) == (1.0, 0.0)

    assert normalize_probabilities(0.5) == (0.5, 0.5)

    assert normalize_probabilities(1.5, 3.0) == pytest.approx(
        (0.333333, 0.666666), rel=1e-5
    )

    assert normalize_probabilities(0.5, 0.25) == pytest.approx(
        (0.666666, 0.333333), rel=1e-5
    )


def test_choose_probe_direction() -> None:
    # Deterministic cases
    assert choose_probe_direction(1.0) == ProbeDirection.DEEPER
    assert choose_probe_direction(0.0, 1.0) == ProbeDirection.BROADER

    # Statistical test
    random.seed(42)  # Set seed for reproducibility

    # Run multiple times and check distribution
    trials = 1000
    deeper_count = sum(
        1
        for _ in range(trials)
        if choose_probe_direction(0.5, 0.5) == ProbeDirection.DEEPER
    )

    # With equal probabilities, expect roughly 50% DEEPER
    assert 450 <= deeper_count <= 550  # Allow for some variance

    # Test biased probability (0.66 vs 0.33)
    deeper_count = sum(
        1
        for _ in range(trials)
        if choose_probe_direction(0.5, 0.25) == ProbeDirection.DEEPER
    )

    # With 2:1 ratio, expect roughly 66% DEEPER
    assert 630 <= deeper_count <= 730  # Allow for some variance
