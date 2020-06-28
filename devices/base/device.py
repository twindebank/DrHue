from dataclasses import dataclass
from typing import Type

from devices.base.connector import BaseConnector
from devices.base.data_handler import BaseDataHandler


@dataclass
class Device:
    connector: Type[BaseConnector]
    data_handler: Type[BaseDataHandler]
    config_topic: str
    state_topic: str
    command_topic: str
    