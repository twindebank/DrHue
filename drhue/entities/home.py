from __future__ import annotations
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from drhue.entities.base import Entity
from drhue.entities.room import Room


@dataclass
class Home(Entity):
    rooms: List[Room] = field(default_factory=dict)

    def __post_init__(self):
        self.sub_entities = self.rooms

    def run(self):
        while True:
            self.sync_states()
            self.run_rules()
            self.context.update_and_wait()

    def run_rules(self):
        for rule in self.sorted_rules:
            rule.apply()
