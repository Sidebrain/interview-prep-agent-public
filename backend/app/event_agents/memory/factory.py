from app.event_agents.memory.protocols import MemoryStore
from app.event_agents.memory.stores import MongoStore

from .providers import YAMLConfigProvider


def create_memory_store(
    config_path: str | None = None,
    debug: bool = False,
) -> MemoryStore:
    """Create a new memory store instance with all required dependencies."""
    return MongoStore(
        config_provider=YAMLConfigProvider(config_path),
        debug=debug,
    )
