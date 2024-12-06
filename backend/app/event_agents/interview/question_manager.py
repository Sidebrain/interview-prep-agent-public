import logging
import json

from typing import TYPE_CHECKING
from pydantic import BaseModel
import yaml

from app.types.interview_concept_types import (
    QuestionAndAnswer,
)

if TYPE_CHECKING:
    from app.event_agents.orchestrator.thinker import (
        Thinker,
    )
    from app.event_agents.orchestrator.broker import Broker

logger = logging.getLogger(__name__)

class QuestionManager:
    def __init__(self, thinker: "Thinker"):
        self.thinker = thinker
        self.questions: list[QuestionAndAnswer] = []
        self.current_question: QuestionAndAnswer | None = None

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

    async def gather_questions(
        self,
    ) -> list[QuestionAndAnswer]:
        """
        Load and process interview questions from the configuration file.

        Reads questions template from config/artifacts.yaml,
        processes it through the thinker to generate structured questions.

        Returns:
            list[QuestionAndAnswer]: List of structured interview questions
        """
        logger.info(
            "Gathering questions",
            extra={
                "context": {
                    "questions_remaining": len(self.questions),
                    "current_question": (
                        self.current_question.question[:30] + "..."
                        if self.current_question
                        else None
                    ),
                }
            },
        )

        with open("config/artifacts_v2.yaml", "r") as f:
            artifacts = yaml.safe_load(f)
        question_string = artifacts["interview questions"]

        messages = [
            {"role": "user", "content": question_string},
        ]

        class Questions(BaseModel):
            questions: list[QuestionAndAnswer]

        response: Questions = await self.thinker.extract_structured_response(
            Questions, messages=messages, debug=True
        )
        self.questions = response.questions

        logger.info("Questions prepared: %s", self)
        return response.questions

    async def get_next_question(self) -> QuestionAndAnswer:
        """
        Retrieve the next question from the question queue.

        Returns:
            QuestionAndAnswer: The next question to be asked
            None: If no questions remain
        """
        try:
            self.current_question = self.questions.pop(0)
            logger.info("Next question ready: %s", self)
            return self.current_question
        except IndexError:
            logger.info("No more questions: %s", self)
            return None

