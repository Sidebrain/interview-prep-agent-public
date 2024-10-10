import asyncio
from fastapi import WebSocket
from pydantic import BaseModel
from yaml import safe_load

from app.intelligence.artificial import ArtificialIntelligence
from app.intelligence.reasoning_structure import InterviewAgentConfig
from app.types.agent_types import AgentMessage


class BaseAgent:
    def __init__(self, goal: str, websocket: WebSocket = None):
        self.goal = goal
        self.websocket = websocket
        self.memory = []
        self.intelligence = ArtificialIntelligence(self.memory)
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.goal}"

    async def schema_based_knowledge_generator(self, schema: BaseModel):
        # for key in schema.model_dump().keys():
        for key in ["role", "company_name", "team_name", "internal_requirements"]:
            system = safe_load(open("config/game_manager.yaml"))[
                "recruiting_coordinator"
            ]["system"]
            action = f"Generate response for {key} in markdown"
            await self.generate_response(
                message=AgentMessage(content=action, routing_key="streaming"),
                system=system,
            )
        pass

    async def process_goal(self) -> str:
        goal = AgentMessage(content=self.goal, routing_key="streaming")
        return await self.intelligence.route_to_appropriate_generator(
            message=goal, system=None, websocket=self.websocket
        )

    async def generate_response(self, message: AgentMessage, system: str = None) -> str:
        await self.intelligence.route_to_appropriate_generator(
            message=message,
            websocket=self.websocket,
            response_format=InterviewAgentConfig,
            system=system,
            use_memory=True,
        )
        if message.routing_key == "structured":
            await self.schema_based_knowledge_generator(InterviewAgentConfig)


async def main():
    agent = BaseAgent()
    print(agent)
    agent.goal = "Find the meaning of life"
    print(await agent.process_goal())


if __name__ == "__main__":
    print(asyncio.run(main()))
