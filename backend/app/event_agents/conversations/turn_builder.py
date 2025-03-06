from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID, uuid4

from app.event_agents.types import InterviewAbilities
from app.types.interview_concept_types import QuestionAndAnswer
from app.types.websocket_types import WebsocketFrame


@dataclass
class TurnContext:
    question: QuestionAndAnswer
    turn_id: UUID
    abilities: InterviewAbilities
    answer: Optional[WebsocketFrame] = None
    evaluations: list[WebsocketFrame] = field(default_factory=list)
    perspectives: list[WebsocketFrame] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return all(
            [
                self.question is not None,
                self.answer is not None,
                self._check_abiltiy_completeness(),
            ]
        )

    def _check_abiltiy_completeness(self) -> bool:
        return all(
            [
                self.abilities.evaluations_enabled
                and len(self.evaluations) > 0,
                self.abilities.perspectives_enabled
                and len(self.perspectives) > 0,
            ]
        )


class TurnBuilder:
    def __init__(self) -> None:
        self._active_turns: dict[UUID, TurnContext] = {}

    def start_turn(
        self, question: QuestionAndAnswer, abilities: InterviewAbilities
    ) -> None:
        turn_id = uuid4()
        self._active_turns[turn_id] = TurnContext(
            question=question,
            turn_id=turn_id,
            abilities=abilities,
        )

    def add_answer(self, turn_id: UUID, answer: WebsocketFrame) -> None:
        if turn_id not in self._active_turns:
            raise ValueError(f"Turn {turn_id} not found")
        self._active_turns[turn_id].answer = answer

    def add_evaluation(
        self, turn_id: UUID, evaluation: WebsocketFrame
    ) -> None:
        if turn_id not in self._active_turns:
            raise ValueError(f"Turn {turn_id} not found")
        self._active_turns[turn_id].evaluations.append(evaluation)

    def add_perspective(
        self, turn_id: UUID, perspective: WebsocketFrame
    ) -> None:
        if turn_id not in self._active_turns:
            raise ValueError(f"Turn {turn_id} not found")
        self._active_turns[turn_id].perspectives.append(perspective)
