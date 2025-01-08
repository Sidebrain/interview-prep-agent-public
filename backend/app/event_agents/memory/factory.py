from uuid import UUID

from app.event_agents.memory.protocols import MemoryStore
from app.event_agents.memory.stores import MongoStore
from app.event_agents.memory.stores.mongo import EntityType

from .providers import YAMLConfigProvider


def create_memory_store(
    agent_id: UUID,
    entity: EntityType,
    config_path: str | None = None,
    debug: bool = False,
) -> MemoryStore:
    """Create a new memory store instance with all required dependencies."""
    return MongoStore(
        agent_id=agent_id,
        config_provider=YAMLConfigProvider(config_path),
        entity=entity,
        debug=debug,
    )
