import logging
from typing import Type, TypeVar

import instructor
from openai import AsyncClient
from openai.types.chat import ChatCompletion
from pydantic import BaseModel

from app.constants import DEBUG_CONFIG, model
from app.event_agents.roles.types import RoleContext
from app.services.llms.openai_client import openai_async_client

# Create a logger instance
logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class Thinker:
    debug = DEBUG_CONFIG["thinker"]

    def __init__(
        self,
        client: AsyncClient = openai_async_client,
    ) -> None:
        self.client = client
        self._role_context: RoleContext | None = None

    @property
    def role_context(self) -> RoleContext | None:
        return self._role_context

    @role_context.setter
    def role_context(self, role_context: RoleContext) -> None:
        self._role_context = role_context

    def _boost_message_context_with_role(
        self, messages: list[dict[str, str]]
    ) -> list[dict[str, str]]:
        if self.role_context:
            messages.insert(
                0,
                {
                    "role": "system",
                    "content": self.role_context.system_prompt,
                },
            )
        return messages

    async def generate(
        self,
        messages: list[dict[str, str]],
        use_role_context: bool = True,
        debug: bool = False,
        max_tokens: int | None = None,
    ) -> ChatCompletion:
        # kwargs with None values are not passed to the client
        if use_role_context:
            messages = self._boost_message_context_with_role(messages)

        kwargs = {
            "messages": messages,
            "model": model,
        }
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens  # type: ignore

        # having to manually specify type, because kwargs unpacking breaks the type inference
        response: ChatCompletion = (
            await self.client.chat.completions.create(
                **kwargs  # type: ignore
            )
        )

        if self.debug and debug:
            logger.debug(response.model_dump_json(indent=4))

        return response

    async def extract_structured_response(
        self,
        pydantic_structure_to_extract: Type[T],
        messages: list[dict[str, str]],
        debug: bool = False,
        use_role_context: bool = False,
    ) -> T:
        if use_role_context:
            messages = self._boost_message_context_with_role(messages)

        instructor_client = instructor.from_openai(self.client)
        extracted_structure = (
            await instructor_client.chat.completions.create(
                model=model,
                response_model=pydantic_structure_to_extract,
                messages=messages,  # type: ignore
            )
        )
        if self.debug and debug:
            logger.debug(extracted_structure.model_dump_json(indent=4))

        return extracted_structure

    async def think_with_tool(
        self,
        messages: list[dict[str, str]],
        tool: dict[str, str],
        debug: bool = False,
        use_role_context: bool = False,
    ) -> ChatCompletion:
        if use_role_context:
            messages = self._boost_message_context_with_role(messages)

        response = await self.client.chat.completions.create(
            messages=messages,  # type: ignore
            model=model,
            tools=[{"type": "function", "function": tool}],
        )
        if self.debug and debug:
            logger.debug(response.model_dump_json(indent=4))

        return response
