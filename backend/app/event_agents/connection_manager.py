import logging
from typing import Dict
from uuid import UUID

from fastapi import WebSocket

from app.event_agents.orchestrator.broker import Agent, StartEvent
from app.event_agents.websocket_handler import Channel

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Channel] = {}

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
            logger.info(f"Client {token} connected")
        return agent

    def disconnect(self, token: str):
        if token in self.active_connections:
            del self.active_connections[token]
