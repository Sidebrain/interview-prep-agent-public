import logging
from typing import List, TypeVar
from uuid import uuid4
from openai.types.chat import ChatCompletion
from pydantic import BaseModel

from app.agents import dispatcher
from app.event_agents.memory.protocols import MemoryStore
from app.event_agents.orchestrator.thinker import Thinker

from abc import ABC, abstractmethod

from app.types.interview_concept_types import (
    QuestionAndAnswer,
)
from app.agents.dispatcher import Dispatcher
from app.types.websocket_types import (
    AddressType,
    WebsocketFrame,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", str, BaseModel)


class EvaluatorBase(ABC):

    def __init__(
        self,
        evaluation_schema: T,
    ):
        self.evaluation_schema = evaluation_schema

    async def evaluate(
        self,
        questions: List[QuestionAndAnswer],
        memory_store: "MemoryStore",
        thinker: "Thinker",
        debug: bool = False,
    ) -> WebsocketFrame:
        """
        Evaluate an answer.
        """
        logger.debug("\033[32mEvaluating answer\033[0m")
        context_messages = (
            await self.retreive_and_build_context_messages(
                questions=questions,
                memory_store=memory_store,
                address_filter=[],
                custom_user_instruction=(
                    self.evaluation_schema
                    if isinstance(
                        self.evaluation_schema, str
                    )
                    else None
                ),
            )
        )
        if debug:
            logger.debug(
                f"\033[32mContext messages: {context_messages}\033[0m"
            )
        evaluation = await self.ask_thinker_for_evaluation(
            messages=context_messages,
            thinker=thinker,
        )
        if debug:
            logger.debug(
                f"\033[32mEvaluation: {evaluation}\033[0m"
            )
        evaluation_frame = (
            Dispatcher.package_and_transform_to_webframe(
                evaluation,
                address="content",
                frame_id=str(uuid4()),
            )
        )
        if debug:
            logger.debug(
                f"\033[32mEvaluation frame: {evaluation_frame.model_dump_json(indent=4)}\033[0m"
            )
        return evaluation_frame

    async def retreive_and_build_context_messages(
        self,
        questions: List[QuestionAndAnswer],
        memory_store: "MemoryStore",
        address_filter: List[AddressType],
        custom_user_instruction: str,
        debug: bool = False,
    ) -> List[dict[str, str]]:
        """
        Retreive context from memory store.
        """
        messages = memory_store.extract_memory_for_generation(
            address_filter=address_filter,
            custom_user_instruction=custom_user_instruction,
        )
        if debug:
            logger.debug(
                f"\033[32mContext messages: {messages}\033[0m"
            )
        for question in questions:
            messages.insert(
                -2,  # insert before the answer
                {
                    "role": "user",
                    "content": question.question,
                },
            )
        return messages

    @abstractmethod
    async def ask_thinker_for_evaluation(
        self,
        messages: List[
            dict[str, str]
        ],  # the context to send LLM
        thinker: "Thinker",
    ) -> ChatCompletion:
        """
        Ask questions to the thinker.
        """
        response = await thinker.generate(
            messages=messages,
        )
        return response


class EvaluatorSimple(EvaluatorBase):
    async def ask_thinker_for_evaluation(
        self,
        messages: List[dict[str, str]],
        thinker: "Thinker",
    ) -> ChatCompletion:
        return await super().ask_thinker_for_evaluation(
            messages, thinker
        )


class EvaluatorStructured(EvaluatorBase):
    async def ask_thinker_for_evaluation(
        self,
        messages: List[dict[str, str]],
        thinker: "Thinker",
    ) -> ChatCompletion:
        structured_evaluation_response = await thinker.extract_structured_response(
            messages=messages,
            pydantic_structure_to_extract=self.evaluation_schema,
        )
        return structured_evaluation_response
