import pytest
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

from app.event_agents.interview.coordinator import Coordinator

@pytest.fixture
def session_id() -> UUID:
    return uuid4()

@pytest.fixture
def coordinator() -> Coordinator:
    return Coordinator()

def test_coordinator_initialization(coordinator: Coordinator) -> None:
    assert isinstance(coordinator, Coordinator)

def test_coordinator_gathering_questions(coordinator: Coordinator) -> None:
    pass