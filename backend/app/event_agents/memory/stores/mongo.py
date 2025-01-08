import logging
from datetime import datetime
from typing import List
from uuid import UUID

from dotenv import load_dotenv

from app.event_agents.memory.stores.types import EntityType
from app.types.websocket_types import (
    WebsocketFrame,
)

from ..base_memory_store import BaseMemoryStore
from ..protocols import ConfigProvider

load_dotenv()

logger = logging.getLogger(__name__)


class MongoStore(BaseMemoryStore):
    """
    MongoDB implementation of MemoryStore protocol.

    Stores WebsocketFrames in MongoDB for persistence and scalability.

    Implements:
        MemoryStore (Protocol): Interface for memory storage operations
    """

    def __init__(
        self,
        agent_id: UUID,
        config_provider: ConfigProvider,
        entity: EntityType,
        debug: bool = False,
    ) -> None:
        super().__init__(
            config_provider=config_provider,
            debug=debug,
            agent_id=agent_id,
            entity=entity,
        )

    async def _sync_memory(self) -> None:
        if not self.entity:
            raise ValueError("Entity is not set")
        self.memory = self.entity.memory

    async def add(self, frame: WebsocketFrame) -> None:
        if not self.entity:
            raise ValueError("Entity is not set")
        await self.entity.update(
            {
                "$push": {"memory": frame.model_dump()},
                "$set": {"updated_at": datetime.now()},
            },
        )
        await self._sync_memory()

    async def clear(self) -> None:
        if not self.entity:
            raise ValueError("Entity is not set")
        await self.entity.delete()
        self.memory.clear()

    def get(self) -> List[WebsocketFrame]:
        return self.memory
