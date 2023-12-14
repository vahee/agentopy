from typing import List

from collections import OrderedDict

from agentopy.protocols import IActionSpace, IAction
from agentopy.action import Action


class ActionSpace(IActionSpace):
    """Implements a base action space class"""

    def __init__(self) -> None:
        self._actions: OrderedDict[str, IAction] = OrderedDict()

    def get_action(self, name: str) -> IAction:
        """Returns the action with the specified name"""
        assert name in self._actions, f"Action {name} not found"
        return self._actions[name]

    def register_actions(self, actions: List[IAction]) -> None:
        """Registers the specified action in the action space"""

        for action in actions:
            self._actions[action.name()] = action

    def all_actions(self) -> List[IAction]:
        return list(self._actions.values())


class WithActionSpaceMixin:
    """Implements a mixin for classes that have an action space"""

    def __init__(self) -> None:
        super().__init__()
        self._action_space: IActionSpace = ActionSpace()

    @property
    def action_space(self):
        """Returns the action space"""
        return self._action_space

    @action_space.setter
    def action_space(self, action_space: IActionSpace) -> None:
        """Sets the action space"""
        self._action_space = action_space
