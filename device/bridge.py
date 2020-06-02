import os

import requests
from loguru import logger

from device.contracts.raw import RawHueBridgeData


class DrHueBridge:
    """
    """

    def __init__(self):
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
        return os.environ["HUE_USERNAME"].strip()

    def get_raw_data(self):
        """
        Have to call scenes endpoint to get enough data to match scene with scene name.
        """
        raw_data = self.get()
        scene_data = {scene_id: self.get_scene_data(scene_id) for scene_id in raw_data['scenes']}

        return RawHueBridgeData(
            bridge=raw_data,
            scenes=scene_data
        )

    def scene(self):
        """
        Hue APi doesn't seem to expose a method to get an active scene given a light group.
        This tries to deduce the active scene by matching light states for scenes with light active light states.
        """
        scenes_for_room = {scene_id: scene for scene_id, scene in self.bridge.data['scenes'].items() if
                           tuple(sorted(scene['lights'])) == self.light_ids}
        for scene_id, scene in scenes_for_room.items():
            scene_with_light_states = self.bridge.get_scene_data(scene_id)
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
                return self.store_state(scene['name'])
        return self.store_state(None)

    def get_scene_data(self, scene_id):
        return self.get(f'scenes/{scene_id}')

    def _put(self, relative_path, payload):
        logger.debug(f"Sending payload to '{relative_path}': {payload}")
        r = requests.put(f"{self.api_path}/{relative_path}", json=payload)
        r.raise_for_status()
        return r.json()

    def get(self, relative_path=''):
        path_str = f' ({relative_path})' if relative_path else ''
        logger.debug(f"Reading from bridge {path_str}...")
        data = self._get(relative_path)
        if isinstance(data, list):
            for val in data:
                if 'error' in val:
                    raise ConnectionError(val['error'])
        return data

    def _get(self, relative_path=''):
        r = requests.get(f"{self.api_path}/{relative_path}")
        r.raise_for_status()
        return r.json()
