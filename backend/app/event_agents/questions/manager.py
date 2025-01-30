import json
import logging
from uuid import uuid4

from app.agents.dispatcher import Dispatcher
from app.event_agents.interview.notifications import NotificationManager
from app.event_agents.orchestrator.events import AskQuestionEvent
from app.event_agents.questions.generation_strategies.base import (
    BaseQuestionGenerationStrategy,
)
from app.event_agents.questions.generation_strategies.interview import (
    InterviewQuestionGenerationStrategy,
)
from app.event_agents.schemas.mongo_schemas import Interviewer
from app.event_agents.types import InterviewContext
from app.types.interview_concept_types import (
    QuestionAndAnswer,
)

logger = logging.getLogger(__name__)


class QuestionManager:
    def __init__(
        self,
        interview_context: InterviewContext,
        interviewer: Interviewer,
        strategy: BaseQuestionGenerationStrategy | None = None,
    ) -> None:
        self.interview_context = interview_context
        self.questions: list[QuestionAndAnswer] = []
        self.current_question: QuestionAndAnswer | None = None
        self.interviewer = interviewer
        # defaults to interview question generation strategy
        self.strategy = strategy or InterviewQuestionGenerationStrategy(
            interview_context=interview_context
        )

    def __repr__(self) -> str:
        return json.dumps(
            {
                "type": "QuestionManager",
                "questions_remaining": len(self.questions),
                "current_question": (
                    self.current_question.question[:30] + "..."
                    if self.current_question
                    else None
                ),
            },
            indent=2,
        )

    async def initialize(self) -> None:
        try:
            self.questions = await self.strategy.initialize()
        except Exception as e:
            logger.error(
                "Error initializing question manager",
                extra={"context": {"error": str(e)}},
            )

    async def get_next_question(
        self,
    ) -> QuestionAndAnswer | None:
        try:
            self.current_question = self.questions.pop(0)
            logger.info("Next question ready: %s", self)
            return self.current_question
        except IndexError:
            logger.info("No more questions: %s", self)
            return None

    async def ask_next_question(self) -> None:
        """Request and publish next question."""
        next_question = await self.get_next_question()

        if next_question is None:
            logger.info("Interview complete: %s", self)
            await NotificationManager.send_notification(
                self.interview_context.broker,
                "Questions exhausted. Interview ended.",
            )
        else:
            # add the question to memory
            #! this needs a CQRS
            await self.add_questions_to_memory(next_question)

            await self.interview_context.broker.publish(
                AskQuestionEvent(
                    question=next_question,
                    interview_id=self.interview_context.interview_id,
                )
            )

    async def add_questions_to_memory(
        self, question: QuestionAndAnswer
    ) -> None:
        """Add questions to memory."""
        question_frame = Dispatcher.package_and_transform_to_webframe(
            question.question,  # type: ignore
            "content",
            frame_id=str(uuid4()),
        )
        await self.interview_context.memory_store.add(question_frame)
