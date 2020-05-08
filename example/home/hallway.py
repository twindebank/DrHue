from drhue import times
from drhue.entities.lights import Lights
from drhue.entities.room import Room
from drhue.entities.sensor import Sensor
from drhue.rules import Rule, Rules

lights = Lights("Hallway")
sensor = Sensor("Hallway sensor")


class Awake(Rule):
    start = times.wakeup
    end = times.bedtime

    def apply(self):
        if sensor.read('motion') and sensor.read('dark'):
            lights.turn_on(scene='Read', timeout_mins=3)


class NotAwakeMorning(Rule):
    start = times.day_start
    end = times.wakeup

    def apply(self):
        if sensor.read('motion') and sensor.read('dark'):
            lights.turn_on(scene='Dimmed', timeout_mins=3)


class NotAwakeNight(NotAwakeMorning):
    start = times.bedtime
    end = times.day_end


class HallwayRules(Rules):
    rules = [Awake, NotAwakeMorning, NotAwakeNight]


hallway = Room(
    name="Hallway",
    devices=[
        lights,
        sensor
    ],
    rules=[HallwayRules]
)
