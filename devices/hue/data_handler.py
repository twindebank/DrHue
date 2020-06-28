from dataclasses import dataclass, field
from typing import Dict

from devices.base.data_handler import generate_payloads_from_config, BaseDataHandler
from devices.hue.data_structures.lights import LightGroup
from devices.hue.data_structures.sensor import Sensors


@dataclass
class HueDataHandler(BaseDataHandler):
    name = 'hue'

    light_groups: Dict[str, LightGroup] = field(default_factory=list)
    sensors: Sensors = field(default_factory=list)

    @staticmethod
    def from_raw(raw_data: dict) -> dict:
        light_groups = {
            group_data['name']: LightGroup.from_raw(group_data['name'], group_id, raw_data)
            for group_id, group_data in raw_data['groups'].items()
        }

        return {
            "light_groups": light_groups,
            "sensors": Sensors.from_raw(raw_data['sensors']),
        }

    def get_api_calls_from_config(self, config):
        calls = {}
        for light_group_name, light_group_config in config.get('light_groups', {}).items():
            light_group_calls = generate_payloads_from_config(
                self.light_groups[light_group_name],
                light_group_config
            )
            calls.update(light_group_calls)

            for light_name, light_config in light_group_config.get('lights', []).items():
                light_calls = generate_payloads_from_config(
                    self.light_groups[light_group_name].lights[light_name],
                    light_config
                )
                calls.update(light_calls)
        return calls
