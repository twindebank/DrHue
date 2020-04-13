import os
from abc import ABC, abstractmethod

import requests
from loguru import logger

"""
todo:
- wire up bridge payload write
- set up proper logging
- start considering bridgness and stuff too
- tidy it out and get ready for github
- set up database: log all data AND log my data:
- events when state changes
- events when state unexpected



"""


class DrHueBridge:

    def __init__(self):
        self.bridge_data = {}
        self.staged_changes = {}
        self.ip = self._get_bridge_ip()
        self.username = self._get_username()
        self.api_path = f"http://{self.ip}/api/{self.username}"

    @staticmethod
    def _get_bridge_ip():
        response = requests.get("https://discovery.meethue.com/")
        ip = response.json()[0]['internalipaddress']
        return ip

    @staticmethod
    def _get_username():
        return os.getenv("HUE_USERNAME")

    def read(self):
        logger.info("Receiving new data from hub...")
        req = requests.get(self.api_path)
        req.raise_for_status()
        self.bridge_data = req.json()

    def set(self, entity_path, payload):
        self.staged_changes.setdefault(entity_path, {}).update(payload)

    def write(self):
        for entity_path, payload in self.staged_changes.items():
            logger.debug(f"Sending payload to '{entity_path}': {payload}")
            r = requests.put(f"{self.api_path}/{entity_path}", json=payload)
            r.raise_for_status()
            status_msgs = r.json()
            err = False
            for msg in status_msgs:
                if 'error' in msg:
                    print(msg['error'])
                    err = True
            if err:
                raise RuntimeError()

        self.staged_changes = {}

    def get_sensor(self, name):
        return DrHueSensor(self, name)

    def get_lights(self, name):
        return DrHueLights(self, name)


class _DrHueAdapter(ABC):
    def __init__(self, bridge, name):
        self._bridge = bridge
        self.name = name

    def stage_changes(self, payload):
        self._bridge.set(self.entity_action_path, payload)

    @property
    @abstractmethod
    def entity_action_path(self):
        pass


class DrHueSensor(_DrHueAdapter):
    def __init__(self, bridge, name):
        super().__init__(bridge, name)
        self.motion_sensor_key, self.temp_sensor_key, self.light_sensor_key = self._get_sensor_keys()

    def _get_sensor_keys(self):
        motion_sensor_key = None
        for key, sensor in self._bridge.bridge_data["sensors"].items():
            if self.name == sensor["name"]:
                motion_sensor_key = key
                break
        if motion_sensor_key is None:
            raise ModuleNotFoundError()

        uuid = self._bridge.bridge_data["sensors"][motion_sensor_key]["uniqueid"]
        partial_uuid = uuid.split('-')[0]
        temp_sensor_key, light_sensor_key = None, None
        for key, sensor in self._bridge.bridge_data["sensors"].items():
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
        """Read only interface for now."""
        raise NotImplementedError()

    @property
    def motion(self):
        return self._bridge.bridge_data['sensors'][self.motion_sensor_key]['state']['presence']

    @property
    def temperature(self):
        return self._bridge.bridge_data['sensors'][self.temp_sensor_key]['state']['temperature']

    @property
    def daylight(self):
        return self._bridge.bridge_data['sensors'][self.light_sensor_key]['state']['daylight']

    @property
    def lightlevel(self):
        return self._bridge.bridge_data['sensors'][self.light_sensor_key]['state']['lightlevel']

    @property
    def dark(self):
        return self._bridge.bridge_data['sensors'][self.light_sensor_key]['state']['dark']


class DrHueLights(_DrHueAdapter):
    def __init__(self, bridge, name):
        super().__init__(bridge, name)
        self.group_key = self._get_group_key()

    @property
    def entity_action_path(self):
        return f"groups/{self.group_key}/action"

    def _get_group_key(self):
        group_key = None
        for key, group in self._bridge.bridge_data["groups"].items():
            if self.name == group["name"]:
                group_key = key
                break
        if group_key is None:
            raise ModuleNotFoundError()
        return group_key

    @property
    def on(self):
        return self._bridge.bridge_data['groups'][self.group_key]['action']['on']

    @on.setter
    def on(self, state):
        self.stage_changes({"on": state})

    @property
    def brightness(self):
        return self._bridge.bridge_data['groups'][self.group_key]['action']['bri']

    @brightness.setter
    def brightness(self, brightness):
        """0-254"""
        self.stage_changes({"bri": brightness})
