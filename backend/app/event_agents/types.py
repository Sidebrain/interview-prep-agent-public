from dataclasses import dataclass
from uuid import UUID

from app.event_agents.memory.protocols import MemoryStore
from app.event_agents.orchestrator.broker import Broker
from app.event_agents.orchestrator.thinker import Thinker


@dataclass
class AgentContext:
    agent_id: UUID
    session_id: UUID
    broker: Broker
    thinker: Thinker
    memory_store: MemoryStore
