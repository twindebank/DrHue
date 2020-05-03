from unittest.mock import patch, call

import pytest

from drhue.bridge import DrHueBridge


@pytest.fixture
def stubbed_drhuebridge():
    with patch.object(DrHueBridge, '_get_bridge_ip', return_value='ip_addr'), \
         patch.object(DrHueBridge, '_get_username', return_value='username'), \
         patch.object(DrHueBridge, '_put', return_value={'response': 'put_response_payload'}), \
         patch.object(DrHueBridge, '_get', return_value={'response': 'get_response_payload'}):
        yield DrHueBridge()


def test_bridge_api_path(stubbed_drhuebridge):
    assert stubbed_drhuebridge.api_path == 'http://ip_addr/api/username'


def test_bridge_stage_change_and_write_to_bridge(stubbed_drhuebridge):
    stubbed_drhuebridge.stage_change('entity_path', {'test': 'payload'})
    stubbed_drhuebridge.write_to_bridge()
    stubbed_drhuebridge._put.assert_called_with('entity_path', {'test': 'payload'})


def test_bridge_stage_multiple_changes_and_write_to_bridge(stubbed_drhuebridge):
    stubbed_drhuebridge.stage_change('entity_path', {'test': 'payload'})
    stubbed_drhuebridge.stage_change('entity_path2', {'test': 'payload'})
    stubbed_drhuebridge.write_to_bridge()
    stubbed_drhuebridge._put.call_args_list == [
        call('entity_path', {'test': 'payload'}),
        call('entity_path2', {'test': 'payload'}),
    ]


def test_bridge_stage_multiple_changes_to_same_path_with_update_and_write_to_bridge(stubbed_drhuebridge):
    stubbed_drhuebridge.stage_change('entity_path', {'test': 'payload'})
    stubbed_drhuebridge.stage_change('entity_path', {'test2': 'payload'}, update=True)
    stubbed_drhuebridge.write_to_bridge()
    stubbed_drhuebridge._put.assert_called_with('entity_path', {'test': 'payload', 'test2': 'payload'})


def test_bridge_stage_multiple_nested_changes_to_same_path_with_update_and_write_to_bridge(stubbed_drhuebridge):
    stubbed_drhuebridge.stage_change('entity_path', {'test': {'nested_list': [1, 2]}})
    stubbed_drhuebridge.stage_change('entity_path', {'test': {'nested_list': [3, 4]}}, update=True)
    stubbed_drhuebridge.write_to_bridge()
    stubbed_drhuebridge._put.assert_called_with('entity_path', {'test': {'nested_list': [1, 2, 3, 4]}})


def test_bridge_stage_multiple_changes_to_same_path_without_update_and_write_to_bridge(stubbed_drhuebridge):
    stubbed_drhuebridge.stage_change('entity_path', {'test': 'payload'})
    stubbed_drhuebridge.stage_change('entity_path', {'test2': 'payload'}, update=False)
    stubbed_drhuebridge.write_to_bridge()
    stubbed_drhuebridge._put.assert_called_with('entity_path', {'test2': 'payload'})


def test_bridge_auth_error(stubbed_drhuebridge):
    with patch.object(
            stubbed_drhuebridge,
            '_get',
            return_value=[
                {
                    'error':
                        {'type': 1, 'address': '/', 'description': 'unauthorized user'}
                }
            ]
    ):
        with pytest.raises(ConnectionError):
            stubbed_drhuebridge.read_data_from_bridge()


def test_bridge_scene_not_found(stubbed_drhuebridge):
    with patch.object(
            stubbed_drhuebridge,
            '_get',
            return_value=[
                {
                    'error':
                        {'type': 3, 'address': '/scenes/lala', 'description': 'resource, /scenes/lala, not available'}
                }
            ]
    ):
        with pytest.raises(ConnectionError):
            stubbed_drhuebridge.get_scehe_data('non_existent_scene')
