from typing import Protocol, Optional, List, Dict
from app.types.websocket_types import WebsocketFrame, CompletionFrameChunk, AddressType

# All memory related protocol definitions

class MemoryStore(Protocol):
    """Base protocol for storing and retrieving WebsocketFrames."""
    def add(self, frame: WebsocketFrame) -> None: ...
    def clear(self) -> None: ...
    def get(self) -> List[WebsocketFrame]: ...
    def find_parent_frame(self, completion_frame: CompletionFrameChunk) -> Optional[WebsocketFrame]: ...
    def extract_memory_for_generation(
        self,
        custom_user_instruction: Optional[Dict[str, str]] = None,
        address_filter: List[AddressType] = []
    ) -> List[Dict[str, str]]: ...

class ConfigProvider(Protocol):
    """Protocol for configuration management."""
    def get_system_prompt(self) -> List[Dict[str, str]]: ...

class MessagePublisher(Protocol):
    """Protocol for publishing messages."""
    def publish(self, topic: str, frame: WebsocketFrame) -> None: ...
