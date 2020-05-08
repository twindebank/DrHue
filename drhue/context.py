import datetime
import time
from dataclasses import dataclass

import pytz
from astral import LocationInfo

from drhue.bridge import DrHueBridge
from drhue.times import TimeHelper


@dataclass
class Context:
    bridge: DrHueBridge
    refresh_interval: int = 5
    timezone: datetime.tzinfo = pytz.timezone('Europe/London')
    city: LocationInfo = LocationInfo("London", "England", "Europe/London", 51.5, -0.116)
    bedtime: datetime.time = datetime.time(hour=23, minute=45)
    wakeup: datetime.time = datetime.time(hour=8, minute=0)

    def __post_init__(self):
        self.times = TimeHelper(self.city, self.bedtime, self.wakeup, self.timezone)

    def update_and_wait(self, log=True):
        self.bridge.write_to_bridge()
        time.sleep(self.refresh_interval)
        self.times.update()
        self.bridge.read_data_from_bridge(log)
