import logging
import traceback
from uuid import UUID

from fastapi import HTTPException, WebSocket
from pydantic import BaseModel, ValidationError

from app.event_agents.interview.manager import InterviewManager
from app.event_agents.memory.factory import create_memory_store
from app.event_agents.orchestrator import Broker, Thinker
from app.event_agents.schemas.mongo_schemas import (
    Interviewer,
    InterviewSession,
)
from app.event_agents.types import InterviewContext
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


async def create_interview(
    websocket: WebSocket, interview_session_id: UUID
) -> "InterviewManager":
    interview_session = await InterviewSession.get(interview_session_id)
    if not interview_session:
        raise HTTPException(
            status_code=404, detail="Interview session not found"
        )

    interviewer = await Interviewer.get(
        interview_session.interviewer_id
    )
    if not interviewer:
        raise HTTPException(
            status_code=404, detail="Interviewer not found"
        )

    broker = Broker()

    max_time_allowed = interview_session.max_time_allowed or 10 * 60

    channel = Channel(
        websocket=websocket,
        interview_id=interview_session_id,
        broker=broker,
    )

    thinker = Thinker()
    memory_store = create_memory_store(
        agent_id=interview_session.interviewer_id,
        entity=interview_session,
    )

    interview_context = InterviewContext(
        interview_id=interview_session.id,
        agent_id=interviewer.id,
        interviewer=interviewer,
        memory_store=memory_store,
        broker=broker,
        thinker=thinker,
        channel=channel,
        max_time_allowed=max_time_allowed,
    )

    interview_manager = InterviewManager(
        interview_context=interview_context,
    )

    return interview_manager
