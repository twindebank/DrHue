from __future__ import annotations
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Type, Dict

from loguru import logger

from drhue.bridge import DrHueLights, DrHueSensor


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

    def run_all_rules(self):
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
    these need to store state of timeout
    needs to store things like relax/read
    """
    adapter_class = DrHueLights

    # todo: tidy this
    _on: bool = False
    _brightness: int = 0

    @property
    def on(self):
        if self._on != self.adapter.on:
            logger.warning("inconsistent state, something happened outside program")
            self._on = self.adapter.on
        return self._on

    @on.setter
    def on(self, state):
        if self._on != self.adapter.on:
            logger.warning("inconsistent state, something happened outside program")
        self.adapter.on = state
        self._on = state

    @property
    def brightness(self):
        if self._brightness != self.adapter.brightness:
            logger.info("inconsistent state, something happened outside program")
            self._brightness = self.adapter.brightness
        return self._brightness

    @brightness.setter
    def brightness(self, brightness):
        self.adapter.brightness = brightness
        self._brightness = brightness

    def timeout(self, timedelta):
        pass

    def relax(self):
        pass

    def read(self):
        pass


class Sensor(_HueEntity):
    adapter_class = DrHueSensor

    @property
    def motion(self):
        return self.adapter.motion

    @property
    def temperature(self):
        return self.adapter.temperature

    @property
    def daylight(self):
        return self.adapter.daylight

    @property
    def dark(self):
        return self.adapter.dark


class GoogleEntity(_Entity):
    pass


class GoogleHome(GoogleEntity):
    pass


class Chromecast(GoogleEntity):
    pass


class Vacuum(GoogleEntity):
    pass


class Room(_Entity, ABC):
    devices: List[_Entity]
    devices_dict: Dict[str, _Entity]
    is_exit: bool = False

    _device_classes: List[Type[_Entity]] = None
    _connecting_rooms: List[Room] = None

    def __init__(self, bridge):
        self.devices = []
        self.devices_dict = {}
        for device_class in self._device_classes:
            if issubclass(device_class, _HueEntity):
                device = device_class(bridge)
            else:
                device = device_class()
            self.devices.append(device)
            self.devices_dict[device.name] = device

        self._connecting_rooms = []
        self._rules = []

    def __rshift__(self, room):
        room >> self
        self._connecting_rooms.append(room)

    def get_device(self, name):
        return self.devices_dict[name]

    @property
    def connecting_rooms(self):
        return self._connecting_rooms

    @abstractmethod
    def run_rules(self):
        pass
