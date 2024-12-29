from dataclasses import dataclass
from uuid import UUID

from app.event_agents.memory.protocols import MemoryStore
from app.event_agents.orchestrator.broker import Broker
from app.event_agents.orchestrator.thinker import Thinker


@dataclass(frozen=True)
class InterviewContext:
    interview_id: UUID
    agent_id: UUID
    memory_store: MemoryStore
    broker: Broker
    thinker: Thinker
