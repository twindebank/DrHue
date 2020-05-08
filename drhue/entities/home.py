from __future__ import annotations
from __future__ import annotations

from dataclasses import dataclass, field
from multiprocessing import Process
from typing import List

from drhue.entities.base import Entity
from drhue.entities.room import Room
from drhue.server import start_server


@dataclass
class Home(Entity):
    rooms: List[Room] = field(default_factory=dict)

    def __post_init__(self):
        self.sub_entities = self.rooms

    def run(self, webserver=False):
        if webserver:
            Process(target=start_server).start()

        while True:
            self.sync_states()
            self.run_rules()
            self.context.update_and_wait()

    def run_rules(self):
        for rule in self.sorted_rules:
            rule.apply()
