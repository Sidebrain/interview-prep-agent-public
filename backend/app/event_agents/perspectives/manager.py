import asyncio
import logging

from app.event_agents.memory.protocols import MemoryStore
from app.event_agents.perspectives.perspective_base import (
    PerspectiveBase,
)
from app.event_agents.perspectives.registry import PerspectiveRegistry
from app.types.interview_concept_types import QuestionAndAnswer
from app.types.websocket_types import WebsocketFrame

logger = logging.getLogger(__name__)


class PerspectiveManager:
    def __init__(
        self,
        perspective_registry: PerspectiveRegistry,
        memory_store: "MemoryStore",
    ) -> None:
        self.perspective_registry = perspective_registry
        self.memory_store = memory_store

    def get_perspectives(self) -> dict[str, PerspectiveBase]:
        print("\033[91mgetting perspectives\033[0m")
        return self.perspective_registry.get_perspectives()

    async def handle_perspective(
        self, questions: list[QuestionAndAnswer]
    ) -> list[WebsocketFrame]:
        perspective_tasks = []

        # tasks to initialize each perspective
        perspectives = list(self.get_perspectives().values())

        # tasks to evaluate each perspective
        print(f"\033[91mperspectives: {len(perspectives)}\033[0m")
        for perspective in perspectives:
            task = perspective.evaluate(questions, self.memory_store)
            perspective_tasks.append(task)

        # run all perspective evaluations concurrently
        perspective_frames = await asyncio.gather(*perspective_tasks)

        # Filter out any exceptions and log them
        filtered_frames = []
        for result in perspective_frames:
            if isinstance(result, Exception):
                logger.error(
                    f"Perspective evaluation failed: {str(result)}",
                    exc_info=True,
                )
            else:
                filtered_frames.append(result)
        return filtered_frames
