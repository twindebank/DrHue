from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass

from drhue.state import State


@dataclass
class DrHueAdapter(ABC):
    """
    Adapters should handle translating raw data from the hub to a clean interface
    that can be used to read or write device states.
    """
    bridge: DrHueBridge
    name: str

    def __post_init__(self):
        self.state = State()

    def stage_changes(self, payload, update=True):
        self.bridge.stage_change(self.entity_action_path, payload, update)

    @property
    @abstractmethod
    def entity_action_path(self):
        pass

    def store_state(self, val):
        caller_name = inspect.stack()[1].function
        self.state[f"{self.name} ({caller_name})"] = val
        return val
