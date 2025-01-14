import logging
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.event_agents.schemas.mongo_schemas import User
from app.services.auth.firebase import verify_token_and_return_user

security = HTTPBearer()

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/verify_token_and_create_user")
async def verify_token_and_create_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Any:
    token = credentials.credentials
    firebase_user = await verify_token_and_return_user(token)

    user = await User.find_one({"firebase_id": firebase_user.uid})

    if not user:
        user = User(
            firebase_id=firebase_user.uid,
            email=firebase_user.email,
            name=firebase_user.display_name,
            phone_number="dummy number",
        )
        await user.create()

    logger.debug(
        "User created",
        extra={
            "context": {
                "firebase_user": firebase_user,
                "user": user.model_dump(),
            }
        },
    )

    # return user

    return {"message": "Token is valid", "user_info": user}
