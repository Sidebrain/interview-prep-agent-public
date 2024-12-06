from abc import ABC, abstractmethod
import logging
from typing import List, Protocol, AsyncIterator
from typing import TYPE_CHECKING
from uuid import UUID
import asyncio

from app.event_agents.orchestrator.events import (
    AddToMemoryEvent,
)
from app.types.interview_concept_types import (
    QuestionAndAnswer,
)
from openai.types.chat import ChatCompletion

if TYPE_CHECKING:
    from app.event_agents.orchestrator.broker import Broker
    from app.event_agents.orchestrator.thinker import (
        Thinker,
    )
    from app.event_agents.evaluations.evaluator_base import (
        EvaluatorBase,
    )
    from app.event_agents.memory.protocols import (
        MemoryStore,
    )
    from app.types.websocket_types import WebsocketFrame
    from app.event_agents.evaluations.registry import EvaluatorRegistry

logger = logging.getLogger(__name__)


class EvaluationManager:
    def __init__(
        self,
        broker: "Broker",
        session_id: UUID,
        thinker: "Thinker",
        # evaluators: List["EvaluatorBase"],
        evaluator_registry: "EvaluatorRegistry",
        memory_store: "MemoryStore",
    ):
        self.session_id = session_id
        self.broker = broker
        self.thinker = thinker
        # self.evaluators = evaluators
        self.memory_store = memory_store
        self.evaluator_registry = evaluator_registry

    async def handle_evaluation(
        self,
        questions: List[QuestionAndAnswer],
    ) -> list["WebsocketFrame"]:
        """
        Handle evaluations concurrently and yield results as they complete.
        """
        evaluation_tasks = []

        # Create tasks for all evaluations
        for evaluator in self.evaluator_registry.get_evaluators():
            task = self.run_evaluation(evaluator, questions)
            evaluation_tasks.append(task)

        # Run all evaluations concurrently
        evaluation_frames = await asyncio.gather(*evaluation_tasks, return_exceptions=True)
        
        # Filter out any exceptions and log them
        filtered_frames = []
        for result in evaluation_frames:
            if isinstance(result, Exception):
                logger.error(
                    f"Evaluation failed: {str(result)}",
                    exc_info=True,
                )
            else:
                filtered_frames.append(result)

        return filtered_frames

    async def run_evaluation(self, evaluator, questions):
        """Helper method to run individual evaluations"""
        return await evaluator.evaluate(
            questions,
            self.memory_store,
            self.thinker,
        )
