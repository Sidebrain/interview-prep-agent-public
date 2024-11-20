from typing import Optional, List, Dict
from .protocols import ConfigProvider, MessagePublisher
from app.types.websocket_types import WebsocketFrame, CompletionFrameChunk, AddressType

import logging

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
        # memory_topic: str,
        config_provider: ConfigProvider,
        message_publisher: MessagePublisher,
        debug: bool = False,
    ):
        self.memory: List[WebsocketFrame] = []
        # self.memory_topic = memory_topic
        self.config_provider = config_provider
        self.message_publisher = message_publisher
        self.debug = debug

    async def add(self, frame: WebsocketFrame) -> None:
        """Add a frame to memory and publish update."""
        logger.info(f"Adding frame to memory: {frame.model_dump_json(indent=4)}")
        self.memory.append(frame)
        # self.message_publisher.publish(self.memory_topic, frame)

    def clear(self) -> None:
        """Clear all frames from memory."""
        self.memory = []

    def get(self) -> List[WebsocketFrame]:
        """Get all frames from memory."""
        return self.memory.copy()  # Return copy to prevent external modification

    def find_parent_frame(
        self, completion_frame: CompletionFrameChunk, debug: bool = False
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
                logger.debug("Available websocket frame, completion chunk ids")
                logger.debug(
                    [
                        (frame.frame.id, frame.frame.content)
                        for frame in reversed(self.memory)
                    ]
                )
            return None

    def extract_memory_for_generation(
        self,
        custom_user_instruction: Optional[Dict[str, str]] = None,
        address_filter: List[AddressType] = [],
    ) -> List[Dict[str, str]]:
        """Extract memory in format needed for generation."""
        system = self.config_provider.get_system_prompt()

        memory_content = [
            {
                "role": message.frame.role,
                "content": message.frame.content,
            }
            for message in self.memory
            if not address_filter or message.address in address_filter
        ]

        if custom_user_instruction:
            memory_content.append(custom_user_instruction)

        return system + memory_content
