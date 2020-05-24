# one loop:
# - publishing hub telemetry every second
# - state every 10s
# - subscribe to config topic
import time

from device.client import Client


def main():
    client = Client(
        device_id='rpi',
        registry_id='home',
        project_id='theo-home',
    )

    # here load up bridge

    i = 0
    while True:
        client.loop()
        time.sleep(1)
        i += 1
        # send telemetery every second for all sensors
        if i % 10 == 0:
            # send state every 10 seconds
            client.send_state("i'm a state!!!")
            client.send_telemetry_event("i'm a telemetery event!!!")


if __name__ == '__main__':
    main()
