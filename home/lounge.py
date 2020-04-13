from datetime import datetime

from astral import now
from loguru import logger

import drhue.home as home
from drhue.time_periods import get_time_periods


class LoungeLights(home.Lights):
    name = "Lounge"


class LoungeSensor(home.Sensor):
    name = "Lounge sensor"


class LoungeSpeaker(home.GoogleHome):
    name = "Lounge speaker"


class Chromecast(home.Chromecast):
    name = "Telly"


class Boopy(home.Vacuum):
    name = "boopy"


class Lounge(home.Room):
    """
    eventually:
    come on first in eve as light starts to dip with read
    then fade into relax
    then read when dinner
    then relax
    then off when bed
    dim when come down in night


    """
    name = 'Lounge'
    _device_classes = [
        LoungeLights,
        LoungeSensor,
        LoungeSpeaker,
        Chromecast,
        Boopy
    ]

    def run_rules(self):


        times = get_time_periods()
        if times["sunrise"] << datetime.now() << times["sunset"]:
            return

        # elif time between sunset and dusk and motion detected
            # activiate read with timeout of 30min
            # turn off after

        # elif time between dusk and bedtime
            # activate read with timeout of 1 hour

        # elif time between bedtime and dawn next day



        if self.get_device(LoungeSensor.name).motion:
            logger.debug("Motion detected.")
            self.get_device(LoungeLights.name).on = True
        else:
            logger.debug("Motion not detected.")
            self.get_device(LoungeLights.name).on = False
