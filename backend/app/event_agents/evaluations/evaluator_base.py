import logging
from typing import List
from uuid import uuid4
from openai.types.chat import ChatCompletion

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


class EvaluatorBase:

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
            await self.retreive_context_messages(
                questions,
                memory_store,
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

    async def retreive_context_messages(
        self,
        questions: List[QuestionAndAnswer],
        memory_store: "MemoryStore",
        debug: bool = True,
    ) -> List[dict[str, str]]:
        """
        Retreive context from memory store.
        """
        messages = memory_store.extract_memory_for_generation(
            address_filter=[],
            custom_user_instruction="check the relevance of the answer to the question",
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

    # async def package_and_publish_evaluation(
    #     self, evaluation: ChatCompletion
    # ) -> None:
    #     """
    #     Package and publish the evaluation.
    #     """
    #     frame_to_publish = Dispatcher.package_and_transform_to_webframe(
    #         evaluation,
    #         address=AddressTypeEnum.THOUGHT,
    #         #! for now new frame id, figuire out what to do later
    #         frame_id=str(uuid4()),
    #     )
    #     raise NotImplementedError
