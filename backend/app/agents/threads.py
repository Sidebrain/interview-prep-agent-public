import asyncio
from functools import singledispatchmethod
import json
import traceback
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
        self, messages: list[dict[str, str]] = None, include_tools: bool = False
    ) -> Tuple[ChatCompletionMessage, StopReason]:
        tool = {
            "name": "hiring_manager_requirements",
            "description": "Gather hiring manager requirements to construct the job artefacts that will help with recruiting.",
            "parameters": HiringManagerRequirements.model_json_schema(),
        }

        if include_tools:
            response = await self.client.chat.completions.create(
                messages=messages,
                model="gpt-4o-mini",
                tools=[{"type": "function", "function": tool}],
            )
        else:
            response = await self.client.chat.completions.create(
                messages=messages,
                model="gpt-4o-mini",
            )
        finish_reason = response.choices[0].finish_reason
        message = response.choices[0].message
        # if finish_reason == "tool_calls" | "stop":
        #     print("\n---- Stack trace ----\n")
        #     for line in traceback.format_stack():
        #         print(line.strip())
        #     print("\n---- End of stack trace ----\n")
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

    async def single_turn(self, introspection: bool = False) -> None:
        if len(self.messages) >= 2:
            user_input = input("Enter your response: ")
            if user_input == "q":
                return None, "quit"
            self.load_message_to_memory(user_input)
            await asyncio.gather(
                *[
                    self.fill_datacard(),
                    self.fill_rating_rubric(),
                ]
            )

            # memory seen by the llm
            self.log_memory()

        # generating the next question
        response_message, stop_reason = await self.intellect.generate(
            self.messages, include_tools=True
        )
        print(response_message.content, end=f"\n{"="*30}\n")
        # generate eval answer
        await self.generate_evaluation(response_message)
        self.load_message_to_memory(response_message)
        return response_message, stop_reason

    def log_memory(
        self, messages: list = None, filepath: str = "docs/sample/memory.md"
    ) -> None:
        if not messages:
            messages = self.messages
        with open(filepath, "w") as f:
            for msg in messages:
                f.writelines(f"{msg['role']}: {msg['content']}\n\n")

    async def execute(self) -> None:
        await asyncio.gather(
            *[self.generate_datacard_to_fill(), self.generate_rating_rubric()]
        )
        await self.generate_rubric_card_to_fill()
        _, stop_reason = await self.single_turn()
        while stop_reason != "tool_calls":
            _, stop_reason = await self.single_turn()
            if stop_reason == "quit":
                break
        print("--------------- End of conversation ---------------")
        print(f"{stop_reason=}")
        print("\n---- Stack trace ----\n")
        for line in traceback.format_stack():
            print(line.strip())
        print("\n---- End of stack trace ----\n")
        self.relegate_control()

    async def generate_rating_rubric(self) -> None:
        system = """You are responsible for generating a rating rubric to evaluate performance of the hiring manager you are speaking to. 
Remember that you are an experienced recruiting coordinator and have worked with hundreds of hiring managers.
You know what makes a good hiring manager and what doesn't. You are here to provide a fair and accurate evaluation of the hiring manager's performance."""
        res, stop_reason = await self.intellect.generate(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": "Generate a rating rubric"},
            ]
        )
        self.write_to_file(res, "docs/sample/rubric.md")

    async def generate_rubric_card_to_fill(self) -> None:
        system = """You are the recruiting coordinator. 
Take the rating rubric and use it to generate a rubric card that you can fill in as the hiring manager answers more of your questions.
Make it structured and easy to fill in as you go along along with space for notes, followups and feedback."""
        with open("docs/sample/rubric.md", "r") as f:
            rubric = f.read()
        res, stop_reason = await self.intellect.generate(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": rubric},
                {"role": "user", "content": "Generate a rubric to fill in"},
            ]
        )
        self.write_to_file(res, "docs/sample/rubric_card.md")

    async def generate_datacard_to_fill(self) -> None:
        system = """As a recruiting coordinator you are filling in a datacard so that you can take that back and use it to create the job artefacts.
Your job in this task is to simply generate a datacard that you can progressively fill in as the hiring manager answers more of your questions."""
        res, stop_reason = await self.intellect.generate(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": "Generate a datacard"},
            ]
        )
        self.write_to_file(res, "docs/sample/datacard.md")

    async def fill_datacard(self) -> None:
        system = """You are the recriting coordinator. 
You are here to fill in the datacard with the information provided by the hiring manager.
You should include notes, follow ups and any other relevant information that you think is important.
The document is structured in a way that you can easily fill in the information as you go along.
Make sure to fill in the information in the correct sections.
Only fill in the datacard, keep all your comments and notes in the datacard. Nothing outside.
Only use the information provided by the hiring manager."""

        with open("docs/sample/datacard.md", "r") as f:
            datacard = f.read()
        messages = [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": "Here is the conversation so far between the hiring manager and the recruiting coordinator",
            },
            *self.messages,
            {"role": "user", "content": "Here is the datacard"},
            {"role": "user", "content": datacard},
            {"role": "user", "content": "Fill in the datacard"},
        ]
        res, stop_reason = await self.intellect.generate(messages)
        self.write_to_file(res, "docs/sample/datacard.md")

    async def fill_rating_rubric(self) -> None:
        system = """You are the recruiting coordinator.
Your job here is to fill in the rating rubric as the hiring manager answers your questions.
You should provide a fair and accurate evaluation of the hiring manager's performance.
The rubric is structured in a way that you can easily fill in the information as you go along.
Make sure to fill in the information in the correct sections.
Only fill in the rubric, keep all your comments and notes in the rubric. Nothing outside."""
        with open("docs/sample/rubric_card.md", "r") as f:
            rubric_card = f.read()
        messages = [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": "Here is the conversation so far between the hiring manager and the recruiting coordinator",
            },
            *self.messages,
            {"role": "user", "content": "Here is the rating rubric"},
            {"role": "user", "content": rubric_card},
            {"role": "user", "content": "Fill in the rating rubric"},
        ]
        res, stop_reason = await self.intellect.generate(messages)
        self.write_to_file(res, "docs/sample/filled_rubric.md")

    async def generate_evaluation(
        self, assistant_output: ChatCompletionMessage
    ) -> None:
        system = """You are the hiring manager. You are here to provide the requirements for the role you are hiring for. You give thorough and detailed answers to every question you are asked.
You are not tied to any company, role or team, you can answer freely. You are allowed to make any assumptions or provide any information you think is relevant.
You answer the question but also take context into account and know when the question asked was already answered in the context."""
        shadow_message_list = [
            {"role": "system", "content": system},
            *[msg for msg in self.messages if msg["role"] == "user"],
            {"role": "user", "content": assistant_output.content},
        ]
        self.log_memory(shadow_message_list, "docs/sample/eval.md")
        response_msg, stop_reason = await self.intellect.generate(
            messages=shadow_message_list, include_tools=True
        )
        print(response_msg.content, end=f"\n{"*"*30}\n")

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

    def write_to_file(self, message: ChatCompletionMessage, filepath: str) -> None:
        try:
            with open(filepath, "w") as f:
                f.write(message.content)
        except FileNotFoundError:
            print("File not found")

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
