import logging
import json

from typing import TYPE_CHECKING
from uuid import UUID, uuid4
from app.agents.dispatcher import Dispatcher
from app.event_agents.orchestrator.events import (
    AskQuestionEvent,
    InterviewEndEvent,
    InterviewEndReason,
    QuestionsGatheringEvent,
)

from app.types.websocket_types import WebsocketFrame

if TYPE_CHECKING:
    from app.event_agents.orchestrator.broker import Broker

logger = logging.getLogger(__name__)


class InterviewEventHandler:
    def __init__(self, broker: "Broker", session_id: UUID):
        self.broker = broker
        self.session_id = session_id

    def __repr__(self) -> str:
        return json.dumps(
            {
                "type": "InterviewEventHandler",
                "session": self.session_id.hex[:8],
            },
            indent=2,
        )

    async def handle_interview_end(self, event: InterviewEndEvent):
        """
        Handle the end of an interview session.

        Args:
            event (InterviewEndEvent): Event containing the reason for interview end
                (timeout or questions_exhausted)

        Publishes appropriate end message to the websocket based on the end reason.
        """
        logger.info(
            "Interview ended",
            extra={
                "context": {
                    "session": self.session_id.hex[:8],
                    "reason": event.reason.value,
                    "handler_type": "InterviewEventHandler",
                }
            },
        )

        match event.reason:
            case InterviewEndReason.questions_exhausted:
                end_interview_message = (
                    Dispatcher.package_and_transform_to_webframe(
                        "Questions exhausted. Interview ended.",
                        "content",
                        frame_id=str(uuid4()),
                    )
                )
                await self.broker.publish(end_interview_message)
            case InterviewEndReason.timeout:
                end_interview_message = (
                    Dispatcher.package_and_transform_to_webframe(
                        "Timeout. Interview ended.",
                        "content",
                        frame_id=str(uuid4()),
                    )
                )
                await self.broker.publish(end_interview_message)
            case _:
                logger.info(
                    "Interview ended with unknown reason: %s",
                    {
                        "handler": self,
                        "reason": event.reason,
                    },
                )

    async def handle_ask_question(
        self, event: AskQuestionEvent
    ) -> WebsocketFrame:
        """
        Process and publish a question to be asked during the interview.

        Args:
            event (AskQuestionEvent): Event containing the question to be asked

        Returns:
            WebsocketFrame: The formatted question frame sent to the client

        Publishes both a thought frame and content frame for the question.
        """
        logger.info(
            "Publishing question",
            extra={
                "handler": self,
                "question_length": len(event.question.question),
            },
        )

        frame_id = str(uuid4())
        question_thought_frame = Dispatcher.package_and_transform_to_webframe(
            event.question,
            "thought",
            frame_id=frame_id,
        )
        await self.broker.publish(question_thought_frame)

        question_frame = Dispatcher.package_and_transform_to_webframe(
            event.question.question,
            "content",
            frame_id=frame_id,
        )
        await self.broker.publish(question_frame)
        return question_frame

    async def handle_questions_gathering_event(
        self, event: QuestionsGatheringEvent
    ) -> None:
        try:
            status_message = event.status.value
            logger.info(
                "Questions gathering status: %s",
                {"handler": self, "status": status_message},
            )

            websocket_frame = Dispatcher.package_and_transform_to_webframe(
                status_message,
                "content",
                frame_id=str(uuid4()),
            )

            await self.broker.publish(websocket_frame)
        except Exception as e:
            logger.error(
                "Questions gathering failed: %s",
                {"handler": self, "error": str(e)},
            )
