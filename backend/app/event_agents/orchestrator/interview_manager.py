import asyncio
import logging
import json
from dataclasses import asdict, dataclass
from typing import Any, Dict

from typing import TYPE_CHECKING
from uuid import UUID, uuid4
from pydantic import BaseModel
import yaml
from app.agents.dispatcher import Dispatcher
from app.event_agents.evaluations.manager import (
    EvaluationManager,
)
from app.event_agents.orchestrator.events import (
    AddToMemoryEvent,
    AskQuestionEvent,
    InterviewEndEvent,
    InterviewEndReason,
    QuestionsGatheringEvent,
    Status,
)

from app.types.interview_concept_types import (
    QuestionAndAnswer,
)
from app.types.websocket_types import WebsocketFrame

if TYPE_CHECKING:
    from app.event_agents.orchestrator.thinker import (
        Thinker,
    )
    from app.event_agents.orchestrator.broker import Broker
    from app.event_agents.memory.protocols import (
        MemoryStore,
    )
logger = logging.getLogger(__name__)


@dataclass
class LogContext:
    """Base class for structured logging context"""

    def to_dict(self) -> Dict[str, Any]:
        return {
            k: v
            for k, v in asdict(self).items()
            if v is not None
        }


class InterviewManager:
    def __init__(
        self,
        session_id: UUID,
        broker: "Broker",
        thinker: "Thinker",
        memory_store: "MemoryStore",
        eval_manager: EvaluationManager,
        max_time_allowed: int | None = None,
    ):
        self.broker = broker
        self.thinker = thinker
        self.session_id = session_id
        self.max_time_allowed = (
            max_time_allowed if max_time_allowed else 2 * 60
        )  # 2 minutes default
        self.time_manager = TimeManager(
            broker, session_id, self.max_time_allowed
        )
        self.interview_event_handler = (
            InterviewEventHandler(broker, session_id)
        )
        self.question_manager = QuestionManager(thinker)
        self.eval_manager = eval_manager
        self.memory_store = memory_store

    def __repr__(self) -> str:
        return json.dumps(
            {
                "type": "InterviewManager",
                "session": self.session_id.hex[:8],
                "time_remaining": self.max_time_allowed
                - self.time_manager.time_elapsed,
                "questions_remaining": len(
                    self.question_manager.questions
                ),
                "current_question": (
                    self.question_manager.current_question.question[
                        :30
                    ]
                    + "..."
                    if self.question_manager.current_question
                    else None
                ),
            },
            indent=2,
        )

    async def subscribe(self) -> None:
        """
        Subscribe to interview-related events.

        Subscribes to:
        - QuestionsGatheringEvent
        - AskQuestionEvent
        - InterviewEndEvent
        """
        logger.debug(
            "Subscribing to questions gathering event for session %s",
            self.session_id,
        )
        await self.broker.subscribe(
            QuestionsGatheringEvent,
            self.interview_event_handler.handle_questions_gathering_event,
        )
        await self.broker.subscribe(
            AskQuestionEvent,
            self.interview_event_handler.handle_ask_question,
        )
        await self.broker.subscribe(
            InterviewEndEvent,
            self.interview_event_handler.handle_interview_end,
        )
        await self.broker.subscribe(
            AddToMemoryEvent,
            self.handle_add_to_memory_event,
        )

    async def handle_add_to_memory_event(
        self, new_memory_event: AddToMemoryEvent
    ) -> None:
        """Handle new memory event and trigger next question."""
        logger.info(
            "Processing answer: %s",
            {
                "manager": self,
                "answer_length": (
                    len(
                        new_memory_event.frame.frame.content
                    )
                    if new_memory_event.frame.frame.content
                    else 0
                ),
            },
        )

        try:
            await self.memory_store.add(
                new_memory_event.frame
            )
            evaluations = await self.eval_manager.handle_evaluation(
                questions=[
                    self.question_manager.current_question
                ]
            )
            logger.info(
                "Answer processed: %s",
                {
                    "manager": self,
                    "evaluation_count": len(evaluations),
                },
            )

            for evaluation in evaluations:
                await self.broker.publish(evaluation)
            await self.ask_next_question()
        except Exception as e:
            logger.error(
                "Answer processing failed: %s",
                {"manager": self, "error": str(e)},
            )
            raise

    async def initialize(self) -> list[QuestionAndAnswer]:
        """
        Initialize the interview session and start the question gathering process.

        This method:
        1. Publishes initial questions gathering event
        2. Gathers questions using the question manager
        3. Publishes completion event
        4. Starts the interview timer
        5. Initiates the first question

        Returns:
            list[QuestionAndAnswer]: List of gathered questions for the interview
        """
        logger.info(
            "Starting new interview session: %s", self
        )

        # # Gather questions
        # questions = (
        #     await self.question_manager.gather_questions()
        # )
        # logger.info(
        #     "Questions gathered: %s",
        #     {
        #         "session": self.session_id.hex[:8],
        #         "question_count": len(questions),
        #     },
        # )

        # First event
        in_progress_event = QuestionsGatheringEvent(
            status=Status.in_progress,
            session_id=self.session_id,
        )

        await self.broker.publish(in_progress_event)

        # gather questions and store them in the instance variable
        questions = (
            await self.question_manager.gather_questions()
        )

        logger.info(
            "Questions gathered: %s",
            {
                "session": self.session_id.hex[:8],
                "question_count": len(questions),
            },
        )

        # Second event
        completed_question_gathering_event = (
            QuestionsGatheringEvent(
                status=Status.completed,
                session_id=self.session_id,
            )
        )

        await self.broker.publish(
            completed_question_gathering_event
        )
        logger.debug(
            "\033[33m\nCompleted gathering %d questions. Published event.\n\033[0m",
            len(self.question_manager.questions),
        )

        # Start time tracking in the background# Start timer
        asyncio.create_task(self.time_manager.start_timer())
        logger.info("Timer started: %s", self.time_manager)

        let_user_know_timer_started_event = Dispatcher.package_and_transform_to_webframe(
            f"Timer started. You have {self.max_time_allowed} {'seconds' if self.max_time_allowed <= 60 else 'minutes'} to answer the questions.",
            "content",
            frame_id=str(uuid4()),
        )
        await self.broker.publish(
            let_user_know_timer_started_event
        )

        # Start asking questions
        try:
            await self.ask_next_question()
        except Exception as e:
            logger.error(
                "Failed to ask first question",
                extra={
                    "session_id": self.session_id,
                    "manager_state": repr(self),
                    "error": str(e),
                },
                exc_info=True,
            )

        return questions

    async def ask_next_question(self) -> None:
        """Request and publish next question."""
        next_question = (
            await self.question_manager.get_next_question()
        )

        if next_question is None:
            logger.info("Interview complete: %s", self)
            interview_end_event = InterviewEndEvent(
                reason=InterviewEndReason.questions_exhausted,
                session_id=self.session_id,
            )
            await self.broker.publish(interview_end_event)
        else:
            logger.info(
                "Asking question: %s", self.question_manager
            )
            await self.broker.publish(
                AskQuestionEvent(
                    question=next_question,
                    session_id=self.session_id,
                )
            )


class TimeManager:
    def __init__(
        self,
        broker: "Broker",
        session_id: UUID,
        max_time_allowed: int,
    ):
        self.broker = broker
        self.session_id = session_id
        self.max_time_allowed = max_time_allowed
        self.time_elapsed = 0

    def __repr__(self) -> str:
        return json.dumps(
            {
                "type": "TimeManager",
                "session": self.session_id.hex[:8],
                "elapsed": self.time_elapsed,
                "remaining": self.max_time_allowed
                - self.time_elapsed,
            },
            indent=2,
        )

    async def start_timer(self) -> None:
        """
        Start the interview timer that monitors interview duration.

        Continuously checks if the interview has exceeded the maximum allowed time.
        If exceeded, emits an InterviewEndEvent with timeout reason.
        Checks every 5 seconds until timeout or interview completion.
        """
        while True:
            await asyncio.sleep(5)  # Check every 5 seconds
            self.time_elapsed += 5

            if self.time_elapsed >= self.max_time_allowed:
                logger.info("Interview timeout reached")
                timeout_event = InterviewEndEvent(
                    reason=InterviewEndReason.timeout,
                    session_id=self.session_id,
                )
                await self.broker.publish(timeout_event)
                break


class QuestionManager:
    def __init__(self, thinker: "Thinker"):
        self.thinker = thinker
        self.questions: list[QuestionAndAnswer] = []
        self.current_question: QuestionAndAnswer | None = (
            None
        )

    def __repr__(self) -> str:
        return json.dumps(
            {
                "type": "QuestionManager",
                "questions_remaining": len(self.questions),
                "current_question": (
                    self.current_question.question[:30]
                    + "..."
                    if self.current_question
                    else None
                ),
            },
            indent=2,
        )

    async def gather_questions(
        self,
    ) -> list[QuestionAndAnswer]:
        """
        Load and process interview questions from the configuration file.

        Reads questions template from config/artifacts.yaml,
        processes it through the thinker to generate structured questions.

        Returns:
            list[QuestionAndAnswer]: List of structured interview questions
        """
        logger.info(
            "Gathering questions",
            extra={
                "context": {
                    "questions_remaining": len(
                        self.questions
                    ),
                    "current_question": (
                        self.current_question.question[:30]
                        + "..."
                        if self.current_question
                        else None
                    ),
                }
            },
        )

        with open("config/artifacts.yaml", "r") as f:
            artifacts = yaml.safe_load(f)
        question_string = artifacts["artifacts"][
            "interview_questions"
        ]

        messages = [
            {"role": "user", "content": question_string},
        ]

        class Questions(BaseModel):
            questions: list[QuestionAndAnswer]

        response: Questions = (
            await self.thinker.extract_structured_response(
                Questions, messages=messages, debug=True
            )
        )
        self.questions = response.questions

        logger.info("Questions prepared: %s", self)
        return response.questions

    async def get_next_question(self) -> QuestionAndAnswer:
        """
        Retrieve the next question from the question queue.

        Returns:
            QuestionAndAnswer: The next question to be asked
            None: If no questions remain
        """
        try:
            self.current_question = self.questions.pop(0)
            logger.info("Next question ready: %s", self)
            return self.current_question
        except IndexError:
            logger.info("No more questions: %s", self)
            return None


class InterviewEventHandler:
    def __init__(self, broker: "Broker", session_id: UUID):
        self.broker = broker
        self.session_id = session_id

    def __repr__(self) -> str:
        return json.dumps(
            {
                "type": "InterviewEventHandler",
                "session": self.session_id.hex[:8],
            },
            indent=2,
        )

    async def handle_interview_end(
        self, event: InterviewEndEvent
    ):
        """
        Handle the end of an interview session.

        Args:
            event (InterviewEndEvent): Event containing the reason for interview end
                (timeout or questions_exhausted)

        Publishes appropriate end message to the websocket based on the end reason.
        """
        logger.info(
            "Interview ended",
            extra={
                "context": {
                    "session": self.session_id.hex[:8],
                    "reason": event.reason.value,
                    "handler_type": "InterviewEventHandler",
                }
            },
        )

        match event.reason:
            case InterviewEndReason.questions_exhausted:
                end_interview_message = Dispatcher.package_and_transform_to_webframe(
                    "Questions exhausted. Interview ended.",
                    "content",
                    frame_id=str(uuid4()),
                )
                await self.broker.publish(
                    end_interview_message
                )
            case InterviewEndReason.timeout:
                end_interview_message = Dispatcher.package_and_transform_to_webframe(
                    "Timeout. Interview ended.",
                    "content",
                    frame_id=str(uuid4()),
                )
                await self.broker.publish(
                    end_interview_message
                )
            case _:
                logger.info(
                    "Interview ended with unknown reason: %s",
                    {
                        "handler": self,
                        "reason": event.reason,
                    },
                )

    async def handle_ask_question(
        self, event: AskQuestionEvent
    ) -> WebsocketFrame:
        """
        Process and publish a question to be asked during the interview.

        Args:
            event (AskQuestionEvent): Event containing the question to be asked

        Returns:
            WebsocketFrame: The formatted question frame sent to the client

        Publishes both a thought frame and content frame for the question.
        """
        logger.info(
            "Publishing question: %s",
            {
                "handler": self,
                "question_length": len(
                    event.question.question
                ),
            },
        )

        frame_id = str(uuid4())
        question_thought_frame = (
            Dispatcher.package_and_transform_to_webframe(
                event.question,
                "thought",
                frame_id=frame_id,
            )
        )
        await self.broker.publish(question_thought_frame)

        question_frame = (
            Dispatcher.package_and_transform_to_webframe(
                event.question.question,
                "content",
                frame_id=frame_id,
            )
        )
        await self.broker.publish(question_frame)
        return question_frame

    async def handle_questions_gathering_event(
        self, event: QuestionsGatheringEvent
    ) -> None:
        try:
            status_message = event.status.value
            logger.info(
                "Questions gathering status: %s",
                {"handler": self, "status": status_message},
            )

            websocket_frame = Dispatcher.package_and_transform_to_webframe(
                status_message,
                "content",
                frame_id=str(uuid4()),
            )

            await self.broker.publish(websocket_frame)
        except Exception as e:
            logger.error(
                "Questions gathering failed: %s",
                {"handler": self, "error": str(e)},
            )
