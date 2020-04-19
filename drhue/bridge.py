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

    def set(self, entity_path, payload, update=True):
        if update:
            self.staged_changes.setdefault(entity_path, {}).update(payload)
        else:
            self.staged_changes[entity_path] = payload

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

    def stage_changes(self, payload, update=True):
        self._bridge.set(self.entity_action_path, payload, update)

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
    def light_ids(self):
        return tuple(sorted(self._bridge.bridge_data['groups'][self.group_key]['lights']))

    @property
    def light_states(self):
        light_states = {}
        for light_id in self.light_ids:
            light_states[light_id] = self._bridge.bridge_data['lights'][light_id]['state']
        return light_states

    @property
    def on(self):
        return self._bridge.bridge_data['groups'][self.group_key]['action']['on']

    @on.setter
    def on(self, state):
        """if state is off then dont set scenes or anything"""
        self.stage_changes({"on": state}, update=state)

    @property
    def brightness(self):
        return self._bridge.bridge_data['groups'][self.group_key]['action']['bri']

    @brightness.setter
    def brightness(self, brightness):
        """1-254"""
        self.stage_changes({"bri": brightness})

    @property
    def _scene_lookup(self):
        return {scene_info['name'] + str(tuple(sorted(scene_info['lights']))): scene_id for scene_id, scene_info in
                self._bridge.bridge_data['scenes'].items()}

    def _get_scene_id(self, scene_name):
        try:
            return self._scene_lookup[scene_name + str(self.light_ids)]
        except KeyError:
            logger.error(f"Scene '{scene_name}' not found for group {self.name}.")

    @property
    def scene(self):
        scenes_for_room = {scene_id: scene for scene_id, scene in self._bridge.bridge_data['scenes'].items() if
                           tuple(sorted(scene['lights'])) == self.light_ids}
        for scene_id, scene in scenes_for_room.items():
            req = requests.get(f"{self._bridge.api_path}/scenes/{scene_id}")
            req.raise_for_status()
            scene_with_light_states = req.json()
            light_states_for_scene = scene_with_light_states['lightstates']  # on bri xy
            light_states = self.light_states
            match = False
            for light_id, light_state_for_scene in light_states_for_scene.items():
                light_state = light_states[light_id]
                for state in light_state_for_scene:
                    if light_state[state] != light_state_for_scene[state]:
                        match = False
                        break
                    match = True
                if match:
                    break
            if match:
                return scene['name']
        return None

    @scene.setter
    def scene(self, scene_name):
        """Relax, Read, Concentrate, ..."""
        if not scene_name:
            return

        scene_id = self._get_scene_id(scene_name)
        if scene_id:
            self.stage_changes({"scene": scene_id})
