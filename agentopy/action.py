import inspect
from typing import Callable, Dict

from agentopy.protocols import IAction
from agentopy.schemas import ActionResult, EntityInfo


class Action(IAction):
    """Implements an action class"""

    def __init__(self, name: str, description: str, action_fn: Callable, component_info: EntityInfo) -> None:
        self._name: str = name
        self._description: str = description
        self._action_fn: Callable = action_fn
        self._component_info: EntityInfo = component_info

    def name(self) -> str:
        """Returns the name of the action"""
        return self._name

    def description(self) -> str:
        """Returns the description of the action"""
        return self._description

    def component_info(self) -> EntityInfo:
        """Returns the information about the component"""
        return self._component_info

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

    async def call(self, *args, **kwargs) -> ActionResult:
        """Performs the action"""
        return await self._action_fn(*args, **kwargs)
