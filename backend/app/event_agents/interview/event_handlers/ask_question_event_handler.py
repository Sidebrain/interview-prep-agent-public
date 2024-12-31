import logging
from uuid import uuid4

from app.agents.dispatcher import Dispatcher
from app.event_agents.orchestrator.events import (
    AskQuestionEvent,
)
from app.event_agents.types import InterviewContext

logger = logging.getLogger(__name__)


class AskQuestionEventHandler:
    def __init__(self, interview_context: InterviewContext) -> None:
        self.interview_context = interview_context

    async def handler(self, event: AskQuestionEvent) -> None:
        """Send the question to the user."""
        frame_id = str(uuid4())
        question_thought_frame = (
            Dispatcher.package_and_transform_to_webframe(
                event.question,  # type: ignore
                "thought",
                frame_id=frame_id,
            )
        )
        question_frame = Dispatcher.package_and_transform_to_webframe(
            event.question.question,  # type: ignore
            "content",
            frame_id=frame_id,
        )
        await self.interview_context.broker.publish(
            question_thought_frame
        )
        await self.interview_context.broker.publish(question_frame)
