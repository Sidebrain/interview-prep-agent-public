from typing import Any, List

from pydantic import BaseModel

from app.event_agents.orchestrator.events import BaseEvent
from app.types.interview_concept_types import QuestionAndAnswer
from app.types.websocket_types import WebsocketFrame


class EvaluationSchema(BaseModel):
    name: str
    schema: type[BaseModel] | str  # type: ignore


class AgentConfig(BaseModel):
    agent_id: str
    job_description: str
    rating_rubric: str
    question_set: str
    structured_questions: List[QuestionAndAnswer]
    evaluations: List[EvaluationSchema]


class MessageMemory(BaseModel):
    message: WebsocketFrame
    evaluation: List[WebsocketFrame]
    perspective: List[WebsocketFrame]


class ReportMemory(BaseModel):
    recruiter_report: List[WebsocketFrame]
    candidate_report: List[WebsocketFrame]


class InterviewMemory(BaseModel):
    user_info: str
    session_id: str
    agent_id: str
    memory: List[MessageMemory]
    events: List[BaseEvent]
    reports: ReportMemory

    def to_json(self) -> str:
        """Convert the entire interview memory to JSON string"""
        return self.model_dump_json()

    @classmethod
    def from_json(cls, json_str: str) -> "InterviewMemory":
        """Create an InterviewMemory instance from JSON string"""
        return cls.model_validate_json(json_str)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary (useful for MongoDB)"""
        return self.model_dump()


class LongTermMemory(BaseModel):
    agent_config: AgentConfig
    interview_memory: InterviewMemory
