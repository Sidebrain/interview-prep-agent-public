import random
from typing import Optional

from app.event_agents.conversations.types import ProbeDirection


def normalize_probabilities(
    depth_probability: Optional[float] = None,
    breadth_probability: Optional[float] = None,
) -> tuple[float, float]:
    """Normalize depth and breadth probabilities to sum to 1.0.

    If neither is provided, defaults to equal 0.5 probabilities.
    If only one is provided, sets the other to the complement.
    if both are provided normalizes them to sum to 1.0
    """
    if not depth_probability and not breadth_probability:
        # Default to equal probability
        depth_probability = 0.5
        breadth_probability = 0.5

    elif depth_probability and not breadth_probability:
        breadth_probability = 1 - depth_probability

    elif breadth_probability and not depth_probability:
        depth_probability = 1 - breadth_probability

    elif depth_probability and breadth_probability:
        # Normalize to sum to 1.0
        total = depth_probability + breadth_probability
        depth_probability = depth_probability / total
        breadth_probability = breadth_probability / total

    else:
        raise ValueError("Invalid probabilities")

    return depth_probability, breadth_probability


def choose_probe_direction(
    depth_probability: Optional[float] = None,
    breadth_probability: Optional[float] = None,
) -> ProbeDirection:
    """Sample a direction based on relative preference of depth vs breadth.

    Args:
        depth_probability: Probability of choosing depth.
        breadth_probability: Probability of choosing breadth.
    """

    depth_probability, breadth_probability = normalize_probabilities(
        depth_probability, breadth_probability
    )

    return random.choices(
        list(ProbeDirection),
        weights=[depth_probability, breadth_probability],
    )[0]
