import os
from typing import Any

from beanie import init_beanie
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from app.event_agents.schemas.mongo_schemas import (
    AgentProfile,
    Candidate,
    Interviewer,
    InterviewSession,
)

load_dotenv()

# MongoDB connection URL - update with your actual connection details
MONGO_URL = os.getenv("MONGO_URL")
DATABASE_NAME = os.getenv("MONGO_DATABASE")


async def init_db() -> None:
    client: AsyncIOMotorClient[Any] = AsyncIOMotorClient(MONGO_URL)
    if not DATABASE_NAME:
        raise ValueError("DATABASE_NAME is not set")
    await init_beanie(
        database=client[DATABASE_NAME],
        document_models=[
            Interviewer,
            Candidate,
            InterviewSession,
            AgentProfile,
        ],
    )
