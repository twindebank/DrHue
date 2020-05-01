from dataclasses import dataclass

import requests
from loguru import logger

from drhue.adapter.base import DrHueAdapter


@dataclass
class DrHueLights(DrHueAdapter):
    def __post_init__(self):
        self.group_key = self._get_group_key()

    @property
    def entity_action_path(self):
        return f"groups/{self.group_key}/action"

    def _get_group_key(self):
        group_key = None
        for key, group in self.bridge.bridge_data["groups"].items():
            if self.name == group["name"]:
                group_key = key
                break
        if group_key is None:
            raise ValueError(f"Group '{group_key}' not found.")
        return group_key

    @property
    def light_ids(self):
        return tuple(sorted(self.bridge.bridge_data['groups'][self.group_key]['lights']))

    @property
    def light_states(self):
        light_states = {}
        for light_id in self.light_ids:
            light_states[light_id] = self.bridge.bridge_data['lights'][light_id]['state']
        return light_states

    @property
    def on(self):
        return self.bridge.bridge_data['groups'][self.group_key]['action']['on']

    @on.setter
    def on(self, state):
        """if state is off then dont set scenes or anything"""
        self.stage_changes({"on": state}, update=state)

    @property
    def brightness(self):
        return self.bridge.bridge_data['groups'][self.group_key]['action']['bri']

    @brightness.setter
    def brightness(self, brightness):
        """1-254"""
        self.stage_changes({"bri": brightness})

    @property
    def _scene_lookup(self):
        return {scene_info['name'] + str(tuple(sorted(scene_info['lights']))): scene_id for scene_id, scene_info in
                self.bridge.bridge_data['scenes'].items()}

    def _get_scene_id(self, scene_name):
        try:
            return self._scene_lookup[scene_name + str(self.light_ids)]
        except KeyError:
            logger.error(f"Scene '{scene_name}' not found for group {self.name}.")

    @property
    def scene(self):
        scenes_for_room = {scene_id: scene for scene_id, scene in self.bridge.bridge_data['scenes'].items() if
                           tuple(sorted(scene['lights'])) == self.light_ids}
        for scene_id, scene in scenes_for_room.items():
            req = requests.get(f"{self.bridge.api_path}/scenes/{scene_id}")
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
