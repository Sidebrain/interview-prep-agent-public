import asyncio
from typing import TYPE_CHECKING
from uuid import UUID, uuid4
from pydantic import BaseModel
import yaml
from app.agents.dispatcher import Dispatcher
from app.event_agents.orchestrator.events import (
    QuestionsGatheringEvent,
    Status,
    UserReadyEvent,
)
import logging

from app.types.interview_concept_types import QuestionAndAnswer

if TYPE_CHECKING:
    from app.event_agents.orchestrator.thinker import Thinker
    from app.event_agents.orchestrator.broker import Broker

logger = logging.getLogger(__name__)


class InterviewManager:
    def __init__(self, broker: "Broker", thinker: "Thinker", session_id: UUID):
        self.broker = broker
        self.thinker = thinker
        self.session_id = session_id

    async def subscribe(self):
        logger.debug(
            f"Subscribing to questions gathering event for session {self.session_id}"
        )
        await self.broker.subscribe(
            QuestionsGatheringEvent, self.handle_questions_gathering_event
        )
        logger.debug(f"Subscribing to user ready event for session {self.session_id}")
        await self.broker.subscribe(UserReadyEvent, self.handle_user_ready_event)

    async def handle_user_ready_event(self, event: UserReadyEvent):
        """
        Handle the user ready event.
        """
        try:
            logger.debug(f"User ready event received for session {event.session_id}")
            await self.ask_question(event)
        except Exception as e:
            logger.error(f"Error handling user ready event: {e}", exc_info=True)
            # You might want to publish an error event here if needed

    async def ask_question(self, event: UserReadyEvent):
        """
        Ask the next question.
        """
        frame_id = str(uuid4())
        question = event.questions.pop(0)
        question_thought_frame = Dispatcher.package_and_transform_to_webframe(
            question,
            "thought",
            frame_id=frame_id,
        )
        await self.broker.publish(question_thought_frame)

        question_frame = Dispatcher.package_and_transform_to_webframe(
            question.question,
            "content",
            frame_id=frame_id,
        )
        await self.broker.publish(question_frame)
        return question_frame

    async def initialize(self) -> list[QuestionAndAnswer]:
        logger.info(f"Initializing interview session {self.session_id}")

        # First event
        in_progress_event = QuestionsGatheringEvent(
            status=Status.in_progress,
            questions=[],
            session_id=self.session_id,
        )

        await self.broker.publish(in_progress_event)
        logger.debug(f"Published in_progress event for session {self.session_id}")

        questions = await self.gather_questions()
        logger.debug(
            f"Gathered {len(questions)} questions for session {self.session_id}"
        )

        # Second event
        completed_event = QuestionsGatheringEvent(
            status=Status.completed,
            questions=questions,
            session_id=self.session_id,
        )

        await self.broker.publish(completed_event)
        logger.debug(f"Published completed event for session {self.session_id}")

        user_ready_event = UserReadyEvent(
            questions=questions,
            session_id=self.session_id,
        )

        await self.broker.publish(user_ready_event)

        return questions

    def gathering_status_string(self, status: Status) -> str:
        match status:
            case Status.in_progress:
                return "Questions gathering in progress."
            case Status.completed:
                return "Questions gathering completed."
            case Status.failed:
                return "Questions gathering failed."
            case Status.idle:
                return "Questions gathering idle."

    async def handle_questions_gathering_event(self, event: QuestionsGatheringEvent):
        """
        Handle the questions gathered event.
        """
        try:
            status_message = self.gathering_status_string(event.status)
            logger.debug(f"Questions gathering status: {status_message}")

            websocket_frame = Dispatcher.package_and_transform_to_webframe(
                status_message,
                "content",
                frame_id=str(uuid4()),
            )

            await self.broker.publish(websocket_frame)
        except Exception as e:
            logger.error(
                f"Error handling questions gathering event: {e}", exc_info=True
            )
            # You might want to publish an error event here

    async def gather_questions(self) -> list[QuestionAndAnswer]:
        with open("config/artifacts.yaml", "r") as f:
            artifacts = yaml.safe_load(f)
        question_string = artifacts["artifacts"]["interview_questions"]
        logger.debug(
            f"Loaded question template (first 100 chars): {question_string[:100]}"
        )

        messages = [
            {"role": "user", "content": question_string},
        ]

        class Questions(BaseModel):
            questions: list[QuestionAndAnswer]

        response: Questions = await self.thinker.extract_structured_response(
            Questions, messages=messages, debug=True
        )
        return response.questions
