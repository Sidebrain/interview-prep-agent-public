from typing import Literal

from pydantic import BaseModel


class AgentMessage(BaseModel):
    content: str
    routing_key: Literal["streaming", "structured"]


