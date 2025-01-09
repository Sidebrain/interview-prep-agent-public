from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field

from app.types.websocket_types import WebsocketFrame


class CollectionName(str, Enum):
    INTERVIEWERS = "interviewers"
    CANDIDATES = "candidates"
    INTERVIEW_SESSIONS = "interview_sessions"


class Interviewer(Document):
    id: UUID = Field(default_factory=uuid4)  # type: ignore
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    job_description: str = Field(default="")
    rating_rubric: str = Field(default="")
    question_bank: str = Field(default="")
    memory: List[WebsocketFrame] = Field(default_factory=list)

    class Settings:
        name = CollectionName.INTERVIEWERS.value


class Candidate(Document):
    id: UUID = Field(default_factory=uuid4)  # type: ignore
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    name: str
    email: str
    phone_number: str
    memory: List[WebsocketFrame] = Field(default_factory=list)

    class Settings:
        name = CollectionName.CANDIDATES.value


class InterviewSessionStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InterviewSession(Document):
    id: UUID = Field(default_factory=uuid4)  # type: ignore
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    interviewer_id: UUID
    candidate_id: UUID
    status: InterviewSessionStatusEnum = Field(
        default=InterviewSessionStatusEnum.PENDING
    )
    start_time: datetime | None = None
    end_time: datetime | None = None
    memory: List[WebsocketFrame] = Field(default_factory=list)

    class Settings:
        name = CollectionName.INTERVIEW_SESSIONS.value
