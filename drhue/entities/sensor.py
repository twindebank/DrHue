from drhue.adapter.sensor import DrHueSensor
from drhue.entities.base import HueEntity, AdapterProperty


class Sensor(HueEntity):
    adapter_properties = [
        AdapterProperty('motion', bool, default=False, read_only=True),
        AdapterProperty('temperature', int, default=1, read_only=True),
        AdapterProperty('daylight', bool, read_only=True),
        AdapterProperty('dark', bool, read_only=True),
        AdapterProperty('lightlevel', int, read_only=True),
    ]

    _adapter_class = DrHueSensor
