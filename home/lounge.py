from loguru import logger

import drhue.home as home


class LoungeLights(home.Lights):
    name = "Lounge"


class LoungeSensor(home.Sensor):
    name = "Lounge sensor"


class LoungeSpeaker(home.GoogleHome):
    name = "Lounge speaker"


class Chromecast(home.Chromecast):
    name = "Telly"


class Boopy(home.Vacuum):
    name = "Boopy"


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

    def room_rules(self):

        # if self.context.sunrise < self.context.now < self.context.sunset:
        #     return

        # elif time between sunset and dusk and motion detected
        # activiate read with timeout of 30min
        # turn off after

        # elif time between dusk and bedtime
        # activate read with timeout of 1 hour

        # elif time between bedtime and dawn next day

        if self.devices[LoungeSensor].motion:
            logger.debug("Motion detected.")
            self.devices[LoungeLights].turn_on(scene='Relax', timeout_mins=1)
        # else:
        #     logger.debug("Motion not detected.")
        #     self.devices[LoungeLights].turn_off()
