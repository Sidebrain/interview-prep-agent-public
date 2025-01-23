from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field

from app.types.websocket_types import WebsocketFrame


class CollectionName(str, Enum):
    INTERVIEWERS = "interviewers"
    CANDIDATES = "candidates"
    INTERVIEW_SESSIONS = "interview_sessions"
    AGENT_PROFILES = "agent_profiles"


class BehaviorMode(str, Enum):
    INTERVIEW = "INTERVIEW"
    PEER_INTERVIEW = "PEER_INTERVIEW"
    SERVICE = "SERVICE"


class Interviewer(Document):
    id: UUID = Field(default_factory=uuid4)  # type: ignore
    behavior_mode: BehaviorMode = Field(default=BehaviorMode.INTERVIEW)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    job_description: str = Field(default="")
    rating_rubric: str = Field(default="")
    question_bank: str = Field(default="")
    question_bank_structured: str = Field(default="")

    memory: List[WebsocketFrame] = Field(default_factory=list)

    class Settings:
        name = CollectionName.INTERVIEWERS.value

    async def save(self, *args, **kwargs) -> None:  # type: ignore
        """Override the save method to create an agent profile along with the interviewer"""
        # First save the interviewer
        await super().save(*args, **kwargs)
        await self.sync_agent_profile()

    async def sync_agent_profile(self) -> None:
        # Look if agent profile exists using proper query syntax
        agent_profile = await AgentProfile.find_one(
            {"interviewer_id": self.id}  # Use dictionary for query
        )

        if agent_profile:
            # Update the agent profile
            agent_profile.job_description = self.job_description
            agent_profile.rating_rubric = self.rating_rubric
            agent_profile.behavior_mode = self.behavior_mode
            await agent_profile.save()
        else:
            # Create a new agent profile
            await AgentProfile.create_from_interviewer(self)

    @classmethod
    async def get(cls, *args, **kwargs) -> Optional["Interviewer"]:  # type: ignore
        interviewer = await super().get(*args, **kwargs)
        if interviewer:
            await interviewer.sync_agent_profile()
        return interviewer


class AgentProfile(Document):
    id: UUID = Field(default_factory=uuid4)  # type: ignore
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    # role_name: str
    job_description: str
    rating_rubric: str
    behavior_mode: BehaviorMode = Field(default=BehaviorMode.INTERVIEW)
    interviewer_id: UUID
    # skills: list[str]
    # tools: Optional[List[str]] = None
    # communication_style: Optional[CommunicationStyle] = None
    question_bank_structured: str = Field(default="")
    question_bank: str = Field(default="")

    class Settings:
        name = CollectionName.AGENT_PROFILES.value

    @classmethod
    async def create_from_interviewer(
        cls, interviewer: Interviewer
    ) -> "AgentProfile":
        return await cls(
            job_description=interviewer.job_description,
            rating_rubric=interviewer.rating_rubric,
            behavior_mode=interviewer.behavior_mode,
            interviewer_id=interviewer.id,
        ).create()


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
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


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
    max_time_allowed: int = Field(default=10 * 60)

    class Settings:
        name = CollectionName.INTERVIEW_SESSIONS.value
