from __future__ import annotations

from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import Any, List

from drhue.context import Context, Time
from drhue.helpers import default_field


@dataclass
class TimeRule(ABC):
    entity: Entity
    start: Time
    end: Time

    @abstractmethod
    def apply(self):
        pass

@dataclass
class Rules:
    entity: Entity
    time_rules: List
    priority = 0

    def __post_init__(self):
        self.context: Context = self.entity.context
        """
        here: 
        - veify start is day start
        - verify end is day end 
        - verify all times contiguoud
        """

    def apply(self):
        """
        - go through each rule and check if now between startds and ends
        """
