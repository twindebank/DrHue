import datetime
from dataclasses import dataclass

from astral import LocationInfo
from astral.sun import sun


@dataclass
class Time:
    name: str
    offset: datetime.timedelta = datetime.timedelta(0)

    def add_offset(self, **timedelta_args):
        return Time(self.name, datetime.timedelta(**timedelta_args))

    def __eq__(self, other):
        return self.name == other.name and self.offset == other.offset

    def __ne__(self, other):
        return not self.__eq__(other)


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
class TimeHelper:
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

    def get(self, time: Time):
        return getattr(self, time.name) + time.offset

    def __getitem__(self, item):
        return self.get(item)

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
