from typing import List, Dict, Any, Iterable
import asyncio as aio
import logging

from agentopy.protocols import IAgent, IPolicy, IEnvironment, IAgentComponent, IAction
from agentopy.schemas import SharedStateKeys
from agentopy.state import WithStateMixin

logger = logging.getLogger('agent')


class Agent(WithStateMixin, IAgent):
    """Implements an agent that takes actions to achieve a goal"""

    AGENT_MODE_OBSERVING = 'observing'
    AGENT_MODE_THINKING = 'thinking'
    AGENT_MODE_ACTING = 'acting'

    def __init__(
        self,
        policy: IPolicy,
        environment: IEnvironment,
        components: List[IAgentComponent],
        heartrate_ms: float = 1000
    ):
        """Initializes the agent with the specified name and policy"""
        super().__init__()
        self._policy: IPolicy = policy
        self._environment: IEnvironment = environment
        self._components: List[IAgentComponent] = components
        self._heartrate_ms: float = heartrate_ms

        self._mode = self.AGENT_MODE_OBSERVING

        for component in self._environment.components:
            self.policy.action_space.register_actions(
                component.action_space.all_actions())

        for component in self._components:
            self.policy.action_space.register_actions(
                component.action_space.all_actions())

    @property
    def policy(self) -> IPolicy:
        return self._policy

    @property
    def environment(self) -> IEnvironment:
        return self._environment

    @property
    def _mode(self) -> str:
        return self.state.get_item(SharedStateKeys.AGENT_MODE)

    @_mode.setter
    def _mode(self, value: str) -> None:
        self.state.set_item(SharedStateKeys.AGENT_MODE, value)

    def info(self) -> Dict[str, Any]:
        """Returns information about the agent"""
        return {
            "policy": self.policy.info(),
            "environment": self.environment.info(),
            "components": [component.info() for component in self._components],
            "heartrate_ms": self._heartrate_ms,
        }

    def start(self) -> Iterable[aio.Task]:
        """
        Starts the agent and returns the tasks for the components and the agent itself.
        """
        tasks = set()

        async def start_component(component: IAgentComponent):
            while True:
                await component.tick()
                await aio.sleep(0)

        async def start_agent():
            while True:
                await self.heartbeat()
                await aio.sleep(self._heartrate_ms / 1000)

        task = aio.create_task(start_agent())
        tasks.add(task)
        task.add_done_callback(tasks.discard)

        for component in self._components:
            task = aio.create_task(start_component(component))
            tasks.add(task)
            task.add_done_callback(tasks.discard)

        return tasks

    async def observe(self) -> None:
        """Observe the environment and update the agent's internal state."""
        for component_name, component_state in await self.environment.observe():
            prefix = f"environment/components/{component_name}/"
            self.state.clear(prefix)
            self.state.merge(component_state, prefix)

        self._mode = self.AGENT_MODE_THINKING

    async def think(self) -> None:
        """
        Decide on the next action based on the agent's policy and update the agent's state accordingly.
        """
        # [thinking] agent decides on the next action
        action, arguments, thoughts = await self.policy.action(self.state)

        self._mode = self.AGENT_MODE_ACTING
        self.state.set_item(SharedStateKeys.AGENT_ACTION, action)
        self.state.set_item(SharedStateKeys.AGENT_ACTION_ARGS, arguments)
        self.state.set_item(SharedStateKeys.AGENT_THOUGHTS, thoughts)

    async def act(self) -> None:
        """Perform the action that was decided on in the previous step and update the agent's state accordingly."""
        action = self.state.get_item(SharedStateKeys.AGENT_ACTION)
        arguments = self.state.get_item(SharedStateKeys.AGENT_ACTION_ARGS)

        result = await action.call(**arguments)
        self.state.set_item(SharedStateKeys.AGENT_ACTION_RESULT, result)

        self._mode = self.AGENT_MODE_OBSERVING

    async def heartbeat(self) -> None:
        """The agent's heartbeat, which is called periodically to update the agent's internal state."""
        logger.info(f"Agent heartbeat in {self._mode} mode")

        await aio.gather(*[component.on_agent_heartbeat(self) for component in self._components])

        if self._heartrate_ms == 0:
            # if heartrate_ms is 0, then the heartbeat is synchronous, so we do all modes in one heartbeat
            if self._mode == self.AGENT_MODE_OBSERVING:
                await self.observe()
            if self._mode == self.AGENT_MODE_THINKING:
                await self.think()
            if self._mode == self.AGENT_MODE_ACTING:
                await self.act()
        else:
            # if heartrate_ms is not 0, then the heartbeat is asynchronous, so we do one mode per heartbeat
            if self._mode == self.AGENT_MODE_OBSERVING:
                await self.observe()
            elif self._mode == self.AGENT_MODE_THINKING:
                await self.think()
            elif self._mode == self.AGENT_MODE_ACTING:
                await self.act()
