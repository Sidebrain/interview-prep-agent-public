import asyncio
import json
import logging
import math
import traceback
from typing import Awaitable, Callable
from uuid import uuid4

from app.agents.dispatcher import Dispatcher
from app.event_agents.evaluations.manager import EvaluationManager
from app.event_agents.interview.notifications import NotificationManager
from app.event_agents.interview.question_manager import QuestionManager
from app.event_agents.interview.time_manager import TimeManager
from app.event_agents.orchestrator.events import (
    AddToMemoryEvent,
    AskQuestionEvent,
    ErrorEvent,
    MessageReceivedEvent,
)
from app.event_agents.perspectives.manager import PerspectiveManager
from app.event_agents.types import InterviewContext
from app.types.interview_concept_types import QuestionAndAnswer
from app.types.websocket_types import WebsocketFrame

logger = logging.getLogger(__name__)


class MessageEventHandler:
    def __init__(self, interview_context: InterviewContext) -> None:
        self.interview_context = interview_context

    async def handler(self, event: MessageReceivedEvent) -> None:
        try:
            message = event.message
            if message is None:
                return
            parsed_message = WebsocketFrame.model_validate_json(
                message, strict=False
            )
            logger.info(
                f"Received message, parsed into websocket frame: {parsed_message}"
            )
            new_memory = AddToMemoryEvent(
                frame=parsed_message,
                interview_id=self.interview_context.interview_id,
            )
            await self.interview_context.broker.publish(new_memory)

        except json.JSONDecodeError:
            logger.error("Failed to decode the message")
            return
        except Exception as e:
            logger.error(
                f"Error in handle_message_received_event: {str(e)}"
            )
            raise


class WebsocketEventHandler:
    def __init__(self, interview_context: InterviewContext) -> None:
        self.interview_context = interview_context

    async def handler(self, event: WebsocketFrame) -> None:
        try:
            await self.interview_context.channel.send_message(
                event.model_dump_json(by_alias=True)
            )
        except Exception as e:
            logger.error(
                f"Error in handle_websocket_frame: {str(e)}",
                extra={
                    "context": {
                        "event": event.model_dump(by_alias=True),
                        "agent_id": str(
                            self.interview_context.agent_id
                        ),
                        "interview_id": str(
                            self.interview_context.interview_id
                        ),
                        "traceback": traceback.format_exc(),
                    }
                },
            )
            error_event = ErrorEvent(
                error=str(e),
                interview_id=self.interview_context.interview_id,
            )
            await self.interview_context.broker.publish(error_event)
            raise


class AskQuestionEventHandler:
    def __init__(self, interview_context: InterviewContext) -> None:
        self.interview_context = interview_context

    async def handler(self, event: AskQuestionEvent) -> None:
        """Send the question to the user."""
        frame_id = str(uuid4())
        question_thought_frame = (
            Dispatcher.package_and_transform_to_webframe(
                event.question,  # type: ignore
                "thought",
                frame_id=frame_id,
            )
        )
        question_frame = Dispatcher.package_and_transform_to_webframe(
            event.question.question,  # type: ignore
            "content",
            frame_id=frame_id,
        )
        await self.interview_context.broker.publish(
            question_thought_frame
        )
        await self.interview_context.broker.publish(question_frame)


class AnswerProcessor:
    def __init__(
        self,
        interview_context: InterviewContext,
        question_manager: QuestionManager,
        evaluation_manager: EvaluationManager,
        perspective_manager: PerspectiveManager,
    ) -> None:
        self.interview_context = interview_context
        self.question_manager = question_manager
        self.evaluation_manager = evaluation_manager
        self.perspective_manager = perspective_manager

    async def handler(self, event: AddToMemoryEvent) -> None:
        """Process the answer."""
        try:
            await self._add_answer_to_memory(event)
            await self._generate_evaluations_and_perspectives()
            await self.question_manager.ask_next_question()
        except Exception as e:
            logger.error(
                f"Error in handle_add_to_memory_event: {str(e)}"
            )
            raise

    async def _add_answer_to_memory(
        self, event: AddToMemoryEvent
    ) -> None:
        """Add the answer to memory."""
        await self.interview_context.memory_store.add(event.frame)

    async def _generate_evaluations_and_perspectives(self) -> None:
        """Generate and publish evaluations and perspectives for the current question."""
        evaluations, perspectives = await asyncio.gather(
            self._generate_evaluations(), self._generate_perspectives()
        )

        logger.info(
            "Answer processed",
            extra={
                "manager": self,
                "evaluation_count": len(evaluations),
                "perspective_count": len(perspectives),
            },
        )

        await self._publish_results(evaluations, perspectives)

    async def _generate_evaluations(self) -> list[WebsocketFrame]:
        """Generate evaluations for the current question."""
        if self.question_manager.current_question is None:
            return []
        evaluations = await self.evaluation_manager.handle_evaluation(
            questions=[self.question_manager.current_question]
        )
        logger.info(
            "Evaluations generated",
            extra={
                "context": {
                    "evaluation_count": len(evaluations),
                }
            },
        )
        return evaluations

    async def _generate_perspectives(self) -> list[WebsocketFrame]:
        """Generate perspectives for the current question."""
        if self.question_manager.current_question is None:
            return []
        perspectives = (
            await self.perspective_manager.handle_perspective(
                questions=[self.question_manager.current_question]
            )
        )
        logger.info(
            "Perspectives generated",
            extra={
                "context": {
                    "manager": self,
                    "perspective_count": len(perspectives),
                }
            },
        )
        return perspectives

    async def _publish_results(
        self,
        evaluations: list[WebsocketFrame],
        perspectives: list[WebsocketFrame],
    ) -> None:
        """Publish evaluations and perspectives to the broker."""
        for evaluation in evaluations:
            await self.interview_context.broker.publish(evaluation)
        for perspective in perspectives:
            await self.interview_context.broker.publish(perspective)

    def _get_answer_length(
        self, new_memory_event: AddToMemoryEvent
    ) -> int:
        """Calculate the length of the answer content."""
        return (
            len(new_memory_event.frame.frame.content)
            if new_memory_event.frame.frame.content
            else 0
        )


class InterviewLifecyceManager:
    def __init__(
        self,
        interview_context: InterviewContext,
        question_manager: QuestionManager,
        time_manager: TimeManager,
        evaluation_manager: EvaluationManager,
        perspective_manager: PerspectiveManager,
        setup_subscribers: Callable[[], Awaitable[None]],
    ) -> None:
        self.interview_context = interview_context
        self.question_manager = question_manager
        self.time_manager = time_manager
        self.evaluation_manager = evaluation_manager
        self.perspective_manager = perspective_manager
        self.setup_subscribers = setup_subscribers

    async def stop(self) -> None:
        """Stop the interview manager and clean up all resources."""
        await self.interview_context.broker.stop()

    async def initialize(self) -> list[QuestionAndAnswer]:
        logger.info("Starting new interview session: %s", self)

        # originally part of start function of agent
        await self.setup_subscribers()
        await self.interview_context.broker.start()

        await self.question_manager.initialize()

        timer_notification_string = await self.start_interview_timer()

        await NotificationManager.send_notification(
            self.interview_context.broker,
            timer_notification_string,
        )

        await self.initialize_evaluation_systems()
        await self.begin_questioning()

        self.save_state()

        return self.question_manager.questions

    async def start_interview_timer(self) -> str:
        """Start the interview timer and notify the user."""
        asyncio.create_task(self.time_manager.start_timer())
        logger.info("Timer started: %s", self.time_manager)

        time_unit = (
            "seconds"
            if self.interview_context.max_time_allowed < 60
            else "minutes"
        )
        time_to_answer = (
            self.interview_context.max_time_allowed
            if self.interview_context.max_time_allowed < 60
            else math.ceil(self.interview_context.max_time_allowed / 60)
        )

        timer_notification_string = f"Timer started. You have {time_to_answer} {time_unit} to answer the questions."
        return timer_notification_string

    def save_state(self) -> None:
        self.question_manager.save_state()
        self.evaluation_manager.evaluator_registry.save_state()

    async def initialize_evaluation_systems(self) -> None:
        """Initialize evaluation and perspective systems."""
        await self.evaluation_manager.evaluator_registry.initialize()
        await NotificationManager.send_notification(
            self.interview_context.broker,
            "Evaluator registry initialized.",
        )

        await self.perspective_manager.perspective_registry.initialize()
        await NotificationManager.send_notification(
            self.interview_context.broker,
            "Perspective registry initialized.",
        )

    async def begin_questioning(self) -> None:
        """Start the question-asking process."""
        try:
            await self.question_manager.ask_next_question()
        except Exception as e:
            logger.error(
                "Failed to ask first question",
                extra={
                    "interview_id": self.interview_context.interview_id,
                    "manager_state": repr(self),
                    "error": str(e),
                },
                exc_info=True,
            )
