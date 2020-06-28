from unittest.mock import Mock, MagicMock

import pytest

from drhue.adapter.lights import DrHueLights
from drhue.bridge import DrHueBridge


def test_lights_get_group_key():
    bridge = Mock(spec=DrHueBridge)
    bridge.raw_data = {
        'lights': {
            '1': 'one',
            '2': 'two',
        },
        'groups': {
            '1': {'name': 'TestGroupName', 'lights': ['1', '2']}
        },
    }

    lights = DrHueLights(bridge, 'TestGroupName')
    assert lights.group_key == '1'


def test_lights_group_not_found():
    bridge = Mock(spec=DrHueBridge)
    bridge.raw_data = {
        'lights': {
            '1': 'one',
            '2': 'two',
        },
        'groups': {
            '1': {'name': 'TestGroupName', 'lights': ['1', '2']}
        },
    }
    with pytest.raises(ValueError):
        DrHueLights(bridge, 'TestFakeGroupName')


def test_get_lights_scene():
    bridge = Mock(spec=DrHueBridge)
    bridge.raw_data = {
        'lights': {
            '1': {'state': {'state1': 'val1'}},
            '2': {'state': {'state2': 'val2'}},
        },
        'groups': {
            '1': {'name': 'TestGroupName', 'lights': ['1', '2']}
        },
        'scenes': {
            'test_scene_id': {
                'name': 'scene1',
                'lights': ['1', '2']
            }
        }
    }
    light_states = {
        'test_scene_id': {
            'lightstates': {'1': {'state1': 'val1'}, '2': {'state2': 'val2'}}
        }
    }
    bridge._get_scene_data = MagicMock()
    bridge._get_scene_data.side_effect = lambda scene_id: light_states[scene_id]
    lights = DrHueLights(bridge, 'TestGroupName')
    assert lights.scene == 'scene1'


def test_get_lights_scene_no_matching_scene():
    bridge = Mock(spec=DrHueBridge)
    bridge.raw_data = {
        'lights': {
            '1': {'state': {'state1': 'val4'}},
            '2': {'state': {'state2': 'val5'}},
        },
        'groups': {
            '1': {'name': 'TestGroupName', 'lights': ['1', '2']}
        },
        'scenes': {
            'test_scene_id': {
                'name': 'scene1',
                'lights': ['1', '2']
            }
        }
    }
    light_states = {
        'test_scene_id': {
            'lightstates': {'1': {'state1': 'val1'}, '2': {'state2': 'val2'}}
        }
    }
    bridge._get_scene_data = MagicMock()
    bridge._get_scene_data.side_effect = lambda scene_id: light_states[scene_id]
    lights = DrHueLights(bridge, 'TestGroupName')
    assert lights.scene is None
