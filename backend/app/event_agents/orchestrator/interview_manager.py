import asyncio
from typing import TYPE_CHECKING
from uuid import UUID, uuid4
from pydantic import BaseModel
import yaml
from app.agents.dispatcher import Dispatcher
from app.event_agents.orchestrator.events import QuestionsGatheringEvent, Status
import logging

from app.types.interview_concept_types import QuestionAndAnswer

if TYPE_CHECKING:
    from app.event_agents.orchestrator.thinker import Thinker
    from app.event_agents.orchestrator.broker import Broker

logger = logging.getLogger(__name__)


class InterviewManager:
    def __init__(self, broker: "Broker", thinker: "Thinker"):
        self.broker = broker
        self.thinker = thinker

    async def subscribe(self):
        await self.broker.subscribe(
            QuestionsGatheringEvent, self.handle_questions_gathering_event
        )

    async def initialize(self, session_id: UUID) -> list[QuestionAndAnswer]:
        logger.info(f"Initializing interview session {session_id}")
        
        # First event
        in_progress_event = QuestionsGatheringEvent(
            status=Status.in_progress,
            questions=[],
            session_id=session_id,
        )
        
        await self.broker.publish(in_progress_event)
        logger.debug(f"Published in_progress event for session {session_id}")
        
        questions = await self.gather_questions()
        logger.debug(f"Gathered {len(questions)} questions for session {session_id}")
        
        # Second event
        completed_event = QuestionsGatheringEvent(
            status=Status.completed,
            questions=questions,
            session_id=session_id,
        )
        
        await self.broker.publish(completed_event)
        logger.debug(f"Published completed event for session {session_id}")
        
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
        status_message = self.gathering_status_string(event.status)
        logger.debug(f"Questions gathering status: {status_message}")
        
        websocket_frame = Dispatcher.package_and_transform_to_webframe(
            status_message,
            "content",
            frame_id=str(uuid4()),
        )
        logger.debug(f"Sending websocket frame for session {event.session_id}")
        await self.broker.publish(websocket_frame)

    async def gather_questions(self) -> list[QuestionAndAnswer]:
        with open("config/artifacts.yaml", "r") as f:
            artifacts = yaml.safe_load(f)
        question_string = artifacts["artifacts"]["interview_questions"]
        logger.debug(f"Loaded question template (first 100 chars): {question_string[:100]}")
        
        messages = [
            {"role": "user", "content": question_string},
        ]

        class Questions(BaseModel):
            questions: list[QuestionAndAnswer]

        response: Questions = await self.thinker.extract_structured_response(
            Questions, messages=messages, debug=True
        )
        return response.questions
