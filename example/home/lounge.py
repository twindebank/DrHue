from drhue import times
from drhue.entities.google import GoogleHome, Chromecast, Vacuum
from drhue.entities.lights import Lights
from drhue.entities.room import Room
from drhue.entities.sensor import Sensor
from drhue.rules import Rule, Rules

lights = Lights(name='Lounge')
sensor = Sensor(name='Lounge sensor')


class EarlyMorning(Rule):
    start = times.day_start
    end = times.wakeup

    def apply(self):
        if sensor.read('motion') and sensor.read('dark'):
            lights.turn_on(scene='Dimmed', timeout_mins=5)


class Daytime(Rule):
    start = times.wakeup
    end = times.sunset.add_offset(hours=-1)

    def apply(self):
        if sensor.read('motion') and sensor.read('dark'):
            lights.turn_on(scene='Read', timeout_mins=15)


class Evening(Rule):
    start = times.sunset.add_offset(hours=-1)
    end = times.sunset.add_offset(minutes=30)

    def apply(self):
        if sensor.read('motion'):
            lights.turn_on(scene='Read', timeout_mins=30)


class Night(Rule):
    start = times.sunset.add_offset(minutes=30)
    end = times.bedtime

    def apply(self):
        if sensor.read('motion'):
            lights.turn_on(scene='Read', timeout_mins=30)


class LateNight(EarlyMorning):
    start = times.bedtime
    end = times.day_end


class LoungeRules(Rules):
    rules = [EarlyMorning, Daytime, Evening, Night, LateNight]


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
