import asyncio
from functools import singledispatch
import json
from typing import Tuple
from uuid import uuid4
import instructor
from openai import AsyncClient
from openai.types.chat import ChatCompletion
from pydantic import BaseModel
import yaml
from app.services.llms.openai_client import openai_async_client


from app.types.interview_concept_types import (
    QuestionAndAnswer,
    hiring_requirements,
)
from app.types.websocket_types import CompletionFrameChunk, WebsocketFrame, AddressType
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

# globally unify the model
model = "gpt-4o-mini-2024-07-18"


class Dispatcher:
    @singledispatch
    def package_and_transform_to_webframe(
        response, address: AddressType, frame_id: str
    ): ...

    @package_and_transform_to_webframe.register(ChatCompletion)
    def _(response, address: AddressType, frame_id: str):

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
            address=address,
            frame=completion_frame,
        )

    @package_and_transform_to_webframe.register(BaseModel)
    def _(response, address: AddressType, frame_id: str):
        completion_frame = CompletionFrameChunk(
            id=str(uuid4()),
            object="chat.completion",
            model=model,
            role="assistant",
            content=response.model_dump_json(indent=4),
            delta=None,
            index=0,
            finish_reason="stop",
        )

        return WebsocketFrame(
            frame_id=frame_id,
            type="completion",
            address=address,
            frame=completion_frame,
        )


class Thinker:
    def __init__(self, client: AsyncClient = None):
        if client is None:
            client = openai_async_client
        self.client = client

    async def generate(
        self,
        messages: list[dict[str, str]],
        frame_id: str,
        address: AddressType = "content",
    ) -> Tuple[WebsocketFrame, ChatCompletion]:
        # print("-" * 30, "printing the messages that are being sent to the thinker")
        # print(messages)
        response = await self.client.chat.completions.create(
            messages=messages,
            model=model,
        )

        logger.debug(response.model_dump_json(indent=4))

        websocket_frame = Dispatcher.package_and_transform_to_webframe(
            response, address, frame_id
        )

        return websocket_frame, response

    async def extract_structured_response(
        self,
        pydantic_structure_to_extract: BaseModel,
        messages: list[dict[str, str]],
        frame_id: str,
    ) -> Tuple[WebsocketFrame, BaseModel]:
        instructor_client = instructor.from_openai(self.client)
        extracted_structure = await instructor_client.chat.completions.create(
            model=model,
            response_model=pydantic_structure_to_extract,
            messages=messages,
        )
        # print("printing the extracted structure", extracted_structure)

        websocket_frame = Dispatcher.package_and_transform_to_webframe(
            extracted_structure, "thought", frame_id
        )

        return websocket_frame, extracted_structure

    async def think_with_tool(
        self, messages: list[dict[str, str]], tool: dict[str, str], frame_id: str
    ) -> Tuple[WebsocketFrame, ChatCompletion]:
        response = await self.client.chat.completions.create(
            messages=messages,
            model=model,
            tools=[{"type": "function", "function": tool}],
        )
        # print(
        #     "printing the response from the think_with_tool method",
        #     response.model_dump_json(indent=4),
        # )

        websocket_frame = Dispatcher.package_and_transform_to_webframe(
            response, "content", frame_id
        )
        return websocket_frame, response


class Memory:
    def __init__(self):
        self.memory: list[WebsocketFrame] = []

    def add(self, frame: WebsocketFrame):
        self.memory.append(frame)

    def clear(self):
        self.memory = []

    def extract_memory_for_generation(
        self, custom_user_instruction: dict[str, str] = None
    ):
        with open("config/agent_v2.yaml", "r") as file:
            config = yaml.safe_load(file)
            system = [
                {
                    "role": "system",
                    "content": config["interview_agent"]["system_prompt"],
                }
            ]
            # print("system", system)

        return (
            system
            + [
                {
                    "role": message.frame.role,
                    "content": message.frame.content,
                }
                for message in self.memory
            ]
            + ([custom_user_instruction] if custom_user_instruction else [])
        )

    def get(self):
        return self.memory


class Agent:
    def __init__(self, channel: Channel):
        self.thinker = Thinker()
        self.memory = Memory()
        self.channel = channel
        self.interview = Interview(self.thinker, self.memory, self.channel)

    async def think(self) -> None:
        """This function is called as soon as the websocket is connected. It is the entry point for the agent. It is responsible for generating the first message to the user."""
        frame_id = str(uuid4())
        frame_to_send, _ = await self.thinker.generate(
            messages=self.memory.extract_memory_for_generation(), frame_id=frame_id
        )
        self.memory.add(frame_to_send)  # Add the frame to memory
        # print("printing the frame that is being sent right before sending")
        # print(frame_to_send.model_dump_json(indent=4))
        await self.channel.send_message(frame_to_send.model_dump_json(by_alias=True))

    async def internal_thought_projection(self):
        """Use this to generate helper text"""
        raise NotImplementedError

    async def generate_all_artefacts(
        self, frame_id: str
    ) -> Tuple[list[WebsocketFrame], list[ChatCompletion]]:
        """Use this to generate artefacts"""
        artefacts_to_generate = [
            "job description",
            "high surface aera interview questions",
            "rating rubric",
        ]
        generated_items = await asyncio.gather(
            *[
                self.generate_single_artefact(artefact, frame_id)
                for artefact in artefacts_to_generate
            ]
        )
        frames, responses = zip(*generated_items)
        return frames, responses

    async def generate_single_artefact(
        self, artefact: str, frame_id: str
    ) -> Tuple[WebsocketFrame, ChatCompletion]:
        messages = self.memory.extract_memory_for_generation(
            custom_user_instruction={
                "role": "user",
                "content": f"Using the previous information provided by the user, generate a high quality and detailed: {artefact}",
            }
        )
        websocket_frame, response = await self.thinker.generate(
            messages=messages, frame_id=frame_id, address="artefact"
        )
        return websocket_frame, response

    async def receive_message(self):
        msg = await self.channel.receive_message()
        if msg is None:
            return
        # print("printing the message that is being received")
        # print(msg)
        frame_id = str(uuid4())
        try:
            # json_msg = json.loads(msg)
            # print("printing the json message that is being received", json_msg)
            parsed_message = WebsocketFrame.model_validate_json(msg, strict=False)
            # print("printing the parsed message", parsed_message)
            self.memory.add(parsed_message)
            await self.interview(frame_id=frame_id)
        except json.JSONDecodeError:
            logger.error("Failed to decode the message")
            return
        except IndexError:
            logger.error("Popping from empty concept list")
            # generate artefacts at this point
            (frames, responses) = await self.generate_all_artefacts(frame_id)
            print(frames, sep=f"\n{'-'*30}\n")

            await asyncio.gather(
                *[
                    self.channel.send_message(frame.model_dump_json(by_alias=True))
                    for frame in frames
                ]
            )
            return


class Interview:
    def __init__(self, thinker: Thinker, memory: Memory, channel: Channel):
        self.concepts = hiring_requirements.copy()
        self.thinker = thinker
        self.memory = memory
        self.channel = channel
        pass

    async def generate_q_and_a_for_concept(
        self, concept: BaseModel, frame_id: str
    ) -> Tuple[WebsocketFrame, QuestionAndAnswer]:
        print("printing the concept that is being interviewed", concept)
        info_to_extract_from_user = [
            field_details.description
            for field, field_details in concept.model_fields.items()
            if field != "reward"
        ]
        print("printing the current instruction", info_to_extract_from_user)
        messages = self.memory.extract_memory_for_generation(
            custom_user_instruction={
                "role": "user",
                "content": """Ask a question to get the following information:\n{info_to_extract_from_user} """.format(
                    info_to_extract_from_user=" ".join(info_to_extract_from_user)
                ),
            }
        )
        q_and_a_frame, q_and_a = await self.thinker.extract_structured_response(
            pydantic_structure_to_extract=QuestionAndAnswer,
            messages=messages,
            frame_id=frame_id,
        )
        return q_and_a_frame, q_and_a

    async def __call__(self, frame_id: str):
        concept = self.concepts.pop(0)
        q_and_a_frame, q_and_a = await self.generate_q_and_a_for_concept(
            concept, frame_id
        )
        # await self.channel.send_message(q_and_a.model_dump_json(by_alias=True))
        frame_to_send_to_user = WebsocketFrame(
            frame_id=frame_id,
            type="completion",
            address="content",
            frame=CompletionFrameChunk(
                content=q_and_a.question,
                role="assistant",
                finish_reason="stop",
                index=0,
                delta=None,
                id=str(uuid4()),
                model=model,
                object="chat.completion",
            ),
        )
        self.memory.add(frame_to_send_to_user)

        await asyncio.gather(
            *[
                self.channel.send_message(
                    frame_to_send_to_user.model_dump_json(by_alias=True)
                ),
                self.channel.send_message(q_and_a_frame.model_dump_json(by_alias=True)),
            ]
        )
