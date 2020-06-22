import datetime
from functools import lru_cache


def clearable_cached_property(f):
    return property(lru_cache(maxsize=1)(f))


class Parser:
    _data = None

    def __init__(self, data_holding_class):
        self.data_holding_class = data_holding_class

    @property
    def data(self):
        if self._data is None:
            raise ValueError("Must attach data before using parser.")
        return self._data

    @data.setter
    def data(self, data):
        self._clear_cache()
        self._data = data

    @clearable_cached_property
    def parsed_data(self):
        return self.data_holding_class.from_raw(self.data)

    @clearable_cached_property
    def state(self):
        return {
            "data": self.parsed_data.get_state(),
            "source": self.data_holding_class.name,
            "type": "state",
            "collected_datetime": datetime.datetime.now().isoformat()
        }

    @clearable_cached_property
    def telemetry(self):
        return {
            "data": self.parsed_data.get_telemetry(),
            "source": self.data_holding_class.name,
            "type": "telemetry",
            "collected_datetime": datetime.datetime.now().isoformat()
        }

    def _clear_cache(self):
        type(self).parsed_data.fget.cache_clear()
        type(self).state.fget.cache_clear()
        type(self).telemetry.fget.cache_clear()

    def parse_config_message(self, message):
        pass
