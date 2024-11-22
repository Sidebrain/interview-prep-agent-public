import asyncio
from typing import TYPE_CHECKING
from uuid import UUID, uuid4
from pydantic import BaseModel
import yaml
from app.agents.dispatcher import Dispatcher
from app.event_agents.orchestrator.events import (
    AskQuestionEvent,
    InterviewEndEvent,
    InterviewEndReason,
    QuestionsGatheringEvent,
    Status,
)
import logging

from app.types.interview_concept_types import QuestionAndAnswer
from app.types.websocket_types import WebsocketFrame

if TYPE_CHECKING:
    from app.event_agents.orchestrator.thinker import Thinker
    from app.event_agents.orchestrator.broker import Broker

logger = logging.getLogger(__name__)


class InterviewManager:
    def __init__(
        self,
        broker: "Broker",
        thinker: "Thinker",
        session_id: UUID,
        max_time_allowed: int | None = None,
    ):
        self.broker = broker
        self.thinker = thinker
        self.session_id = session_id
        self.max_time_allowed = (
            max_time_allowed if max_time_allowed else 2 * 60
        )  # 2 minutes default
        self.time_manager = TimeManager(broker, session_id, self.max_time_allowed)
        self.interview_event_handler = InterviewEventHandler(broker, session_id)
        self.question_manager = QuestionManager(thinker)

    async def subscribe(self):
        logger.debug(
            f"Subscribing to questions gathering event for session {self.session_id}"
        )
        await self.broker.subscribe(
            QuestionsGatheringEvent,
            self.interview_event_handler.handle_questions_gathering_event,
        )
        await self.broker.subscribe(
            AskQuestionEvent, self.interview_event_handler.handle_ask_question
        )
        await self.broker.subscribe(
            InterviewEndEvent, self.interview_event_handler.handle_interview_end
        )

    async def initialize(self) -> list[QuestionAndAnswer]:
        logger.info(f"Initializing interview session {self.session_id}")

        # First event
        in_progress_event = QuestionsGatheringEvent(
            status=Status.in_progress,
            session_id=self.session_id,
        )

        await self.broker.publish(in_progress_event)

        # gather questions and store them in the instance variable
        questions = await self.question_manager.gather_questions()

        # Second event
        completed_question_gathering_event = QuestionsGatheringEvent(
            status=Status.completed,
            session_id=self.session_id,
        )

        await self.broker.publish(completed_question_gathering_event)
        logger.debug(
            f"\033[33m\nCompleted gathering {len(self.question_manager.questions)} questions. Published event.\n\033[0m"
        )

        # Start time tracking in the background
        asyncio.create_task(self.time_manager.start_timer())

        let_user_know_timer_started_event = Dispatcher.package_and_transform_to_webframe(
            f"Timer started. You have {self.max_time_allowed} {'seconds' if self.max_time_allowed <= 60 else 'minutes'} to answer the questions.",
            "content",
            frame_id=str(uuid4()),
        )
        await self.broker.publish(let_user_know_timer_started_event)

        # Start asking questions
        try:
            await self.ask_next_question()
        except Exception as e:
            logger.error(f"Error asking next question: {e}", exc_info=True)

        return questions

    async def ask_next_question(self) -> None:
        logger.debug(
            f"\033[33mAsking next question for session {self.session_id}\033[0m"
        )
        logger.debug(
            f"\033[33mQuestions left: {len(self.question_manager.questions)}\033[0m"
        )
        logger.debug(
            f"\033[33mCurrent question: {self.question_manager.current_question}\033[0m"
        )

        next_question = await self.question_manager.get_next_question()
        if next_question is None:
            logger.info(f"No questions left to ask for session {self.session_id}")
            interview_end_event = InterviewEndEvent(
                reason=InterviewEndReason.questions_exhausted,
                session_id=self.session_id,
            )
            await self.broker.publish(interview_end_event)
            return
        else:
            ask_question_event = AskQuestionEvent(
                question=next_question,
                session_id=self.session_id,
            )
            await self.broker.publish(ask_question_event)


class TimeManager:
    def __init__(self, broker: "Broker", session_id: UUID, max_time_allowed: int):
        self.broker = broker
        self.session_id = session_id
        self.max_time_allowed = max_time_allowed
        self.time_elapsed = 0

    async def start_timer(self) -> None:
        """
        Continuously checks if the interview has exceeded the maximum allowed time.
        If exceeded, emits an InterviewEndEvent with timeout reason.
        """
        while True:
            await asyncio.sleep(5)  # Check every 5 seconds
            self.time_elapsed += 5

            if self.time_elapsed >= self.max_time_allowed:
                logger.info(f"Interview timeout reached ")
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
        self.current_question: QuestionAndAnswer | None = None

    async def gather_questions(self) -> list[QuestionAndAnswer]:
        with open("config/artifacts.yaml", "r") as f:
            artifacts = yaml.safe_load(f)
        question_string = artifacts["artifacts"]["interview_questions"]
        logger.debug(
            f"Loaded question template (first 100 chars): {question_string[:100]}"
        )

        messages = [
            {"role": "user", "content": question_string},
        ]

        class Questions(BaseModel):
            questions: list[QuestionAndAnswer]

        response: Questions = await self.thinker.extract_structured_response(
            Questions, messages=messages, debug=True
        )
        self.questions = response.questions
        return response.questions

    async def get_next_question(self) -> QuestionAndAnswer:
        try:
            self.current_question = self.questions.pop(0)
            logger.debug(
                f"\033[31mAsking question: {self.current_question.question} \033[0m"
            )
            return self.current_question
        except IndexError:
            logger.info(f"No questions left to ask")
            return None


class InterviewEventHandler:
    def __init__(self, broker: "Broker", session_id: UUID):
        self.broker = broker
        self.session_id = session_id

    async def handle_interview_end(self, event: InterviewEndEvent):
        logger.info(f"Interview ended for session {self.session_id}")
        match event.reason:
            case InterviewEndReason.questions_exhausted:
                logger.info(f"Questions exhausted for session {self.session_id}")
                end_interview_message = Dispatcher.package_and_transform_to_webframe(
                    "Questions exhausted. Interview ended.",
                    "content",
                    frame_id=str(uuid4()),
                )
                await self.broker.publish(end_interview_message)
            case InterviewEndReason.timeout:
                logger.info(f"Timeout for session {self.session_id}")
                end_interview_message = Dispatcher.package_and_transform_to_webframe(
                    "Timeout. Interview ended.",
                    "content",
                    frame_id=str(uuid4()),
                )
                await self.broker.publish(end_interview_message)
            case _:
                logger.info(f"Interview ended for session {self.session_id}")

    async def handle_ask_question(self, event: AskQuestionEvent) -> WebsocketFrame:
        """
        Ask the next question.
        """
        frame_id = str(uuid4())
        question_thought_frame = Dispatcher.package_and_transform_to_webframe(
            event.question,
            "thought",
            frame_id=frame_id,
        )
        await self.broker.publish(question_thought_frame)

        question_frame = Dispatcher.package_and_transform_to_webframe(
            event.question.question,
            "content",
            frame_id=frame_id,
        )
        await self.broker.publish(question_frame)
        return question_frame

    async def handle_questions_gathering_event(self, event: QuestionsGatheringEvent):
        """
        Handle the questions gathered event.
        """
        try:
            status_message = self.gathering_status_string(event.status)
            logger.debug(f"Questions gathering status: {status_message}")

            websocket_frame = Dispatcher.package_and_transform_to_webframe(
                status_message,
                "content",
                frame_id=str(uuid4()),
            )

            await self.broker.publish(websocket_frame)
        except Exception as e:
            logger.error(
                f"Error handling questions gathering event: {e}", exc_info=True
            )
            # You might want to publish an error event here

    def gathering_status_string(self, status: Status) -> str:
        match status:
            case Status.in_progress:
                return "Questions gathering in progress."
            case Status.completed:
                return "Questions gathering completed."
            case Status.failed:
                return "Questions gathering failed."
            case Status.idle:
                return "Questions gathering idle."
