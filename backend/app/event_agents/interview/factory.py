import logging
from uuid import UUID

from fastapi import HTTPException, WebSocket

from app.event_agents.conversations.tree import Tree
from app.event_agents.interview.manager import InterviewManager
from app.event_agents.memory.factory import create_memory_store
from app.event_agents.orchestrator import Broker, Thinker
from app.event_agents.schemas.mongo_schemas import (
    AgentProfile,
    Interviewer,
    InterviewSession,
)
from app.event_agents.types import InterviewAbilities, InterviewContext
from app.event_agents.websocket_handler import Channel

logger = logging.getLogger(__name__)


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

    agent_profile = await AgentProfile.find_one(
        {"interviewer_id": interviewer.id}
    )
    if not agent_profile:
        raise HTTPException(
            status_code=404, detail="Agent profile not found"
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

    conversation_tree = Tree(
        max_depth=4,
        max_breadth=6,
    )

    interview_abilities = InterviewAbilities(
        evaluations_enabled=True,
        perspectives_enabled=False,
    )

    interview_context = InterviewContext(
        interview_id=interview_session.id,  # type: ignore
        interview_abilities=interview_abilities,
        agent_id=interviewer.id,  # type: ignore
        interviewer=interviewer,
        agent_profile=agent_profile,
        memory_store=memory_store,
        broker=broker,
        thinker=thinker,
        channel=channel,
        max_time_allowed=max_time_allowed,
        conversation_tree=conversation_tree,
    )

    interview_manager = InterviewManager(
        interview_context=interview_context,
    )

    return interview_manager
