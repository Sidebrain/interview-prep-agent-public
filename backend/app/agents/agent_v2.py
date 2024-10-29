from datetime import datetime
from enum import Enum
import json
from typing import Literal, Optional, get_type_hints
from uuid import uuid4
import instructor
from openai import AsyncClient
from pydantic import BaseModel, Field, model_validator
import yaml
from app.services.llms.openai_client import openai_async_client

from openai.types.chat import ChatCompletionMessage, ChatCompletion

from app.types.interview_concept_types import Role
from app.types.websocket_types import (
    CompletionFrameChunk,
    WebsocketFrame,
)
from app.websocket_handler import Channel
import logging

# Create a child logger instance
logger = logging.getLogger(__name__)

# Add handlers to the child logger
file_handler = logging.FileHandler("logs/app.jsonl", mode="a")  # 'a' mode for appending
stream_handler = logging.StreamHandler()

# Set the logging level and format for the handlers
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Optionally set the logging level for the child logger
logger.setLevel(logging.DEBUG)


class ThinkerIntelligenceEnum(Enum):
    # The source of the entity's intelligence
    human = "human"
    artificial = "artificial_intelligence"


class HumanInputHandler:
    """Not using this right now, but it's a placeholder for a human input handler.
    The output interface is same as openai's chatcompletion.
    We'll see if it will be useful."""

    def __init__(self):
        pass

    async def create(self, messages: list[dict[str, str]] = None):
        # Simulate the behavior of OpenAI's chat completion
        user_input = input("User: ")
        return ChatCompletion(
            id=uuid4(),
            created=int(datetime.now().timestamp()),
            model="human",
            object="human.completion",
            choices=[
                ChatCompletionMessage(
                    role="user",
                    content=user_input,
                )
            ],
        )


def package_into_frame(response, frame_id: str) -> WebsocketFrame:
    raise NotImplementedError


class Thinker:
    def __init__(self, client: AsyncClient = None):
        if client is None:
            client = openai_async_client
        self.client = client

    async def generate(self, messages: list[dict[str, str]], frame_id: str):
        print("-" * 30, "printing the messages that are being sent to the thinker")
        print(messages)
        response = await self.client.chat.completions.create(
            messages=messages,
            model="gpt-4o-mini-2024-07-18",
        )

        logger.debug(response.model_dump_json(indent=4))

        completion_frame = CompletionFrameChunk(
            id=response.id,
            object=response.object,
            model=response.model,
            role=response.choices[0].message.role,
            content=response.choices[0].message.content,
            delta=None,
            index=response.choices[0].index,
            finish_reason=response.choices[0].finish_reason,
        )

        return WebsocketFrame(
            frame_id=frame_id,
            type="completion",
            address="content",
            frame=completion_frame,
        )

    async def extract_structured_response(
        self,
        pydantic_structure_to_extract: BaseModel,
        messages: list[dict[str, str]],
        frame_id: str,
    ):
        model = "gpt-4o-mini-2024-07-18"
        isntructor_client = instructor.from_openai(self.client)
        extracted_structure = await isntructor_client.chat.completions.create(
            model=model,
            response_model=pydantic_structure_to_extract,
            messages=messages,
        )
        print("printing the extracted structure", extracted_structure)

        completion_frame = CompletionFrameChunk(
            id=str(uuid4()),
            object="chat.completion",
            model=model,
            role="assistant",
            content=extracted_structure.model_dump_json(indent=4),
            delta=None,
            index=0,
            finish_reason="stop",
        )

        websocket_frame = WebsocketFrame(
            frame_id=frame_id,
            type="completion",
            address="thought",
            frame=completion_frame,
        )

        return websocket_frame


class Memory:
    def __init__(self):
        self.memory: list[WebsocketFrame] = []

    def add(self, frame: WebsocketFrame):
        self.memory.append(frame)

    def clear(self):
        self.memory = []

    def extract_memory_for_generation(self):
        with open("config/agent_v2.yaml", "r") as file:
            config = yaml.safe_load(file)
            system = [
                {
                    "role": "system",
                    "content": config["interview_agent"]["system_prompt"],
                }
            ]
            print("system", system)

        return system + [
            {
                "role": message.frame.role,
                "content": message.frame.content,
            }
            for message in self.memory
        ]

    def get(self):
        return self.memory


class Agent:
    def __init__(self, channel: Channel):
        self.thinker = Thinker()
        self.memory = Memory()
        self.channel = channel

    async def think(self, extract: bool = False):
        frame_id = str(uuid4())
        frame_to_send = await self.thinker.generate(
            messages=self.memory.extract_memory_for_generation(), frame_id=frame_id
        )
        if extract:
            structured_extraction = await self.thinker.extract_structured_response(
                pydantic_structure_to_extract=Role,
                messages=self.memory.extract_memory_for_generation(),
                frame_id=frame_id,
            )
        self.memory.add(frame_to_send)  # Add the frame to memory
        # print("printing the frame that is being sent right before sending")
        # print(frame_to_send.model_dump_json(indent=4))
        await self.channel.send_message(frame_to_send.model_dump_json(by_alias=True))

        if extract:
            await self.channel.send_message(
                structured_extraction.model_dump_json(by_alias=True)
            )

    async def internal_thought_projection(self):
        """Use this to generate helper text"""
        raise NotImplementedError

    async def generate_artefact(self):
        """Use this to generate artefacts"""
        raise NotImplementedError

    async def interview(self, pydantic_type: BaseModel, frame_id: str):
        """Use this to interview the user"""
        structured_extraction = await self.thinker.extract_structured_response(
            pydantic_structure_to_extract=pydantic_type,
            messages=self.memory.extract_memory_for_generation(),
            frame_id=frame_id,
        )
        print("structured exrtraction yielded", structured_extraction)
        return structured_extraction

    async def receive_message(self):
        msg = await self.channel.receive_message()
        if msg is None:
            return
        print("printing the message that is being received")
        print(msg)
        try:
            # json_msg = json.loads(msg)
            # print("printing the json message that is being received", json_msg)
            parsed_message = WebsocketFrame.model_validate_json(msg, strict=False)
            print("printing the parsed message", parsed_message)
            self.memory.add(parsed_message)
            await self.think(extract=True)
        except json.JSONDecodeError:
            logger.error("Failed to decode the message")
            return
