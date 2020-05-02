from dataclasses import dataclass, field
from typing import List, Type

from drhue.entities.base import Entity


@dataclass
class Room(Entity):
    devices: List[Entity] = field(default_factory=list)
    is_exit: bool = False

    def __post_init__(self):
        self.sub_entities = self.devices
        self.connecting_rooms = []

    def __rshift__(self, room):
        room >> self
        self.connecting_rooms.append(room)
