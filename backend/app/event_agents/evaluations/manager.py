import asyncio
import logging
from typing import TYPE_CHECKING, List

from app.event_agents.evaluations.evaluator_base import T
from app.event_agents.types import AgentContext
from app.types.interview_concept_types import (
    QuestionAndAnswer,
)
from app.types.websocket_types import WebsocketFrame

if TYPE_CHECKING:
    from app.event_agents.evaluations.evaluator_base import (
        EvaluatorBase,
    )
    from app.event_agents.evaluations.registry import EvaluatorRegistry
    from app.types.websocket_types import WebsocketFrame

logger = logging.getLogger(__name__)


class EvaluationManager:
    def __init__(
        self,
        agent_context: "AgentContext",
        evaluator_registry: "EvaluatorRegistry",
    ) -> None:
        self.agent_context = agent_context
        self.evaluator_registry = evaluator_registry

    async def handle_evaluation(
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
        return await evaluator.evaluate(
            questions,
            self.agent_context,
            debug=True,
        )
