from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class DrHueAdapter(ABC):
    """
    Adapters should handle translating raw data from the hub to a clean interface
    that can be used to read or write device states.
    """
    bridge: DrHueBridge
    name: str

    def stage_changes(self, payload, update=True):
        self.bridge.stage_change(self.entity_action_path, payload, update)

    @property
    @abstractmethod
    def entity_action_path(self):
        pass
