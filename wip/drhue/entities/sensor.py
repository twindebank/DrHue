from dataclasses import dataclass
from typing import Type, List

from drhue.adapter.sensor import DrHueSensor
from drhue.entities.base import HueEntity, EntityProperty
from drhue.helpers import default_field


@dataclass
class Sensor(HueEntity):
    _entity_properties: List[EntityProperty] = default_field([
        EntityProperty('motion', bool, default=False, read_only=True),
        EntityProperty('temperature', int, default=1, read_only=True),
        EntityProperty('daylight', bool, read_only=True),
        EntityProperty('dark', bool, read_only=True),
        EntityProperty('lightlevel', int, read_only=True),
    ])

    _adapter_class: Type[DrHueSensor] = DrHueSensor
