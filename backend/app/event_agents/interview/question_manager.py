import json
import logging
from uuid import uuid4

import yaml
from pydantic import BaseModel

from app.agents.dispatcher import Dispatcher
from app.event_agents.interview.notifications import NotificationManager
from app.event_agents.memory.config_builder import ConfigBuilder
from app.event_agents.orchestrator.events import AskQuestionEvent
from app.event_agents.types import InterviewContext
from app.types.interview_concept_types import (
    QuestionAndAnswer,
)

logger = logging.getLogger(__name__)


class Questions(BaseModel):
    questions: list[QuestionAndAnswer]


class QuestionManager:
    def __init__(
        self,
        interview_context: InterviewContext,
        question_file_path: str | None = None,
    ) -> None:
        self.interview_context = interview_context
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

    def are_questions_gathered_in_memory(self) -> bool:
        try:
            return "questions" in ConfigBuilder.load_state(
                self.interview_context.agent_id
            )
        except FileNotFoundError:
            return False

    async def load_questions_from_memory(self) -> bool:
        loaded_state = ConfigBuilder.load_state(
            self.interview_context.agent_id
        )
        if "questions" in loaded_state:
            self.questions = loaded_state["questions"]
            await NotificationManager.send_notification(
                self.interview_context.broker,
                "Questions loaded from memory",
            )
            return True
        else:
            logger.info("No questions found in memory")
            return False

    async def initialize(self) -> None:
        if self.are_questions_gathered_in_memory():
            questions_loaded_successfully = (
                await self.load_questions_from_memory()
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
        await NotificationManager.send_notification(
            self.interview_context.broker,
            "Interview started. Gathering questions...",
        )
        await self.gather_questions()

        await NotificationManager.send_notification(
            self.interview_context.broker,
            "Questions gathered. Starting interview timer...",
        )
        return None

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
        return await self.interview_context.thinker.extract_structured_response(
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

    def save_state(self) -> None:
        ConfigBuilder.save_state(
            self.interview_context.agent_id,
            {"questions": self.questions},
        )

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
