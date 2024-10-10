import asyncio
from fastapi import WebSocket

from app.intelligence.artificial import ArtificialIntelligence
from app.intelligence.reasoning_structure import InterviewAgentConfig
from app.types.agent_types import AgentMessage


class BaseAgent:
    def __init__(self, goal: str, websocket: WebSocket = None):
        self.goal = goal
        self.intelligence = ArtificialIntelligence()
        self.websocket = websocket
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.goal}"

    async def process_goal(self) -> str:
        return await self.intelligence.process_response(self.goal, self.websocket)

    async def route(self, message: AgentMessage) -> str:
        return await self.intelligence.route_response(
            message, self.websocket, response_format=InterviewAgentConfig
        )

    async def process_message(self, message: str) -> str:
        await self.intelligence.process_response(message, self.websocket)


async def main():
    agent = BaseAgent()
    print(agent)
    agent.goal = "Find the meaning of life"
    print(await agent.process_goal())


if __name__ == "__main__":
    print(asyncio.run(main()))
