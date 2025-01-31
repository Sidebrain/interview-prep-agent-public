from enum import Enum


class ProbeDirection(str, Enum):
    """Direction in which the conversation can grow."""

    DEEPER = "depth"  # Vertical growth
    BROADER = "breadth"  # Horizontal growth
