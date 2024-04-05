from typing import List, Tuple, Dict, Any, Iterable
import asyncio as aio

from agentopy.protocols import IEnvironment, IEnvironmentComponent, IState


class Environment(IEnvironment):
    """Implements a base environment class"""

    def __init__(self, components: List[IEnvironmentComponent]) -> None:
        """Initializes the environment with the specified state and components"""
        self._components: List[IEnvironmentComponent] = components

    def start(self) -> Iterable[aio.Task]:
        """Starts the environment and returns the tasks for the components"""
        tasks = set()

        async def start_component(component: IEnvironmentComponent):
            while True:
                await component.tick()
                await aio.sleep(0)
        for component in self._components:
            task = aio.create_task(start_component(component))
            tasks.add(task)
            task.add_done_callback(tasks.discard)
        return tasks

    @property
    def components(self) -> List[IEnvironmentComponent]:
        """Returns the components of the environment"""
        return self._components

    async def observe(self, caller_context: IState) -> List[Tuple[str, IState]]:
        """Returns the current state of the environment"""
        coroutines = []

        for component in self._components:
            context = caller_context.slice_by_prefix(f"_any")
            context.merge(caller_context.slice_by_prefix(
                f"_any/observe"), None)
            context.merge(caller_context.slice_by_prefix(
                f"{component.info().name}/_any"), None)
            context.merge(caller_context.slice_by_prefix(
                f"{component.info().name}/observe"), None)
            coroutines.append(component.observe(context))

        states = await aio.gather(*coroutines)
        return [(component.info().name, state) for component, state in zip(self._components, states)]

    def info(self) -> Dict[str, Any]:
        """Returns information about the environment"""
        return {
            "components": [component.info() for component in self._components],
        }
