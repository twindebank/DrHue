import datetime

import pytz
from astral import LocationInfo
from astral.sun import sun


class Context:
    dawn: datetime.time
    sunrise: datetime.time
    noon: datetime.time
    sunset: datetime.time
    dusk: datetime.time
    bedtime: datetime.time

    def __init__(self, bridge, bedtime=datetime.time(hour=23, minute=45)):
        self.bridge = bridge
        self.bedtime = bedtime
        self._city = LocationInfo("London", "England", "Europe/London", 51.5, -0.116)

    def __getattr__(self, item):
        if item in ['dawn', 'sunrise', 'noon', 'sunset', 'dusk']:
            return sun(self._city.observer, date=datetime.datetime.now())[item]
        else:
            return self.__dict__[item]

    @property
    def now(self):
        return datetime.datetime.now(tz=pytz.timezone('Europe/London'))
