from functools import lru_cache


def clearable_cached_property(f):
    return property(lru_cache(maxsize=1)(f))


class Parser:
    _raw_data = None

    def __init__(self, data_holding_class):
        self.data_holding_class = data_holding_class

    @property
    def raw_data(self):
        if self._raw_data is None:
            raise ValueError("Must attach data before using parser.")
        return self._raw_data

    @raw_data.setter
    def raw_data(self, data):
        self._clear_cache()
        self._raw_data = data

    @clearable_cached_property
    def parsed_data(self):
        return self.data_holding_class.from_raw(self.raw_data)

    @clearable_cached_property
    def state(self):
        return self.parsed_data.get_state()

    def has_state_changed(self, old_state):
        return not equal_dicts(self.state, old_state, ignore_keys=['parsed_datetime', 'collected_datetime'])

    @clearable_cached_property
    def telemetry(self):
        return self.parsed_data.get_telemetry()

    def has_telemetry_changed(self, old_telemetry):
        return not equal_dicts(self.telemetry, old_telemetry, ignore_keys=['parsed_datetime', 'collected_datetime'])

    def _clear_cache(self):
        type(self).parsed_data.fget.cache_clear()
        type(self).state.fget.cache_clear()
        type(self).telemetry.fget.cache_clear()

    def parse_config(self, config):
        return self.parsed_data.get_api_calls_from_config(config)


def equal_dicts(d1, d2, ignore_keys):
    if None in [d1, d2]:
        return False
    ignored = set(ignore_keys)
    for k1, v1 in d1.items():
        if k1 not in ignored and (k1 not in d2 or d2[k1] != v1):
            return False
    for k2, v2 in d2.items():
        if k2 not in ignored and k2 not in d1:
            return False
    return True
