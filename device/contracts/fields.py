import copy

STATE = 'state'
TELEMETRY = 'telemetry'

from dataclasses import field, _is_dataclass_instance, fields


def state_field(api_path, payload_key, accepts_null=False, *args, **kwargs):
    metadata = kwargs.get('metadata', {})
    metadata['type'] = STATE
    metadata['api_path'] = api_path
    metadata['payload_key'] = payload_key
    metadata['accepts_null'] = accepts_null
    return field(*args, metadata=metadata, **kwargs)


def telemetry_field(*args, **kwargs):
    metadata = kwargs.get('metadata', {})
    metadata['type'] = TELEMETRY
    return field(*args, metadata={"type": TELEMETRY}, **kwargs)


def asdict(obj, dict_factory=dict, filter_field_type=None):
    """
    Version of dataclasses.asdict that can use field type infomation.
    """
    if _is_dataclass_instance(obj):
        result = []
        for f in fields(obj):
            if filter_field_type is None:
                continue

            field_type_from_metadata = f.metadata.get('type', None)
            if field_type_from_metadata != filter_field_type and field_type_from_metadata is not None:
                continue
            value = asdict(getattr(obj, f.name), dict_factory, filter_field_type)
            result.append((f.name, value))
        return dict_factory(result)
    elif isinstance(obj, tuple) and hasattr(obj, '_fields'):
        return type(obj)(*[asdict(v, dict_factory, filter_field_type) for v in obj])
    elif isinstance(obj, (list, tuple)):
        return type(obj)(asdict(v, dict_factory, filter_field_type) for v in obj)
    elif isinstance(obj, dict):
        return type(obj)((asdict(k, dict_factory, filter_field_type),
                          asdict(v, dict_factory, filter_field_type))
                         for k, v in obj.items())
    else:
        return copy.deepcopy(obj)
