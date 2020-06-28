from dataclasses import dataclass

from drhue.adapter.base import DrHueAdapter


@dataclass
class DrHueSensor(DrHueAdapter):
    def __post_init__(self):
        super().__post_init__()
        self.motion_sensor_key, self.temp_sensor_key, self.light_sensor_key = self._get_sensor_keys()

    def _get_sensor_keys(self):
        motion_sensor_key = None
        for key, sensor in self.bridge.raw_data["sensors"].items():
            if self.name == sensor["name"]:
                motion_sensor_key = key
                break
        if motion_sensor_key is None:
            raise ModuleNotFoundError()

        uuid = self.bridge.raw_data["sensors"][motion_sensor_key]["uniqueid"]
        partial_uuid = uuid.split('-')[0]
        temp_sensor_key, light_sensor_key = None, None
        for key, sensor in self.bridge.raw_data["sensors"].items():
            if sensor.get('uniqueid', '').startswith(partial_uuid):
                if sensor['type'] == 'ZLLTemperature':
                    temp_sensor_key = key
                if sensor['type'] == 'ZLLLightLevel':
                    light_sensor_key = key

        if temp_sensor_key is None or light_sensor_key is None:
            raise ModuleNotFoundError()

        return motion_sensor_key, temp_sensor_key, light_sensor_key

    @property
    def entity_action_path(self):
        raise NotImplementedError()

    @property
    def motion(self):
        return self.store_state(self.bridge.raw_data['sensors'][self.motion_sensor_key]['state']['presence'])

    @property
    def temperature(self):
        return self.store_state(self.bridge.raw_data['sensors'][self.temp_sensor_key]['state']['temperature'] / 100)

    @property
    def daylight(self):
        return self.store_state(self.bridge.raw_data['sensors'][self.light_sensor_key]['state']['daylight'])

    @property
    def lightlevel(self):
        return self.store_state(self.bridge.raw_data['sensors'][self.light_sensor_key]['state']['lightlevel'])

    @property
    def dark(self):
        return self.store_state(self.bridge.raw_data['sensors'][self.light_sensor_key]['state']['dark'])
