from typing import TYPE_CHECKING
from uuid import UUID, uuid4
from pydantic import BaseModel
import yaml
from app.agents.dispatcher import Dispatcher
from app.event_agents.orchestrator.events import QuestionsGatheredEvent
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
            QuestionsGatheredEvent, self.handle_questions_gathered_event
        )

    async def initialize(self, session_id: UUID) -> list[QuestionAndAnswer]:
        questions = await self.gather_questions()
        questions_gathered_event = QuestionsGatheredEvent(
            questions=questions, session_id=session_id
        )
        await self.broker.publish(questions_gathered_event)

    async def handle_questions_gathered_event(self, event: QuestionsGatheredEvent):
        """
        Handle the questions gathered event.
        """
        logger.info(
            f"\nQuestions gathering complete. {len(event.questions)} questions gathered.\n"
        )
        websocket_frame = Dispatcher.package_and_transform_to_webframe(
            "Completed questions gathering.",
            "content",
            frame_id=str(uuid4()),
        )
        logger.info(f"websocket_frame: {websocket_frame.model_dump_json(indent=4)}")
        await self.broker.publish(websocket_frame)

    async def gather_questions(self) -> list[QuestionAndAnswer]:
        with open("config/artifacts.yaml", "r") as f:
            artifacts = yaml.safe_load(f)
        question_string = artifacts["artifacts"]["interview_questions"]
        logger.info(f"question_string: {question_string[:100]}")
        messages = [
            {"role": "user", "content": question_string},
        ]

        class Questions(BaseModel):
            questions: list[QuestionAndAnswer]

        response: Questions = await self.thinker.extract_structured_response(
            Questions, messages=messages, debug=True
        )
        return response.questions
