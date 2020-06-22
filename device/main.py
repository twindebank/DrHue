from loguru import logger

from bridge import DrHueBridge
from contracts.bridge import ParsedBridgeData
from mqtt_client import Client
from parser import Parser

"""
todo: https://www.notion.so/IoT-RPi-Design-d9dde3651c4d4517bc793547fb895ede
"""


def main():
    logger.add("log.log", rotation="1Mb")

    bridge = DrHueBridge()
    bridge_parser = Parser(
        data_holding_class=ParsedBridgeData
    )

    def message_callback(*_, message):
        """todo"""
        return
        api_calls = bridge_parser.parse_config_message(message)
        for url, payload in api_calls.items():
            bridge.call(url, payload)

    client = Client(
        device_id='rpi',
        registry_id='home',
        project_id='theo-home',
        on_message_callback=message_callback
    )

    prev_telemetry_data = None
    prev_state_data = None
    while True:
        bridge_parser.data = bridge.get_raw_data()
        client.loop()
        if prev_telemetry_data != bridge_parser.telemetry['data']:
            logger.info('Telemetry changed!')
            client.send_telemetry_event(bridge_parser.telemetry)
            prev_telemetry_data = bridge_parser.telemetry['data']
        if prev_state_data != bridge_parser.state['data']:
            logger.info('State changed!')
            client.send_state(bridge_parser.state)
            prev_state_data = bridge_parser.state['data']
        client.loop()


if __name__ == '__main__':
    main()
