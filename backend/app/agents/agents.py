import asyncio
from typing import AsyncGenerator, Literal
from fastapi import WebSocket
from openai import AsyncClient
from pydantic import BaseModel
from uuid import uuid4

from app.services.llms.openai_client import openai_async_client
from app.types.websocket_types import WebSocketStreamResponse


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
            model="gpt-4o-mini",
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    async def process_response(
        self, context: str, websocket: WebSocket = None, verbose: bool = True
    ) -> str:
        id = uuid4().int
        index = 0
        full_response = []
        async for response in self.generate_response(context):
            index += 1
            if websocket:
                response_model = WebSocketStreamResponse(
                    id=id, index=index, type="chunk", content=response
                )
                await websocket.send_text(response_model.model_dump_json())
            if verbose:
                # print(response, end="", flush=True)
                print(response_model.index, end=", ", flush=True)
            full_response.append(response)

        if websocket:
            response_model = WebSocketStreamResponse(
                id=id, index=index + 1, type="complete", content=None
            )
            await websocket.send_text(response_model.model_dump_json())

        return " ".join(full_response)


class BaseAgent:
    def __init__(self, goal: str, websocket: WebSocket = None):
        self.goal = goal
        self.intelligence = AiIntelligence()
        self.websocket = websocket
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.goal}"

    async def process_goal(self) -> str:
        return await self.intelligence.process_response(self.goal, self.websocket)

    async def process_message(self, message: str) -> str:
        # await self.websocket.send_text(f"User sent: {message}")
        return await self.intelligence.process_response(message, self.websocket)


async def main():
    agent = BaseAgent()
    print(agent)
    agent.goal = "Find the meaning of life"
    print(await agent.process_goal())


if __name__ == "__main__":
    print(asyncio.run(main()))
