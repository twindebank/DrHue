from __future__ import annotations

from abc import abstractmethod, ABC
from dataclasses import dataclass

from drhue.context import Context


@dataclass
class Rule(ABC):
    entity: Entity
    priority = 0

    def __post_init__(self):
        self.context: Context = self.entity.context

    @abstractmethod
    def apply(self):
        pass
