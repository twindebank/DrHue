from __future__ import annotations
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Type

from drhue.bridge import DrHueBridge











class Home:
    rooms: List[Room]
    _room_types: List[Type[Room]]
    _bridge: DrHueBridge = None

    def __init__(self, bridge):
        self._bridge = bridge
        # maybe store rooms as dicts
        self.rooms = [room(bridge) for room in self._room_types]
        self.rooms_as_dict = {room.name: room for room in self.rooms}

    def update(self):
        pass

    def _apply_rules(self):
        for room in self.rooms:
            room.apply_rules()
        self.apply_rules()

    # implement global rules across rooms, overwrite room-level rules
    def apply_rules(self):
        pass


class HueEntity(ABC):
    _bridge: DrHueBridge = None

    def __init__(self, bridge):
        self._bridge = bridge

    @abstractmethod
    def read(self):
        pass


class Lights(HueEntity):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    def write(self):
        pass


class Sensor(HueEntity):
    def __init__(self, sensor_name):
        self.sensor_name = sensor_name

    def link_bridge(self, bridge):
        self._bridge = bridge
        # todo


class GoogleEntity:
    pass


class GoogleHome(GoogleEntity):
    def __init__(self, name):
        self.name = name


class Chromecast(GoogleEntity):
    def __init__(self, name):
        self.name = name


class Vacuum(GoogleEntity):
    def __init__(self, name):
        self.name = name


class Room(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    lights: Optional[Lights] = None
    sensor: Optional[Sensor] = None
    google_home: Optional[GoogleHome] = None
    chromecast: Optional[Chromecast] = None
    vacuum: Optional[Vacuum] = None
    is_exit: bool = False

    _connecting_rooms: List[Room] = None
    _rules: List
    _bridge: DrHueBridge

    def __init__(self, bridge):
        self._connecting_rooms = []
        self._rules = []

        self._link_bridge(bridge)

    def __rshift__(self, room):
        room >> self
        self._connecting_rooms.append(room)

    def _link_bridge(self, bridge):
        self._bridge = bridge
        if self.lights:
            self.lights.link_bridge(bridge)
        if self.sensor:
            self.sensor.link_bridge(bridge)

    @property
    def connecting_rooms(self):
        return self._connecting_rooms

    def apply_rules(self):
        raise NotImplementedError()
