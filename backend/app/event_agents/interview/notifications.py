from typing import TYPE_CHECKING
from uuid import uuid4

from app.agents.dispatcher import Dispatcher

if TYPE_CHECKING:
    from app.event_agents.orchestrator.broker import Broker

import logging

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self, broker: "Broker") -> None:
        self.broker = broker

    async def send_notification(self, notification: str) -> None:
        try:    
            frame = Dispatcher.package_and_transform_to_webframe(
                notification,
                "content",
                frame_id=str(uuid4()),
            )
            await self.broker.publish(frame)
        except Exception as e:
            logger.error(f"Error sending notification: {e}")

