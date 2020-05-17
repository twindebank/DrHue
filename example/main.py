import datetime

from drhue.bridge import DrHueBridge
from drhue.context import Context
from drhue.entities.home import Home
from example.home.bedroom import bedroom
from example.home.hallway import hallway
from example.home.kitchen import kitchen
from example.home.lounge import lounge
from example.home.office import office
from example.home.toilet import toilet


def run_main_loop():
    context = Context(
        bridge=DrHueBridge(),
        bedtime=datetime.time(hour=23, minute=45),
        refresh_interval=0,
        webserver=True
    )

    home = Home(
        name='Home',
        rooms=[
            lounge,
            hallway,
            kitchen,
            office,
            toilet,
            bedroom
        ]
    )
    home.attach_context(context)
    home.start()


if __name__ == '__main__':
    run_main_loop()
