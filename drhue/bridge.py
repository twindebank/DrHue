import os

import requests
from deepmerge import always_merger
from loguru import logger


class DrHueBridge:
    """
    Fairly light class responsible for interaction with bridge.
    Instead of writing states directly to the bridge on change, changes are staged then written
    at the end of each cycle. This reduces the number of calls to the bridge and prevents jitter, eg
    if one rule says turn light A on, and the next says turn light A off, this way only the higher priority
    change will be applied and the lights wont 'jitter'.

    Responsibilities:
    - Authenticating to the bridge.
        This requires you to have a username set up for now, see
        https://developers.meethue.com/develop/get-started-2/ for help.
    - Staging changes of states to be written the bridge.
        During a run cycle, changes will be 'staged'. Eg. Turn some lights on or set a scene.
    - Writing state changes to the bridge.
        At the end of a run cycle, the state changes will be written to the bridge.
    - Reading states from the bridge and presenting the raw data for other classes to consume.
    """

    def __init__(self):
        self.data = {}
        self.staged_changes = {}
        self.ip = self._get_bridge_ip()
        self.username = self._get_username()
        self.api_path = f"http://{self.ip}/api/{self.username}"
        self.read_data_from_bridge()

    @staticmethod
    def _get_bridge_ip():
        response = requests.get("https://discovery.meethue.com/")
        ip = response.json()[0]['internalipaddress']
        return ip

    @staticmethod
    def _get_username():
        return os.getenv("HUE_USERNAME").strip()

    def read_data_from_bridge(self):
        data = self.get()

        self.data = data

    def stage_change(self, entity_path, payload, update=True):
        if update:
            always_merger.merge(
                self.staged_changes.setdefault(entity_path, {}),
                payload
            )
        else:
            self.staged_changes[entity_path] = payload

    def write_to_bridge(self):
        for entity_path, payload in self.staged_changes.items():
            status_msgs = self._put(entity_path, payload)
            err = False
            for msg in status_msgs:
                if 'error' in msg:
                    print(msg['error'])
                    err = True
            if err:
                raise RuntimeError()

        self.staged_changes = {}

    def get_scehe_data(self, scene_id):
        return self.get(f'scenes/{scene_id}')

    def _put(self, relative_path, payload):
        logger.debug(f"Sending payload to '{relative_path}': {payload}")
        r = requests.put(f"{self.api_path}/{relative_path}", json=payload)
        r.raise_for_status()
        return r.json()

    def get(self, relative_path=''):
        logger.debug(f"Reading '{relative_path}' from bridge...")
        data = self._get(relative_path)
        if isinstance(data, list):
            for val in data:
                if 'error' in val:
                    raise ConnectionError(val['error'])
        return data

    def _get(self, relative_path=''):
        r = requests.get(f"{self.api_path}/{relative_path}")
        r.raise_for_status()
        return r.json()
