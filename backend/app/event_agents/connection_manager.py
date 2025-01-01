import logging
from typing import Dict
from uuid import UUID

from fastapi import WebSocket

from app.event_agents.interview.factory import create_interview
from app.event_agents.interview.manager import InterviewManager

logger = logging.getLogger(__name__)

test_interview_id = UUID("123e4567-e89b-12d3-a456-426614174000")


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[str, InterviewManager] = {}

    def __repr__(self) -> str:
        return f"ConnectionManager(active_connections={len(self.active_connections)})"

    async def connect(
        self, websocket: WebSocket, token: str
    ) -> InterviewManager:
        logger.info(f"Connection attempt for token: {token}")

        # Clean up any existing connection first
        if token in self.active_connections:
            logger.warning(
                "Cleaning up existing connection for token",
                extra={"context": {"token": token}},
            )
            await self._cleanup_connection(token)

        await websocket.accept()

        # Create new connection
        interview_manager = create_interview(
            websocket=websocket, interview_id=test_interview_id
        )

        # Initialize agent
        await interview_manager.initialize()

        self.active_connections[token] = interview_manager
        logger.info(
            "New interview established",
            extra={
                "context": {
                    "token": token,
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
