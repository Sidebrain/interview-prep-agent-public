from typing import Optional

from pydantic import BaseModel

from app.types.interview_concept_types import QuestionAndAnswer
from app.types.websocket_types import WebsocketFrame


class Turn(BaseModel):
    """A single turn in a conversation, representing one exchange."""

    question: Optional[QuestionAndAnswer] = None
    answer: WebsocketFrame
    parent: Optional["Turn"] = None
    children: list["Turn"] = []
    _depth: int = 0
    _breadth: int = 0

    @property
    def depth(self) -> int:
        return self._depth

    @property
    def breadth(self) -> int:
        return self._breadth

    def get_full_historic_context(self) -> list[dict[str, str]]:
        """Get the full context of this turn."""
        context: list[dict[str, str]] = []
        if self.parent:
            context = self.parent.get_full_historic_context()
        context.extend(self.get_context())
        return context

    def get_context(self) -> list[dict[str, str]]:
        """Get the context of this turn."""
        context: list[dict[str, str]] = []
        answer_content = self.answer.frame.content or None
        question_content = (
            self.question.question if self.question else None
        )

        if not answer_content and not question_content:
            return []

        if question_content:
            context.append(
                {
                    "role": "assistant",
                    "content": question_content,
                }
            )

        if answer_content:
            context.append(
                {
                    "role": "user",
                    "content": answer_content,
                }
            )

        return context
