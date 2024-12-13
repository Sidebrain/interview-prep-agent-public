from datetime import datetime
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
    in_progress = "Questions gathering in progress."
    completed = "Questions gathering completed."
    failed = "Questions gathering failed."
    idle = "Questions gathering idle."


class QuestionsGatheringEvent(BaseEvent):
    status: Status
    session_id: UUID


class AskQuestionEvent(BaseEvent):
    question: QuestionAndAnswer
    session_id: UUID


class InterviewEndReason(Enum):
    questions_exhausted = "questions_exhausted"
    user_ended = "user_ended"
    error = "error"
    timeout = "timeout"


class InterviewEndEvent(BaseEvent):
    reason: InterviewEndReason
    session_id: UUID
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()))


class InterviewSummaryRaiseEvent(BaseEvent):
    session_id: UUID


class AnswerReceivedEvent(MessageReceivedEvent):
    question: QuestionAndAnswer
