import os
from abc import ABC, abstractmethod

import requests


class DrHueBridge:

    def __init__(self):
        self.bridge_data = {}
        self.staged_changes = {}
        self.ip = self._get_bridge_ip()
        self.username = self._get_username()
        self.api_path = f"https://{self.ip}/{self.username}/api"

    @staticmethod
    def _get_bridge_ip():
        response = requests.get("https://discovery.meethue.com/")
        ip = response.json()[0]['internalipaddress']
        return ip

    @staticmethod
    def _get_username():
        return os.getenv("HUE_USERNAME")

    def read(self):
        req = requests.get(self.api_path)
        req.raise_for_status()
        self.bridge_data = req.json()

    def set(self, entity_path, payload):
        self.staged_changes[entity_path] = payload

    def write(self):
        for entity_path, payload in self.staged_changes.items():
            r = requests.post(f"{self.api_path}/{entity_path}", json=payload)
            r.raise_for_status()

        self.staged_changes = {}

    def get_sensor(self, name):
        return DrHueSensor(self, name)

    def get_lights(self, name):
        return DrHueLights(self, name)


"""
all interaction with raw api data happens here and presented behind helper classes
objects below provide easy read/write interface to properties like on/off, bridgtness, colour, etc

"""


class _DrHueAdapter(ABC):
    def __init__(self, bridge, name):
        self._bridge = bridge
        self.name = name

    def stage_changes(self, payload):
        self._bridge.set(self.entity_path, payload)

    @property
    @abstractmethod
    def entity_path(self):
        pass


class DrHueSensor(_DrHueAdapter):
    @property
    def entity_path(self):
        return ''

    @property
    def motion(self):
        return False

    @property
    def temperature(self):
        return 15.5

    @property
    def daylight(self):
        return True

    @property
    def dark(self):
        return False


class DrHueLights(_DrHueAdapter):
    @property
    def entity_path(self):
        return ''

    @property
    def on(self):
        return False

    @on.setter
    def on(self, state):
        self.stage_changes({"state": state})
