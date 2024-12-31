from app.event_agents.orchestrator.events import (
    PerspectivesGeneratedEvent,
)
from app.event_agents.types import InterviewContext


class PerspectiveGeneratedEventHandler:
    def __init__(self, interview_context: InterviewContext) -> None:
        self.interview_context = interview_context

    async def handler(self, event: PerspectivesGeneratedEvent) -> None:
        for perspective in event.perspectives:
            await self.interview_context.broker.publish(perspective)
