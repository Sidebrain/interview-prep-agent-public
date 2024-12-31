import json
import logging

from app.event_agents.orchestrator.events import (
    AddToMemoryEvent,
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
