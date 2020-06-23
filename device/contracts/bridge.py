from dataclasses import dataclass, field
from typing import Dict

from contracts.fields import asdict, STATE, TELEMETRY
from contracts.lights import LightGroup
from contracts.sensor import Sensors

"""
todo make a base class from this to use for other data sources
"""


@dataclass
class ParsedBridgeData:
    name = 'hue'

    light_groups: Dict[str, LightGroup] = field(default_factory=list)
    sensors: Sensors = field(default_factory=list)

    @classmethod
    def from_raw(cls, bridge_data: dict):
        light_groups = {
            group_data['name']: LightGroup.from_raw(group_data['name'], group_id, bridge_data)
            for group_id, group_data in bridge_data['groups'].items()
        }

        return cls(
            light_groups=light_groups,
            sensors=Sensors.from_raw(bridge_data['sensors']),
        )

    def get_state(self):
        return asdict(self, field_type=STATE, include_non_typed=True)

    def get_telemetry(self):
        return asdict(self, field_type=TELEMETRY, include_non_typed=True)

    def get_api_calls_from_config(self, config):
        for light_group, light_group_data in config.get('light_groups', {}).items():
            pass
