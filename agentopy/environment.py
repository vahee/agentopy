from typing import List, Tuple, Dict, Any, Iterable
import asyncio as aio

from agentopy.protocols import IEnvironment, IEnvironmentComponent, IState


class Environment(IEnvironment):
    """Implements a base environment class"""

    def __init__(self, components: List[IEnvironmentComponent]) -> None:
        """Initializes the environment with the specified state and components"""
        self._components: List[IEnvironmentComponent] = components

    def start(self, sync=False) -> Iterable[aio.Task]:
        """Starts the environment and returns the tasks for the components"""
        tasks = set()

        if not sync:
            async def start_component(component: IEnvironmentComponent):
                while True:
                    await component.tick()
                    await aio.sleep(0)
            for component in self._components:
                task = aio.create_task(start_component(component))
                tasks.add(task)
                task.add_done_callback(tasks.discard)
        else:
            async def start_all_components():
                while True:
                    for component in self._components:
                        await component.tick()
                    await aio.sleep(0)

            tasks.add(aio.create_task(start_all_components()))
        return tasks

    @property
    def components(self) -> List[IEnvironmentComponent]:
        """Returns the components of the environment"""
        return self._components

    async def observe(self, caller_context: IState) -> List[Tuple[str, IState]]:
        """Returns the current state of the environment"""
        states = []

        for component in self._components:
            context = caller_context.slice_by_prefix(f"_any")
            context.merge(caller_context.slice_by_prefix(
                f"_any.observe"), None)
            context.merge(caller_context.slice_by_prefix(
                f"environment.components.{component.info().name}._any"), None)
            context.merge(caller_context.slice_by_prefix(
                f"environment.components.{component.info().name}.observe"), None)
            states.append(await component.observe(context))

        return [(component.info().name, state) for component, state in zip(self._components, states)]

    def info(self) -> Dict[str, Any]:
        """Returns information about the environment"""
        return {
            "components": [component.info() for component in self._components],
        }
