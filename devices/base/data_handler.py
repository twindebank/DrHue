import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from typing import Dict, Any

from loguru import logger

from devices.base.fields import asdict, STATE, TELEMETRY


@dataclass
class BaseDataHandler(ABC):
    collected_datetime: str = None
    parsed_datetime: str = None

    @property
    @abstractmethod
    def name(self):
        pass

    @classmethod
    def from_raw_outer(cls, raw_data: dict):
        return cls(
            **cls.from_raw(cls, raw_data),
            parsed_datetime=datetime.datetime.now().isoformat(),
            collected_datetime=raw_data['collected_datetime']
        )

    @abstractmethod
    @staticmethod
    def from_raw(raw_data: dict) -> dict:
        pass

    def get_state(self):
        return asdict(self, filter_field_type=STATE)

    def get_telemetry(self):
        return asdict(self, filter_field_type=TELEMETRY)

    @abstractmethod
    def get_api_calls_from_config(self, config) -> Dict[str, Dict[str, Any]]:
        pass


def generate_payloads_from_config(data_class, config):
    """
    iterate through data class fields and generate calls to send back to the hub based on the field metadata and config
    value
    """
    calls = {}
    for f in fields(data_class):
        if f.metadata.get('type', None) != STATE or f.name not in config:
            continue

        config_value = config[f.name]

        if config_value is None and not f.metadata['accepts_null']:
            logger.warning(f"State '{f.name}' cannot be set to null.")
            continue

        api_path = f.metadata['api_path']
        if api_path is None:
            logger.warning(f"State '{f.name}' is not mutable.")
            continue

        formatted_api_path = api_path.format(id=data_class.id)
        payload_key = f.metadata['payload_key']
        calls.setdefault(formatted_api_path, {})[payload_key] = config_value
    return calls
