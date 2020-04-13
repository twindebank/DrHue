import datetime

from astral import LocationInfo
from astral.sun import sun

city = LocationInfo("London", "England", "Europe/London", 51.5, -0.116)


def get_time_periods():
    """
    dawn
    sunrise
    noon
    sunset
    dusk
    """
    s = sun(city.observer, date=datetime.datetime.now())
    return s
