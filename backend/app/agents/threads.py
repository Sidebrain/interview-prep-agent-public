import asyncio
from functools import singledispatchmethod
import json
from typing_extensions import Required
from typing import Literal, Optional, Tuple, TypedDict, Union, Iterable

from fastapi import WebSocket
from openai import AsyncClient
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from pydantic import BaseModel, Field

#! remove later
import openai
import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai_async_client = openai.AsyncClient(
    api_key=OPENAI_API_KEY,
)
################################

StopReason = Literal["stop", "length", "tool_calls", "content_filter", "function_call"]


class ArtificialIntelligence:
    def __init__(self, client: AsyncClient = None) -> None:
        if not client:
            client = openai_async_client
        self.client = client

    async def generate(
        self, messages: list[dict[str, str]] = None
    ) -> Tuple[ChatCompletionMessage, StopReason]:
        tool = {
            "name": "hiring_manager_requirements",
            "description": "Gather hiring manager requirements to construct the job artefacts that will help with recruiting.",
            "parameters": HiringManagerRequirements.model_json_schema(),
        }

        response = await self.client.chat.completions.create(
            messages=messages,
            model="gpt-4o-mini",
            tools=[{"type": "function", "function": tool}],
        )
        finish_reason = response.choices[0].finish_reason
        message = response.choices[0].message
        return message, finish_reason
        # return response
        # return response.choices[0].message.content


#### PYdantic schema of data needed before functiona call is invoked ####
class HiringManagerRequirements(BaseModel):
    role: str = Field(..., description="The role you are hiring for")
    designation: str = Field(..., description="The official designation of the person ")
    company_name: str = Field(..., description="The name of the company")
    requirement_detailsd: str = Field(
        ...,
        description="and seniority (junior, mid, senior), whether they have experience building a team",
    )
    budget_for_role: int = Field(..., description="The budget for the role")
    expected_salary: int = Field(..., description="The expected salary for the role")
    backup_plan: str = Field(
        ...,
        description="The backup plan if the role is not filled or the candidate is not a godf for",
    )
    # hiring_timeline: strNumber = Field(..., description="The timeline for hiring")
    culture_fit: str

    pass


class Agent:
    def __init__(
        self,
    ) -> None:
        self.goal = ...
        self.intellect = ArtificialIntelligence()
        self.messages = [
            {
                "role": "system",
                "content": """
You are a helpful recruitment coordinator. 
You are here to help gather hiring manager requirements. 
You are conversational and ask questions one by one, not all at once. 
""",
            }
        ]

    async def single_turn(self) -> None:
        if len(self.messages) >= 2:
            user_input = input("Enter your response: ")
            self.load_message_to_memory(user_input)
        response_message, stop_reason = await self.intellect.generate(self.messages)
        print(response_message.content, end=f"\n{"-"*30}\n")
        # generate eval answer
        await self.generate_evaluation(response_message)
        self.load_message_to_memory(response_message)
        return response_message, stop_reason

    async def execute(self) -> None:
        _, stop_reason = await self.single_turn()
        while stop_reason != "tool_calls":
            response_msg, stop_reason = await self.single_turn()
        self.relegate_control()

    async def generate_evaluation(
        self, assistant_output: ChatCompletionMessage
    ) -> None:
        system = """You are the hiring manager. You are here to provide the requirements for the role you are hiring for. You give thorough and detailed answers to every question you are asked.
You are not tied to any company, role or team, you can answer freely. You are allowed to make any assumptions or provide any information you think is relevant.
You answer the question but also take context into account and know when the question asked was already answered in the context."""
        shadow_message_list = [
            {"role": "system", "content": system},
            {"role": "user", "content": assistant_output.content},
        ]
        response_msg, stop_reason = await self.intellect.generate(
            messages=shadow_message_list
        )
        print(response_msg.content, end=f"\n{"x"*30}\n")

        return system

    @singledispatchmethod
    def load_message_to_memory(self, message) -> None:
        raise NotImplementedError

    @load_message_to_memory.register
    def _(self, message: str) -> None:
        json_message = {"role": "user", "content": message}
        self.messages.append(json_message)

    @load_message_to_memory.register
    def _(self, message: ChatCompletionMessage) -> None:
        json_response = {"role": message.role, "content": message.content}
        self.messages.append(json_response)

    def relegate_control(
        self,
    ) -> None:
        print("Control has been relinquished")


if __name__ == "__main__":
    a = Agent()
    # a.generate_evaluation()
    asyncio.run(a.execute())
    # json_schema = json.dumps(HiringManagerRequirements.model_json_schema(), indent=4)
    # print(json_schema)
