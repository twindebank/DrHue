import datetime
import time
from dataclasses import dataclass

import pytz
from astral import LocationInfo
from astral.sun import sun

from drhue.bridge import DrHueBridge


@dataclass
class Time:
    name: str


dawn = Time('dawn')
sunrise = Time('sunrise')
noon = Time('noon')
sunset = Time('sunset')
dusk = Time('dusk')
day_end = Time('day_end')
day_start = Time('day_start')
bedtime = Time('bedtime_datetime')
wakeup = Time('wakeup_datetime')


@dataclass
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

    def update(self, dt=None, offset=datetime.timedelta(0)):
        self.now = datetime.datetime.now(tz=self.timezone) + offset if dt is None else dt + offset
        self.sun = sun(self.city.observer, date=self.now, tzinfo=self.timezone)

    # def _is_in_interval(self, lower, upper, dt=None, lower_offset=datetime.timedelta(0),
    #                     upper_offset=datetime.timedelta(0)):
    #     dt = self.now if dt is None else dt
    #     return lower + lower_offset < dt < upper + upper_offset
    #
    # def is_after_bedtime(self, dt=None, lower_offset=None, upper_offset=None):
    #     return self._is_in_interval(self.bedtime_datetime, self.day_end, dt, lower_offset, upper_offset) or \
    #            self._is_in_interval(self.day_start, self.wakeup_datetime, dt, lower_offset, upper_offset)
    #
    # def is_after_sunset(self, dt=None, lower_offset=None, upper_offset=None):
    #     return self._is_in_interval(self.sunset, self.day_end, dt, lower_offset, upper_offset)
    #
    # def is_before_sunset(self, lower_bound=None, dt=None, lower_offset=None, upper_offset=None):
    #     lower_bound = self.sunrise if lower_bound is None else self.sunrise
    #     return self._is_in_interval(lower_bound, self.sunset, dt, lower_offset, upper_offset)
    #
    # def is_evening_golden_hour(self, dt=None, lower_offset=None, upper_offset=None):
    #     start, end = golden_hour(self.city.observer, self.now, tzinfo=self.timezone, direction=SunDirection.SETTING)
    #     return self._is_in_interval(start, end, dt, lower_offset, upper_offset)
    #
    # def is_after_evening_golden_hour(self, dt=None, lower_offset=None, upper_offset=None):
    #     start, end = golden_hour(self.city.observer, self.now, tzinfo=self.timezone, direction=SunDirection.SETTING)
    #     return self._is_in_interval(end, self.day_end, dt, lower_offset, upper_offset)
    #
    # def is_before_evening_golden_hour(self, dt=None, lower_offset=None, upper_offset=None):
    #     return not self.is_after_evening_golden_hour(dt)
    #
    # def is_evening_blue_hour(self, dt=None, lower_offset=None, upper_offset=None):
    #     start, end = blue_hour(self.city.observer, self.now, tzinfo=self.timezone, direction=SunDirection.SETTING)
    #     return self._is_in_interval(start, end, dt, lower_offset, upper_offset)
    #
    # def is_morning_golden_hour(self, dt=None, lower_offset=None, upper_offset=None):
    #     start, end = golden_hour(self.city.observer, self.now, tzinfo=self.timezone, direction=SunDirection.RISING)
    #     return self._is_in_interval(start, end, dt, lower_offset, upper_offset)
    #
    # def is_morning_blue_hour(self, dt=None, lower_offset=None, upper_offset=None):
    #     start, end = blue_hour(self.city.observer, self.now, tzinfo=self.timezone, direction=SunDirection.RISING)
    #     return self._is_in_interval(start, end, dt, lower_offset, upper_offset)

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
        self.bridge.write_to_bridge()
        time.sleep(self.refresh_interval)
        self.times.update()
        self.bridge.read_data_from_bridge()
