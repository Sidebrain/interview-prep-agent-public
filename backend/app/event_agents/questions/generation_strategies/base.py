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
        self.questions: list[QuestionAndAnswer] = []

    @abstractmethod
    async def prepare_question_context(
        self,
    ) -> list[dict[str, str]]:
        raise NotImplementedError

    async def initialize(self) -> None:
        if self.are_questions_gathered_in_memory():
            questions_loaded_successfully = (
                await self.load_questions_from_memory()
            )
            await NotificationManager.send_notification(
                self.interview_context.broker,
                f"{len(self.questions)} questions loaded from agent profile mongo memory",
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
        await self.prepare_interview()
        # load the questions from the strategy
        self.questions = self.questions

    def are_questions_gathered_in_memory(self) -> bool:
        if self.interview_context.agent_profile.question_bank_structured:
            return True
        else:
            return False

    async def load_questions_from_memory(self) -> bool:
        try:
            #! this is a hack to get the questions from the mongo memory
            #! we need to fix this later
            # First parse the string into a Python list
            questions_list = json.loads(
                self.interview_context.agent_profile.question_bank_structured
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
                "Questions loaded from mongo agent profile memory",
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

    async def prepare_interview(self) -> None:
        await NotificationManager.send_notification(
            self.interview_context.broker,
            "Interview started. Building question bank...",
        )
        await self.gather_questions()
        await self.persist_questions()

        await NotificationManager.send_notification(
            self.interview_context.broker,
            "Question bank built. Starting interview timer...",
        )
        return None

    async def persist_questions(self) -> None:
        logger.info(
            "Persisting questions",
            extra={
                "context": {
                    "questions_length": len(self.questions),
                    "question #1": self.questions[0],
                }
            },
        )
        question_bank_structured = json.dumps(
            self.questions, cls=AgentConfigJSONEncoder
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
        self.questions = response.questions

        return response.questions
