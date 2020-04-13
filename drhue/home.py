from __future__ import annotations
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Type

from drhue.bridge import DrHueLights


class _Entity(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass


class Home(_Entity, ABC):
    rooms: List[Room]

    @property
    @abstractmethod
    def room_definitions(self) -> List[Type[Room]]:
        pass

    def __init__(self, bridge):
        self.rooms = [room(bridge) for room in self.room_definitions]
        self.rooms_as_dict = {room.name: room for room in self.rooms}

    def _run_rules(self):
        for room in self.rooms:
            room.run_rules()
        self.run_rules()

    @abstractmethod
    def run_rules(self):
        pass


class _HueEntity(_Entity, ABC):
    """
    name must be tied to hue entity
    """


    def __init__(self, bridge):
        self.adapter = self.adapter_class(bridge, self.name)

    @property
    @abstractmethod
    def adapter_class(self):
        pass


class Lights(_HueEntity, ABC):
    """
    links to hue groups
    """
    _on: bool = False
    _brightness: float = 0

    adapter_class = DrHueLights

    @property
    def on(self):
        if self._on != self.adapter.on:
            print("inconsistent state, something happened outside program")
            self._on = self.adapter.on
        return self._on

    @on.setter
    def on(self, state):
        self.adapter.on = state
        self._on = state


class Sensor(_HueEntity):

    @property
    def motion(self):
        return False

    @property
    def temperature(self):
        return 15.5

    @property
    def daylight(self):
        return True

    @property
    def dark(self):
        return False


class GoogleEntity(_Entity):
    pass


class GoogleHome(GoogleEntity):
    pass


class Chromecast(GoogleEntity):
    pass


class Vacuum(GoogleEntity):
    pass


class Room(_Entity, ABC):
    device_classes: List[Type[_Entity]] = None
    devices: List[_Entity]
    is_exit: bool = False

    _connecting_rooms: List[Room] = None

    def __init__(self, bridge):
        self.devices = []
        for device_class in self.device_classes:
            if isinstance(type(device_class), _HueEntity):
                self.devices.append(device_class(bridge))
            else:
                self.devices.append(device_class())

        self._connecting_rooms = []
        self._rules = []

    def __rshift__(self, room):
        room >> self
        self._connecting_rooms.append(room)

    @property
    def connecting_rooms(self):
        return self._connecting_rooms

    @abstractmethod
    def run_rules(self):
        pass
