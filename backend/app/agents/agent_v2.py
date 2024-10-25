from datetime import datetime
from enum import Enum
from uuid import uuid4
from openai import AsyncClient
from app.services.llms.openai_client import openai_async_client

from openai.types.chat import ChatCompletionMessage, ChatCompletion

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


class Thinker:
    def __init__(self, client: AsyncClient = None):
        if client is None:
            client = openai_async_client
        self.client = client

    async def generate(
        self,
        messages: list[dict[str, str]] = None,
    ):
        frame_id = str(uuid4())
        if messages is None:
            messages = [
                {
                    "role": "system",
                    "content": "Hello, how can I help you today?",
                },
                {
                    "role": "user",
                    "content": "I want to understand whether time is an invention of thought or a natural phenomenon.",
                },
                {
                    "role": "user",
                    "content": "Is there a difference between mental time and chronological time. Is one the source of most of our mental pain?",
                },
            ]
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


class Agent:
    def __init__(self, channel: Channel):
        self.thinker = Thinker()
        self.channel = channel

    async def think(self, messages: list[dict[str, str]] = None):
        frame_to_send = await self.thinker.generate(messages=messages)
        print("printing the frame that is being sent right before sending")
        print(frame_to_send.model_dump_json(indent=4))
        await self.channel.send_message(frame_to_send.model_dump_json())

    async def receive_message(self):
        await self.channel.receive_message()
