from __future__ import annotations
from __future__ import annotations

from abc import ABC, abstractmethod, ABCMeta
from typing import List, Type, Dict, Union

from loguru import logger

from drhue.bridge import DrHueLights, DrHueSensor


class _Entity(metaclass=ABCMeta):
    def __init__(self, context):
        self.context = context

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    def __hash__(self):
        return hash(self.name)


class Home(_Entity, metaclass=ABCMeta):
    rooms: List[Room]

    @property
    @abstractmethod
    def room_classes(self) -> List[Type[Room]]:
        pass

    def __init__(self, context):
        super().__init__(context)
        self.context.bridge.read()
        self.rooms = [room(context) for room in self.room_classes]
        self.rooms_as_dict = {room.name: room for room in self.rooms}

    def run_all_rules(self):
        for room in self.rooms:
            room.run_rules()
        self.run_rules()

    @abstractmethod
    def run_rules(self):
        pass


class _HueEntity(_Entity, metaclass=ABCMeta):
    """
    name must be tied to hue entity
    """

    def __init__(self, context):
        super().__init__(context)
        self.adapter = self.adapter_class(context.bridge, self.name)

    @property
    @abstractmethod
    def adapter_class(self):
        pass


class Lights(_HueEntity, metaclass=ABCMeta):
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


class _GoogleEntity(_Entity, ABC):
    pass


class GoogleHome(_GoogleEntity):
    pass


class Chromecast(_GoogleEntity):
    pass


class Vacuum(_GoogleEntity):
    pass


DEVICES = [Lights, Sensor, GoogleHome, Chromecast, Vacuum]


class Room(_Entity, metaclass=ABCMeta):
    devices: Dict[Union[[Type[device] for device in DEVICES]], Union[[device for device in DEVICES]]]
    is_exit: bool = False

    @property
    @abstractmethod
    def _device_classes(self) -> List[Union[[Type[device] for device in DEVICES]]]:
        pass

    _connecting_rooms: List[Type[Room]] = None

    def __init__(self, context):
        super().__init__(context)
        self.devices = {}
        for device_class in self._device_classes:
            device = device_class(context)
            self.devices[device_class] = device

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
