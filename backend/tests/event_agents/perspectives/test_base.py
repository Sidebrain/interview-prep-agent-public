from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest

from app.event_agents.memory.protocols import MemoryStore
from app.event_agents.orchestrator.broker import Broker
from app.event_agents.orchestrator.thinker import Thinker
from app.event_agents.perspectives.perspective_base import (
    PerspectiveBase,
)
from app.event_agents.types import AgentContext
from app.types.interview_concept_types import QuestionAndAnswer
from app.types.websocket_types import WebsocketFrame
from tests.event_agents.perspectives.conftest import (
    create_mock_websocket_frames,
    create_test_memory_store,
)


@pytest.fixture
def perspective() -> PerspectiveBase:
    return PerspectiveBase(perspective="Test Perspective")


@pytest.fixture
def memory_store() -> MemoryStore:
    store = create_test_memory_store()
    store.memory = create_mock_websocket_frames()
    return store


@pytest.fixture
def sample_questions() -> list[QuestionAndAnswer]:
    return [
        QuestionAndAnswer(
            question="Test question",
            sample_answer="Test answer",
            options="Test options",
        )
    ]


@pytest.fixture
def agent_context(memory_store: MemoryStore) -> AgentContext:
    return AgentContext(
        agent_id=uuid4(),
        session_id=uuid4(),
        broker=Mock(spec=Broker),
        thinker=Mock(spec=Thinker),
        memory_store=memory_store,
    )


# Unit Tests for Atomic Functions
def test_perspective_base_initialization(
    perspective: PerspectiveBase,
) -> None:
    """Test basic initialization of PerspectiveBase"""
    assert perspective.perspective == "Test Perspective"


def test_get_correlation_id(
    perspective: PerspectiveBase, memory_store: MemoryStore
) -> None:
    """Test extraction of correlation ID from memory store"""
    correlation_id = perspective._get_correlation_id(memory_store)
    assert correlation_id == "test-correlation-id-human-4"


def test_create_evaluation_instruction(
    perspective: PerspectiveBase,
) -> None:
    """Test creation of evaluation instruction"""
    instruction = perspective._create_evaluation_instruction()
    assert "You are a Test Perspective" in instruction
    assert "You thrive working in teams" in instruction


def test_package_response(perspective: PerspectiveBase) -> None:
    """Test packaging of analysis into WebsocketFrame"""
    result = perspective._package_response(
        "Test analysis", "test-correlation-id"
    )
    assert isinstance(result, WebsocketFrame)
    assert result.correlation_id == "test-correlation-id"
    assert result.address == "perspective"


# Integration Tests
@pytest.mark.asyncio
async def test_evaluate_perspective(
    perspective: PerspectiveBase,
    agent_context: AgentContext,
    sample_questions: list[QuestionAndAnswer],
) -> None:
    """Test the full evaluation pipeline"""
    with patch.object(
        perspective, "_build_evaluation_context", new_callable=AsyncMock
    ) as mock_context:
        mock_context.return_value = [
            {"role": "human", "content": "test context"},
            {"role": "human", "content": "test context"},
            {"role": "human", "content": "custom user instruction"},
        ]

        with patch.object(
            agent_context.thinker, "generate", new_callable=AsyncMock
        ) as mock_generate:
            mock_generate.return_value = "Analysis Result"

            result = await perspective.evaluate(
                sample_questions, agent_context
            )

            assert isinstance(result, WebsocketFrame)
            assert (
                result.correlation_id == "test-correlation-id-human-4"
            )
            assert result.address == "perspective"


@pytest.mark.asyncio
async def test_retrieve_and_build_context_messages(
    perspective: PerspectiveBase,
    agent_context: AgentContext,
    sample_questions: list[QuestionAndAnswer],
) -> None:
    """Test context message building"""
    with patch.object(
        agent_context.memory_store, "extract_memory_for_generation"
    ) as mock_extract:
        mock_extract.return_value = [
            {"role": "user", "content": "test message"}
        ]

        messages = (
            await perspective.retrieve_and_build_context_messages(
                questions=sample_questions,
                memory_store=agent_context.memory_store,
                address_filter=["human"],
                custom_user_instruction="test instruction",
            )
        )

        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "test message"
        mock_extract.assert_called_once()
