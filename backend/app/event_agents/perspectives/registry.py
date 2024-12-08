import asyncio
from app.event_agents.perspectives.perspective_base import PerspectiveBase
from app.event_agents.perspectives.perspectors import (
    product_manager_perspective,
    sales_manager_perspective,
    engineering_manager_perspective,
    design_manager_perspective,
)


class PerspectiveRegistry:
    def __init__(self) -> None:
        self._perspectives: dict[str, PerspectiveBase] = {}

    async def initialize(self) -> None:
        print("\033[91minitializing perspectives\033[0m")
        await self.add_default_perspectives()
        print("\033[91mperspectives initialized\033[0m")
        print(f"\033[91mperspectives: {len(self.get_perspectives())}\033[0m")

    async def add_default_perspectives(self) -> None:
        default_perspectors = [
            product_manager_perspective,
            sales_manager_perspective,
            engineering_manager_perspective,
            design_manager_perspective,
        ]
        perspector_initialize_tasks = []

        for perspector in default_perspectors:
            task = self.register_perspective(perspector)
            perspector_initialize_tasks.append(task)

        await asyncio.gather(*perspector_initialize_tasks)
        return

    async def register_perspective(
        self, perspective_agent: PerspectiveBase
    ) -> None:
        await perspective_agent.initialize()
        self._perspectives.update(
            {perspective_agent.perspective: perspective_agent}
        )

    def get_perspectives(self) -> dict[str, PerspectiveBase]:
        return self._perspectives
