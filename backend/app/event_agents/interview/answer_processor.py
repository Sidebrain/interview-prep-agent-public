import asyncio
import logging

from app.event_agents.evaluations.manager import EvaluationManager
from app.event_agents.interview.question_manager import QuestionManager
from app.event_agents.orchestrator.events import (
    AddToMemoryEvent,
)
from app.event_agents.perspectives.manager import PerspectiveManager
from app.event_agents.types import InterviewContext
from app.types.websocket_types import WebsocketFrame

logger = logging.getLogger(__name__)


class AnswerProcessor:
    def __init__(
        self,
        interview_context: InterviewContext,
        question_manager: QuestionManager,
        evaluation_manager: EvaluationManager,
        perspective_manager: PerspectiveManager,
    ) -> None:
        self.interview_context = interview_context
        self.question_manager = question_manager
        self.evaluation_manager = evaluation_manager
        self.perspective_manager = perspective_manager

    async def handler(self, event: AddToMemoryEvent) -> None:
        """Process the answer."""
        try:
            await self._add_answer_to_memory(event)
            await self._generate_evaluations_and_perspectives()
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

    async def _generate_evaluations_and_perspectives(self) -> None:
        """Generate and publish evaluations and perspectives for the current question."""
        evaluations, perspectives = await asyncio.gather(
            self._generate_evaluations(), self._generate_perspectives()
        )

        logger.info(
            "Answer processed",
            extra={
                "manager": self,
                "evaluation_count": len(evaluations),
                "perspective_count": len(perspectives),
            },
        )

        await self._publish_results(evaluations, perspectives)

    async def _generate_evaluations(self) -> list[WebsocketFrame]:
        """Generate evaluations for the current question."""
        if self.question_manager.current_question is None:
            return []
        evaluations = await self.evaluation_manager.handle_evaluation(
            questions=[self.question_manager.current_question]
        )
        logger.info(
            "Evaluations generated",
            extra={
                "context": {
                    "evaluation_count": len(evaluations),
                }
            },
        )
        return evaluations

    async def _generate_perspectives(self) -> list[WebsocketFrame]:
        """Generate perspectives for the current question."""
        if self.question_manager.current_question is None:
            return []
        perspectives = (
            await self.perspective_manager.handle_perspective(
                questions=[self.question_manager.current_question]
            )
        )
        logger.info(
            "Perspectives generated",
            extra={
                "context": {
                    "manager": self,
                    "perspective_count": len(perspectives),
                }
            },
        )
        return perspectives

    async def _publish_results(
        self,
        evaluations: list[WebsocketFrame],
        perspectives: list[WebsocketFrame],
    ) -> None:
        """Publish evaluations and perspectives to the broker."""
        for evaluation in evaluations:
            await self.interview_context.broker.publish(evaluation)
        for perspective in perspectives:
            await self.interview_context.broker.publish(perspective)

    def _get_answer_length(
        self, new_memory_event: AddToMemoryEvent
    ) -> int:
        """Calculate the length of the answer content."""
        return (
            len(new_memory_event.frame.frame.content)
            if new_memory_event.frame.frame.content
            else 0
        )
