from dataclasses import dataclass
from typing import Dict

from device.contracts.raw import RawHueBridgeData


class SensorNotFound(Exception):
    pass


@dataclass
class SensorState:
    name: str

    @classmethod
    def from_raw(cls, name: str, motion_sensor_data: Dict, temp_sensor_data: Dict, light_sensor_data: Dict):
        pass
        # todo: here
        # need to work this out a bit better
        # otherwise have to go through getting keys for both state and telemetry
        # state refreshed less oftem
        # state stores mapping
        # use mapping info from state to build telemetry

        # also need to clear up organisation a bit
        # and add hardware and firmware info to lights and stuff


@dataclass
class SensorStates:
    sensors: Dict[str, SensorState]

    @classmethod
    def from_raw(cls, raw_data: RawHueBridgeData):
        sensor_names = set(sensor['name'] for sensor in raw_data.bridge['sensors'].values())
        for sensor_name in sensor_names:
            motion_sensor_key = None
            for key, sensor in raw_data.bridge["sensors"].items():
                if sensor_name == sensor["name"]:
                    motion_sensor_key = key
                    break
            if motion_sensor_key is None:
                raise SensorNotFound(sensor_name)

            uuid = raw_data.bridge["sensors"][motion_sensor_key]["uniqueid"]
            partial_uuid = uuid.split('-')[0]
            temp_sensor_key, light_sensor_key = None, None
            for key, sensor in raw_data.bridge["sensors"].items():
                if sensor.get('uniqueid', '').startswith(partial_uuid):
                    if sensor['type'] == 'ZLLTemperature':
                        temp_sensor_key = key
                    if sensor['type'] == 'ZLLLightLevel':
                        light_sensor_key = key

            if temp_sensor_key is None or light_sensor_key is None:
                raise SensorNotFound(sensor_name)

        return cls(
            name=''
        )


@dataclass
class SensorTelemetry:
    pass
