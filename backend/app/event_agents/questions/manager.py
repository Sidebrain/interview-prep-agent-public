import json
import logging
from uuid import uuid4

from app.agents.dispatcher import Dispatcher
from app.event_agents.interview.notifications import NotificationManager
from app.event_agents.memory.json_decoders import AgentConfigJSONDecoder
from app.event_agents.orchestrator.events import AskQuestionEvent
from app.event_agents.questions.generation_strategies import (
    BaseQuestionGenerationStrategy,
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

    def are_questions_gathered_in_memory(self) -> bool:
        if self.interviewer.question_bank_structured:
            return True
        else:
            return False

    async def load_questions_from_memory(self) -> bool:
        try:
            #! this is a hack to get the questions from the mongo memory
            #! we need to fix this later
            # First parse the string into a Python list
            questions_list = json.loads(
                self.interviewer.question_bank_structured
            )
            # Then create the structure expected by the decoder
            dct = {"questions": questions_list}
            # Finally decode with our custom decoder
            decoded = json.loads(
                json.dumps(dct),  # Convert dict to JSON string
                cls=AgentConfigJSONDecoder,
            )
            self.questions = decoded["questions"]

            logger.info(
                "Questions loaded from mongo memory",
                extra={
                    "context": {
                        "#questions": len(self.questions),
                        "question #1": self.questions[0],
                    }
                },
            )
            return True
        except Exception as e:
            logger.error(
                "Error loading questions from mongo memory",
                extra={"context": {"error": str(e)}},
            )
            return False

    async def initialize(self) -> None:
        if self.are_questions_gathered_in_memory():
            questions_loaded_successfully = (
                await self.load_questions_from_memory()
            )
            await NotificationManager.send_notification(
                self.interview_context.broker,
                f"{len(self.questions)} questions loaded from mongo memory",
            )
            logger.debug(
                "Questions loaded from memory",
                extra={
                    "context": {
                        "#questions": len(self.questions),
                    }
                },
            )

            if questions_loaded_successfully:
                return

        # If questions are not loaded from memory, gather them
        await self.strategy.build_structured_question_bank()

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
