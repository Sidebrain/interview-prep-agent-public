import asyncio
import logging

from app.event_agents.orchestrator.commands import (
    GeneratePerspectiveCommand,
)
from app.event_agents.orchestrator.events import (
    PerspectivesGeneratedEvent,
)
from app.event_agents.perspectives.perspective_base import (
    PerspectiveBase,
)
from app.event_agents.perspectives.registry import PerspectiveRegistry
from app.event_agents.types import InterviewContext
from app.types.interview_concept_types import QuestionAndAnswer
from app.types.websocket_types import WebsocketFrame

logger = logging.getLogger(__name__)


class PerspectiveManager:
    def __init__(
        self,
        interview_context: "InterviewContext",
        perspective_registry: PerspectiveRegistry,
    ) -> None:
        self.interview_context = interview_context
        self.perspective_registry = perspective_registry

    def get_perspectives(self) -> dict[str, "PerspectiveBase"]:
        print("\033[91mgetting perspectives\033[0m")
        return self.perspective_registry.get_perspectives()

    async def handle_perspective_command(
        self, event: GeneratePerspectiveCommand
    ) -> None:
        """Handle the perspective command."""
        perspectives = await self.generate_perspectives(event.questions)
        perspectives_generated_event = PerspectivesGeneratedEvent(
            perspectives=perspectives,
            interview_id=self.interview_context.interview_id,
        )
        await self.interview_context.broker.publish(
            perspectives_generated_event
        )

    async def generate_perspectives(
        self, questions: list[QuestionAndAnswer]
    ) -> list[WebsocketFrame]:
        perspective_tasks = []

        # tasks to initialize each perspective
        perspectives = list(self.get_perspectives().values())

        # tasks to evaluate each perspective
        print(f"\033[91mperspectives: {len(perspectives)}\033[0m")
        for perspective in perspectives:
            task = perspective.evaluate(
                questions=questions,
                interview_context=self.interview_context,
            )
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

    async def handle_perspectives_generated(
        self, event: PerspectivesGeneratedEvent
    ) -> None:
        """Handle the perspectives generated event."""
        for perspective in event.perspectives:
            await self.interview_context.broker.publish(perspective)
