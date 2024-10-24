from fastapi import APIRouter

from app.api.v2 import websocket_router


router = APIRouter()

router.include_router(
    websocket_router.router, prefix="/websocket", tags=["websocket", "v2"]
)
