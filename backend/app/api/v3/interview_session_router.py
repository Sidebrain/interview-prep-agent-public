from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.event_agents.schemas.mongo_schemas import (
    Candidate,
    CitizenshipEnum,
    EducationEnum,
    GenderEnum,
    Interviewer,
    InterviewSession,
)

router = APIRouter()


@router.get("/{interview_id}")
async def validate_interview(
    interview_id: str,
) -> dict[str, str]:
    interviewer = await Interviewer.find_one(
        {"interviewer_id": interview_id}
    )
    if interviewer is None:
        raise HTTPException(
            status_code=404, detail="Interviewer not found"
        )
    return {
        "message": f"Interview {interview_id} validated",
    }


@router.post("/", response_model=Interviewer)
async def create_interviewer(
    interviewer_string: str,
) -> Interviewer:
    interviewer = Interviewer(interviewer_id=interviewer_string)
    await interviewer.insert()
    return interviewer


@router.post("/candidate")
async def create_candidate() -> Candidate:
    default_candidate = Candidate(
        name="Anudeep",
        email="anudeep@sidebrain.co",
        phone="7304448472",
        links=[
            "https://www.linkedin.com/in/anudeepyegireddi/",
            "https://twitter.com/anudeepy_",
        ],
        dob=datetime(1998, 1, 1),
        location="Bengaluru, Karnataka, India",
        education=EducationEnum.BACHELORS,
        citizenship=CitizenshipEnum.CITIZEN,
        gender=GenderEnum.MALE,
    )
    await default_candidate.insert()
    return default_candidate


@router.post("/session")
async def create_interview_session() -> InterviewSession:
    interview_session = InterviewSession(
        interviewer_id="123",
        candidate_id="456",
        
    )
    await interview_session.insert()
    return interview_session
