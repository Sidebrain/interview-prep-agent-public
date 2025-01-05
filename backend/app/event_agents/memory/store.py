import logging
from typing import List

from app.event_agents.memory.base_memory_store import BaseMemoryStore
from app.types.websocket_types import (
    WebsocketFrame,
)

from .protocols import ConfigProvider

logger = logging.getLogger(__name__)


class InMemoryStore(BaseMemoryStore):
    """
    In-memory implementation of MemoryStore protocol with publishing capabilities.

    This implementation stores WebsocketFrames in memory, provides search capabilities,
    and publishes updates to subscribers.

    Implements:
        MemoryStore (Protocol): Interface for memory storage operations
    """

    def __init__(
        self,
        config_provider: ConfigProvider,
        debug: bool = False,
    ) -> None:
        super().__init__(config_provider, debug)


    async def add(self, frame: WebsocketFrame) -> None:
        if not isinstance(frame, WebsocketFrame):
            raise TypeError(
                f"Expected WebsocketFrame but got {type(frame).__name__}"
            )

        self.memory.append(frame)
        self.save_state()

    def save_state(self) -> None:
        """Save all frames to a file."""
        with open("config/memory.json", "w") as file:
            file.write(
                "\n".join(
                    frame.model_dump_json(indent=4)
                    for frame in self.memory
                )
            )

    def clear(self) -> None:
        """Clear all frames from memory."""
        self.memory = []

    def get(self) -> List[WebsocketFrame]:
        """Get all frames from memory."""
        return self.memory
