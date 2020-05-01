from dataclasses import dataclass, field
from typing import Union, List, Type

from drhue.entities.base import Entity, HueEntity
from drhue.entities.google import GoogleEntity


@dataclass
class Room(Entity):
    devices: List[Type[Union[HueEntity, GoogleEntity, Entity]]] = field(default_factory=list)
    is_exit: bool = False

    def __post_init__(self):
        self.sub_entities = self.devices
        self.connecting_rooms = []

    def __rshift__(self, room):
        room >> self
        self.connecting_rooms.append(room)
