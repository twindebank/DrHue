import datetime
import time

from drhue.bridge import DrHueBridge
from drhue.context import Context
from home.my_home import MyHome


def run_main_loop():
    bridge = DrHueBridge()
    context = Context(
        bridge=bridge,
        bedtime=datetime.time(hour=23, minute=45)
    )
    home = MyHome(context=context)
    while True:
        context.bridge.read()
        home.run_all_rules()
        context.bridge.write()
        time.sleep(1)


if __name__ == '__main__':
    run_main_loop()
