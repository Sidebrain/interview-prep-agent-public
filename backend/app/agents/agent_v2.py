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
logger.propagate = False

# globally unify the model
model = "gpt-4o-mini-2024-07-18"

# After the imports, before the logger setup

DEBUG_CONFIG = {
    "dispatcher": False,
    "thinker": False,
    "interview": False,
    "agent": True,
    "memory": True,
}


class Dispatcher:
    debug = DEBUG_CONFIG["dispatcher"]

    @singledispatch
    def package_and_transform_to_webframe(
        response,
        address: AddressType,
        frame_id: str,
        title: str = None,
        debug: bool = False,
    ) -> WebsocketFrame: ...

    @package_and_transform_to_webframe.register(ChatCompletion)
    def _(
        response,
        address: AddressType,
        frame_id: str,
        title: str = None,
        debug: bool = False,
    ):

        completion_frame = CompletionFrameChunk(
            id=response.id,
            object=response.object,
            model=response.model,
            role=response.choices[0].message.role,
            content=response.choices[0].message.content,
            delta=None,
            title=title,
            index=response.choices[0].index,
            finish_reason=response.choices[0].finish_reason,
        )

        websocket_frame = WebsocketFrame(
            frame_id=frame_id,
            type="completion",
            address=address,
            frame=completion_frame,
        )

        if Dispatcher.debug and debug:
            logger.debug(websocket_frame.model_dump_json(indent=4))

        return websocket_frame

    @package_and_transform_to_webframe.register(BaseModel)
    def _(
        response,
        address: AddressType,
        frame_id: str,
        title: str = None,
        debug: bool = False,
    ):
        completion_frame = CompletionFrameChunk(
            id=str(uuid4()),
            object="chat.completion",
            model=model,
            role="assistant",
            content=response.model_dump_json(indent=4, by_alias=True),
            delta=None,
            title=title,
            index=0,
            finish_reason="stop",
        )

        websocket_frame = WebsocketFrame(
            frame_id=frame_id,
            type="completion",
            address=address,
            frame=completion_frame,
        )

        if Dispatcher.debug and debug:
            logger.debug(websocket_frame.model_dump_json(indent=4))

        return websocket_frame


class Thinker:
    debug = DEBUG_CONFIG["thinker"]

    def __init__(self, client: AsyncClient = None):
        if client is None:
            client = openai_async_client
        self.client = client

    async def generate(
        self, messages: list[dict[str, str]], debug: bool = False
    ) -> ChatCompletion:
        response = await self.client.chat.completions.create(
            messages=messages,
            model=model,
        )

        if self.debug and debug:
            logger.debug(response.model_dump_json(indent=4))

        return response

    async def extract_structured_response(
        self,
        pydantic_structure_to_extract: BaseModel,
        messages: list[dict[str, str]],
        debug: bool = False,
    ) -> BaseModel:
        instructor_client = instructor.from_openai(self.client)
        extracted_structure = await instructor_client.chat.completions.create(
            model=model,
            response_model=pydantic_structure_to_extract,
            messages=messages,
        )
        if self.debug and debug:
            logger.debug(extracted_structure.model_dump_json(indent=4))

        return extracted_structure

    async def think_with_tool(
        self, messages: list[dict[str, str]], tool: dict[str, str], debug: bool = False
    ) -> ChatCompletion:
        response = await self.client.chat.completions.create(
            messages=messages,
            model=model,
            tools=[{"type": "function", "function": tool}],
        )
        if self.debug and debug:
            logger.debug(response.model_dump_json(indent=4))

        return response


class Memory:
    debug = DEBUG_CONFIG["memory"]

    def __init__(self):
        self.memory: list[WebsocketFrame] = []

    def add(self, frame: WebsocketFrame):
        self.memory.append(frame)

    def clear(self):
        self.memory = []

    def parent_frame_for_completion_chunk(
        self, completion_frame: CompletionFrameChunk, debug: bool = False
    ) -> WebsocketFrame:
        """
        Find the parent frame for a completion frame chunk.
        This is useful when a completion frame chunk is generated, and we need to find the parent frame.

        Args:
            completion_frame (CompletionFrameChunk): The completion frame chunk to find the parent frame for.

        Returns:
            WebsocketFrame: The parent frame for the completion frame chunk.
        """
        try:
            parent_frame = next(
                (
                    frame
                    for frame in self.memory[::-1]
                    if frame.frame.id == completion_frame.id
                )
            )
            if self.debug and debug:
                logger.debug(
                    f"Found parent frame: {parent_frame.model_dump_json(indent=4)}"
                )
            return parent_frame
        except StopIteration:
            if self.debug and debug:
                logger.debug(
                    f"No parent frame found for completion frame: {completion_frame.id}"
                )
                logger.debug("Available websocket frame, completion chunk ids")
                logger.debug(
                    [
                        (frame.frame.id, frame.frame.content)
                        for frame in self.memory[::-1]
                    ]
                )
            return None

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
    debug = DEBUG_CONFIG["agent"]

    def __init__(self, channel: Channel):
        self.thinker = Thinker()
        self.memory = Memory()
        self.channel = channel
        self.interview = Interview(self.thinker, self.memory, self.channel)

    async def think(self) -> None:
        """This function is called as soon as the websocket is connected.
        It is the entry point for the agent.
        It is responsible for generating the first message to the user."""

        frame_id = str(uuid4())
        response = await self.thinker.generate(
            messages=self.memory.extract_memory_for_generation()
        )
        frame_to_send = Dispatcher.package_and_transform_to_webframe(
            response, "content", frame_id
        )
        self.memory.add(frame_to_send)  # Add the frame to memory

        await self.channel.send_message(frame_to_send.model_dump_json(by_alias=True))

    async def internal_thought_projection(self):
        """Use this to generate helper text"""
        raise NotImplementedError

    async def generate_all_artifacts(
        self, frame_id: str
    ) -> Tuple[list[WebsocketFrame], list[ChatCompletion]]:
        """Use this to generate artifacts"""
        artifacts_to_generate = [
            # "Short description of the job",
            "job description",
            "interview questions",
            "rating rubric in table format",
        ]
        generated_items = await asyncio.gather(
            *[
                self.generate_single_artifact(artifact, frame_id)
                for artifact in artifacts_to_generate
            ]
        )
        frames, responses = zip(*generated_items)
        return frames, responses

    async def generate_single_artifact(
        self, artifact: str, frame_id: str, debug: bool = True
    ) -> Tuple[WebsocketFrame, ChatCompletion]:
        messages = self.memory.extract_memory_for_generation(
            custom_user_instruction={
                "role": "user",
                "content": f"Using the previous information provided by the user, generate a high quality and detailed: {artifact}",
            }
        )
        response = await self.thinker.generate(messages=messages)
        websocket_frame = Dispatcher.package_and_transform_to_webframe(
            response, "artifact", frame_id, title=artifact.title()
        )
        self.memory.add(websocket_frame)
        if self.debug and debug:
            # logger.debug(f"Artifact generated: {artifact}")
            # logger.debug(websocket_frame.model_dump_json(indent=4))
            logger.debug(
                f"Artifact generated: {artifact} \n frame n length: {len(websocket_frame.model_dump_json())}\n\n"
            )
        return websocket_frame, response

    async def regenerate_artefact(
        self, incoming_parsed_frame: WebsocketFrame, debug: bool = False
    ):

        try:
            parent_frame = self.memory.parent_frame_for_completion_chunk(
                incoming_parsed_frame.frame
            )
            # generate a new artifact frame with the same id as the parent frame
            new_artifact_frame, _ = await self.generate_single_artifact(
                parent_frame.frame.title, parent_frame.frame_id
            )
            self.memory.add(new_artifact_frame)
            await self.channel.send_message(
                new_artifact_frame.model_dump_json(by_alias=True)
            )
            return
        except Exception as e:
            logger.error(f"Failed to regenerate artifact: {str(e)}")
            return

    async def receive_message(self, debug: bool = True, verbose: bool = False):
        msg = await self.channel.receive_message()
        if msg is None:
            return
        frame_id = str(uuid4())
        try:
            parsed_message = WebsocketFrame.model_validate_json(msg, strict=False)

            if self.debug and debug:
                logger.debug(
                    f"Message received: {parsed_message.model_dump_json(indent=4)}"
                )

            if parsed_message.type == "signal.regenerate":
                # if messge is regenerate, then dont do anything and wait for the next message non signal regenerate message
                await self.regenerate_artefact(parsed_message, debug)
                return

            self.memory.add(parsed_message)
            await self.interview(frame_id=frame_id)
        except json.JSONDecodeError:
            logger.error("Failed to decode the message")
            return
        except IndexError:
            logger.error("Popping from empty concept list")
            (frames, responses) = await self.generate_all_artifacts(frame_id)
            if self.debug and debug and verbose:
                for frame in frames:
                    logger.debug(frame.model_dump_json(indent=4))
                    logger.debug(f"\n{'-'*30}\n")

            await asyncio.gather(
                *[
                    self.channel.send_message(frame.model_dump_json(by_alias=True))
                    for frame in frames
                ]
            )
            return


class Interview:
    debug = DEBUG_CONFIG["interview"]

    def __init__(self, thinker: Thinker, memory: Memory, channel: Channel):
        self.concepts = hiring_requirements.copy()
        self.thinker = thinker
        self.memory = memory
        self.channel = channel
        pass

    async def generate_q_and_a_for_concept(
        self, concept: BaseModel, frame_id: str, debug: bool = False
    ) -> Tuple[WebsocketFrame, QuestionAndAnswer]:
        if self.debug and debug:
            logger.debug(f"printing the concept that is being interviewed: {concept}")

        info_to_extract_from_user = [
            field_details.description
            for field, field_details in concept.model_fields.items()
            if field != "reward"
        ]
        if self.debug and debug:
            logger.debug(
                f"printing the current instruction: {info_to_extract_from_user}"
            )
        messages = self.memory.extract_memory_for_generation(
            custom_user_instruction={
                "role": "user",
                "content": """Ask a question to get the following information:\n{info_to_extract_from_user} """.format(
                    info_to_extract_from_user=" ".join(info_to_extract_from_user)
                ),
            }
        )
        q_and_a = await self.thinker.extract_structured_response(
            pydantic_structure_to_extract=QuestionAndAnswer,
            messages=messages,
        )
        websocket_frame = Dispatcher.package_and_transform_to_webframe(
            q_and_a, "thought", frame_id
        )
        return websocket_frame, q_and_a

    async def __call__(self, frame_id: str):
        concept = self.concepts.pop(0)
        q_and_a_frame, q_and_a = await self.generate_q_and_a_for_concept(
            concept, frame_id
        )
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
