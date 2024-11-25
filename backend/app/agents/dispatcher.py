from functools import singledispatch
from app.types.websocket_types import (
    AddressType,
    WebsocketFrame,
    CompletionFrameChunk,
)
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
        correlation_id: str | None = None,
        title: str = None,
        debug: bool = False,
    ) -> WebsocketFrame: ...

    @package_and_transform_to_webframe.register(str)
    def _(
        response,
        address: AddressType,
        frame_id: str,
        correlation_id: str | None = None,
        title: str = None,
        debug: bool = False,
    ) -> WebsocketFrame:
        """
            Base dispatch method for transforming responses into WebSocket frames.
            This method serves as the base for type-specific implementations.

            Args:
                response: The response object to transform
                address (AddressType): The destination address for the WebSocket frame
                frame_id (str): Unique identifier for the frame
                title (str, optional): Optional title for the completion frame
                debug (bool, optional): Flag to enable debug logging

        Returns:
            WebsocketFrame: A standardized WebSocket frame

        Raises:
                NotImplementedError: If no implementation exists for the response type
        """
        completion_frame = CompletionFrameChunk(
            id=str(uuid4()),
            object="chat.completion",
            model=model,
            role="assistant",
            content=response,
            delta=None,
            title=title,
            index=0,
            finish_reason="stop",
        )

        if correlation_id is None:
            correlation_id = str(uuid4())

        websocket_frame = WebsocketFrame(
            frame_id=frame_id,
            correlation_id=correlation_id,
            type="completion",
            address=address,
            frame=completion_frame,
        )

        if Dispatcher.debug and debug:
            logger.debug(
                websocket_frame.model_dump_json(indent=4)
            )

        return websocket_frame

    @package_and_transform_to_webframe.register(
        ChatCompletion
    )
    def _(
        response,
        address: AddressType,
        frame_id: str,
        correlation_id: str | None = None,
        title: str = None,
        debug: bool = False,
    ) -> WebsocketFrame:

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

        if correlation_id is None:
            correlation_id = str(uuid4())

        websocket_frame = WebsocketFrame(
            frame_id=frame_id,
            correlation_id=correlation_id,
            type="completion",
            address=address,
            frame=completion_frame,
        )

        if Dispatcher.debug and debug:
            logger.debug(
                websocket_frame.model_dump_json(indent=4)
            )

        return websocket_frame

    @package_and_transform_to_webframe.register(BaseModel)
    def _(
        response,
        address: AddressType,
        frame_id: str,
        correlation_id: str | None = None,
        title: str = None,
        debug: bool = False,
    ) -> WebsocketFrame:
        completion_frame = CompletionFrameChunk(
            id=str(uuid4()),
            object="chat.completion",
            model=model,
            role="assistant",
            content=response.model_dump_json(
                indent=4, by_alias=True
            ),
            delta=None,
            title=title,
            index=0,
            finish_reason="stop",
        )

        if correlation_id is None:
            correlation_id = str(uuid4())

        websocket_frame = WebsocketFrame(
            frame_id=frame_id,
            correlation_id=correlation_id,
            type="completion",
            address=address,
            frame=completion_frame,
        )

        if Dispatcher.debug and debug:
            logger.debug(
                websocket_frame.model_dump_json(indent=4)
            )

        return websocket_frame
