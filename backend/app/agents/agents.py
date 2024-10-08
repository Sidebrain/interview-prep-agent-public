import asyncio
from typing import AsyncGenerator

from fastapi import WebSocket
from openai import AsyncClient
from app.services.llms.openai_client import openai_async_client


class AiIntelligence:
    def __init__(self, client: AsyncClient = openai_async_client, iq: int = 100):
        self.iq = iq
        self.client = client

    async def generate_response(self, context: str) -> AsyncGenerator[str, None]:
        stream = await self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": context},
            ],
            model="gpt-4o",
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    async def process_response(self, context: str) -> str:
        full_response = []
        async for response in self.generate_response(context):
            print(response, end="", flush=False)
            full_response.append(response)

        return " ".join(full_response)


class BaseAgent:
    def __init__(self, output_destination: WebSocket = None):
        self.goal: str = None
        self.intelligence = AiIntelligence()
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.goal}"

    async def process_goal(self) -> str:
        return await self.intelligence.process_response(self.goal)


async def main():
    agent = BaseAgent()
    print(agent)
    agent.goal = "Find the meaning of life"
    print(await agent.process_goal())


if __name__ == "__main__":
    print(asyncio.run(main()))
