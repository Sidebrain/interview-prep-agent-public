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
        """Creates a channel, agent, and connects the channel to the agent.

        Args:
            websocket (WebSocket): _description_
            token (str): _description_

        Returns:
            Agent: _description_
        """
        await websocket.accept()
        if token not in self.active_connections:
            # creating a channel with an agent
            channel = Channel(websocket)
            agent = Agent(channel=channel)
            channel.agent = agent

            # start the broker
            await agent.start()

            # create start event
            start_event = StartEvent(
                session_id=agent.session_id,
                client_id=UUID(token),
            )

            # emit start event
            await agent.broker.publish(start_event)

            self.active_connections[token] = channel
            logger.debug(
                {
                    "event": "client_connected",
                    "token": token,
                    "session_id": str(agent.session_id),
                }
            )
        return agent

    def disconnect(self, token: str) -> None:
        if token in self.active_connections:
            logger.debug(
                {
                    "event": "client_disconnected",
                    "token": token,
                    "session_id": str(
                        self.active_connections[token].agent.session_id
                    ),
                }
            )
            del self.active_connections[token]
