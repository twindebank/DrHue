import datetime
from dataclasses import dataclass

import pytz
from astral import LocationInfo
from astral.sun import sun

from drhue.bridge import DrHueBridge




@dataclass
class Context:
    """
    todo: here

    need more sophisticated times here
    some kind of rolling window
    """
    bridge: DrHueBridge
    bedtime: datetime.time = datetime.time(hour=23, minute=45)
    city: LocationInfo = LocationInfo("London", "England", "Europe/London", 51.5, -0.116)
    refresh_interval: int = 5

    def get_time(self, time) -> datetime.datetime:
        if time in ['dawn', 'sunrise', 'noon', 'sunset', 'dusk']:
            return sun(self.city.observer, date=datetime.datetime.now())[time]
        elif time == 'bedtime':
            return datetime.datetime.combine(datetime.datetime.now(), self.bedtime)
        elif time == 'day_end':
            return datetime.datetime.combine(
                datetime.datetime.now(),
                datetime.time(hour=23, minute=59, second=59, microsecond=999)
            )
        elif time == 'day_start':
            return datetime.datetime.combine(
                datetime.datetime.now(),
                datetime.time(hour=0, minute=0, second=0, microsecond=0)
            )

    @property
    def now(self):
        return datetime.datetime.now(tz=pytz.timezone('Europe/London'))
