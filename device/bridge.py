import os

import requests
from loguru import logger


class DrHueBridge:
    """
    """

    def __init__(self):
        self.raw_data = {}
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
        return os.environ["HUE_USERNAME"].strip()

    def read_data_from_bridge(self):
        self.raw_data = self.get()
        # parse raw data here into config, have to iterate through and call scenes

    def get_scene_data(self, scene_id):
        return self.get(f'scenes/{scene_id}')

    def _put(self, relative_path, payload):
        logger.debug(f"Sending payload to '{relative_path}': {payload}")
        r = requests.put(f"{self.api_path}/{relative_path}", json=payload)
        r.raise_for_status()
        return r.json()

    def get(self, relative_path=''):
        path_str = f' ({relative_path})' if relative_path else ''
        logger.debug(f"Reading from bridge {path_str}...")
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
