from fastapi import APIRouter, HTTPException

from app.event_agents.schemas.mongo_schemas import Interviewer

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


@router.post("/")
async def create_interviewer(
    interviewer_string: str,
) -> Interviewer:
    interviewer = Interviewer(interviewer_id=interviewer_string)
    await interviewer.insert()
    # Refresh from DB to get all fields populated
    # await interviewer.fetch_all()
    return interviewer
