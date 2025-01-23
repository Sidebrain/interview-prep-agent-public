import logging
from typing import Dict

from fastapi import WebSocket

from app.agents.agent_v2 import Agent
from app.event_agents.schemas.mongo_schemas import Interviewer
from app.websocket_handler import Channel

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[str, Channel] = {}

    async def connect(self, websocket: WebSocket, token: str) -> Agent:
        """Creates a channel, agent, and connects the channel to the agent.

        Args:
            websocket (WebSocket): _description_
            token (str): _description_

        Returns:
            Agent: _description_
        """
        logger.info(
            "Client connected", extra={"context": {"token": token}}
        )
        await websocket.accept()
        if token not in self.active_connections:
            # creating a channel with an agent
            channel = Channel(websocket)
            interviewer = await Interviewer.get(token)

            if not interviewer:
                interviewer = Interviewer(id=token)
                await interviewer.insert()

            agent = Agent(channel=channel, interviewer=interviewer)
            channel.agent = agent
            self.active_connections[token] = channel
        print(f"Client connected: {token}")
        return agent

    def disconnect(self, token: str) -> None:
        if token in self.active_connections:
            del self.active_connections[token]
