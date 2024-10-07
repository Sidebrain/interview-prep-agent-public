from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.services.auth.firebase import verify_token


router = APIRouter()

# Create a reusable security dependency
security = HTTPBearer()


@router.get("/verify_token")
async def verify_firebase_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    token = credentials.credentials
    user_info = await verify_token(token)

    return {"message": "Token is valid", "user_info": user_info}
