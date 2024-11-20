import instructor
from openai import AsyncClient
from openai.types.chat import ChatCompletion
from pydantic import BaseModel

from app.constants import DEBUG_CONFIG, model
from app.services.llms.openai_client import openai_async_client

import logging

# Create a logger instance
logger = logging.getLogger(__name__)

from openai import AsyncClient


class Thinker:
    debug = DEBUG_CONFIG["thinker"]

    def __init__(self, client: AsyncClient = None, debug: bool = True):
        if client is None:
            client = openai_async_client
        self.client = client
        self.debug = debug

    async def generate(
        self, messages: list[dict[str, str]], debug: bool = False
    ) -> ChatCompletion:
        response = await self.client.chat.completions.create(
            messages=messages,
            model=model,
        )

        if self.debug and debug:
            logger.debug(response.model_dump_json(indent=4))

        return response

    async def extract_structured_response(
        self,
        pydantic_structure_to_extract: BaseModel,
        messages: list[dict[str, str]],
        debug: bool = False,
    ) -> BaseModel:
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
        self, messages: list[dict[str, str]], tool: dict[str, str], debug: bool = False
    ) -> ChatCompletion:
        response = await self.client.chat.completions.create(
            messages=messages,
            model=model,
            tools=[{"type": "function", "function": tool}],
        )
        if self.debug and debug:
            logger.debug(response.model_dump_json(indent=4))

        return response
