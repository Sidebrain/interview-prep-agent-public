from fastapi import APIRouter

from app.api.v3 import interview_session_router, websocket_router

router = APIRouter()

router.include_router(
    websocket_router.router,
    prefix="/websocket",
    tags=["websocket", "v3"],
)
router.include_router(
    interview_session_router.router,
    prefix="/interview",
    tags=["interview", "v3"],
)
