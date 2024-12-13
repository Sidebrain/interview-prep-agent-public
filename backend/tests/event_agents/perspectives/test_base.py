import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.event_agents.perspectives.perspective_base import PerspectiveBase
from app.event_agents.memory.store import InMemoryStore
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
def memory_store() -> InMemoryStore:
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


# Unit Tests for Atomic Functions
def test_perspective_base_initialization(perspective):
    """Test basic initialization of PerspectiveBase"""
    assert perspective.perspective == "Test Perspective"
    assert perspective.description is None
    assert hasattr(perspective, "thinker")


def test_get_correlation_id(perspective, memory_store):
    """Test extraction of correlation ID from memory store"""
    correlation_id = perspective._get_correlation_id(memory_store)
    assert correlation_id == "test-correlation-id-human-4"


def test_ensure_description_exists_raises_error(perspective):
    """Test that _ensure_description_exists raises error when description is None"""
    with pytest.raises(ValueError) as exc_info:
        perspective._ensure_description_exists()
    assert "Description not initialized" in str(exc_info.value)


def test_ensure_description_exists_passes(perspective):
    """Test that _ensure_description_exists passes when description exists"""
    perspective.description = "Test Description"
    perspective._ensure_description_exists()  # Should not raise exception


def test_create_evaluation_instruction(perspective):
    """Test creation of evaluation instruction"""
    perspective.description = "Test Description"
    instruction = perspective._create_evaluation_instruction()
    assert "You are a Test Perspective" in instruction
    assert "Test Description" in instruction


def test_package_response(perspective):
    """Test packaging of analysis into WebsocketFrame"""
    result = perspective._package_response(
        "Test analysis", "test-correlation-id"
    )
    assert isinstance(result, WebsocketFrame)
    assert result.correlation_id == "test-correlation-id"
    assert result.address == "evaluation"


# Integration Tests
@pytest.mark.asyncio
async def test_initialize_perspective(perspective):
    """Test the full initialization process"""
    with patch.object(
        perspective.thinker, "generate", new_callable=AsyncMock
    ) as mock_generate:
        mock_generate.return_value.choices = [
            Mock(message=Mock(content="Generated Description"))
        ]

        with patch("builtins.open", create=True) as mock_open:
            description = await perspective.initialize()

            assert description == "Generated Description"
            assert perspective.description == "Generated Description"
            mock_open.assert_called_once_with(
                "config/Test Perspective.txt", "w"
            )


@pytest.mark.asyncio
async def test_evaluate_perspective(
    perspective, memory_store, sample_questions
):
    """Test the full evaluation pipeline"""
    perspective.description = "Test Description"
    perspective._ensure_description_exists()

    with patch.object(
        perspective, "_build_evaluation_context", new_callable=AsyncMock
    ) as mock_context:
        mock_context.return_value = [
            {"role": "human", "content": "test context"},
            {"role": "human", "content": "test context"},
            {"role": "human", "content": "custom user instruction"},
        ]

        with patch.object(
            perspective.thinker, "generate", new_callable=AsyncMock
        ) as mock_generate:
            mock_generate.return_value = "Analysis Result"

            result = await perspective.evaluate(sample_questions, memory_store)

            assert isinstance(result, WebsocketFrame)
            assert result.correlation_id == "test-correlation-id-human-4"
            assert result.address == "evaluation"


@pytest.mark.asyncio
async def test_retrieve_and_build_context_messages(
    perspective, memory_store, sample_questions
):
    """Test context message building"""
    with patch.object(
        memory_store, "extract_memory_for_generation"
    ) as mock_extract:
        mock_extract.return_value = [
            {"role": "user", "content": "test message"}
        ]

        messages = await perspective.retrieve_and_build_context_messages(
            questions=sample_questions,
            memory_store=memory_store,
            address_filter=["human"],
            custom_user_instruction="test instruction",
            debug=True,
        )

        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "test message"
        mock_extract.assert_called_once()


@pytest.mark.asyncio
async def test_write_perspective_description(perspective):
    """Test writing perspective description to file"""
    test_description = "Test Description"

    with patch("builtins.open", create=True) as mock_open:
        perspective.write_perspective_description_to_txt(test_description)
        mock_open.assert_called_once_with(
            f"config/{perspective.perspective}.txt", "w"
        )


def test_create_initialization_messages(perspective):
    """Test creation of initialization messages"""
    messages = perspective._create_initialization_messages()
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert perspective.perspective in messages[0]["content"]
