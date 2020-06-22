from unittest.mock import MagicMock, patch

import pytest

from drhue.adapter.base import DrHueAdapter
from drhue.entities.base import Entity, HueEntity, EntityProperty


def test_syncing_entity_state_with_adapter_state():
    properties = [
        EntityProperty(name='state_with_default_matching_adapter', value_type=str, default='adapter_val'),
        EntityProperty(name='state_with_default_not_matching_adapter', value_type=str, default='not_adapter_val'),
        EntityProperty(name='state_no_default', value_type=str),
        EntityProperty(name='state_with_default_matching_adapter_read_only', value_type=str, read_only=True,
                       default='adapter_val'),
        EntityProperty(name='state_with_default_not_matching_adapter_read_only', value_type=str, read_only=True,
                       default='not_adapter_val'),
        EntityProperty(name='state_no_default_read_only', value_type=str, read_only=True)
    ]

    adapter = MagicMock(spec=DrHueAdapter)
    adapter.state_with_default_matching_adapter = 'adapter_val'
    adapter.state_with_default_not_matching_adapter = 'adapter_val'
    adapter.state_no_default = 'adapter_val'
    adapter.state_with_default_matching_adapter_read_only = 'adapter_val'
    adapter.state_with_default_not_matching_adapter_read_only = 'adapter_val'
    adapter.state_no_default_read_only = 'adapter_val'

    device = HueEntity(
        name='device',
        _entity_properties=properties,
        _adapter=adapter
    )
    room = Entity(name='room', sub_entities=[device])

    with patch('drhue.entities.base.logger') as logger:
        room.sync_states()

    warning_logs = [call[0][0] for call in logger.warning.call_args_list]
    assert len(warning_logs) == 2
    assert "state_with_default_not_matching_adapter" in warning_logs[0]
    assert "state_no_default" in warning_logs[1]

    for p in properties:
        assert p.read() == 'adapter_val', p.name
        assert device.read(p.name) == 'adapter_val', p.name


def test_exception_raised_when_try_to_set_read_only_property():
    properties = [
        EntityProperty(name='state_read_only', value_type=str, read_only=True)
    ]

    adapter = MagicMock(spec=DrHueAdapter)
    adapter.state_read_only = 'adapter_val'

    device = HueEntity(
        name='device',
        _entity_properties=properties,
        _adapter=adapter
    )
    with pytest.raises(ValueError):
        device.set('state_read_only', 'balala')

