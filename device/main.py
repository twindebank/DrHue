from loguru import logger

from bridge import DrHueBridge
from client import Client
from parser import Parser

"""
todo: https://www.notion.so/IoT-RPi-Design-d9dde3651c4d4517bc793547fb895ede
"""


def main():
    logger.add("log.log", rotation="1Mb")
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
            client.send_telemetry_event(parser.telemetry)
            prev_telemetry = parser.telemetry
        if prev_state != parser.state:
            logger.info('State changed!')
            client.send_state(parser.state)
            prev_state = parser.state
        client.loop()


if __name__ == '__main__':
    main()
