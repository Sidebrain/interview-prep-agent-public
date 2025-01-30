from dataclasses import dataclass
from uuid import UUID

from app.event_agents.memory.protocols import MemoryStore
from app.event_agents.orchestrator.broker import Broker
from app.event_agents.orchestrator.thinker import Thinker
from app.event_agents.questions.types import ConversationTree
from app.event_agents.schemas.mongo_schemas import (
    AgentProfile,
    Interviewer,
)
from app.event_agents.websocket_handler import Channel


@dataclass(frozen=True)
class InterviewContext:
    interview_id: UUID
    agent_id: UUID
    interviewer: Interviewer
    memory_store: MemoryStore
    broker: Broker
    thinker: Thinker
    channel: Channel
    agent_profile: AgentProfile
    conversation_tree: ConversationTree
    max_time_allowed: int
