from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class DrHueAdapter(ABC):
    bridge: DrHueBridge
    name: str

    def stage_changes(self, payload, update=True):
        self.bridge.set(self.entity_action_path, payload, update)

    @property
    @abstractmethod
    def entity_action_path(self):
        pass
