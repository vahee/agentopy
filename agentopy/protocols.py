from typing import Optional, List, Any, Tuple, Dict, Protocol, Iterable, runtime_checkable
import asyncio as aio

from agentopy.schemas import ActionResult, EntityInfo


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

    def set_nested_item(self, prefix: str, data: Dict[str, Any]) -> None:
        """Sets the state item with the specified prefix and data"""
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

    def slice_by_prefix(self, prefix: str) -> 'IState':
        """Returns a new state with items that have the specified prefix"""
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

    async def call(self, *args: Any, **kwargs: Any) -> ActionResult:
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

    def entity_info(self) -> EntityInfo:
        """Returns the information about the parent entity"""
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

    def start(self) -> Iterable[aio.Task]:
        """Starts the agent"""
        ...

    def info(self) -> EntityInfo:
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


class IEnvironmentComponent(Protocol):
    """Implements an environment component that can be interacted with"""

    @property
    def action_space(self) -> IActionSpace:
        """Returns the action space of the component"""
        ...

    def info(self) -> EntityInfo:
        """Returns information about the component"""
        ...

    async def tick(self) -> None:
        """Performs a single step of the component's lifecycle"""
        ...

    async def observe(self, caller_context: IState) -> IState:
        """Returns the current state of the component for the specified observer"""
        ...


class IAgentComponent(Protocol):
    """Implements an agent component"""

    @property
    def action_space(self) -> IActionSpace:
        """Returns the action space of the component"""
        ...

    def info(self) -> EntityInfo:
        """Returns information about the component"""
        ...

    async def on_agent_heartbeat(self, agent: IAgent) -> None:
        """Callback on agent heartbeat"""
        ...

    async def tick(self) -> None:
        """Performs a single step of the component's lifecycle"""
        ...


@runtime_checkable
class IEnvironment(Protocol):
    """Implements an environment that can be interacted with"""

    async def observe(self, caller_context: IState) -> List[Tuple[str, IState]]:
        """Returns the current state of the environment for the specified observer"""
        ...

    @property
    def components(self) -> List[IEnvironmentComponent]:
        """Returns the components of the environment"""
        ...

    def info(self) -> EntityInfo:
        """Returns information about the environment"""
        ...

    def start(self) -> Iterable[aio.Task]:
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

    def info(self) -> EntityInfo:
        """Returns information about the policy"""
        ...
