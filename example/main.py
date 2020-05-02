import datetime

from drhue.bridge import DrHueBridge
from drhue.context import Context
from drhue.entities.home import Home
from example.home.lounge import lounge


def run_main_loop():
    context = Context(
        bridge=DrHueBridge(),
        bedtime=datetime.time(hour=23, minute=45),
        refresh_interval=1
    )
    home = Home(
        name='Home',
        rooms=[lounge]
    )
    home.attach_context(context)
    home.run()


if __name__ == '__main__':
    run_main_loop()
