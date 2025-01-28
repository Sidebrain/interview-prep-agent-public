import asyncio
import json
import logging
from typing import Tuple
from uuid import uuid4

import yaml
from openai.types.chat import ChatCompletion
from pydantic import BaseModel

from app.agents.dispatcher import Dispatcher
from app.constants import DEBUG_CONFIG, model
from app.event_agents.memory.factory import create_memory_store
from app.event_agents.memory.protocols import MemoryStore
from app.event_agents.orchestrator.thinker import Thinker
from app.event_agents.schemas.mongo_schemas import Interviewer
from app.types.interview_concept_types import (
    QuestionAndAnswer,
    hiring_requirements,
)
from app.types.websocket_types import (
    CompletionFrameChunk,
    WebsocketFrame,
)
from app.websocket_handler import Channel

# Create a logger instance
logger = logging.getLogger(__name__)


class Agent:
    debug = DEBUG_CONFIG["agent"]

    def __init__(
        self, channel: Channel, interviewer: Interviewer
    ) -> None:
        self.agent_id = str(uuid4())
        self.thinker = Thinker()
        self.interviewer = interviewer
        self.memory = create_memory_store(
            agent_id=self.interviewer.id,
            entity=self.interviewer,
            config_path="config/agent_v2.yaml",
        )
        self.channel = channel
        self.interview = Interview(
            self.thinker, self.memory, self.channel
        )
        self.artifact_dict: dict[str, str] = {}

    async def think(self) -> None:
        """This function is called as soon as the websocket is connected.
        It is the entry point for the agent.
        It is responsible for generating the first message to the user."""

        frame_id = str(uuid4())
        response = await self.thinker.generate(
            messages=self.memory.extract_memory_for_generation()
        )
        frame_to_send = Dispatcher.package_and_transform_to_webframe(
            response,  # type: ignore
            "content",
            frame_id,
        )
        await self.memory.add(frame_to_send)  # Add the frame to memory

        await self.channel.send_message(
            frame_to_send.model_dump_json(by_alias=True)
        )

    async def internal_thought_projection(self) -> None:
        """Use this to generate helper text"""
        raise NotImplementedError

    def save_artifacts_to_yaml(self) -> None:
        with open("config/artifacts_v2.yaml", "w") as file:
            yaml.dump(self.artifact_dict, file)

    async def save_artifacts_to_mongo_return_interviewer(
        self,
    ) -> Interviewer:
        # save the artifacts to the mongo memory
        # and return the interviewer object
        self.interviewer.question_bank = self.artifact_dict[
            "interview questions"
        ]
        self.interviewer.rating_rubric = self.artifact_dict[
            "rating rubric in table format"
        ]
        self.interviewer.job_description = self.artifact_dict[
            "job description"
        ]
        await self.interviewer.save()
        return self.interviewer

    def add_artifact_to_dict(self, artifact: str, content: str) -> None:
        self.artifact_dict[artifact] = content
        logger.info(
            f"\033[33mArtifact added to dictionary: {artifact}\033[0m"
        )
        logger.info(
            f"\033[33mLength of artifact dict: {len(self.artifact_dict.keys())}\033[0m"
        )
        # check if all three artifacts are present
        # if they are then save to the yaml file
        if len(self.artifact_dict.keys()) == 3:
            logger.info("Saving artifacts to yaml file")
            self.save_artifacts_to_yaml()

    def clean_previous_artifacts(self) -> None:
        self.artifact_dict = {}
        self.save_artifacts_to_yaml()

    async def generate_all_artifacts(
        self, frame_id: str
    ) -> Tuple[list[WebsocketFrame], list[ChatCompletion]]:
        """Use this to generate artifacts"""
        self.clean_previous_artifacts()
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

    async def generate_save_send_artifacts(self, frame_id: str) -> None:
        frames, _ = await self.generate_all_artifacts(frame_id)
        interviewer = (
            await self.save_artifacts_to_mongo_return_interviewer()
        )
        await self.send_onboarding_link(interviewer)

        if self.debug:
            for frame in frames:
                logger.debug(frame.model_dump_json(indent=4))
                logger.debug(f"\n{'-'*30}\n")

        await asyncio.gather(
            *[
                self.channel.send_message(
                    frame.model_dump_json(by_alias=True)
                )
                for frame in frames
            ]
        )

    async def generate_single_artifact(
        self, artifact: str, frame_id: str, debug: bool = True
    ) -> Tuple[WebsocketFrame, ChatCompletion]:
        messages = self.memory.extract_memory_for_generation(
            custom_user_instruction=f"Using the previous information provided by the user, generate a high quality and detailed: {artifact}"
        )
        response = await self.thinker.generate(messages=messages)
        # save the artifact to the artifact dictionary
        # primary reason is to save to the yaml file
        self.add_artifact_to_dict(
            artifact, response.choices[0].message.content
        )
        websocket_frame = Dispatcher.package_and_transform_to_webframe(
            response,  # type: ignore
            "artifact",
            frame_id,
            title=artifact.title(),
        )
        await self.memory.add(websocket_frame)
        if self.debug and debug:
            # logger.debug(f"Artifact generated: {artifact}")
            # logger.debug(websocket_frame.model_dump_json(indent=4))
            logger.debug(
                f"Artifact generated: {artifact} \n frame n length: {len(websocket_frame.model_dump_json())}\n\n"
            )
        return websocket_frame, response

    async def regenerate_artefact(
        self, incoming_parsed_frame: WebsocketFrame, debug: bool = False
    ) -> None:
        try:
            parent_frame = self.memory.find_parent_frame(
                incoming_parsed_frame.frame
            )
            # generate a new artifact frame with the same id as the parent frame
            new_artifact_frame, _ = await self.generate_single_artifact(
                parent_frame.frame.title.lower(), parent_frame.frame_id
            )
            self.memory.add(new_artifact_frame)
            await self.channel.send_message(
                new_artifact_frame.model_dump_json(by_alias=True)
            )
            return
        except Exception as e:
            logger.error(f"Failed to regenerate artifact: {str(e)}")
            return

    async def receive_message(
        self, debug: bool = True, verbose: bool = False
    ) -> None:
        msg = await self.channel.receive_message()
        if msg is None:
            return
        frame_id = str(uuid4())
        try:
            parsed_message = WebsocketFrame.model_validate_json(
                msg, strict=False
            )

            if self.debug and debug:
                logger.debug(
                    f"Message received: {parsed_message.model_dump_json(indent=4)}"
                )

            if parsed_message.type == "signal.regenerate":
                # if messge is regenerate, then dont do anything and wait for the next message non signal regenerate message
                await self.regenerate_artefact(parsed_message, debug)
                return

            await self.memory.add(parsed_message)
            await self.interview(frame_id=frame_id)
        except json.JSONDecodeError:
            logger.error("Failed to decode the message")
            return
        except IndexError:
            logger.error("Popping from empty concept list")
            await self.generate_save_send_artifacts(frame_id)
            return

    async def send_onboarding_link(
        self, interviewer: Interviewer
    ) -> None:
        # send the onboarding link
        frame_to_send = Dispatcher.package_and_transform_to_webframe(
            f"You are ready to share this interviwer. Here is the link: http://localhost:3000/onboarding/{interviewer.id}",
            address="content",
            frame_id=str(uuid4()),
            title="last message can be sent to the user",
        )
        await self.channel.send_message(
            frame_to_send.model_dump_json(by_alias=True)
        )


class Interview:
    debug = DEBUG_CONFIG["interview"]

    def __init__(
        self, thinker: Thinker, memory: MemoryStore, channel: Channel
    ):
        self.concepts = hiring_requirements.copy()
        self.thinker = thinker
        self.memory = memory
        self.channel = channel
        pass

    async def generate_q_and_a_for_concept(
        self,
        concept: type[BaseModel],
        frame_id: str,
        debug: bool = True,
    ) -> Tuple[WebsocketFrame, QuestionAndAnswer]:
        if self.debug and debug:
            logger.debug(
                f"printing the concept that is being interviewed: {concept}"
            )

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
            address_filter=[
                "content",
                "human",
            ],  # so that the context does not include the in between thought frames
            custom_user_instruction=f"""Ask a question to get the following information:\n{info_to_extract_from_user} """.format(
                info_to_extract_from_user=" ".join(
                    info_to_extract_from_user
                )
            ),
        )

        if self.debug and debug:
            logger.debug(
                "messages that form context for question generation: "
            )
            logger.debug(f"messages: {messages}")
            for m in messages:
                logger.debug(f"{m.items()}")
                logger.debug(f"\n{'-'*30}\n")

        q_and_a = await self.thinker.extract_structured_response(
            pydantic_structure_to_extract=QuestionAndAnswer,
            messages=messages,
        )
        websocket_frame = Dispatcher.package_and_transform_to_webframe(
            q_and_a,  # type: ignore
            "thought",
            frame_id,
        )
        return websocket_frame, q_and_a

    async def __call__(self, frame_id: str) -> None:
        concept = self.concepts.pop(0)
        (
            q_and_a_frame,
            q_and_a,
        ) = await self.generate_q_and_a_for_concept(concept, frame_id)
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
        await self.memory.add(frame_to_send_to_user)

        await asyncio.gather(
            *[
                self.channel.send_message(
                    frame_to_send_to_user.model_dump_json(by_alias=True)
                ),
                self.channel.send_message(
                    q_and_a_frame.model_dump_json(by_alias=True)
                ),
            ]
        )
