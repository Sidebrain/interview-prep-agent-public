from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from pydantic.json_schema import GenerateJsonSchema
from typing import Literal, List, Optional


class CompletionFrameChunk(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
    id: str
    object: Literal["chat.completion", "chat.completion.chunk", "human.completion"]
    model: str
    role: Literal["assistant", "user"]
    content: str | None
    delta: str | None
    index: int = 0
    finish_reason: Literal[
        "stop",
        "length",
        "tool_calls",
        "content_filter",
        "function_call",
    ]


class WebsocketFrame(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
    frame_id: str
    type: Literal["completion", "streaming", "heartbeat", "error", "input"]
    address: Literal["content", "artefact", "human", "thought"]
    frame: CompletionFrameChunk


## Old types


class WebSocketStreamResponse(BaseModel):
    id: int
    type: Literal["chunk", "complete", "error", "heartbeat", "structured"]
    index: int = 0
    content: str | None
    sender: str = "bot"
