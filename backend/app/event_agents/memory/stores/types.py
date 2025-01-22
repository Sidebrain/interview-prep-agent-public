from app.event_agents.schemas.mongo_schemas import (
    AgentProfile,
    Candidate,
    Interviewer,
    InterviewSession,
)

EntityType = Interviewer | Candidate | InterviewSession | AgentProfile
