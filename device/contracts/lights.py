from dataclasses import dataclass
from typing import List, Dict, Optional

from device.contracts.raw import RawHueBridgeData


@dataclass
class LightState:
    name: str
    id: str
    on: bool
    brightness: int
    hue: Optional[int]
    saturation: Optional[int]
    effect: Optional[str]
    xy: Optional[List[int]]
    colour_temp: Optional[int]
    colour_mode: Optional[str]
    reachable: Optional[bool]

    @classmethod
    def from_raw(cls, light_name: str, light_id: str, light_state_data: dict):
        return cls(
            name=light_name,
            id=light_id,
            on=light_state_data['on'],
            brightness=light_state_data['bri'],
            hue=light_state_data.get('hue', None),
            saturation=light_state_data.get('saturation', None),
            effect=light_state_data.get('effect', None),
            colour_temp=light_state_data.get('ct', None),
            xy=light_state_data.get('xy', None),
            colour_mode=light_state_data.get('colormode', None),
            reachable=light_state_data.get('reachable', None)
        )

    def __eq__(self, other):
        matches = []
        for prop in self.__dict__:
            this_attr = getattr(self, prop)
            if this_attr is None:
                break
            other_attr = getattr(other, prop)
            if other_attr is None:
                break
            if this_attr == other_attr:
                matches.append(True)
            else:
                matches.append(False)
                break
        return len(matches) and all(matches)


@dataclass
class LightsState:
    all_on: bool
    any_on: bool
    scene: Optional[str]
    lights: Dict[str, LightState]

    @classmethod
    def from_raw(cls, group_id: str, raw_data: RawHueBridgeData):
        lights = {
            light_data['name']: LightState.from_raw(light_data['name'], light_id, light_data['state'])
            for light_id, light_data in raw_data.bridge['lights'].items()
            if light_id in raw_data.bridge['groups'][group_id]['lights']
        }
        return cls(
            all_on=raw_data.bridge['groups'][group_id]['state']['all_on'],
            any_on=raw_data.bridge['groups'][group_id]['state']['any_on'],
            scene=get_active_scene_from_raw(group_id, lights, raw_data.scenes),
            lights=lights
        )


def get_active_scene_from_raw(group_id: str, lights: Dict[str, LightState], raw_scene_data: Dict):
    scenes_for_group = {
        scene_id: scene_data
        for scene_id, scene_data in raw_scene_data.items()
        if scene_data.get('group', None) == group_id
    }
    for scene_id, scene_data in scenes_for_group.items():
        match = False
        for light_name, light_state in lights.items():
            scene_light_state = LightState.from_raw(light_state.name, light_state.id, scene_data['lightstates'][light_state.id])
            scene_light_state.on = light_state.on
            if not scene_light_state == light_state:
                match = False
                break
            match = True

        if match:
            return scenes_for_group[scene_id]
