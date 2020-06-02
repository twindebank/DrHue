from dataclasses import dataclass
from typing import Dict


@dataclass
class RawHueBridgeData:
    bridge: Dict
    scenes: Dict


@dataclass
class RawData:
    hue_bridge: RawHueBridgeData
