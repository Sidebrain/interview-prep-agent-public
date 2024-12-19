import json
import logging
from typing import TYPE_CHECKING

import yaml
from pydantic import BaseModel

from app.event_agents.types import AgentContext
from app.types.interview_concept_types import (
    QuestionAndAnswer,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class Questions(BaseModel):
    questions: list[QuestionAndAnswer]


class QuestionManager:
    def __init__(
        self,
        agent_context: "AgentContext",
        question_file_path: str | None = None,
    ):
        self.agent_context = agent_context
        self.thinker = agent_context.thinker
        self.questions: list[QuestionAndAnswer] = []
        self.current_question: QuestionAndAnswer | None = None
        self.question_file_path = (
            question_file_path or "config/artifacts_v2.yaml"
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

    def get_question_generation_messages(
        self, question_file_path: str | None = None
    ) -> list[dict[str, str]]:
        question_file_path = (
            question_file_path or self.question_file_path
        )
        with open(self.question_file_path, "r") as f:
            artifacts = yaml.safe_load(f)
        question_string = artifacts["interview questions"]

        messages = [
            {"role": "user", "content": question_string},
        ]
        return messages

    async def extract_structured_questions(
        self, messages: list[dict[str, str]]
    ) -> Questions:
        return await self.thinker.extract_structured_response(
            Questions, messages=messages, debug=True
        )

    async def gather_questions(
        self,
    ) -> list[QuestionAndAnswer]:
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

        context = self.get_question_generation_messages()

        response = await self.extract_structured_questions(context)
        self.questions = response.questions

        logger.info("Questions prepared: %s", self)
        return response.questions

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
