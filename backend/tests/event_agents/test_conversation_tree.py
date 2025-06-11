import random
from typing import Callable
from uuid import uuid4

import pytest

from app.agents.dispatcher import Dispatcher
from app.event_agents.conversations.tree import Tree
from app.event_agents.conversations.turn import Turn
from app.event_agents.conversations.types import ProbeDirection
from app.event_agents.conversations.utils import (
    choose_probe_direction,
    normalize_probabilities,
)
from app.types.interview_concept_types import QuestionAndAnswer


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


@pytest.fixture
def conv_tree() -> Tree:
    return Tree(max_depth=3, max_breadth=3)


@pytest.fixture
def make_turn() -> Callable[..., Turn]:
    def _make_turn(
        question_text: str | None = None,
        answer_text: str | None = None,
    ) -> Turn:
        question = QuestionAndAnswer(
            question=question_text
            or f"Test question {random.randint(1, 1000)}?",
            sample_answer=f"Sample answer {random.randint(1, 1000)}",
            options=f"option{random.randint(1, 100)}, option{random.randint(1, 100)}",
        )

        answer = Dispatcher.package_and_transform_to_webframe(
            answer_text or f"Test answer {random.randint(1, 1000)}",  # type: ignore
            "content",
            str(uuid4()),
        )

        return Turn(
            question=question,
            answer=answer,
        )

    return _make_turn


def test_add_root(
    conv_tree: Tree,
    make_turn: Callable[..., Turn],
) -> None:
    assert conv_tree.max_depth == 3
    assert conv_tree.max_breadth == 3
    assert conv_tree.current_depth == 0
    assert conv_tree.current_breadth == 0
    assert conv_tree.current_position is None

    turn_1 = make_turn(
        question_text="What is the capital of France?",
        answer_text="it is surely paris",
    )

    conv_tree.add_turn(
        turn_1,
        direction=ProbeDirection.DEEPER,
    )
    assert conv_tree.current_depth == 0
    assert conv_tree.current_breadth == 0
    assert conv_tree.current_position is not None
    assert conv_tree.current_position.question == turn_1.question
    assert conv_tree.current_position.answer == turn_1.answer

    current_position = conv_tree.current_position
    assert current_position.children == []

    assert conv_tree.move_up() is False
    assert conv_tree.move_to_child(0) is False
    assert conv_tree.move_to(current_position) is True

    assert current_position.get_full_historic_context() == [
        {
            "role": "assistant",
            "content": turn_1.question.question,
        },
        {
            "role": "user",
            "content": turn_1.answer.frame.content,
        },
    ]

    turn_2 = make_turn(
        question_text="what is the tastiest food in the world?",
        answer_text="biryani, hands down",
    )

    conv_tree.add_turn(
        turn_2,
        direction=ProbeDirection.DEEPER,
    )

    assert conv_tree.current_depth == 1
    assert conv_tree.current_breadth == 0
    assert conv_tree.current_position is not None
    assert conv_tree.current_position.parent == turn_1
    assert conv_tree.current_position.question == turn_2.question
    assert conv_tree.current_position.answer == turn_2.answer

    assert conv_tree.move_up() is True
    assert conv_tree.move_to_child(0) is True
    assert conv_tree.move_to(turn_1) is True
    assert conv_tree.move_to_child(0) is True

    assert conv_tree.current_position.get_full_historic_context() == [
        {
            "role": "assistant",
            "content": turn_1.question.question,
        },
        {
            "role": "user",
            "content": turn_1.answer.frame.content,
        },
        {
            "role": "assistant",
            "content": turn_2.question.question,
        },
        {
            "role": "user",
            "content": turn_2.answer.frame.content,
        },
    ]


def test_add_root_with_broader_probe(
    conv_tree: Tree,
    make_turn: Callable[..., Turn],
) -> None:
    # Add initial root turn
    turn_1 = make_turn(
        question_text="What is your favorite season?",
        answer_text="Summer is my favorite",
    )
    conv_tree.add_turn(turn_1, direction=ProbeDirection.DEEPER)

    assert conv_tree.root == turn_1

    # Add a broader turn
    turn_2 = make_turn(
        question_text="What other activities do you enjoy?",
        answer_text="I enjoy hiking and swimming",
    )
    conv_tree.add_turn(turn_2, direction=ProbeDirection.BROADER)

    # Verify tree structure
    assert conv_tree.current_depth == 0
    assert conv_tree.current_breadth == 1
    assert conv_tree.current_position is not None
    assert (
        conv_tree.current_position.parent is not None
    )  # Should be at root level
    assert conv_tree.current_position.question == turn_2.question
    assert conv_tree.current_position.answer == turn_2.answer

    # Test navigation
    assert conv_tree.move_to(turn_1) is True
    assert conv_tree.current_position.question == turn_1.question

    # Verify context includes both turns but maintains independence
    assert turn_2.get_full_historic_context() == [
        {
            "role": "assistant",
            "content": turn_2.question.question,
        },
        {
            "role": "user",
            "content": turn_2.answer.frame.content,
        },
    ]


def test_mixed_probe_directions(
    conv_tree: Tree,
    make_turn: Callable[..., Turn],
) -> None:
    # Create a more complex tree with mixed directions
    turn_1 = make_turn(
        question_text="What's your main hobby?",
        answer_text="Reading books",
    )
    conv_tree.add_turn(turn_1, direction=ProbeDirection.DEEPER)

    turn_2 = make_turn(
        question_text="What genre do you prefer?",
        answer_text="Science fiction",
    )
    conv_tree.add_turn(turn_2, direction=ProbeDirection.DEEPER)

    turn_3 = make_turn(
        question_text="Do you have other hobbies?",
        answer_text="Yes, gardening",
    )
    conv_tree.add_turn(turn_3, direction=ProbeDirection.BROADER)

    # Verify tree structure
    assert conv_tree.current_depth == 1
    assert conv_tree.current_breadth == 1

    # Test navigation between branches
    assert conv_tree.move_to(turn_1) is True
    assert conv_tree.move_to_child(0) is True
    assert conv_tree.current_position.question == turn_2.question

    assert conv_tree.move_to(turn_3) is True
    assert conv_tree.current_position.question == turn_3.question

    # Verify independent contexts
    deeper_context = turn_2.get_full_historic_context()
    assert len(deeper_context) == 4  # Should include turn_1 and turn_2

    broader_context = turn_3.get_full_historic_context()
    assert len(broader_context) == 4  # Should only include turn_3
