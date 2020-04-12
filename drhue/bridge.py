import os

import requests
from phue import Bridge


class DrHueBridge:
    def __init__(self):
        self.phue_bridge = Bridge(ip=self._get_bridge_ip(), username=self._get_username())

    @staticmethod
    def _get_bridge_ip():
        response = requests.get("https://discovery.meethue.com/")
        ip = response.json()[0]['internalipaddress']
        return ip

    @staticmethod
    def _get_username():
        return os.getenv("HUE_USERNAME")

    def get_light_group(self, group_name):
        pass


def get_bridge():
    return DrHueBridge()
