from typing import Literal

from pydantic import BaseModel


class WebSocketStreamResponse(BaseModel):
    id: int
    type: Literal["chunk", "complete", "error", "heartbeat", "structured"]
    index: int = 0
    content: str | None
    sender: str = "bot"
