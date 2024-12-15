import asyncio
import logging
import json

from uuid import UUID

from app.event_agents.interview.notifications import NotificationManager

logger = logging.getLogger(__name__)

class TimeManager:
    def __init__(
        self,
        notification_manager: "NotificationManager",
        session_id: UUID,
        max_time_allowed: int,
    ):
        self.notification_manager = notification_manager
        self.session_id = session_id
        self.max_time_allowed = max_time_allowed
        self.time_elapsed = 0

    def __repr__(self) -> str:
        return json.dumps(
            {
                "type": "TimeManager",
                "session": self.session_id.hex[:8],
                "elapsed": self.time_elapsed,
                "remaining": self.max_time_allowed - self.time_elapsed,
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
                await self.notification_manager.send_notification(
                    "Interview timeout reached. Ending interview..."
                )
                break
