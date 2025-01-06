import asyncio
import logging
from typing import List

from app.event_agents.evaluations.evaluator_base import (
    EvaluatorBase,
    T,
)
from app.event_agents.evaluations.registry import EvaluatorRegistry
from app.event_agents.orchestrator.commands import (
    GenerateEvaluationsCommand,
)
from app.event_agents.orchestrator.events import (
    EvaluationsGeneratedEvent,
)
from app.event_agents.types import InterviewContext
from app.types.interview_concept_types import (
    QuestionAndAnswer,
)
from app.types.websocket_types import WebsocketFrame

logger = logging.getLogger(__name__)


class EvaluationManager:
    def __init__(
        self,
        interview_context: InterviewContext,
        evaluator_registry: "EvaluatorRegistry",
    ) -> None:
        self.interview_context = interview_context
        self.evaluator_registry = evaluator_registry

    async def handle_evaluation_command(
        self, event: GenerateEvaluationsCommand
    ) -> None:
        """Handle the evaluation command."""
        evaluations = await self.generate_evaluations(event.questions)
        evaluations_generated_event = EvaluationsGeneratedEvent(
            evaluations=evaluations,
            interview_id=self.interview_context.interview_id,
        )
        await self.interview_context.broker.publish(
            evaluations_generated_event
        )

    async def generate_evaluations(
        self,
        questions: List[QuestionAndAnswer],
    ) -> list["WebsocketFrame"]:
        """
        Handle evaluations concurrently and yield results as they complete.
        """
        evaluation_tasks = []

        # tasks to initialize each evaluator
        evaluators = list(
            self.evaluator_registry.get_evaluators().values()
        )

        # tasks to evaluate each evaluator
        for evaluator in evaluators:
            task = self.run_evaluation(evaluator, questions)
            evaluation_tasks.append(task)

        # Run all evaluations concurrently and handle exceptions
        results = await asyncio.gather(*evaluation_tasks)
        filtered_frames = [
            result
            for result in results
            if isinstance(result, WebsocketFrame)
        ]
        return filtered_frames

    async def run_evaluation(
        self,
        evaluator: "EvaluatorBase[T]",
        questions: List[QuestionAndAnswer],
    ) -> "WebsocketFrame":
        """Helper method to run individual evaluations"""
        evaluation = await evaluator.evaluate(
            questions,
            self.interview_context,
            debug=True,
        )
        await self.interview_context.memory_store.add(evaluation)
        return evaluation

    async def handle_evaluations_generated(
        self, event: EvaluationsGeneratedEvent
    ) -> None:
        """Handle the evaluations generated event."""
        for evaluation in event.evaluations:
            await self.interview_context.broker.publish(evaluation)
