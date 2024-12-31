import logging

from app.event_agents.interview.question_manager import QuestionManager
from app.event_agents.orchestrator.commands import (
    GenerateEvaluationCommand,
    GeneratePerspectiveCommand,
)
from app.event_agents.orchestrator.events import (
    AddToMemoryEvent,
)
from app.event_agents.types import InterviewContext

logger = logging.getLogger(__name__)


class AnswerProcessor:
    def __init__(
        self,
        interview_context: InterviewContext,
        question_manager: QuestionManager,
    ) -> None:
        self.interview_context = interview_context
        self.question_manager = question_manager

    async def handler(self, event: AddToMemoryEvent) -> None:
        """Process the answer."""
        try:
            await self._add_answer_to_memory(event)
            await self._issue_appropriate_command()
            await self.question_manager.ask_next_question()
        except Exception as e:
            logger.error(
                f"Error in handle_add_to_memory_event: {str(e)}"
            )
            raise

    async def _add_answer_to_memory(
        self, event: AddToMemoryEvent
    ) -> None:
        """Add the answer to memory."""
        await self.interview_context.memory_store.add(event.frame)

    async def _issue_appropriate_command(self) -> None:
        try:
            if self.question_manager.current_question is None:
                return
            generate_evaluations_command = GenerateEvaluationCommand(
                questions=[self.question_manager.current_question]
            )
            await self.interview_context.broker.publish(
                generate_evaluations_command
            )
            generate_perspectives_command = GeneratePerspectiveCommand(
                questions=[self.question_manager.current_question]
            )
            await self.interview_context.broker.publish(
                generate_perspectives_command
            )
        except Exception as e:
            logger.error(
                f"Error in issue_appropriate_command: {str(e)}"
            )
            raise
