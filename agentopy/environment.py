from typing import List, Tuple, Dict, Any
import asyncio as aio

from agentopy.protocols import IEnvironment, IEnvironmentComponent, IState


class Environment(IEnvironment):
    """Implements a base environment class"""

    def __init__(self, components: List[Tuple[str, IEnvironmentComponent]], tick_rate_ms: float = 1000) -> None:
        """Initializes the environment with the specified state and components"""
        self._components: List[Tuple[str, IEnvironmentComponent]] = components
        self._tick_rate_ms: float = tick_rate_ms

    def start(self) -> aio.Task:
        """Starts the environment by creating an asynchronous task that repeatedly calls the `tick` method and sleeps for 1 second."""
        async def start_task():
            while True:
                await self.tick()
                await aio.sleep(self._tick_rate_ms / 1000)
        return aio.create_task(start_task())

    @property
    def components(self) -> List[Tuple[str, IEnvironmentComponent]]:
        """Returns the components of the environment"""
        return self._components

    async def observe(self) -> List[Tuple[str, IState]]:
        """Returns the current state of the environment"""
        return [(name, component.state) for name, component in self._components]

    def info(self) -> Dict[str, Any]:
        """Returns information about the environment"""
        return {
            "components": [component.info() for _, component in self._components],
            "tick_rate_ms": self._tick_rate_ms,
        }

    async def tick(self) -> None:
        """Ticks the environment"""
        for _, component in self._components:
            await component.on_tick()
