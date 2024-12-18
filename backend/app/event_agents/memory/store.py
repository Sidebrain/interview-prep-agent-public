import logging
from typing import Dict, List, Optional

from app.event_agents.memory.types import LongTermMemory
from app.types.websocket_types import (
    AddressType,
    CompletionFrameChunk,
    WebsocketFrame,
)

from .protocols import ConfigProvider

logger = logging.getLogger(__name__)


class InMemoryStore:
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
        self.memory: List[WebsocketFrame] = []
        self.config_provider = config_provider
        self.debug = debug

    def __repr__(self) -> str:
        return (
            f"MemoryStore(\n"
            f"  config_provider={self.config_provider},\n"
            f"  debug={self.debug},\n"
            f"  memory_frames={len(self.memory)},\n"
            f")"
        )

    async def add(self, frame: WebsocketFrame) -> None:
        """
        Add a frame to memory and publish update.

        Args:
            frame: The WebsocketFrame to add to memory

        Raises:
            TypeError: If frame is not an instance of WebsocketFrame
        """
        logger.debug(
            f"\033[32mAdding frame to memory: {frame.model_dump_json(indent=4)}\033[0m"
        )

        if not isinstance(frame, WebsocketFrame):
            raise TypeError(
                f"Expected WebsocketFrame but got {type(frame).__name__}"
            )

        self.memory.append(frame)

    def clear(self) -> None:
        """Clear all frames from memory."""
        self.memory = []

    def get(self) -> List[WebsocketFrame]:
        """Get all frames from memory."""
        return self.memory

    def find_parent_frame(
        self,
        completion_frame: CompletionFrameChunk,
        debug: bool = False,
    ) -> Optional[WebsocketFrame]:
        """Find parent frame for a completion chunk."""
        try:
            parent_frame = next(
                (
                    frame
                    for frame in reversed(self.memory)
                    if frame.frame.id == completion_frame.id
                )
            )
            if self.debug and debug:
                logger.debug(
                    f"Found parent frame: {parent_frame.model_dump_json(indent=4)}"
                )
            return parent_frame
        except StopIteration:
            if self.debug and debug:
                logger.debug(
                    f"No parent frame found for completion frame: {completion_frame.id}"
                )
                logger.debug(
                    "Available websocket frame, completion chunk ids"
                )
                logger.debug(
                    [
                        (
                            frame.frame.id,
                            frame.frame.content,
                        )
                        for frame in reversed(self.memory)
                    ]
                )
            return None

    def extract_memory_for_generation(
        self,
        custom_user_instruction: Optional[str] = None,
        address_filter: List[AddressType] = [],
    ) -> List[Dict[str, str]]:
        """Extract memory in format needed for generation."""
        logger.debug(
            "Extracting memory for generation",
            extra={
                "context": {
                    "address_filter": address_filter,
                    "current_memory_length": len(self.memory),
                    "custom_user_instruction": custom_user_instruction,
                }
            },
        )
        system = self.config_provider.get_system_prompt()

        memory_content = [
            {
                "role": message.frame.role,
                "content": message.frame.content or "",
            }
            for message in self.memory
            if not address_filter or message.address in address_filter
        ]

        if custom_user_instruction:
            memory_content.append(
                {
                    "role": "user",
                    "content": custom_user_instruction,
                }
            )

        return system + memory_content
