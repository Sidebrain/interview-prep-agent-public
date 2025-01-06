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


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class EducationEnum(str, Enum):
    HIGH_SCHOOL = "high_school"
    ASSOCIATES = "associates"
    BACHELORS = "bachelors"
    MASTERS = "masters"
    DOCTORATE = "doctorate"
    OTHER = "other"


class RaceEnum(str, Enum):
    ASIAN = "asian"
    BLACK = "black"
    HISPANIC = "hispanic"
    WHITE = "white"
    NATIVE_AMERICAN = "native_american"
    PACIFIC_ISLANDER = "pacific_islander"
    MULTIRACIAL = "multiracial"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class CitizenshipEnum(str, Enum):
    CITIZEN = "citizen"
    PERMANENT_RESIDENT = "permanent_resident"
    WORK_VISA = "work_visa"
    STUDENT_VISA = "student_visa"
    OTHER = "other"


class Candidate(Document):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    name: str
    email: str
    country: str = Field(default="India")
    phone: str
    links: list[str] = Field(
        default_factory=list,
    )
    dob: datetime
    location: str
    education: EducationEnum = Field(default=EducationEnum.BACHELORS)
    citizenship: CitizenshipEnum = Field(
        default=CitizenshipEnum.CITIZEN
    )
    gender: GenderEnum = Field(default=GenderEnum.MALE)

    class Settings:
        name = "candidates"


class InterviewSessionStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InterviewSession(Document):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    interviewer_id: str
    candidate_id: str
    status: InterviewSessionStatusEnum = Field(
        default=InterviewSessionStatusEnum.PENDING
    )
    start_time: datetime | None = None
    end_time: datetime | None = None

    @property
    def duration(self) -> int:
        if self.start_time and self.end_time:
            return int(
                (self.end_time - self.start_time).total_seconds()
            )
        return 0

    class Settings:
        name = "interview_sessions"
