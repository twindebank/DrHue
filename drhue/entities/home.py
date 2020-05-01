from __future__ import annotations
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Type, List

from drhue.entities.base import Entity
from drhue.entities.room import Room


@dataclass
class Home(Entity):
    rooms: List[Type[Room]] = field(default_factory=dict)

    def __post_init__(self):
        self.sub_entities = self.rooms

    def run(self):
        while True:
            self.context.bridge.read()
            self.sync_states()
            self.run_rules()
            self.context.bridge.write()
            time.sleep(self.context.refresh_interval)

    def run_rules(self):
        for rule in self.sorted_rules:
            rule.apply()
