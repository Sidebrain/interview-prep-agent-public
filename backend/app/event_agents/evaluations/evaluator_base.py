import logging
from typing import List, TypeVar
from uuid import uuid4
from openai.types.chat import ChatCompletion
from pydantic import BaseModel
import json
from dataclasses import dataclass
from typing import Any, Optional

from app.event_agents.memory.protocols import MemoryStore
from app.event_agents.orchestrator.thinker import Thinker
from app.event_agents.memory.store import InMemoryStore

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


@dataclass
class EvaluationLogContext:
    correlation_id: str
    questions_count: int
    memory_store_size: Optional[int]
    evaluation_schema_type: str
    question_samples: Optional[list] = None
    context_length: Optional[int] = None
    evaluation_type: Optional[str] = None
    frame_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


class EvaluatorBase(ABC):

    def __init__(
        self,
        evaluation_schema: T,
    ):
        self.evaluation_schema = evaluation_schema

    def __repr__(self) -> str:
        return json.dumps(
            {
                "type": self.__class__.__name__,
                "evaluation_schema": (
                    self.evaluation_schema.__class__.__name__
                    if not isinstance(self.evaluation_schema, str)
                    else "string schema"
                ),
            },
            indent=2,
        )

    async def evaluate(
        self,
        questions: List[QuestionAndAnswer],
        memory_store: InMemoryStore,
        thinker: "Thinker",
        debug: bool = False,
    ) -> WebsocketFrame:
        """
        Evaluate an answer.
        """
        # Get the correlation id from the last message in the memory store
        # this is the user input
        correlation_id = memory_store.memory[-1].correlation_id
        # Create input log context
        input_context = EvaluationLogContext(
            correlation_id=correlation_id,
            questions_count=len(questions),
            question_samples=(
                [q.model_dump() for q in questions[:2]] if questions else None
            ),
            memory_store_size=(
                len(memory_store.memory)
                if hasattr(memory_store, "memory")
                else None
            ),
            evaluation_schema_type=(
                self.evaluation_schema.__class__.__name__
                if not isinstance(self.evaluation_schema, str)
                else "string schema"
            ),
        )

        if debug:
            logger.debug(
                "Evaluation Input",
                extra={"context": input_context.to_dict()},
            )

        context_messages = await self.retreive_and_build_context_messages(
            questions=questions,
            memory_store=memory_store,
            address_filter=["human"],
            custom_user_instruction=(
                self.evaluation_schema
                if isinstance(self.evaluation_schema, str)
                else None
            ),
        )

        evaluation = await self.ask_thinker_for_evaluation(
            messages=context_messages,
            thinker=thinker,
        )

        evaluation_frame = Dispatcher.package_and_transform_to_webframe(
            evaluation,
            address="evaluation",
            frame_id=str(uuid4()),
            correlation_id=correlation_id,
        )

        if debug:
            # Create result log context
            result_context = EvaluationLogContext(
                correlation_id=correlation_id,
                questions_count=len(questions),
                context_length=len(context_messages),
                evaluation_type=type(evaluation).__name__,
                frame_id=evaluation_frame.frame_id,
                evaluation_schema_type=(
                    self.evaluation_schema.__class__.__name__
                    if not isinstance(self.evaluation_schema, str)
                    else "string schema"
                ),
            )
            logger.debug(
                "Evaluation Result",
                extra={"context": result_context.to_dict()},
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
                "Memory store messages",
                extra={
                    "context": {
                        "message_count": len(messages),
                        "first_message": (messages[0] if messages else None),
                        "address_filter": address_filter,
                        "has_custom_instruction": custom_user_instruction
                        is not None,
                    }
                },
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
        messages: List[dict[str, str]],  # the context to send LLM
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
        return await super().ask_thinker_for_evaluation(messages, thinker)


class EvaluatorStructured(EvaluatorBase):
    """
    Evaluator that extracts a structured response from the thinker.
    """

    async def ask_thinker_for_evaluation(
        self,
        messages: List[dict[str, str]],
        thinker: "Thinker",
    ) -> ChatCompletion:
        structured_evaluation_response = (
            await thinker.extract_structured_response(
                messages=messages,
                pydantic_structure_to_extract=self.evaluation_schema,
            )
        )
        return structured_evaluation_response
