# one loop:
# - publishing hub telemetry every second
# - state every 10s
# - subscribe to config topic

from device.bridge import DrHueBridge
from device.client import Client
from device.contracts.raw import RawData
from device.contracts.state import State


def main():
    client = Client(
        device_id='rpi',
        registry_id='home',
        project_id='theo-home',
    )

    # here load up bridge

    bridge = DrHueBridge()
    bridge_data = bridge.get_raw_data()
    raw = RawData(hue_bridge=bridge_data)
    state = State.from_raw(raw_data=raw)
    telemetry = Telemetry.from_raw(raw)

    # i = 0
    # while True:
    #     client.loop()
    #     time.sleep(1)
    #     i += 1
    #     # send telemetery every second for all sensors
    #     # get commands for every second, use state to resolve stuff eg scene
    #     if i % 10 == 0:
    #         # send state every 10 seconds
    #         client.send_state("i'm a state!!!")
    #         client.send_telemetry_event("i'm a telemetery event!!!")


if __name__ == '__main__':
    main()
