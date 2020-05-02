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
        if self.context.sunrise < self.context.now < self.context.sunset:
            pass

        if self.context.sunset < self.context.now < self.context.dusk:
            if sensor.read('motion'):
                lights.turn_on(scene='Read', timeout_mins=30)

        if self.context.dusk < self.context.now < self.context.bedtime:
            if sensor.read('motion') and not sensor.read('daylight') and sensor.read('dark'):
                lights.turn_on(scene='Relax', timeout_mins=60)

        if self.context.bedtime < self.context.now < self.context.sunrise:
            if not lights.read('on'):
                if sensor.read('motion') and not sensor.read('daylight') and sensor.read('dark'):
                    lights.turn_on(scene='Dimmed', timeout_mins=5)


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
