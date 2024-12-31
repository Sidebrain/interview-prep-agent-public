from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.types.interview_concept_types import QuestionAndAnswer
from app.types.websocket_types import WebsocketFrame


class BaseEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    timestamp: int = Field(
        default_factory=lambda: int(datetime.now().timestamp())
    )
    correlation_id: UUID = Field(
        default_factory=uuid4
    )  # to track related events


class WebsocketMessageEvent(BaseEvent):
    frame: WebsocketFrame
    interview_id: UUID
    client_id: UUID


class ErrorEvent(BaseEvent):
    error: str
    interview_id: UUID


class AddToMemoryEvent(BaseEvent):
    interview_id: UUID
    frame: WebsocketFrame


class MessageReceivedEvent(BaseEvent):
    message: str
    interview_id: UUID


class AskQuestionEvent(BaseEvent):
    question: QuestionAndAnswer
    interview_id: UUID


class AnswerReceivedEvent(MessageReceivedEvent):
    question: QuestionAndAnswer


class EvaluationsGeneratedEvent(BaseEvent):
    evaluations: list[WebsocketFrame]
    interview_id: UUID


class PerspectivesGeneratedEvent(BaseEvent):
    perspectives: list[WebsocketFrame]
    interview_id: UUID
