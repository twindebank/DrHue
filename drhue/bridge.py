import os

import requests
from loguru import logger

from drhue.adapter.lights import DrHueLights
from drhue.adapter.sensor import DrHueSensor


class DrHueBridge:

    def __init__(self):
        self.bridge_data = {}
        self.staged_changes = {}
        self.ip = self._get_bridge_ip()
        self.username = self._get_username()
        self.api_path = f"http://{self.ip}/api/{self.username}"
        self.read()

    @staticmethod
    def _get_bridge_ip():
        response = requests.get("https://discovery.meethue.com/")
        ip = response.json()[0]['internalipaddress']
        return ip

    @staticmethod
    def _get_username():
        return os.getenv("HUE_USERNAME")

    def read(self):
        logger.debug("Receiving new data from hub...")
        req = requests.get(self.api_path)
        req.raise_for_status()
        self.bridge_data = req.json()

    def set(self, entity_path, payload, update=True):
        if update:
            self.staged_changes.setdefault(entity_path, {}).update(payload)
        else:
            self.staged_changes[entity_path] = payload

    def write(self):
        for entity_path, payload in self.staged_changes.items():
            logger.debug(f"Sending payload to '{entity_path}': {payload}")
            r = requests.put(f"{self.api_path}/{entity_path}", json=payload)
            r.raise_for_status()
            status_msgs = r.json()
            err = False
            for msg in status_msgs:
                if 'error' in msg:
                    print(msg['error'])
                    err = True
            if err:
                raise RuntimeError()

        self.staged_changes = {}

    def get_sensor(self, name):
        return DrHueSensor(self, name)

    def get_lights(self, name):
        return DrHueLights(self, name)
