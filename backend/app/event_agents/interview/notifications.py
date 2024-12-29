from typing import TYPE_CHECKING
from uuid import uuid4

from app.agents.dispatcher import Dispatcher
from app.event_agents.orchestrator.broker import Broker

if TYPE_CHECKING:
    pass

import logging

logger = logging.getLogger(__name__)


class NotificationManager:
    @staticmethod
    async def send_notification(
        broker: Broker, notification: str
    ) -> None:
        try:
            frame = Dispatcher.package_and_transform_to_webframe(
                notification,  # type: ignore
                "content",
                frame_id=str(uuid4()),
            )
            await broker.publish(frame)
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
