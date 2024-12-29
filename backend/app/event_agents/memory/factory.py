from app.event_agents.memory.protocols import MemoryStore

from .providers import YAMLConfigProvider
from .store import InMemoryStore


def create_memory_store(
    config_path: str | None = None,
    debug: bool = False,
) -> MemoryStore:
    """Create a new memory store instance with all required dependencies."""
    return InMemoryStore(
        config_provider=YAMLConfigProvider(config_path),
        debug=debug,
    )
