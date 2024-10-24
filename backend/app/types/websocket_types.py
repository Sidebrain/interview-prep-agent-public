from pydantic import BaseModel
from typing import List, Union, Literal, Optional


class CompletionFrameChunk(BaseModel):
    id: str
    object: Literal["chat.completion"]
    model: str
    role: Literal["assistant"]
    content: str
    finish_reason: Literal["stop"]


class StreamingFrameChunk(BaseModel):
    id: str
    object: Literal["chat.completion.chunk"]
    model: str
    index: int
    content: str
    role: Literal["assistant"]
    finsh_reason: Optional[Literal["stop"]]

class WebsocketFrame(BaseModel):
    frameId: str
    type: Literal["completion", "streaming", "heartbeat", "error"]
    address: Literal["content", "artefact"]
    frame: Union[CompletionFrameChunk, StreamingFrameChunk]


## Old types


class WebSocketStreamResponse(BaseModel):
    id: int
    type: Literal["chunk", "complete", "error", "heartbeat", "structured"]
    index: int = 0
    content: str | None
    sender: str = "bot"
