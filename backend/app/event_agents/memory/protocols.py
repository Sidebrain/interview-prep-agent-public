from typing import (
    Any,
    Dict,
    List,
    Optional,
    Protocol,
    runtime_checkable,
)
from uuid import UUID

from app.types.websocket_types import (
    AddressType,
    CompletionFrameChunk,
    WebsocketFrame,
)

# All memory related protocol definitions


class ConfigProvider(Protocol):
    """Protocol for configuration management."""

    def get_system_prompt(self) -> List[Dict[str, str]]: ...


class MessagePublisher(Protocol):
    """Protocol for publishing messages."""

    def publish(self, topic: str, frame: WebsocketFrame) -> None: ...


@runtime_checkable
class MemoryStore(Protocol):
    """Base protocol for storing and retrieving WebsocketFrames."""

    memory: List[WebsocketFrame]
    config_provider: ConfigProvider
    debug: bool

    # Optional identifiers that implementations may use
    agent_id: Optional[UUID] = None
    entity: Optional[Any] = None

    async def add(self, frame: WebsocketFrame) -> None: ...
    async def clear(self) -> None: ...
    def get(self) -> List[WebsocketFrame]: ...
    def find_parent_frame(
        self,
        completion_frame: CompletionFrameChunk,
        debug: bool = False,
    ) -> Optional[WebsocketFrame]: ...
    def extract_memory_for_generation(
        self,
        custom_user_instruction: Optional[str] = None,
        address_filter: List[AddressType] = [],
    ) -> List[Dict[str, str]]: ...
