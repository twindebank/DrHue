from __future__ import annotations

from abc import abstractmethod, ABC
from dataclasses import dataclass


@dataclass
class Rule(ABC):
    entity: Entity
    priority = 0

    @abstractmethod
    def apply(self):
        pass
