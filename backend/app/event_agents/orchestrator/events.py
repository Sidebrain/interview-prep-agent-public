from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.types.interview_concept_types import QuestionAndAnswer
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


class AddToMemoryEvent(BaseEvent):
    session_id: UUID
    frame: WebsocketFrame


class MessageReceivedEvent(BaseEvent):
    message: str
    session_id: UUID


class Status(Enum):
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"
    idle = "idle"


class QuestionsGatheringEvent(BaseEvent):
    status: Status
    questions: list[QuestionAndAnswer]
    session_id: UUID


class UserReadyEvent(BaseEvent):
    session_id: UUID
    questions: list[QuestionAndAnswer]
