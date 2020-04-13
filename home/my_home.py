from drhue.home import Home
from home.lounge import Lounge


class MyHome(Home):
    room_definitions = [Lounge]

    # do all the fun state tracking in this class/base class
    def run_rules(self):
        pass
