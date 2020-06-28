import datetime
import json
import logging
import ssl
from collections import Callable
from dataclasses import dataclass
from enum import Enum

import jwt
import paho.mqtt.client as mqtt
from loguru import logger

logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.CRITICAL)


class StrEnum(str, Enum):
    def __str__(self) -> str:
        return self.value

    # https://docs.python.org/3.6/library/enum.html#using-automatic-values
    def _generate_next_value_(name, start, count, last_values):
        return name


class MessageType(StrEnum):
    State = 'state'
    Telemetry = 'telemetry'


def create_jwt(project_id, private_key_file, algorithm):
    """Creates a JWT (https://jwt.io) to establish an MQTT connection.
        Args:
         project_id: The cloud project ID this device belongs to
         private_key_file: A path to a file containing either an RSA256 or
                 ES256 private key.
         algorithm: The encryption algorithm to use. Either 'RS256' or 'ES256'
        Returns:
            A JWT generated from the given project_id and private key, which
            expires in 20 minutes. After 20 minutes, your client will be
            disconnected, and a new JWT will have to be generated.
        Raises:
            ValueError: If the private_key_file does not contain a known key.
        """

    token = {
        # The time that the token was issued at
        'iat': datetime.datetime.utcnow(),
        # The time the token expires.
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=20),
        # The audience field should always be set to the GCP project id.
        'aud': project_id
    }

    # Read the private key file.
    with open(private_key_file, 'r') as f:
        private_key = f.read()

    print('Creating JWT using {} from private key file {}'.format(
        algorithm, private_key_file))

    return jwt.encode(token, private_key, algorithm=algorithm)


def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return '{}: {}'.format(rc, mqtt.error_string(rc))


def on_connect(unused_client, unused_userdata, unused_flags, rc):
    """Callback for when a device connects."""
    logger.debug('on_connect', mqtt.connack_string(rc))


def on_disconnect(unused_client, unused_userdata, rc):
    """Paho callback for when a device disconnects."""
    logger.debug('on_disconnect', error_str(rc))


def on_publish(unused_client, unused_userdata, unused_mid):
    """Paho callback when a message is sent to the broker."""
    logger.debug('on_publish')


def on_message(unused_client, unused_userdata, message):
    """Callback when the device receives a message on a subscription."""
    payload = str(message.payload.decode('utf-8'))
    logger.debug('Received message \'{}\' on topic \'{}\' with Qos {}'.format(
        payload, message.topic, str(message.qos))
    )


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed to the broker " + str(mid) + " " + str(granted_qos))


@dataclass
class Client:
    device_id: str  # Cloud IoT Core device id
    registry_id: str  # Cloud IoT Core registry id
    project_id: str
    private_key_file: str = 'creds/cloud_iot_private.pem'  # Path to private key file.
    cloud_region: str = 'europe-west1'
    algorithm: str = 'RS256'  # Which encryption algorithm to use to generate the JWT.
    ca_certs: str = 'creds/roots.pem'  # CA root from https://pki.google.com/roots.pem
    mqtt_bridge_hostname: str = 'mqtt.googleapis.com'
    mqtt_bridge_port: int = 8883
    jwt_exp_mins: datetime.timedelta = datetime.timedelta(minutes=29)

    on_connect_callback: Callable = on_connect
    on_publish_callback: Callable = on_publish
    on_disconnect_callback: Callable = on_disconnect
    on_message_callback: Callable = on_message
    on_subscribe_callback: Callable = on_subscribe

    def __post_init__(self):
        self.client_id = f'projects/{self.project_id}/' \
                         f'locations/{self.cloud_region}/' \
                         f'registries/{self.registry_id}/' \
                         f'devices/{self.device_id}'

        print(f'Device client_id is \'{self.client_id}\'.')

        self.config_topic = f'/devices/{self.device_id}/config'
        self.state_topic = f'/devices/{self.device_id}/state'
        self.telemetry_topic = f'/devices/{self.device_id}/events'
        self.commands_topic = f'/devices/{self.device_id}/commands/#'

        self.client = mqtt.Client(client_id=self.client_id)

        self._set_client_creds()
        self._set_client_callbacks()

        self.client.connect(self.mqtt_bridge_hostname, self.mqtt_bridge_port)

        self.client.subscribe(self.config_topic, qos=1)
        self.client.subscribe(self.commands_topic, qos=0)

        self.jwt_issue_time = datetime.datetime.now()

    def _set_client_creds(self):
        """
        With Google Cloud IoT Core, the username field is ignored, and the password field is used to transmit a JWT to
        authorize the device.
        """
        self.client.username_pw_set(
            username='unused',
            password=create_jwt(self.project_id, self.private_key_file, self.algorithm)
        )
        self.client.tls_set(ca_certs=self.ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

    def _set_client_callbacks(self):
        self.client.on_connect = self.on_connect_callback
        self.client.on_publish = self.on_publish_callback
        self.client.on_disconnect = self.on_disconnect_callback
        self.client.on_message = self.on_message_callback
        self.client.on_subscribe = self.on_subscribe_callback

    def _construct_message(self, source, data_type, payload):
        return json.dumps({
            source: {
                data_type: payload,
                "sent_datetime": datetime.datetime.now().isoformat()
            }
        })

    def send_state(self, source, payload):
        logger.info("Sending state...")
        payload = self._construct_message(source, 'state', payload)
        self.client.publish(self.state_topic, payload, qos=1)

    def send_telemetry_event(self, source, payload):
        logger.info("Sending telemetry event...")
        payload = self._construct_message(source, 'telemetry', payload)
        self.client.publish(self.telemetry_topic, payload, qos=1)

    def add_message_callback(self, topic, callback):
        self.client.message_callback_add(topic, callback)

    def refresh_token(self):
        logger.info("Refreshing token...")
        self.client.disconnect()
        self.__post_init__()

    def loop(self):
        self.client.loop()
        if datetime.datetime.now() - self.jwt_issue_time > self.jwt_exp_mins:
            self.refresh_token()
