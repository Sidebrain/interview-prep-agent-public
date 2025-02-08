import logging
from abc import ABC, abstractmethod

from app.types.interview_concept_types import QuestionAndAnswer

logger = logging.getLogger(__name__)


class AskingStrategy(ABC):
    def __init__(self, questions: list[QuestionAndAnswer]) -> None:
        self.questions = questions

    @abstractmethod
    async def get_next_question(self) -> QuestionAndAnswer | None:
        raise NotImplementedError


class BaseQuestionAskingStrategy(AskingStrategy):
    def __init__(self, questions: list[QuestionAndAnswer]) -> None:
        self.questions = questions

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
    def __init__(self, questions: list[QuestionAndAnswer]) -> None:
        super().__init__(questions)

    async def get_next_question(self) -> QuestionAndAnswer | None:
        return await super().get_next_question()


class Prober:
    def __init__(
        self, parent_question: QuestionAndAnswer
    ) -> None:
        self.parent_question = parent_question

    def get_next_question(
        self, question: QuestionAndAnswer
    ) -> QuestionAndAnswer | None:
        return None
