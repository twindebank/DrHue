import copy

STATE = 'state'
TELEMETRY = 'telemetry'

from dataclasses import field, _is_dataclass_instance, fields


def state_field(api_path, payload_key, *args, **kwargs):
    metadata = kwargs.get('metadata', {})
    metadata['type'] = STATE
    metadata['api_path'] = api_path
    metadata['payload_key'] = payload_key
    return field(*args, metadata=metadata, **kwargs)


def telemetry_field(*args, **kwargs):
    metadata = kwargs.get('metadata', {})
    metadata['type'] = TELEMETRY
    return field(*args, metadata={"type": TELEMETRY}, **kwargs)


def asdict(obj, dict_factory=dict, field_type=None, include_non_typed=True):
    """
    Version of dataclasses.asdict that can use field type infomation.
    """
    if _is_dataclass_instance(obj):
        result = []
        for f in fields(obj):
            field_type_from_metadata = f.metadata.get('type', None)
            if field_type is not None and field_type_from_metadata != field_type:
                if field_type_from_metadata is not None:
                    continue
                elif field_type_from_metadata is None and not include_non_typed:
                    continue
            value = asdict(getattr(obj, f.name), dict_factory, field_type, include_non_typed)
            result.append((f.name, value))
        return dict_factory(result)
    elif isinstance(obj, tuple) and hasattr(obj, '_fields'):
        return type(obj)(*[asdict(v, dict_factory, field_type, include_non_typed) for v in obj])
    elif isinstance(obj, (list, tuple)):
        return type(obj)(asdict(v, dict_factory, field_type, include_non_typed) for v in obj)
    elif isinstance(obj, dict):
        return type(obj)((asdict(k, dict_factory, field_type, include_non_typed),
                          asdict(v, dict_factory, field_type, include_non_typed))
                         for k, v in obj.items())
    else:
        return copy.deepcopy(obj)
