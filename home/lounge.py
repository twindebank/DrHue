from loguru import logger

from drhue.entities.google import GoogleHome, Chromecast, Vacuum
from drhue.entities.lights import Lights
from drhue.entities.room import Room
from drhue.entities.sensor import Sensor
from drhue.rule import Rule

lights = Lights(name='Lounge')
sensor = Sensor(name='Lounge sensor')


class LoungeRules(Rule):
    """
    eventually:
    come on first in eve as light starts to dip with read
    then fade into relax
    then read when dinner
    then relax
    then off when bed
    dim when come down in night
    """

    def apply(self):
        # if self.context.sunrise < self.context.now < self.context.sunset:
        #     return

        # elif time between sunset and dusk and motion detected
        # activiate read with timeout of 30min
        # turn off after

        # elif time between dusk and bedtime
        # activate read with timeout of 1 hour

        # elif time between bedtime and dawn next day

        if sensor.read('motion'):
            logger.debug("Motion detected.")
            lights.turn_on(scene='Relax', timeout_mins=1)
        # else:
        #     logger.debug("Motion not detected.")
        #     self.devices[LoungeLights].turn_off()


lounge = Room(
    name='Lounge',
    devices=[
        lights,
        sensor,
        GoogleHome(name='Lounge speaker'),
        Chromecast(name='Telly'),
        Vacuum(name='Boopy')
    ],
    rules=[LoungeRules]
)
