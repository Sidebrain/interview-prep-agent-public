from functools import singledispatch
from app.types.websocket_types import AddressType, WebsocketFrame, CompletionFrameChunk
from openai.types.chat import ChatCompletion
from pydantic import BaseModel
from uuid import uuid4

from app.constants import DEBUG_CONFIG, model

import logging

# Create a logger instance
logger = logging.getLogger(__name__)


class Dispatcher:
    debug = DEBUG_CONFIG["dispatcher"]

    @singledispatch
    def package_and_transform_to_webframe(
        response,
        address: AddressType,
        frame_id: str,
        title: str = None,
        debug: bool = False,
    ) -> WebsocketFrame: ...

    @package_and_transform_to_webframe.register(ChatCompletion)
    def _(
        response,
        address: AddressType,
        frame_id: str,
        title: str = None,
        debug: bool = False,
    ):

        completion_frame = CompletionFrameChunk(
            id=response.id,
            object=response.object,
            model=response.model,
            role=response.choices[0].message.role,
            content=response.choices[0].message.content,
            delta=None,
            title=title,
            index=response.choices[0].index,
            finish_reason=response.choices[0].finish_reason,
        )

        websocket_frame = WebsocketFrame(
            frame_id=frame_id,
            type="completion",
            address=address,
            frame=completion_frame,
        )

        if Dispatcher.debug and debug:
            logger.debug(websocket_frame.model_dump_json(indent=4))

        return websocket_frame

    @package_and_transform_to_webframe.register(BaseModel)
    def _(
        response,
        address: AddressType,
        frame_id: str,
        title: str = None,
        debug: bool = False,
    ):
        completion_frame = CompletionFrameChunk(
            id=str(uuid4()),
            object="chat.completion",
            model=model,
            role="assistant",
            content=response.model_dump_json(indent=4, by_alias=True),
            delta=None,
            title=title,
            index=0,
            finish_reason="stop",
        )

        websocket_frame = WebsocketFrame(
            frame_id=frame_id,
            type="completion",
            address=address,
            frame=completion_frame,
        )

        if Dispatcher.debug and debug:
            logger.debug(websocket_frame.model_dump_json(indent=4))

        return websocket_frame
