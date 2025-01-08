import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from uuid import UUID

from app.event_agents.memory.protocols import ConfigProvider
from app.event_agents.memory.stores.types import EntityType
from app.types.websocket_types import (
    AddressType,
    CompletionFrameChunk,
    WebsocketFrame,
)

logger = logging.getLogger(__name__)


class BaseMemoryStore(ABC):
    """Base class for memory stores."""

    def __init__(
        self,
        config_provider: ConfigProvider,
        debug: bool = False,
        agent_id: Optional[UUID] = None,
        entity: Optional[EntityType] = None,
    ) -> None:
        self.config_provider = config_provider
        self.debug = debug
        self.agent_id = agent_id
        self.entity = entity
        self.memory: List[WebsocketFrame] = []

    def __repr__(self) -> str:
        base_repr = {
            "config_provider": self.config_provider,
            "debug": self.debug,
            "memory_frames": len(self.memory),
        }

        # Only include optional fields if they're set
        if self.agent_id:
            base_repr["agent_id"] = self.agent_id
        if self.entity:
            base_repr["entity"] = self.entity

        return "\n".join(f"  {k}={v}," for k, v in base_repr.items())

    @abstractmethod
    async def add(self, frame: WebsocketFrame) -> None:
        """Add a frame to memory."""
        raise NotImplementedError

    @abstractmethod
    async def clear(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self) -> List[WebsocketFrame]:
        raise NotImplementedError

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
