from app.event_agents.orchestrator.events import (
    EvaluationsGeneratedEvent,
)
from app.event_agents.types import InterviewContext


class EvaluationsGeneratedEventHandler:
    def __init__(self, interview_context: InterviewContext) -> None:
        self.interview_context = interview_context

    async def handler(self, event: EvaluationsGeneratedEvent) -> None:
        for evaluation in event.evaluations:
            await self.interview_context.broker.publish(evaluation)
