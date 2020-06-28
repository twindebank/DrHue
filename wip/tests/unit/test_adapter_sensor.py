from unittest.mock import Mock

import pytest

from drhue.adapter.sensor import DrHueSensor
from drhue.bridge import DrHueBridge


def test_sensor_get_sensor_keys():
    bridge = Mock(spec=DrHueBridge)
    bridge.raw_data = {
        'sensors': {
            '1': {
                'name': 'Sensor 1',
                'uniqueid': '123-456',
                'type': None
            },
            '2': {
                'name': 'sensor1-temp',
                'uniqueid': '123-789',
                'type': 'ZLLTemperature'
            },
            '3': {
                'name': 'sensor1-light',
                'uniqueid': '123-789',
                'type': 'ZLLLightLevel'
            }

        },
    }

    sensor = DrHueSensor(bridge, 'Sensor 1')
    assert sensor.motion_sensor_key == '1'
    assert sensor.temp_sensor_key == '2'
    assert sensor.light_sensor_key == '3'


def test_sensor_not_found():
    bridge = Mock(spec=DrHueBridge)
    bridge.raw_data = {
        'sensors': {
            '1': {
                'name': 'Sensor 1',
                'uniqueid': '123-456',
                'type': None
            },
            '2': {
                'name': 'sensor1-temp',
                'uniqueid': '123-789',
                'type': 'ZLLTemperature'
            },
            '3': {
                'name': 'sensor1-light',
                'uniqueid': '123-789',
                'type': 'ZLLLightLevel'
            }

        },
    }
    with pytest.raises(ModuleNotFoundError):
        DrHueSensor(bridge, 'Sensor 2')
