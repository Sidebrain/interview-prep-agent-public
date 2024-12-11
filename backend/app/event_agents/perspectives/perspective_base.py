import logging
from typing import List, TypeVar
from uuid import uuid4
from pydantic import BaseModel

from app.agents.dispatcher import Dispatcher
from app.event_agents.memory.protocols import MemoryStore
from app.event_agents.memory.store import InMemoryStore
from app.event_agents.orchestrator.thinker import Thinker


from app.types.interview_concept_types import (
    QuestionAndAnswer,
)
from app.types.websocket_types import AddressType, WebsocketFrame

logger = logging.getLogger(__name__)


class PerspectiveBase:
    def __init__(self, perspective: str) -> None:
        logger.debug(
            "Initializing PerspectiveBase",
            extra={
                "context": {
                    "perspective": perspective,
                    "action": "init",
                    "component": "PerspectiveBase",
                }
            },
        )
        self.perspective = perspective
        self.thinker = Thinker()
        self.description = None

    async def evaluate(
        self,
        questions: List[QuestionAndAnswer],
        memory_store: "InMemoryStore",
    ) -> WebsocketFrame:
        """Main evaluation pipeline for a perspective's analysis"""
        logger.debug(
            "Starting perspective evaluation",
            extra={
                "context": {
                    "perspective": self.perspective,
                }
            },
        )

        correlation_id = self._get_correlation_id(memory_store)
        # self._ensure_description_exists()

        instruction = self._create_evaluation_instruction()
        context = await self._build_evaluation_context(
            questions=questions,
            custom_user_instruction=instruction,
            memory_store=memory_store,
        )
        logger.debug(
            "Built evaluation context",
            extra={"context": {"context": context}},
        )
        analysis = await self._generate_analysis(context)

        logger.debug(
            "Generated analysis",
            extra={
                "context": {
                    "analysis": analysis,
                    "perspective": self.perspective,
                    "action": "generate_analysis",
                    "context": context,
                }
            },
        )

        return self._package_response(analysis, correlation_id)

    def _get_correlation_id(self, memory_store: "InMemoryStore") -> str:
        """Extract correlation ID as the most recent human websocket frame"""
        human_frames = [
            frame for frame in memory_store.memory if frame.address == "human"
        ]
        return human_frames[-1].correlation_id

    def _ensure_description_exists(self) -> None:
        """Verify perspective description is initialized"""
        if self.description is None:
            raise ValueError(
                f"Description not initialized for {self.perspective} perspective"
            )

    def _create_evaluation_instruction(
        self, simple_description: bool = True
    ) -> str:
        """Create the custom instruction for this perspective"""
        if simple_description:
            return (
                f"You are a {self.perspective}. "
                f"You thrive working in teams, coming up with creative solutions collaboratively, and are a great communicator. "
                f"You are provided the transcript of the interview until various points in time. "
                f"Your task is to briefly evaluate the candidate's fit into the team and the company."
                f"Specifically, you are to evaluate the candidate on how well they would work with you and the team."
            )
        else:
            return (
                f"You are a {self.perspective}. "
                f"Here is the description of the things that this perspective would care about: "
                f"{self.description}. "
                f"Your task is to evaluate the candidate from the candidate's responses "
                f"to the questions. "
                f"You are to evaluate the candidate from the perspective of a {self.perspective}."
            )

    async def _build_evaluation_context(
        self,
        questions: List[QuestionAndAnswer],
        custom_user_instruction: str,
        memory_store: "InMemoryStore",
    ) -> List[dict]:
        """Build the context messages for evaluation"""
        return await self.retrieve_and_build_context_messages(
            questions=questions,
            memory_store=memory_store,
            address_filter=["human", "content"],
            custom_user_instruction=custom_user_instruction,
            debug=True,
        )

    async def _generate_analysis(
        self,
        context: List[dict],
    ) -> str:
        """Generate the perspective's analysis"""
        return await self.thinker.generate(
            messages=context,
            debug=True,
        )

    def _package_response(
        self, analysis: str, correlation_id: str
    ) -> WebsocketFrame:
        """Package the analysis into a WebsocketFrame"""
        return Dispatcher.package_and_transform_to_webframe(
            analysis,
            address="perspective",
            frame_id=str(uuid4()),
            correlation_id=correlation_id,
        )

    def write_perspective_description_to_txt(self, description: str) -> None:
        logger.debug(
            "Writing perspective description to file",
            extra={
                "context": {
                    "perspective": self.perspective,
                    "action": "write_description",
                    "component": "PerspectiveBase",
                }
            },
        )
        try:
            with open(f"config/{self.perspective}.txt", "w") as f:
                f.write(description)
            logger.debug(
                "Successfully wrote perspective description",
                extra={
                    "context": {
                        "perspective": self.perspective,
                        "action": "write_description",
                        "status": "success",
                        "component": "PerspectiveBase",
                    }
                },
            )
        except Exception as e:
            logger.error(
                "Failed to write perspective description",
                extra={
                    "context": {
                        "perspective": self.perspective,
                        "error": str(e),
                        "action": "write_description",
                        "status": "error",
                        "component": "PerspectiveBase",
                    }
                },
            )
            raise

    async def initialize(self) -> str:
        """Initialize the perspective by generating and saving its description"""
        logger.debug(
            "Initializing perspective description",
            extra={
                "context": {
                    "perspective": self.perspective,
                    "action": "initialize",
                }
            },
        )

        messages = self._create_initialization_messages()
        # description = await self._generate_description(messages)
        # self._save_description(description)

        return self.description

    def _create_initialization_messages(self) -> List[dict]:
        """Create the messages used to generate the perspective description"""
        return [
            {
                "role": "user",
                "content": (
                    f"You are a {self.perspective}. "
                    f"Your task is to generate a description of the things that this "
                    f"perspective would care about and is key to best working with the "
                    f"candidate."
                ),
            }
        ]

    async def _generate_description(self, messages: List[dict]) -> str:
        """Generate the perspective description using the thinker"""
        response = await self.thinker.generate(
            messages=messages,
            debug=True,
        )

        description = response.choices[0].message.content
        logger.debug(
            "Generated perspective description",
            extra={
                "context": {
                    "perspective": self.perspective,
                    "description": description,
                    "action": "generate_description",
                }
            },
        )
        return description

    def _save_description(self, description: str) -> None:
        """Save the description both in memory and to file"""
        self.description = description
        self._write_description_to_file(description)

    def _write_description_to_file(self, description: str) -> None:
        """Write the perspective description to a file"""
        logger.debug(
            "Writing perspective description to file",
            extra={
                "context": {
                    "perspective": self.perspective,
                    "action": "write_description",
                }
            },
        )
        try:
            with open(f"config/{self.perspective}.txt", "w") as f:
                f.write(description)
            logger.debug(
                "Successfully wrote perspective description",
                extra={
                    "context": {
                        "perspective": self.perspective,
                        "status": "success",
                    }
                },
            )
        except Exception as e:
            logger.error(
                "Failed to write perspective description",
                extra={
                    "context": {
                        "perspective": self.perspective,
                        "error": str(e),
                        "status": "error",
                    }
                },
            )
            raise

    async def retrieve_and_build_context_messages(
        self,
        questions: List[QuestionAndAnswer],
        memory_store: "InMemoryStore",
        address_filter: List[AddressType],
        custom_user_instruction: str,
        debug: bool = False,
    ) -> List[dict[str, str]]:
        logger.debug(
            "Building context messages",
            extra={
                "context": {
                    "question_count": len(questions),
                    "address_filter": address_filter,
                    "action": "build_context",
                    "component": "PerspectiveBase",
                }
            },
        )

        messages = memory_store.extract_memory_for_generation(
            address_filter=address_filter,
            custom_user_instruction=custom_user_instruction,
        )

        #! we likely dont need to do this because we are inserting the questions into the memory store
        # self._insert_questions_before_answer(messages, questions)

        logger.debug(
            "Built context messages",
            extra={
                "message_count": len(messages),
                "context": {
                    "action": "build_context",
                    "status": "complete",
                    "component": "PerspectiveBase",
                },
            },
        )
        return messages

    def _insert_questions_before_answer(
        self, messages: List[dict], questions: List[QuestionAndAnswer]
    ) -> None:
        """Insert questions into messages list before the answer."""
        for question in questions:
            messages.insert(
                -2,  # insert before the answer
                {
                    "role": "user",
                    "content": question.question,
                },
            )
