import datetime
import time
from dataclasses import dataclass

import pytz
from astral import LocationInfo, SunDirection
from astral.sun import sun, golden_hour, blue_hour

from drhue.bridge import DrHueBridge


@dataclass()
class Times:
    """
    todo: implement cache
    """
    city: LocationInfo
    bedtime: datetime.time
    wakeup: datetime.time
    timezone: datetime.tzinfo

    now: datetime.datetime = None
    sun: sun = None

    def __post_init__(self):
        self.update()

    def update(self, dt=None):
        self.now = datetime.datetime.now(tz=self.timezone) if dt is None else dt
        self.sun = sun(self.city.observer, date=self.now, tzinfo=self.timezone)

    def is_after_bedtime(self, dt=None):
        dt = self.now if dt is None else dt
        return self.bedtime_datetime < dt < self.day_end or self.day_start < dt < self.wakeup_datetime

    def is_after_sunset(self, dt=None):
        dt = self.now if dt is None else dt
        return self.sunset < dt < self.day_end or self.day_start < dt < self.sunrise

    def is_evening_golden_hour(self, dt=None):
        dt = self.now if dt is None else dt
        start, end = golden_hour(self.city.observer, self.now, tzinfo=self.timezone, direction=SunDirection.SETTING)
        return start < dt < end

    def is_after_evening_golden_hour(self, dt=None):
        dt = self.now if dt is None else dt
        start, end = golden_hour(self.city.observer, self.now, tzinfo=self.timezone, direction=SunDirection.SETTING)
        return end < dt < self.day_end

    def is_before_evening_golden_hour(self, dt=None):
        return not self.is_after_evening_golden_hour(dt)

    def is_evening_blue_hour(self, dt=None):
        dt = self.now if dt is None else dt
        start, end = blue_hour(self.city.observer, self.now, tzinfo=self.timezone, direction=SunDirection.SETTING)
        return start < dt < end

    def is_morning_golden_hour(self, dt=None):
        dt = self.now if dt is None else dt
        start, end = golden_hour(self.city.observer, self.now, tzinfo=self.timezone, direction=SunDirection.RISING)
        return start < dt < end

    def is_morning_blue_hour(self, dt=None):
        dt = self.now if dt is None else dt
        start, end = blue_hour(self.city.observer, self.now, tzinfo=self.timezone, direction=SunDirection.RISING)
        return start < dt < end

    @property
    def dawn(self):
        return self.sun['dawn']

    @property
    def sunrise(self):
        return self.sun['sunrise']

    @property
    def noon(self):
        return self.sun['noon']

    @property
    def sunset(self):
        return self.sun['sunset']

    @property
    def dusk(self):
        return self.sun['dusk']

    @property
    def day_end(self):
        return datetime.datetime.combine(
            self.now,
            datetime.time(hour=23, minute=59, second=59, microsecond=999, tzinfo=self.timezone)
        )

    @property
    def day_start(self):
        return datetime.datetime.combine(
            self.now,
            datetime.time(hour=0, minute=0, second=0, microsecond=0, tzinfo=self.timezone)
        )

    @property
    def bedtime_datetime(self):
        return datetime.datetime.combine(self.now, self.bedtime, tzinfo=self.timezone)

    @property
    def wakeup_datetime(self):
        return datetime.datetime.combine(self.now, self.wakeup, tzinfo=self.timezone)


@dataclass
class Context:
    bridge: DrHueBridge
    refresh_interval: int = 5
    timezone: datetime.tzinfo = pytz.timezone('Europe/London')
    city: LocationInfo = LocationInfo("London", "England", "Europe/London", 51.5, -0.116)
    bedtime: datetime.time = datetime.time(hour=23, minute=45)
    wakeup: datetime.time = datetime.time(hour=8, minute=0)
    times: Times = None

    def __post_init__(self):
        self.times = Times(self.city, self.bedtime, self.wakeup, self.timezone)

    def update_and_wait(self):
        self.bridge.write()
        time.sleep(self.refresh_interval)
        self.times.update()
        self.bridge.read()
