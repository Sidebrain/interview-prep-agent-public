from typing import AsyncGenerator, Literal, Union
from uuid import uuid4
from fastapi import WebSocket
from openai import AsyncClient
from openai.types.chat import ParsedChatCompletionMessage
from openai.types.chat.chat_completion_message import ChatCompletionMessage
import openai
from pydantic import BaseModel
from yaml import safe_load

from app.types.agent_types import AgentMessage
from app.types.websocket_types import WebSocketStreamResponse
from app.services.llms.openai_client import openai_async_client


class ArtificialIntelligence:
    def __init__(
        self,
        memory: list[str],
        client: AsyncClient = openai_async_client,
        iq: int = 100,
    ):
        self.iq = iq
        self.client = client
        self.memory = memory

    async def generate_response(
        self, context: str, system: str = None, use_memory: bool = False
    ) -> AsyncGenerator[str, None]:
        if system is None:
            system = safe_load(open("config/game_manager.yaml"))["game_manager"][
                "description"
            ]
            print("base case system is: ", system)
        stream = await self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": " ".join(self.memory) if use_memory else "",
                },
                {"role": "user", "content": context},
            ],
            model="gpt-4o-mini",
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    async def generate_structured_response(
        self,
        context: str,
        response_format: BaseModel | None = None,
        websocket: WebSocket = None,
    ):
        id = uuid4().int
        index = 0
        try:
            completion = await self.client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Extract the structured data"},
                    {"role": "user", "content": context},
                ],
                response_format=response_format,
            )
            parsed_response = completion.choices[0].message
            if parsed_response.parsed:
                content: ParsedChatCompletionMessage = parsed_response.parsed
                self.memory.append(content.model_dump_json())
                print("added to memory", self.memory)
            elif parsed_response.refusal:
                print(parsed_response.refusal)
                content: ChatCompletionMessage = parsed_response.refusal

            if websocket:
                response_model = WebSocketStreamResponse(
                    id=id,
                    index=index,
                    type="structured",
                    content=content.model_dump_json(),
                )
                print("sending via websocket", response_model.model_dump_json())
                await websocket.send_text(response_model.model_dump_json())
            else:
                return content
        except Exception as e:
            if type(e) == openai.LengthFinishReasonError:
                print("The response is too long to parse", e)
                pass
            else:
                print(e)
                pass

    async def process_streaming_response(
        self,
        context: str,
        system: str = None,
        websocket: WebSocket = None,
        verbose: bool = False,
        use_memory: bool = False,
    ):
        id = uuid4().int
        index = 0
        full_response = []
        async for response in self.generate_response(context, system, use_memory):
            index += 1
            if websocket:
                response_model = WebSocketStreamResponse(
                    id=id, index=index, type="chunk", content=response
                )
                await websocket.send_text(response_model.model_dump_json())
            if verbose:
                print(response, end="", flush=True)
            full_response.append(response)

        if websocket:
            response_model = WebSocketStreamResponse(
                id=id, index=index + 1, type="complete", content=None
            )
            await websocket.send_text(response_model.model_dump_json())

        return " ".join(full_response)

    async def route_to_appropriate_generator(
        self,
        message: AgentMessage,
        system: str = None,
        websocket: WebSocket = None,
        verbose: bool = False,
        response_format: BaseModel | None = None,
        use_memory: bool = False,
    ) -> str:
        context = message.content

        match message.routing_key:
            case "streaming":
                return await self.process_streaming_response(
                    context, system, websocket, verbose, use_memory
                )
            case "structured":
                print("generating structured response")
                await self.generate_structured_response(
                    context, response_format, websocket
                )

            case _:
                return await self.process_streaming_response(
                    context, websocket, verbose
                )
