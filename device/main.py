import json
import time

from loguru import logger

from device.bridge import DrHueBridge
from device.client import Client
from device.parser import Parser

"""
todo:
- state and telemetery working
- need distinction between state and telemetry in data model
"""


def main():
    bridge = DrHueBridge()
    parser = Parser()

    def message_callback(*_, message):
        """todo"""
        return
        api_calls = parser.parse_config_message(message)
        for url, payload in api_calls.items():
            bridge.call(url, payload)

    client = Client(
        device_id='rpi',
        registry_id='home',
        project_id='theo-home',
        on_message_callback=message_callback
    )

    prev_state = None
    prev_telemetry = None
    while True:
        parser.bridge_data = bridge.get_raw_data()
        client.loop()
        if prev_telemetry != parser.telemetry:
            logger.info('Telemetry changed!')
            client.send_telemetry_event(json.dumps(parser.telemetry))
            prev_telemetry = parser.telemetry
        if prev_state != parser.state:
            logger.info('State changed!')
            client.send_state(json.dumps(parser.state))
            prev_state = parser.state
        time.sleep(1)


if __name__ == '__main__':
    main()
