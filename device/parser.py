from functools import lru_cache

from contracts.bridge import ParsedBridgeData


def clearable_cached_property(f):
    return property(lru_cache(maxsize=1)(f))


class Parser:
    _bridge_data = None

    @property
    def bridge_data(self):
        if self._bridge_data is None:
            raise ValueError("Must attach bridge data before using.")
        return self._bridge_data

    @bridge_data.setter
    def bridge_data(self, data):
        self._clear_cache()
        self._bridge_data = data

    @clearable_cached_property
    def parsed_bridge_data(self):
        return ParsedBridgeData.from_raw(self.bridge_data)

    @clearable_cached_property
    def state(self):
        return self.parsed_bridge_data.get_state()

    @clearable_cached_property
    def telemetry(self):
        return self.parsed_bridge_data.get_telemetry()

    def _clear_cache(self):
        type(self).parsed_bridge_data.fget.cache_clear()
        type(self).state.fget.cache_clear()
        type(self).telemetry.fget.cache_clear()

    def parse_config_message(self, message):
        pass
