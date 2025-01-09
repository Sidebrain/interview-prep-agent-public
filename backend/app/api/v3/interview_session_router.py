from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.event_agents.schemas.mongo_schemas import (
    Candidate,
    Interviewer,
    InterviewSession,
)

router = APIRouter()


@router.get("/{id}")
async def validate_interview(
    id: str,
) -> dict[str, str | bool]:
    # try coercing to UUID
    try:
        interviewer = await Interviewer.get(UUID(id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
    if interviewer is None:
        raise HTTPException(
            status_code=404, detail="Interviewer not found"
        )
    return {
        "interviewer_id": str(interviewer.id),
        "validated": True,
    }


@router.post("/interviewer", response_model=Interviewer)
async def create_interviewer() -> Interviewer:
    interviewer = Interviewer(
        job_description="",
        rating_rubric="",
        question_bank="",
    )
    await interviewer.insert()
    return interviewer


@router.post("/candidate")
async def create_candidate() -> Candidate:
    default_candidate = Candidate(
        name="Anudeep",
        email="anudeep@sidebrain.co",
    )
    await default_candidate.insert()
    return default_candidate


@router.post("/session")
async def create_interview_session(
    interviewer_id: UUID,
    candidate_id: UUID,
) -> InterviewSession:
    interview_session = InterviewSession(
        interviewer_id=interviewer_id,
        candidate_id=candidate_id,
    )
    await interview_session.insert()
    return interview_session
