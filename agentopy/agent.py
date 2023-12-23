from typing import List
import asyncio as aio
import logging

from agentopy.protocols import IAgent, IPolicy, IEnvironment, IAgentComponent, IAction
from agentopy.schemas import ActionResult, SharedStateKeys
from agentopy.state import WithStateMixin
from agentopy.action import Action

logger = logging.getLogger('agent')


class Agent(WithStateMixin, IAgent):
    """Implements an agent that takes actions to achieve a goal"""

    AGENT_MODE_OBSERVING = 'observing'
    AGENT_MODE_THINKING = 'thinking'
    AGENT_MODE_ACTING = 'acting'
    AGENT_MODE_IDLE = 'idle'

    def __init__(
        self,
        policy: IPolicy,
        environment: IEnvironment,
        components: List[IAgentComponent],
        idle_timeout: int = 7200,
        heartrate_ms: float = 1000
    ):
        """Initializes the agent with the specified name and policy"""
        super().__init__()
        self._policy: IPolicy = policy
        self._environment: IEnvironment = environment
        self._components: List[IAgentComponent] = components
        self._idle_timeout: int = idle_timeout
        self._heartreate_ms: float = heartrate_ms

        self._mode = self.AGENT_MODE_OBSERVING

        self.policy.action_space.register_actions(
            [Action("idle",
                    "use this action to stay idle until there are new observations or actions to take", self.idle)])

        for _, component in self._environment.components:
            self.policy.action_space.register_actions(
                component.action_space.all_actions())

        for component in self._components:
            self.policy.action_space.register_actions(
                component.action_space.all_actions())

    @property
    def policy(self) -> IPolicy:
        return self._policy

    @property
    def _mode(self) -> str:
        return self.state.get_item(SharedStateKeys.AGENT_MODE)

    @_mode.setter
    def _mode(self, value: str) -> None:
        self.state.set_item(SharedStateKeys.AGENT_MODE, value)

    def start(self) -> aio.Task:
        """
        Starts the agent's heartbeat task, which sends a heartbeat signal every _heartreate_ms millisconds.
        Returns:
            asyncio.Task: The task that was created to run the heartbeat.
        """
        async def start_task():
            while True:
                await self.heartbeat()
                await aio.sleep(self._heartreate_ms / 1000)
        return aio.create_task(start_task())

    async def observe(self) -> None:
        """Observe the environment and update the agent's internal state."""
        for component_name, component_state in await self._environment.observe():
            prefix = f"{component_name}/"
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

        # [acting] if agent did not get in idle mode, it goes back to observing
        if self._mode != self.AGENT_MODE_IDLE:
            self._mode = self.AGENT_MODE_OBSERVING

    async def idle(self, reason: str = "") -> ActionResult:
        """Does nothing until there are new observations or actions to take"""
        if self._mode != self.AGENT_MODE_IDLE:
            self._mode = self.AGENT_MODE_IDLE
            self._idle_start_time = aio.get_event_loop().time()
        elif aio.get_event_loop().time() - self._idle_start_time > self._idle_timeout:
            self._mode = self.AGENT_MODE_OBSERVING
        return ActionResult(value=f"staying idle for {self._idle_timeout // 3600} hours", success=True)

    async def heartbeat(self) -> None:
        """The agent's heartbeat, which is called periodically to update the agent's internal state."""
        logger.info(f"Agent heartbeat in {self._mode} mode")

        await aio.gather(*[component.on_heartbeat(self.state) for component in self._components])

        if self._heartreate_ms == 0:
            # if heartreate_ms is 0, then the heartbeat is synchronous, so we do all modes in one heartbeat
            if self._mode == self.AGENT_MODE_OBSERVING:
                await self.observe()
            if self._mode == self.AGENT_MODE_THINKING:
                await self.think()
            if self._mode == self.AGENT_MODE_ACTING:
                await self.act()
            if self._mode == self.AGENT_MODE_IDLE:
                await self.idle()
        else:
            # if heartreate_ms is not 0, then the heartbeat is asynchronous, so we do one mode per heartbeat
            if self._mode == self.AGENT_MODE_OBSERVING:
                await self.observe()
            elif self._mode == self.AGENT_MODE_THINKING:
                await self.think()
            elif self._mode == self.AGENT_MODE_ACTING:
                await self.act()
            elif self._mode == self.AGENT_MODE_IDLE:
                await self.idle()
