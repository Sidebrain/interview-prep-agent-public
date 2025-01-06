from datetime import datetime
from enum import Enum

from beanie import Document
from pydantic import Field


class InterviewerStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Interviewer(Document):
    status: InterviewerStatusEnum = Field(
        default=InterviewerStatusEnum.ACTIVE
    )
    interviewer_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "interviewers"
