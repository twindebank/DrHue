from dataclasses import dataclass, field
from typing import Dict

from device.contracts.lights import LightsState
from device.contracts.raw import RawData, RawHueBridgeData
from device.contracts.sensor import SensorState


@dataclass
class HueGroup:
    """
    Assumptions: a group only has one set of lights and one sensor
    """
    name: str
    id: str
    lights: LightsState
    sensors: SensorState

    @classmethod
    def from_raw(cls, group_name: str, group_id: str, raw_data: RawHueBridgeData):
        return cls(
            name=group_name,
            id=group_id,
            lights=LightsState.from_raw(group_id, raw_data),
            sensors=SensorState.from_raw(group_id, raw_data),
        )


@dataclass()
class HueBridgeState:
    groups: Dict[str, HueGroup] = field(default_factory=list)

    @classmethod
    def from_raw(cls, raw_data: RawHueBridgeData):
        groups = {
            group_data['name']: HueGroup.from_raw(group_data['name'], group_id, raw_data) for group_id, group_data in
            raw_data.bridge['groups'].items()
        }

        return cls(groups=groups)


@dataclass
class State:
    hue_bridge_state: HueBridgeState

    @classmethod
    def from_raw(cls, raw_data: RawData):
        return cls(hue_bridge_state=HueBridgeState.from_raw(raw_data=raw_data.hue_bridge))
        pass
