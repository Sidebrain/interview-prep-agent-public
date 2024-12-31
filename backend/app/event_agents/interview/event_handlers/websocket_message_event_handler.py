import logging
import traceback

from app.event_agents.orchestrator.events import (
    ErrorEvent,
)
from app.event_agents.types import InterviewContext
from app.types.websocket_types import WebsocketFrame

logger = logging.getLogger(__name__)


class WebsocketMessageEventHandler:
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
