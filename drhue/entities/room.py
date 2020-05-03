from dataclasses import dataclass, field
from typing import List

from drhue.entities.base import Entity


@dataclass
class Room(Entity):
    devices: List[Entity] = field(default_factory=list)

    def __post_init__(self):
        self.sub_entities = self.devices
