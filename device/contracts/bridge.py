import datetime
from dataclasses import dataclass, field, fields
from typing import Dict

from loguru import logger

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

    collected_datetime: str = None
    parsed_datetime: str = None

    @classmethod
    def from_raw(cls, bridge_data: dict):
        light_groups = {
            group_data['name']: LightGroup.from_raw(group_data['name'], group_id, bridge_data)
            for group_id, group_data in bridge_data['groups'].items()
        }

        return cls(
            light_groups=light_groups,
            sensors=Sensors.from_raw(bridge_data['sensors']),
            parsed_datetime=datetime.datetime.now().isoformat(),
            collected_datetime=bridge_data['collected_datetime']
        )

    def get_state(self):
        return asdict(self, filter_field_type=STATE)

    def get_telemetry(self):
        return asdict(self, filter_field_type=TELEMETRY)

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


def generate_payloads_from_config(data_class, config):
    """
    iterate through data class fields and generate calls to send back to the hub based on the field metadata and config
    value
    """
    calls = {}
    for f in fields(data_class):
        if f.metadata.get('type', None) != STATE or f.name not in config:
            continue

        config_value = config[f.name]

        if config_value is None and not f.metadata['accepts_null']:
            logger.warning(f"State '{f.name}' cannot be set to null.")
            continue

        api_path = f.metadata['api_path']
        if api_path is None:
            logger.warning(f"State '{f.name}' is not mutable.")
            continue

        formatted_api_path = api_path.format(id=data_class.id)
        payload_key = f.metadata['payload_key']
        calls.setdefault(formatted_api_path, {})[payload_key] = config_value
    return calls
