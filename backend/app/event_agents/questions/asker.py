import logging
from abc import ABC

from app.types.interview_concept_types import QuestionAndAnswer

logger = logging.getLogger(__name__)


class BaseQuestionAskingStrategy(ABC):
    def __init__(self, questions: list[QuestionAndAnswer]) -> None:
        self.questions = questions
        self.current_question = self.questions.pop(0)

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
