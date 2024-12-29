import logging
import traceback
from uuid import UUID

from fastapi import HTTPException, WebSocket
from pydantic import BaseModel, ValidationError

from app.event_agents.interview.manager import InterviewManager
from app.event_agents.memory.factory import create_memory_store
from app.event_agents.orchestrator import Broker, Thinker
from app.event_agents.types import AgentContext
from app.event_agents.websocket_handler import Channel

logger = logging.getLogger(__name__)


class InterviewConfig(BaseModel):
    interview_id: UUID
    agent_id: UUID
    max_time_allowed: int | None = None


class InterviewCollection(BaseModel):
    interviews: list[InterviewConfig]

    def find_by_interview_id(
        self, interview_id: UUID
    ) -> InterviewConfig | None:
        return next(
            (
                interview
                for interview in self.interviews
                if interview.interview_id == interview_id
            ),
            None,
        )


def load_all_interviews() -> InterviewCollection:
    with open("config/available_interviews.json", "r") as f:
        try:
            return InterviewCollection.model_validate_json(f.read())
        except ValidationError as e:
            logger.error(
                "Error validating interview config",
                extra={
                    "context": {
                        "error": str(e),
                        "stacktrace": traceback.format_exc(),
                    }
                },
            )
            raise HTTPException(
                status_code=500,
                detail="Error validating interview config",
            )


def create_interview(
    websocket: WebSocket, interview_id: UUID
) -> InterviewManager:
    interview_config = load_all_interviews().find_by_interview_id(
        interview_id
    )
    logger.debug(
        "Interview config",
        extra={"context": {"interview_config": interview_config}},
    )
    if not interview_config:
        raise HTTPException(
            status_code=404, detail="Interview not found"
        )

    broker = Broker()

    max_time_allowed = interview_config.max_time_allowed or 10 * 60

    channel = Channel(
        websocket=websocket,
        interview_id=interview_id,
        broker=broker,
    )

    thinker = Thinker()
    memory_store = create_memory_store()

    agent_context = AgentContext(
        agent_id=interview_config.agent_id,
        interview_id=interview_config.interview_id,
        memory_store=memory_store,
        broker=broker,
        thinker=thinker,
    )

    interview_manager = InterviewManager(
        agent_context=agent_context,
        memory_store=memory_store,
        agent_id=interview_config.agent_id,
        interview_id=interview_config.interview_id,
        channel=channel,
        broker=broker,
        thinker=thinker,
        max_time_allowed=max_time_allowed,
    )

    return interview_manager
