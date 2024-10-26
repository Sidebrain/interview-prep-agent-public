from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from pydantic.json_schema import GenerateJsonSchema
from typing import Literal, List, Optional


######### Receiving Types #########


class ModelControlsConfig(BaseModel):
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: Optional[List[str]] = None


class ModelControls(BaseModel):
    model: str
    provider: str
    controls: ModelControlsConfig


class WebsocketFromFrontendType(BaseModel):
    content: str
    # attachments: List[bytes]  # Equivalent to Blob array in TypeScript
    controls: Optional[ModelControls] = None


######### Sending Types #########


class CompletionFrameChunk(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
    id: str
    object: Literal["chat.completion"]
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
    type: Literal["completion", "streaming", "heartbeat", "error"]
    address: Literal["content", "artefact"]
    frame: CompletionFrameChunk


## Old types


class WebSocketStreamResponse(BaseModel):
    id: int
    type: Literal["chunk", "complete", "error", "heartbeat", "structured"]
    index: int = 0
    content: str | None
    sender: str = "bot"
