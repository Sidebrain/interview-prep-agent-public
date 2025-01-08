from app.event_agents.schemas.mongo_schemas import (
    Candidate,
    Interviewer,
    InterviewSession,
)

EntityType = Interviewer | Candidate | InterviewSession
