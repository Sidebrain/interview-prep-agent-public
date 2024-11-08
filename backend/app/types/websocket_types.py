from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic.json_schema import GenerateJsonSchema
from typing import Literal, List, Optional

AddressType = Literal["content", "artifact", "human", "thought"]


class CompletionFrameChunk(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
    id: str
    object: Literal[
        "chat.completion", "chat.completion.chunk", "human.completion", "human.signal"
    ]
    model: str
    role: Literal["assistant", "user"]
    content: str | None
    delta: str | None
    created_ts: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    title: str | None = None
    index: int = 0
    finish_reason: Literal[
        "stop",
        "length",
        "tool_calls",
        "content_filter",
        "function_call",
    ]

    def get_human_readable_created_ts(self) -> str:
        return datetime.fromtimestamp(self.created_ts).strftime("%Y-%m-%d %H:%M:%S")


class WebsocketFrame(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
    frame_id: str
    type: Literal["completion", "streaming", "heartbeat", "error", "input"]
    address: AddressType
    frame: CompletionFrameChunk


## Old types


class WebSocketStreamResponse(BaseModel):
    id: int
    type: Literal["chunk", "complete", "error", "heartbeat", "structured"]
    index: int = 0
    content: str | None
    sender: str = "bot"
