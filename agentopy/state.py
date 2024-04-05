from typing import Dict, Any, List, Optional

from agentopy.protocols import IState


class State(IState):
    """Implements a universal state object"""

    def __init__(self, max_keys: int = 50) -> None:
        """Initializes the state"""
        self._data: Dict[str, Any] = {}
        self._max_keys: int = max_keys

    def merge(self, other: IState, key_prefix: Optional[str]) -> None:
        """Merges the state with another state"""
        for key, value in other.items().items():
            if key_prefix:
                key = f"{key_prefix}{key}"
            self._data[key] = value

    def clear(self, prefix=None) -> None:
        """Clears the state"""
        if prefix is None:
            self._data = {}
        else:
            # TODO: this is not efficient
            self._data = {k: v for k, v in self._data.items()
                          if not k.startswith(prefix)}

    def set_item(self, key: str, value: Any) -> None:
        """Adds the specified data items to the state"""
        if key not in self._data and len(self._data) >= self._max_keys:
            raise Exception(f"State is full, cannot add item with key {key}")
        self._data[key] = value

    def set_nested_item(self, prefix: str, data: Dict[str, Any]) -> None:
        """Adds the specified data items to the state"""
        def nest(prefix: str, data: Dict[str, Any]):
            for key, value in data.items():
                if isinstance(value, dict):
                    nest(f"{prefix}/{key}", value)
                else:
                    self.set_item(f"{prefix}/{key}", value)
        nest(prefix, data)

    def slice_by_prefix(self, prefix: str) -> IState:
        """Returns a new state with items that have the specified prefix"""
        state = State(self._max_keys)
        for key, value in self._data.items():
            if key.startswith(prefix):
                if key != prefix:
                    key = key[len(prefix):].lstrip('/')
                state.set_item(key, value)
        return state

    def get_item(self, key: str) -> Any:
        """Returns the data item with the specified key"""
        return self._data.get(key)

    def remove_item(self, key: str) -> None:
        """Removes item with specified key"""
        self._data.pop(key, None)

    def items(self) -> Dict[str, Any]:
        """Returns the items in the state"""
        return self._data

    def keys(self) -> List[str]:
        """Returns the keys in the state"""
        return list(self._data.keys())

    def __dict__(self) -> Dict[str, Any]:
        return self._data


class WithStateMixin:
    """Implements a mixin for classes that have a state"""

    def __init__(self, max_state_len: int = 50) -> None:
        """Initializes the mixin with the specified state"""
        super().__init__()
        self._state: IState = State(max_state_len)

    @property
    def state(self) -> IState:
        """Returns the current state of the stateful object"""
        return self._state
