from datetime import datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

RoleType = Literal["assistant", "user"]
FinishReasonType = Literal[
    "stop",
    "length",
    "tool_calls",
    "content_filter",
    "function_call",
]

AddressType = Literal[
    "content",
    "artifact",
    "human",
    "thought",
    "evaluation",
    "perspective",
    "notification",
]
FrameType = Literal[
    "completion",
    "streaming",
    "heartbeat",
    "error",
    "input",
    "signal.regenerate",
]
ObjectType = Literal[
    "chat.completion",
    "chat.completion.chunk",
    "human.completion",
]


class CompletionFrameChunk(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
    id: str
    object: ObjectType
    model: str
    role: RoleType
    content: str | None
    delta: str | None
    created_ts: int = Field(
        default_factory=lambda: int(datetime.now().timestamp())
    )
    title: str | None = None
    index: int = 0
    finish_reason: FinishReasonType

    def get_human_readable_created_ts(self) -> str:
        return datetime.fromtimestamp(self.created_ts).strftime(
            "%Y-%m-%d %H:%M:%S"
        )


class WebsocketFrame(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
    frame_id: str
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))
    type: FrameType
    address: AddressType
    frame: CompletionFrameChunk


## Old types


class WebSocketStreamResponse(BaseModel):
    id: int
    type: Literal[
        "chunk",
        "complete",
        "error",
        "heartbeat",
        "structured",
    ]
    index: int = 0
    content: str | None
    sender: str = "bot"
