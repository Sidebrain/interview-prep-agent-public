import json
import logging
import traceback
from uuid import uuid4

from app.agents.dispatcher import Dispatcher
from app.event_agents.orchestrator.events import (
    AddToMemoryEvent,
    AskQuestionEvent,
    ErrorEvent,
    MessageReceivedEvent,
)
from app.event_agents.types import InterviewContext
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
