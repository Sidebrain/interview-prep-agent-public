import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, List, Optional, TypeVar
from uuid import uuid4

from pydantic import BaseModel

from app.agents.dispatcher import Dispatcher
from app.event_agents.memory.protocols import MemoryStore
from app.event_agents.orchestrator.thinker import Thinker
from app.event_agents.types import AgentContext
from app.types.interview_concept_types import (
    QuestionAndAnswer,
)
from app.types.websocket_types import (
    AddressType,
    WebsocketFrame,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", str, BaseModel)


@dataclass
class EvaluationLogContext:
    schema: str
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


class EvaluatorBase(ABC, Generic[T]):
    def __init__(
        self,
        evaluation_schema: T,
    ) -> None:
        self.evaluation_schema = evaluation_schema

    def __repr__(self) -> str:
        return json.dumps(
            {
                "evaluation_schema": (
                    self.evaluation_schema.model_dump()
                    if isinstance(self.evaluation_schema, BaseModel)
                    else self.evaluation_schema
                ),
            },
            indent=2,
        )

    def save_object(self) -> str:
        s = (
            self.evaluation_schema
            if isinstance(self.evaluation_schema, str)
            else self.evaluation_schema.model_json_schema()
        )
        return s

    async def evaluate(
        self,
        questions: List[QuestionAndAnswer],
        agent_context: "AgentContext",
        debug: bool = False,
    ) -> WebsocketFrame:
        """
        Evaluate an answer.
        """
        memory_store = agent_context.memory_store
        thinker = agent_context.thinker
        debug and print(f"\033[91m{self.__class__.__name__}\033[0m")
        # Get the correlation id from the last message in the memory store
        # this is the user input
        correlation_id = memory_store.memory[-1].correlation_id
        # Create input log context
        input_context = EvaluationLogContext(
            schema=self.evaluation_schema,
            correlation_id=correlation_id,
            questions_count=len(questions),
            question_samples=(
                [q.model_dump() for q in questions[:2]]
                if questions
                else None
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

        context_messages = (
            await self.retreive_and_build_context_messages(
                questions=questions,
                memory_store=memory_store,
                address_filter=["human"],
                custom_user_instruction=(
                    self.evaluation_schema
                    if isinstance(self.evaluation_schema, str)
                    else None
                ),
            )
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
                schema=self.evaluation_schema,
                correlation_id=correlation_id,
                questions_count=len(questions),
                context_length=len(context_messages),
                evaluation_type=type(evaluation).__name__,
                frame_id=evaluation_frame.frame_id,
                memory_store_size=len(memory_store.memory),
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
                        "first_message": (
                            messages[0] if messages else None
                        ),
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
        messages: List[dict[str, str]],
        thinker: "Thinker",
    ) -> T:
        """
        Ask questions to the thinker.
        """
        raise NotImplementedError


class EvaluatorSimple(EvaluatorBase[str]):
    async def ask_thinker_for_evaluation(
        self,
        messages: List[dict[str, str]],
        thinker: "Thinker",
    ) -> str:
        response = await thinker.generate(messages=messages)
        content = response.choices[0].message.content or "No content"
        logger.info(
            "Simple evaluation response",
            extra={"context": {"content": content}},
        )
        return content


class EvaluatorStructured(EvaluatorBase[BaseModel]):
    """
    Evaluator that extracts a structured response from the thinker.
    """

    async def ask_thinker_for_evaluation(
        self,
        messages: List[dict[str, str]],
        thinker: "Thinker",
    ) -> BaseModel:
        structured_evaluation_response: BaseModel = (
            await thinker.extract_structured_response(
                messages=messages,
                pydantic_structure_to_extract=self.evaluation_schema,
            )
        )
        logger.info(
            "Structured evaluation response",
            extra={
                "context": {
                    "type": type(
                        structured_evaluation_response
                    ).__name__,
                    "response": structured_evaluation_response.model_dump(),
                }
            },
        )
        return structured_evaluation_response
