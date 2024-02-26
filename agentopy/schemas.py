from dataclasses import dataclass
from typing import Any


@dataclass
class ActionResult:
    """Defines result of an action"""
    value: Any
    success: bool


@dataclass
class SharedStateKeys:
    """Defines the keys for the shared state"""
    AGENT_MODE: str = "agent/mode"
    AGENT_THOUGHTS: str = "agent/thoughts"
    AGENT_ACTION: str = "agent/action/name"
    AGENT_ACTION_RESULT: str = "agent/action/result"
    AGENT_ACTION_ARGS: str = "agent/action/args"
