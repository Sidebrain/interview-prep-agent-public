from typing import TYPE_CHECKING
from uuid import uuid4

from app.agents.dispatcher import Dispatcher
from app.event_agents.types import AgentContext

if TYPE_CHECKING:
    pass

import logging

logger = logging.getLogger(__name__)


class NotificationManager:
    @staticmethod
    async def send_notification(
        agent_context: "AgentContext", notification: str
    ) -> None:
        try:
            frame = Dispatcher.package_and_transform_to_webframe(
                notification,  # type: ignore
                "content",
                frame_id=str(uuid4()),
            )
            await agent_context.broker.publish(frame)
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
