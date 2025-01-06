import logging
import os
from typing import List

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import DESCENDING

from app.types.websocket_types import (
    WebsocketFrame,
)

from ..base_memory_store import BaseMemoryStore
from ..protocols import ConfigProvider

load_dotenv()

logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI")


class MongoStore(BaseMemoryStore):
    """
    MongoDB implementation of MemoryStore protocol.

    Stores WebsocketFrames in MongoDB for persistence and scalability.

    Implements:
        MemoryStore (Protocol): Interface for memory storage operations
    """

    def __init__(
        self,
        config_provider: ConfigProvider,
        database: str = "chat_memory",
        collection: str = "interview",
        debug: bool = False,
    ) -> None:
        self.client: AsyncIOMotorClient = AsyncIOMotorClient(MONGO_URI)
        self.db = self.client[database]
        self.collection = self.db[collection]
        self.config_provider = config_provider
        self.debug = debug
        self.memory: List[WebsocketFrame] = []  # Cache for quick access

    async def _sync_memory(self) -> None:
        """Synchronize in-memory cache with MongoDB."""
        cursor = self.collection.find().sort("_id", DESCENDING)
        synced_memory = [
            WebsocketFrame.model_validate(doc) async for doc in cursor
        ]
        if synced_memory != self.memory:
            logger.debug(
                "mismatch between synced memory and in-memory cache"
            )
            mismatched_frames = [
                frame
                for frame in synced_memory
                if frame not in self.memory
            ]
            logger.debug(f"Mismatched frames: {mismatched_frames}")

        self.memory = synced_memory

    async def add(self, frame: WebsocketFrame) -> None:
        if not isinstance(frame, WebsocketFrame):
            raise TypeError(
                f"Expected WebsocketFrame but got {type(frame).__name__}"
            )

        # Store in MongoDB
        await self.collection.insert_one(frame.model_dump())

        # Update cache
        self.memory.append(frame)
        await self._sync_memory()

    async def clear(self) -> None:
        """Clear all frames from MongoDB and memory cache."""
        await self.collection.delete_many({})
        self.memory.clear()

    def get(self) -> List[WebsocketFrame]:
        """Get all frames from memory cache."""
        return self.memory
