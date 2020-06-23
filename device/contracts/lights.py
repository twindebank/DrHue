from dataclasses import dataclass
from typing import List, Dict, Optional

from contracts.fields import state_field


@dataclass
class Light:
    name: str
    id: str
    on: bool = state_field(api_path='lights/{id}/state', payload_key='on')
    brightness: int = state_field(api_path='lights/{id}/state', payload_key='bri')
    hue: Optional[int] = state_field(api_path='lights/{id}/state', payload_key='hue')
    saturation: Optional[int] = state_field(api_path='lights/{id}/state', payload_key='sat')
    effect: Optional[str] = state_field(api_path='lights/{id}/state', payload_key='effect')
    xy: Optional[List[int]] = state_field(api_path='lights/{id}/state', payload_key='xy')
    colour_temp: Optional[int] = state_field(api_path='lights/{id}/state', payload_key='ct')
    colour_mode: Optional[str] = state_field(api_path='lights/{id}/state', payload_key='colormode')
    reachable: Optional[bool] = state_field(api_path=None, payload_key=None)

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
        """
        Don't take missing attributes into account when comparing individual lights.

        Todo: should factor this into dedicated function, approx_equal
        """
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
class LightGroup:
    name: str
    id: str
    lights: Dict[str, Light]
    all_on: bool = state_field(api_path="groups/{id}/state", payload_key="all_on")
    any_on: bool = state_field(api_path="groups/{id}/state", payload_key="any_on")
    # todo: do this later, is complicated, need to pass in a func here to convert to api calls to lights
    scene: Optional[str] = state_field(api_path=None, payload_key=None)

    @classmethod
    def from_raw(cls, group_name: str, group_id: str, bridge_data: dict):
        lights = {
            light_data['name']: Light.from_raw(light_data['name'], light_id, light_data['state'])
            for light_id, light_data in bridge_data['lights'].items()
            if light_id in bridge_data['groups'][group_id]['lights']
        }
        return cls(
            name=group_name,
            id=group_id,
            all_on=bridge_data['groups'][group_id]['state']['all_on'],
            any_on=bridge_data['groups'][group_id]['state']['any_on'],
            scene=get_active_scene_from_raw(group_id, lights, bridge_data['scenes']),
            lights=lights
        )


def get_active_scene_from_raw(group_id: str, lights: Dict[str, Light], raw_scene_data: Dict):
    scenes_for_group = {
        scene_id: scene_data
        for scene_id, scene_data in raw_scene_data.items()
        if scene_data.get('group', None) == group_id
    }
    for scene_id, scene_data in scenes_for_group.items():
        match = False
        for light_name, light_state in lights.items():
            scene_light_state = Light.from_raw(light_state.name, light_state.id,
                                               scene_data['lightstates'][light_state.id])
            scene_light_state.on = light_state.on
            if not scene_light_state == light_state:
                match = False
                break
            match = True

        if match:
            return scenes_for_group[scene_id]
