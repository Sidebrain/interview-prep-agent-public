import logging
from typing import Dict
from uuid import UUID

from fastapi import WebSocket

from app.event_agents.agent import Agent
from app.event_agents.orchestrator.events import StartEvent
from app.event_agents.websocket_handler import Channel

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[str, Channel] = {}

    def __repr__(self) -> str:
        return f"ConnectionManager(active_connections={len(self.active_connections)})"

    async def connect(self, websocket: WebSocket, token: str) -> Agent:
        logger.info(f"Connection attempt for token: {token}")
        
        # Clean up any existing connection first
        if token in self.active_connections:
            logger.warning("Cleaning up existing connection for token", 
                         extra={"context": {"token": token}})
            await self._cleanup_connection(token)

        await websocket.accept()
        
        # Create new connection
        channel = Channel(websocket)
        agent = Agent.create(channel)
        channel.agent = agent
        
        # Initialize agent
        await agent.start()
        
        # Create and emit start event
        start_event = StartEvent(
            session_id=agent.session_id,
            client_id=UUID(token),
        )
        await agent.broker.publish(start_event)
        
        self.active_connections[token] = channel
        logger.info("New connection established", 
                   extra={"context": {"token": token, 
                                    "session_id": str(agent.session_id)}})
        return agent

    async def disconnect(self, token: str) -> None:
        """Clean up connection and stop agent"""
        await self._cleanup_connection(token)

    async def _cleanup_connection(self, token: str) -> None:
        """Helper method to cleanup connection and associated resources"""
        if token in self.active_connections:
            channel = self.active_connections[token]
            if channel.agent:
                await channel.agent.stop()
            del self.active_connections[token]
            logger.info("Connection cleaned up", 
                       extra={"context": {"token": token}})
