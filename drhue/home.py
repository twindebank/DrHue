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
    rooms: Dict[Type[Room], Room]

    @property
    @abstractmethod
    def room_classes(self) -> List[Type[Room]]:
        pass

    def __init__(self, context):
        super().__init__(context)
        self.context.bridge.read()
        self.rooms = {room: room(context) for room in self.room_classes}

    def sync_device_states(self):
        for room in self.rooms.values():
            room.sync_device_states()

    def run_all_rules(self):
        for room in self.rooms.values():
            room.room_rules()
        self.home_rules()

    @abstractmethod
    def home_rules(self):
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

    @abstractmethod
    def sync_state(self):
        pass


class Lights(_HueEntity, metaclass=ABCMeta):
    """
    links to hue groups
    these need to store state of timeout
    needs to store things like relax/read
    """
    adapter_class = DrHueLights

    ON, OFF = True, False
    _state: bool = OFF
    _brightness: int = 0

    def sync_state(self):
        """
        if now > timeout, turn off
        could also do brightness fades here, eg fade out over 30 mins:
            create array of current birghtness to zero with length 30min*60*refreshrate
        """
        pass

    def on(self, timeout=None, brightness=None, scene=None):
        self.state = self.ON
        if timeout is not None:
            now = self.context.now
            """
            if we're storing state here then we need a way to make this state consistent with reality on every read/write
            
            """
        pass

    @property
    def state(self):
        if self._state != self.adapter.on:
            logger.warning("inconsistent state, something happened outside program")
            self._state = self.adapter.on
        return self._state

    @state.setter
    def state(self, state):
        if self._state != self.adapter.on:
            logger.warning("inconsistent state, something happened outside program")
        self.adapter.on = state
        self._state = state

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

    def sync_state(self):
        """
        if sensitivituy different from given then re set it
        :return:
        """

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
    def sync_state(self):
        """todo"""


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
        self.devices = {device_class: device_class(context) for device_class in self._device_classes}

        self._connecting_rooms = []
        self._rules = []

    def __rshift__(self, room):
        room >> self
        self._connecting_rooms.append(room)

    @property
    def connecting_rooms(self):
        return self._connecting_rooms

    def sync_device_states(self):
        for device in self.devices.values():
            device.sync_state()

    @abstractmethod
    def room_rules(self):
        pass
