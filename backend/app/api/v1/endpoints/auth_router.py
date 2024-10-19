from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import httpx
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


@router.route("/__/auth/{path:path}", methods=["GET", "POST"])
async def firebase_auth_proxy(request: Request, path: str):
    firebase_url = f"https://public-project-436308.firebaseapp.com/__/auth/{path}"

    client = httpx.AsyncClient()

    # Forward the request method, headers, and body
    method = request.method
    headers = dict(request.headers)
    body = await request.body()

    response = await client.request(method, firebase_url, headers=headers, content=body)

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
    )
