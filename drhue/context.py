import datetime
from dataclasses import dataclass

import pytz
from astral import LocationInfo
from astral.sun import sun

from drhue.bridge import DrHueBridge


@dataclass
class Context:
    bridge: DrHueBridge
    bedtime: datetime.time = datetime.time(hour=23, minute=45)
    city: LocationInfo = LocationInfo("London", "England", "Europe/London", 51.5, -0.116)
    refresh_interval: int = 5

    def __getattr__(self, item):
        if item in ['dawn', 'sunrise', 'noon', 'sunset', 'dusk']:
            return sun(self._city.observer, date=datetime.datetime.now())[item]
        else:
            return self.__dict__[item]

    @property
    def now(self):
        return datetime.datetime.now(tz=pytz.timezone('Europe/London'))
