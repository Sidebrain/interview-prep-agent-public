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
        evaluation_frames = []

        # recieve once all the evaluations are done
        for evaluator in self.evaluator_registry.get_evaluators():
            try:
                evaluation_frame = await evaluator.evaluate(
                    questions,
                    self.memory_store,
                    self.thinker,
                )
                evaluation_frames.append(evaluation_frame)
            except Exception as e:
                logger.error(
                    f"Evaluation failed: {str(e)}",
                    exc_info=True,
                )
        return evaluation_frames
