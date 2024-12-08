from .store import InMemoryStore
from .providers import YAMLConfigProvider, PubSubMessagePublisher


def create_memory_store(
    # memory_topic: str,
    config_path: str | None = None,
    debug: bool = False,
) -> InMemoryStore:
    """Create a new memory store instance with all required dependencies."""
    return InMemoryStore(
        # memory_topic=memory_topic,
        config_provider=YAMLConfigProvider(config_path),
        message_publisher=PubSubMessagePublisher(),
        debug=debug,
    )
