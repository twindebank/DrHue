from drhue.home import Home
from home.lounge import Lounge


class MyHome(Home):
    rooms = [Lounge]

    # do all the fun state tracking in this class/base class
    def apply_rules(self):
        pass
