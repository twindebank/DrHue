import time

from drhue.bridge import DrHueBridge
from home.my_home import MyHome


def run_main_loop():
    bridge = DrHueBridge()
    bridge.read()
    home = MyHome(bridge=bridge)
    while True:
        bridge.read()
        home.run_all_rules()
        bridge.write()
        time.sleep(1)


if __name__ == '__main__':
    run_main_loop()
