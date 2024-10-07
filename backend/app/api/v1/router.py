from fastapi import APIRouter
from app.api.v1.endpoints import auth_router, websocket_router

router = APIRouter()

router.include_router(auth_router.router, prefix="/auth", tags=["auth"])
router.include_router(
    websocket_router.router, prefix="/websocket", tags=["websocket", "v1"]
)
