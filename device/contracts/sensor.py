from dataclasses import dataclass
from typing import Dict

from loguru import logger

from contracts.fields import state_field, telemetry_field


@dataclass
class Sensor:
    name: str

    light_sensor_id: str
    light_sensor_uuid: str
    motion_sensor_id: str
    motion_sensor_uuid: str
    temp_sensor_id: str
    temp_sensor_uuid: str

    # general
    battery: int = telemetry_field()
    reachable: bool = telemetry_field()
    led_indication: bool = state_field(api_path="sensors/{motion_sensor_id}/config", payload_key="ledindication")

    # light sensor
    light_sensor_last_updated: str = telemetry_field()
    light_sensor_level: int = telemetry_field()
    light_sensor_dark: bool = telemetry_field()
    light_sensor_daylight: bool = telemetry_field()
    light_sensor_threshold_dark: int = state_field(
        api_path="sensors/{light_sensor_id}/config", payload_key="tholddark"
    )
    light_sensor_threshold_offset: int = state_field(
        api_path="sensors/{light_sensor_id}/config", payload_key="tholdoffset"
    )

    # motion sensor
    motion_sensor_last_updated: str = telemetry_field()
    motion_sensor_presence: bool = telemetry_field()
    motion_sensor_sensitivity: int = state_field(
        api_path="sensors/{motion_sensor_id}/config", payload_key="sensitivity"
    )
    motion_sensor_sensitivity_max: int = state_field(
        api_path="sensors/{motion_sensor_id}/config", payload_key="sensitivitymax"
    )

    # temp sensor
    temp_sensor_last_updated: str = telemetry_field()
    temp_sensor_temp: int = telemetry_field()

    @classmethod
    def from_raw(
            cls, name: str,
            motion_sensor_key: str, motion_sensor_data: Dict,
            temp_sensor_key: str, temp_sensor_data: Dict,
            light_sensor_key: str, light_sensor_data: Dict
    ):
        return cls(
            name=name,
            battery=motion_sensor_data['config']['battery'],
            reachable=motion_sensor_data['config']['reachable'],
            led_indication=motion_sensor_data['config']['ledindication'],
            light_sensor_id=light_sensor_key,
            light_sensor_uuid=light_sensor_data['uniqueid'],
            light_sensor_last_updated=light_sensor_data['state']['lastupdated'],
            light_sensor_level=light_sensor_data['state']['lightlevel'],
            light_sensor_dark=light_sensor_data['state']['dark'],
            light_sensor_daylight=light_sensor_data['state']['daylight'],
            light_sensor_threshold_dark=light_sensor_data['config']['tholddark'],
            light_sensor_threshold_offset=light_sensor_data['config']['tholdoffset'],
            motion_sensor_id=motion_sensor_key,
            motion_sensor_uuid=motion_sensor_data['uniqueid'],
            motion_sensor_last_updated=motion_sensor_data['state']['lastupdated'],
            motion_sensor_presence=motion_sensor_data['state']['presence'],
            motion_sensor_sensitivity=motion_sensor_data['config']['sensitivity'],
            motion_sensor_sensitivity_max=motion_sensor_data['config']['sensitivitymax'],
            temp_sensor_id=temp_sensor_key,
            temp_sensor_uuid=temp_sensor_data['uniqueid'],
            temp_sensor_last_updated=temp_sensor_data['state']['lastupdated'],
            temp_sensor_temp=temp_sensor_data['state']['temperature'] / 100
        )


@dataclass
class Sensors:
    sensors: Dict[str, Sensor]

    @classmethod
    def from_raw(cls, bridge_sensor_data: dict):
        sensor_names = set(sensor['name'] for sensor in bridge_sensor_data.values())
        sensors = {}
        for sensor_name in sensor_names:
            motion_sensor_key = None
            for key, sensor in bridge_sensor_data.items():
                if sensor_name == sensor["name"] and sensor['type'] == 'ZLLPresence':
                    motion_sensor_key = key
                    break
            if motion_sensor_key is None:
                continue

            uuid = bridge_sensor_data[motion_sensor_key]["uniqueid"]
            partial_uuid = uuid.split('-')[0]
            temp_sensor_key, light_sensor_key = None, None
            for key, sensor in bridge_sensor_data.items():
                if sensor.get('uniqueid', '').startswith(partial_uuid):
                    if sensor['type'] == 'ZLLTemperature':
                        temp_sensor_key = key
                    if sensor['type'] == 'ZLLLightLevel':
                        light_sensor_key = key

            if temp_sensor_key is None or light_sensor_key is None:
                logger.warning(f"Light and temperature data for sensor '{sensor_name}' not found.")
                continue

            sensors[sensor_name] = Sensor.from_raw(
                name=sensor_name,
                motion_sensor_key=motion_sensor_key,
                motion_sensor_data=bridge_sensor_data[motion_sensor_key],
                temp_sensor_key=temp_sensor_key,
                temp_sensor_data=bridge_sensor_data[temp_sensor_key],
                light_sensor_key=light_sensor_key,
                light_sensor_data=bridge_sensor_data[light_sensor_key],
            )

        return cls(
            sensors=sensors
        )
