from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field

from app.types.websocket_types import WebsocketFrame


class Interviewer(Document):
    id: UUID = Field(default_factory=uuid4)  # type: ignore
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    job_description: str
    rating_rubric: str
    question_bank: str

    class Settings:
        name = "interviewers"


class Candidate(Document):
    id: UUID = Field(default_factory=uuid4)  # type: ignore
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    name: str
    email: str

    class Settings:
        name = "candidates"


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
        name = "interview_sessions"
