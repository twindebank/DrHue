from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, List, Type

from loguru import logger

from drhue.adapter.lights import DrHueLights
from drhue.entities.base import HueEntity, EntityProperty
from drhue.helpers import default_field


@dataclass
class Lights(HueEntity):
    _entity_properties: List[EntityProperty] = default_field([
        EntityProperty('on', bool, default=False),
        EntityProperty('brightness', int, default=1),
        EntityProperty('scene', str),
    ])

    _active_timeout: Optional[datetime] = None
    _adapter_class: Type[DrHueLights] = DrHueLights

    def _sync_states(self):
        """
        if now > timeout, turn off
        could also do brightness fades here, eg fade out over 30 mins:
            create array of current birghtness to zero with length 30min*60*refreshrate

        """
        timeout = self.get_active_timeout()
        if timeout is not None and self.context.times.now > timeout:
            logger.info(f"'{self.name}' timed out, switching off.")
            self.set('on', False)
            self.clear_timeout()

    def turn_on(self, timeout_mins=None, brightness=None, scene=None):
        self.set('on', True)
        if timeout_mins is not None:
            self.set_timeout(timeout_mins)
        if brightness is not None:
            self.set('brightness', brightness)
        if scene:
            self.set('scene', scene)

    def turn_off(self):
        self.set('on', False)
        self.set('scene', None)
        self.set('brightness', 1)

    def set_timeout(self, timeout_mins):
        uid = self._adapter.uid
        timeout_dt = self.context.times.now + timedelta(minutes=timeout_mins)
        self.state[f"{uid}.active_timeout"] = str(timeout_dt)

    def clear_timeout(self):
        uid = self._adapter.uid
        self.state[f"{uid}.active_timeout"] = None

    def get_active_timeout(self):
        uid = self._adapter.uid
        timeout_dt_str = self.state.get(f"{uid}.active_timeout", None)
        if timeout_dt_str:
            return datetime.fromisoformat(timeout_dt_str)
