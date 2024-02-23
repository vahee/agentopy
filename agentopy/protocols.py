from typing import Optional, List, Any, Tuple, Dict, Protocol, runtime_checkable
import asyncio as aio

from agentopy.schemas import ActionResult


@runtime_checkable
class IState(Protocol):
    """Interface for a universal state object"""

    def merge(self, other: 'IState', prefix: Optional[str]) -> None:
        """Merges the specified state into the current state"""
        ...

    def clear(self, prefix: Optional[str]) -> None:
        """Clears the state, optionally with the specified prefix"""
        ...

    def set_item(self, key: str, value: Any) -> None:
        """Sets the state item with the specified key and value"""
        ...

    def get_item(self, key: str) -> Any:
        """Returns state item with the specified key"""
        ...

    def items(self) -> Dict[str, Any]:
        """Returns the items in the state"""
        ...

    def remove_item(self, key: str) -> None:
        """Removes state item with specified key"""
        ...

    def keys(self) -> List[str]:
        """Returns the keys in the state"""
        ...


@runtime_checkable
class IStateful(Protocol):
    @property
    def state(self) -> IState:
        """Returns the current state of the stateful object"""
        ...


@runtime_checkable
class IAction(Protocol):
    """Implements an action that can be taken"""
    async def call(self, *args: Any, **kwds: Any) -> ActionResult:
        """Performs the action"""
        ...

    def name(self) -> str:
        """Returns the name of the action"""
        ...

    def description(self) -> str:
        """Returns the description of the action"""
        ...

    def arguments(self) -> Dict[str, str]:
        """Returns the arguments of the action"""
        ...


class IAgent(IStateful, Protocol):
    """Implements an autonomous agent that can interact with the environment"""
    async def heartbeat(self) -> None:
        """Performs a single step of the agent's heartbeat and returns whether the agent is still alive"""
        ...

    @property
    def policy(self) -> 'IPolicy':
        """Returns the policy of the agent"""
        ...

    @property
    def environment(self) -> 'IEnvironment':
        """Returns the environment of the agent"""
        ...

    def start(self) -> aio.Task:
        """Starts the agent"""
        ...

    def info(self) -> Dict[str, Any]:
        """Returns information about the agent"""
        ...


@runtime_checkable
class IActionSpace(Protocol):
    """Implements an action space that can be interacted with"""

    def get_action(self, name: str) -> IAction:
        """Returns the actions in the action space"""
        ...

    def register_actions(self, actions: List[IAction]) -> None:
        """Registers the specified action in the action space"""
        ...

    def all_actions(self) -> List[IAction]:
        """Returns all actions in the action space"""
        ...


class IEnvironmentComponent(IStateful, Protocol):
    """Implements an environment component that can be interacted with"""

    @property
    def action_space(self) -> IActionSpace:
        """Returns the action space of the component"""
        ...

    def info(self) -> Dict[str, Any]:
        """Returns information about the component"""
        ...

    async def on_tick(self) -> None:
        """Performs a single step of the component's lifecycle"""
        ...


class IAgentComponent(IStateful, Protocol):
    """Implements an agent component"""

    @property
    def action_space(self) -> IActionSpace:
        """Returns the action space of the component"""
        ...

    def info(self) -> Dict[str, Any]:
        """Returns information about the component"""
        ...

    async def on_heartbeat(self, agent: IAgent) -> None:
        """Performs a single step of the component's lifecycle"""
        ...


@runtime_checkable
class IEnvironment(Protocol):
    """Implements an environment that can be interacted with"""

    async def observe(self) -> List[Tuple[str, IState]]:
        """Returns the current state of the environment"""
        ...

    @property
    def components(self) -> List[Tuple[str, IEnvironmentComponent]]:
        """Returns the components of the environment"""
        ...

    def info(self) -> Dict[str, Any]:
        """Returns information about the environment"""
        ...

    def start(self) -> aio.Task:
        """Starts the environment"""
        ...


@runtime_checkable
class IPolicy(Protocol):
    """Implements a policy that can be used to select actions"""
    async def action(self, state: IState) -> Tuple[IAction, Dict[str, Any], Dict[str, Any]]:
        """Returns an action to take, along with its arguments and 'thoughts' on why action was chosen"""
        ...

    @property
    def action_space(self) -> IActionSpace:
        """Returns the action space assigned to the policy"""
        ...

    def info(self) -> Dict[str, Any]:
        """Returns information about the policy"""
        ...
