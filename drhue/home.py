from __future__ import annotations
from __future__ import annotations

from abc import ABC, abstractmethod, ABCMeta
from datetime import timedelta, datetime
from typing import List, Type, Dict, Union, Optional, Tuple, Any

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
    adapter_properties: Tuple[Tuple[str, Type, Any]] = ()

    def __init__(self, context):
        super().__init__(context)
        self.adapter = self._adapter_class(context.bridge, self.name)

        def create_getter(prop):
            return lambda self: self.__class__._property_getter(self, prop)

        def create_setter(prop):
            return lambda self, val: self.__class__._property_setter(self, prop, val)

        for (prop, prop_type, default_val) in self.adapter_properties:
            setattr(
                self.__class__,
                f"_{prop}",
                default_val
            )
            setattr(
                self.__class__,
                prop,
                property(
                    fget=create_getter(prop),
                    fset=create_setter(prop)
                )
            )

    @property
    @abstractmethod
    def _adapter_class(self):
        pass

    def sync_state(self):
        for (prop, *_) in self.adapter_properties:
            if not self._check_consistency(prop):
                setattr(self, f"_{prop}", getattr(self.adapter, prop))
            self._check_consistency(prop)

    def _property_getter(self, prop):
        return getattr(self, f"_{prop}")

    def _property_setter(self, prop, val):
        logger.debug(f"Changing '{self.name}' {prop} to '{val}'.")
        setattr(self.adapter, prop, val)
        setattr(self, f"_{prop}", val)

    def _check_consistency(self, prop):
        """
        todo: bug here
        if light turned on and then off,
        adapter remains in same state but entity changes  so consistency checks fail
        dont need to do multiple coinsistency checks, just need to do on read
        :param prop:
        :return:
        """
        entity_state = getattr(self, f"_{prop}")
        adapter_state = getattr(self.adapter, prop)
        if adapter_state != entity_state:
            logger.warning(
                f"Inconsistent state in '{self.name}' for property '{prop}':"
                f"\n\tentity: {entity_state}\n\tadapter: {adapter_state}"
            )
            return False
        return True


class Lights(_HueEntity, metaclass=ABCMeta):
    """
    links to hue groups
    these need to store state of timeout
    """

    adapter_properties = (
        ('on', bool, False),
        ('brightness', int, 1),
        ('scene', Optional[str], None),
    )

    _timeout: Optional[datetime] = None

    _adapter_class = DrHueLights

    def sync_state(self):
        """
        if now > timeout, turn off
        could also do brightness fades here, eg fade out over 30 mins:
            create array of current birghtness to zero with length 30min*60*refreshrate

        """
        super().sync_state()
        if self._timeout is not None and self.context.now > self._timeout:
            logger.debug(f"'{self.name}' timed out, switching off.")
            self.on = False
            self._timeout = None

    def turn_on(self, timeout_mins=None, brightness=None, scene=None):
        self.on = True
        if timeout_mins is not None:
            self.set_timeout(timeout_mins)
        if brightness is not None:
            self.brightness = brightness
        if scene:
            self.scene = scene

    def turn_off(self):
        self.on = False
        self.scene = None
        self.brightness = 1

    def set_timeout(self, timeout_mins):
        self._timeout = self.context.now + timedelta(minutes=timeout_mins)


class Sensor(_HueEntity):
    _adapter_class = DrHueSensor

    def sync_state(self):
        """
        store historical states here
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
