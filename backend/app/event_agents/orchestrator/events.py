from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.types.websocket_types import WebsocketFrame


class BaseEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    correlation_id: UUID = Field(default_factory=uuid4)  # to track related events


class StartEvent(BaseEvent):
    session_id: UUID
    client_id: UUID


class WebsocketMessageEvent(BaseEvent):
    frame: WebsocketFrame
    session_id: UUID
    client_id: UUID


class ThinkEvent(BaseEvent):
    session_id: UUID
    client_id: UUID
    messages: list[dict[str, str]] = Field(default_factory=list)


class AddToMemoryEvent(BaseEvent):
    session_id: UUID
    frame: WebsocketFrame

class MessageReceivedEvent(BaseEvent):
    message: str
    session_id: UUID
