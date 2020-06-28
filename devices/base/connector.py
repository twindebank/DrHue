import datetime
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseConnector(ABC):

    def get_raw_data_outer(self):
        raw_data = self.get_raw_data()
        raw_data['collected_datetime'] = datetime.datetime.now().isoformat()
        return raw_data

    @abstractmethod
    def get_raw_data(self) -> dict:
        pass

    @abstractmethod
    def execute_calls(self, calls: Dict[str, Dict[str, Any]]):
        pass
