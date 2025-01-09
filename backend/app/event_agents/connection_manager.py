import logging
from typing import Dict
from uuid import UUID

from fastapi import HTTPException, WebSocket

from app.event_agents.interview.factory import create_interview
from app.event_agents.interview.manager import InterviewManager
from app.event_agents.schemas.mongo_schemas import InterviewSession

logger = logging.getLogger(__name__)

test_interview_id = UUID("123e4567-e89b-12d3-a456-426614174000")


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[str, InterviewManager] = {}

    def __repr__(self) -> str:
        return f"ConnectionManager(active_connections={len(self.active_connections)})"

    async def connect(
        self, websocket: WebSocket, interview_session_id: str
    ) -> InterviewManager:
        logger.info(
            f"Connection attempt for token: {interview_session_id}"
        )

        # Clean up any existing connection first
        if interview_session_id in self.active_connections:
            logger.warning(
                "Cleaning up existing connection for token",
                extra={"context": {"token": interview_session_id}},
            )
            await self._cleanup_connection(interview_session_id)

        interview_session = await InterviewSession.get(
            interview_session_id
        )
        if not interview_session:
            raise HTTPException(
                status_code=404, detail="Interview session not found"
            )

        await websocket.accept()

        # Create new connection
        interview_manager = await create_interview(
            websocket=websocket,
            interview_session_id=interview_session.id,
        )

        # Initialize agent
        await interview_manager.initialize()

        self.active_connections[interview_session_id] = (
            interview_manager
        )
        logger.info(
            "New interview established",
            extra={
                "context": {
                    "token": interview_session_id,
                    "interview_id": str(interview_manager.interview_id),
                }
            },
        )
        return interview_manager

    async def disconnect(self, token: str) -> None:
        """Clean up connection and stop agent"""
        await self._cleanup_connection(token)

    async def _cleanup_connection(self, token: str) -> None:
        """Helper method to cleanup connection and associated resources"""
        if token in self.active_connections:
            interview_manager: InterviewManager = (
                self.active_connections[token]
            )
            await interview_manager.lifecycle_manager.stop()
            del self.active_connections[token]
            logger.info(
                "Connection cleaned up",
                extra={"context": {"token": token}},
            )
