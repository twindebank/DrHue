from dataclasses import asdict

from device.contracts.lights import LightsState
from device.contracts.state import State


def test_contracts_state_state(raw_hub_data):
    expected = {
        "hue_bridge": {
            "groups": {
                "lounge": {
                    "light_group": {
                        "all_on": False,
                        "any_on": False,
                        "scene": None,
                        "lights": {
                            'sofa': {
                                "on": False,
                                "brightness": 343,
                                "colour": 3443,
                                "etc": 3434
                            }
                        }
                    },
                    "sensor": {}
                }
            },
            "firmware": "wdsadas"
        }
    }
    assert asdict(State.from_raw(raw_hub_data))


def test_contract_lights_lightsstate(raw_hub_data):
    expected = {}
    assert asdict(LightsState.from_dict(raw_hub_data))
