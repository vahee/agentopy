from typing import List, Tuple, Dict, Any
import asyncio as aio

from agentopy.protocols import IEnvironment, IEnvironmentComponent, IState


class Environment(IEnvironment):
    """Implements a base environment class"""

    def __init__(self, components: List[IEnvironmentComponent]) -> None:
        """Initializes the environment with the specified state and components"""
        self._components: List[IEnvironmentComponent] = components

    def start(self) -> List[aio.Task]:
        """Starts the environment and returns the tasks for the components"""
        tasks = []

        async def start_component(component: IEnvironmentComponent):
            while True:
                await component.tick()
                await aio.sleep(0)
        for component in self._components:
            tasks.append(aio.create_task(start_component(component)))
        return tasks

    @property
    def components(self) -> List[IEnvironmentComponent]:
        """Returns the components of the environment"""
        return self._components

    async def observe(self) -> List[Tuple[str, IState]]:
        """Returns the current state of the environment"""
        return [(component.info().name, component.state) for component in self._components]

    def info(self) -> Dict[str, Any]:
        """Returns information about the environment"""
        return {
            "components": [component.info() for component in self._components],
        }
