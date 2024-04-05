import inspect
from typing import Callable, Dict

from agentopy.protocols import IAction, IState
from agentopy.schemas import ActionResult, EntityInfo


class Action(IAction):
    """Implements an action class"""

    def __init__(self, name: str, description: str, action_fn: Callable, entity_info: EntityInfo) -> None:
        self._name: str = name
        self._description: str = description
        self._action_fn: Callable = action_fn
        self._entity_info: EntityInfo = entity_info
        if not inspect.iscoroutinefunction(action_fn):
            raise ValueError("Action function must be a coroutine function")
        if not hasattr(action_fn, '__annotations__'):
            raise ValueError("Action function must have type annotations")
        # check if action_fn has caller_context argument of IState type
        sig = inspect.signature(action_fn)
        if 'caller_context' not in sig.parameters or sig.parameters['caller_context'].annotation != IState:
            raise ValueError(
                "Action function must have 'caller_context' argument of IState type or None")

    def name(self) -> str:
        """Returns the name of the action"""
        return self._name

    def description(self) -> str:
        """Returns the description of the action"""
        return self._description

    def entity_info(self) -> EntityInfo:
        """Returns the information about the parent entity"""
        return self._entity_info

    def arguments(self) -> Dict[str, str]:
        """Returns the arguments of the action"""
        sig = inspect.signature(self._action_fn)
        args = {}
        for name, value in sig.parameters.items():
            if value.annotation.__class__.__name__ == "type":
                args[name] = value.annotation.__name__
            elif value.annotation.__class__.__name__ in ["UnionType", "_UnionGenericAlias"]:
                args[name] = ' | '.join(
                    arg.__name__ for arg in value.annotation.__args__)
        return args

    async def call(self, *, caller_context: IState, **kwargs) -> ActionResult:
        """Performs the action"""

        context = caller_context.slice_by_prefix(f"_any")
        context.merge(caller_context.slice_by_prefix(
            f"_any/{self._name}"), None)
        context.merge(caller_context.slice_by_prefix(
            f"{self._entity_info.name}/_any"), None)
        context.merge(caller_context.slice_by_prefix(
            f"{self._entity_info.name}/{self._name}"), None)

        kwargs['caller_context'] = context
        return await self._action_fn(**kwargs)
