from unittest.mock import AsyncMock
import pytest

from app.event_agents.interview.question_manager import QuestionManager, Questions
from app.types.interview_concept_types import QuestionAndAnswer


@pytest.fixture
def thinker() -> AsyncMock:
    return AsyncMock()

@pytest.fixture
def question_manager(thinker: AsyncMock) -> QuestionManager:
    return QuestionManager(thinker)

@pytest.fixture
def config_artifacts_path() -> str:
    return "config/artifacts_v2.yaml"

@pytest.fixture
def mock_questions() -> list[QuestionAndAnswer]:
    return [
        QuestionAndAnswer(
            question="What is the capital of France?",
            sample_answer="Paris",
            options="Paris, Lyon, Marseille, Toulouse",
        ),
        QuestionAndAnswer(
            question="What is the capital of Germany?",
            sample_answer="Berlin",
            options="Berlin, Munich, Hamburg, Cologne",
        ),
    ]

@pytest.fixture
def mock_context_messages() -> list[dict[str, str]]:
    return [
        {"role": "user", "content": "Generate 2 questions for an interview."},
    ]

def test_question_manager_initialization(question_manager: QuestionManager) -> None:
    assert isinstance(question_manager, QuestionManager)

def test_question_loading_from_yaml(config_artifacts_path: str, question_manager: QuestionManager) -> None:
    assert question_manager.question_file_path == config_artifacts_path
    result = question_manager.get_question_generation_messages()
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], dict)
    assert result[0]["role"] == "user"
    assert result[0]["content"] is not None

@pytest.mark.asyncio
async def test_extract_structured_questions(
    question_manager: QuestionManager,
    thinker: AsyncMock,
    mock_context_messages: list[dict[str, str]],
    mock_questions: list[QuestionAndAnswer],
) -> None:
    # setup mock response
    thinker.extract_structured_response.return_value = Questions(questions=mock_questions)

    # call function
    result = await question_manager.extract_structured_questions(mock_context_messages)

    # Verify the results
    assert result is not None
    assert isinstance(result, Questions)
    assert result.questions == mock_questions

    # Verify the thinker was called with the correct arguments
    thinker.extract_structured_response.assert_called_once_with(
        Questions,
        messages=mock_context_messages,
        debug=True,
    )

@pytest.mark.asyncio
async def test_get_next_question(question_manager: QuestionManager, mock_questions: list[QuestionAndAnswer]) -> None:
    question_manager.questions = mock_questions.copy()
    result = await question_manager.get_next_question()
    assert result is not None
    assert question_manager.current_question is not None
    assert question_manager.current_question == result
    assert isinstance(result, QuestionAndAnswer)
    assert result == mock_questions[0]

    # Verify the questions list was updated
    assert len(question_manager.questions) == len(mock_questions) - 1
    assert question_manager.questions == mock_questions[1:]

    # verify that at the end of the list, the function returns None
    question_manager.questions = []
    result = await question_manager.get_next_question()
    assert result is None
