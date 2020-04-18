import datetime
import time

from drhue.bridge import DrHueBridge
from drhue.context import Context
from home.my_home import MyHome


def run_main_loop():
    context = Context(
        bridge=DrHueBridge(),
        bedtime=datetime.time(hour=23, minute=45)
    )
    home = MyHome(context=context)
    # put this loop logic into home.run()
    # have refresh_rate property in global context
    while True:
        context.bridge.read()
        home.sync_device_states()
        home.run_all_rules()
        context.bridge.write()
        time.sleep(1)


if __name__ == '__main__':
    run_main_loop()
