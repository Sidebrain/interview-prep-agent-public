import json
import logging
from abc import ABC, abstractmethod

from app.event_agents.interview.notifications import NotificationManager
from app.event_agents.memory.json_decoders import AgentConfigJSONDecoder
from app.event_agents.memory.json_encoders import AgentConfigJSONEncoder
from app.event_agents.questions.types import Questions
from app.event_agents.types import InterviewContext
from app.types.interview_concept_types import QuestionAndAnswer

logger = logging.getLogger(__name__)


class BaseQuestionGenerationStrategy(ABC):
    def __init__(self, interview_context: InterviewContext) -> None:
        self.interview_context = interview_context

    @abstractmethod
    async def prepare_question_context(
        self,
    ) -> list[dict[str, str]]:
        raise NotImplementedError

    async def initialize(self) -> list[QuestionAndAnswer]:
        if self.are_questions_gathered_in_memory():
            questions_loaded_successfully = (
                await self.try_load_questions_from_memory()
            )
            await NotificationManager.send_notification(
                self.interview_context.broker,
                f"{len(questions_loaded_successfully)} questions loaded from agent profile mongo memory",
            )
            logger.debug(
                "Questions loaded from memory",
                extra={
                    "context": {
                        "#questions": len(
                            questions_loaded_successfully
                        ),
                    }
                },
            )

            return questions_loaded_successfully

        # If questions are not loaded from memory, gather them
        questions = await self.prepare_interview()
        return questions

    def are_questions_gathered_in_memory(self) -> bool:
        if self.interview_context.agent_profile.question_bank_structured:
            return True
        else:
            return False

    def _parse_structured_questions(
        self, json_str: str
    ) -> list[QuestionAndAnswer]:
        """Parse structured questions from JSON string into QuestionAndAnswer objects."""
        questions_list = json.loads(json_str)
        decoded = json.loads(
            json.dumps({"questions": questions_list}),
            cls=AgentConfigJSONDecoder,
        )
        return decoded["questions"]  # type: ignore

    async def try_load_questions_from_memory(
        self,
    ) -> list[QuestionAndAnswer]:
        """Attempt to load questions from agent profile memory."""
        try:
            structured_data = self.interview_context.agent_profile.question_bank_structured
            questions = self._parse_structured_questions(
                structured_data
            )

            logger.info(
                "Questions loaded from mongo agent profile memory",
                extra={
                    "context": {
                        "#questions": len(questions),
                        "question #1": questions[0],
                    }
                },
            )

            return questions

        except Exception as e:
            logger.error(
                "Error loading questions from mongo memory",
                extra={"context": {"error": str(e)}},
            )
            return []

    async def prepare_interview(self) -> list[QuestionAndAnswer]:
        await NotificationManager.send_notification(
            self.interview_context.broker,
            "Interview started. Building question bank...",
        )
        questions = await self.gather_questions()
        await self.persist_questions(questions)

        await NotificationManager.send_notification(
            self.interview_context.broker,
            "Question bank built. Starting interview timer...",
        )
        return questions

    async def persist_questions(
        self, questions: list[QuestionAndAnswer]
    ) -> None:
        logger.info(
            "Persisting questions",
            extra={
                "context": {
                    "questions_length": len(questions),
                    "question #1": questions[0],
                }
            },
        )
        question_bank_structured = json.dumps(
            questions, cls=AgentConfigJSONEncoder
        )
        self.interview_context.agent_profile.question_bank_structured = question_bank_structured
        await self.interview_context.agent_profile.save()
        logger.info(
            "Questions persisted",
        )

    async def extract_structured_questions(
        self, messages: list[dict[str, str]]
    ) -> Questions:
        structured_questions = await self.interview_context.thinker.extract_structured_response(
            Questions, messages=messages, debug=True
        )
        logger.info(
            "Structured questions generated",
            extra={
                "context": {
                    "structured_questions_length": len(
                        structured_questions.questions
                    ),
                },
            },
        )
        return structured_questions

    async def gather_questions(
        self,
    ) -> list[QuestionAndAnswer]:
        context = await self.prepare_question_context()

        response = await self.extract_structured_questions(context)

        return response.questions
