import datetime
import os

import requests
from loguru import logger


class DrHueBridge:
    """
    """

    def __init__(self):
        self.ip = self._get_bridge_ip()
        self.username = self._get_username()
        self.api_path = f"http://{self.ip}/api/{self.username}"

    @staticmethod
    def _get_bridge_ip():
        response = requests.get("https://discovery.meethue.com/")
        ip = response.json()[0]['internalipaddress']
        return ip

    @staticmethod
    def _get_username():
        return os.environ["HUE_USERNAME"].strip()

    def get_raw_data(self):
        """
        Have to call scenes endpoint to get enough data to match scene with scene name.
        """
        raw_data = self.get()
        scene_data = {scene_id: self.get_scene_data(scene_id) for scene_id in raw_data['scenes']}
        raw_data['scenes'] = scene_data
        raw_data['collected_datetime'] = datetime.datetime.now().isoformat()
        return raw_data

    def get_scene_data(self, scene_id):
        return self.get(f'scenes/{scene_id}')

    def _put(self, relative_path, payload):
        logger.debug(f"Sending payload to '{relative_path}': {payload}")
        r = requests.put(f"{self.api_path}/{relative_path}", json=payload)
        r.raise_for_status()
        return r.json()

    def multi_put(self, calls):
        """


        todo: here


        calls back to bridge failing need to look into it


        :param calls:
        :return:
        """

        for api_path, payload in calls.items():
            status_msgs = self._put(api_path, payload)
            for msg in status_msgs:
                if 'error' in msg:
                    logger.error(msg['error'])

    def get(self, relative_path='') -> dict:
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
