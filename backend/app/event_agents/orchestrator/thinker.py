from typing import Type, TypeVar
import instructor
from openai import AsyncClient
from openai.types.chat import ChatCompletion
from pydantic import BaseModel

from app.constants import DEBUG_CONFIG, model
from app.services.llms.openai_client import openai_async_client

import logging

# Create a logger instance
logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)



class Thinker:
    debug = DEBUG_CONFIG["thinker"]

    def __init__(self, client: AsyncClient = None):
        if client is None:
            client = openai_async_client
        self.client = client

    async def generate(
        self,
        messages: list[dict[str, str]],
        debug: bool = False,
        max_tokens: int | None = None,
    ) -> ChatCompletion:
        # kwargs with None values are not passed to the client
        kwargs = {
            "messages": messages,
            "model": model,
        }
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        # having to manually specify type, because kwargs unpacking breaks the type inference
        response: ChatCompletion = await self.client.chat.completions.create(
            **kwargs
        )

        if self.debug and debug:
            logger.debug(response.model_dump_json(indent=4))

        return response

    async def extract_structured_response(
        self,
        pydantic_structure_to_extract: Type[T],
        messages: list[dict[str, str]],
        debug: bool = False,
    ) -> T:
        instructor_client = instructor.from_openai(self.client)
        extracted_structure = await instructor_client.chat.completions.create(
            model=model,
            response_model=pydantic_structure_to_extract,
            messages=messages,
        )
        if self.debug and debug:
            logger.debug(extracted_structure.model_dump_json(indent=4))

        return extracted_structure

    async def think_with_tool(
        self,
        messages: list[dict[str, str]],
        tool: dict[str, str],
        debug: bool = False,
    ) -> ChatCompletion:
        response = await self.client.chat.completions.create(
            messages=messages,
            model=model,
            tools=[{"type": "function", "function": tool}],
        )
        if self.debug and debug:
            logger.debug(response.model_dump_json(indent=4))

        return response
