import logging
from abc import ABC, abstractmethod

from app.event_agents.types import InterviewContext
from app.types.interview_concept_types import QuestionAndAnswer

logger = logging.getLogger(__name__)


class AskingStrategy(ABC):
    def __init__(
        self,
        questions: list[QuestionAndAnswer],
        interview_context: InterviewContext,
    ) -> None:
        self.questions = questions
        self.interview_context = interview_context

    @abstractmethod
    async def get_next_question(self) -> QuestionAndAnswer | None:
        raise NotImplementedError


class BaseQuestionAskingStrategy(AskingStrategy):
    async def get_next_question(
        self,
    ) -> QuestionAndAnswer | None:
        try:
            current_question = self.questions.pop(0)
            logger.info("Next question ready: %s", self)
            return current_question
        except IndexError:
            logger.info("No more questions: %s", self)
            return None


class DynamicQuestionAskingStrategy(BaseQuestionAskingStrategy):
    async def get_next_question(self) -> QuestionAndAnswer | None:
        store = self.interview_context.memory_store
        thinker = self.interview_context.thinker

        context = store.extract_memory_for_generation(
            custom_user_instruction="""
            You are responsible for generating questions on the fly based on the conversation history.
            Your purpose is to get the candidate to open up and share their true thoughts and feelings.
            You should ask open-ended questions that allow the candidate to speak at length.
            Your central purpose is to get the information from the candidate to build up their resume.
            """
        )
        next_question = await thinker.extract_structured_response(
            pydantic_structure_to_extract=QuestionAndAnswer,
            messages=context,
        )
        logger.debug(
            "Next question generated",
            extra={
                "context": {
                    "strategy": "dynamic",
                    "next_question": next_question.model_dump(),
                    "context-length": len(context),
                    "context": context,
                }
            },
        )
        return next_question


class Prober:
    def __init__(self, parent_question: QuestionAndAnswer) -> None:
        self.parent_question = parent_question

    def get_next_question(
        self, question: QuestionAndAnswer
    ) -> QuestionAndAnswer | None:
        return None
