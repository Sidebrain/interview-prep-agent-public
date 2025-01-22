import json
from abc import ABC, abstractmethod
from uuid import uuid4

from app.agents.dispatcher import Dispatcher
from app.event_agents.interview.notifications import NotificationManager
from app.event_agents.memory.json_encoders import AgentConfigJSONEncoder
from app.event_agents.questions.types import Questions
from app.event_agents.types import InterviewContext
from app.types.interview_concept_types import QuestionAndAnswer


class BaseQuestionGenerationStrategy(ABC):
    def __init__(self, interview_context: InterviewContext) -> None:
        self.interview_context = interview_context

    @abstractmethod
    async def build_structured_question_bank(self) -> None:
        raise NotImplementedError


class InterviewQuestionGenerationStrategy(
    BaseQuestionGenerationStrategy
):
    async def build_structured_question_bank(self) -> None:
        await NotificationManager.send_notification(
            self.interview_context.broker,
            "Interview started. Gathering questions from mongo...",
        )
        await self.gather_questions()
        await self.save_state()

        await NotificationManager.send_notification(
            self.interview_context.broker,
            "Questions gathered. Starting interview timer...",
        )
        return None

    def build_context_to_generate_structured_questions(
        self,
    ) -> list[dict[str, str]]:
        messages = [
            {
                "role": "user",
                "content": self.interview_context.interviewer.question_bank,
            },
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
        context = self.build_context_to_generate_structured_questions()

        response = await self.extract_structured_questions(context)
        self.questions = response.questions

        return response.questions

    async def save_state(self) -> None:
        question_bank_structured = json.dumps(
            self.questions, cls=AgentConfigJSONEncoder
        )
        self.interview_context.interviewer.question_bank_structured = (
            question_bank_structured
        )
        await self.interview_context.interviewer.save()

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
