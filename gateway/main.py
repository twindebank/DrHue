import json

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
        data_handler_class=ParsedBridgeData
    )

    def config_message_callback(client, user_data, message):
        logger.debug(f"MESSAGE RECIEVED: {message}")

        config = json.loads(message.payload)
        hue_config = config.get('hue', {}).get('state', None)
        if hue_config is not None:
            hue_api_calls = bridge_parser.parse_config(hue_config)
            bridge.multi_put(hue_api_calls)

    client = Client(
        device_id='rpi',
        registry_id='home',
        project_id='theo-home',
    )

    client.add_message_callback(client.config_topic, config_message_callback)

    prev_telemetry_data = None
    prev_state_data = None
    while True:
        bridge_parser.raw_data = bridge.get_raw_data()
        client.loop()
        if bridge_parser.has_telemetry_changed(prev_telemetry_data):
            logger.info('Telemetry changed!')
            client.send_telemetry_event(bridge_parser.data_handler_class.name, bridge_parser.telemetry)
            prev_telemetry_data = bridge_parser.telemetry
        if bridge_parser.has_state_changed(prev_state_data):
            logger.info('State changed!')
            client.send_state(bridge_parser.data_handler_class.name, bridge_parser.state)
            prev_state_data = bridge_parser.state
        client.loop()


if __name__ == '__main__':
    main()
