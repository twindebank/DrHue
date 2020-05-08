from drhue import times
from drhue.entities.lights import Lights
from drhue.entities.room import Room
from drhue.entities.sensor import Sensor
from drhue.rules import Rule, Rules

lights = Lights("Kitchen")
sensor = Sensor("Kitchen sensor")


class Awake(Rule):
    start = times.wakeup
    end = times.bedtime

    def apply(self):
        if sensor.read('motion') and sensor.read('dark'):
            lights.turn_on(scene='Bright', timeout_mins=5)


class NotAwakeMorning(Rule):
    start = times.day_start
    end = times.wakeup

    def apply(self):
        if sensor.read('motion') and sensor.read('dark'):
            lights.turn_on(scene='Dimmed', timeout_mins=3)


class NotAwakeNight(NotAwakeMorning):
    start = times.bedtime
    end = times.day_end


class KitchenRules(Rules):
    rules = [Awake, NotAwakeMorning, NotAwakeNight]


kitchen = Room(
    name="kitchen",
    devices=[
        lights,
        sensor
    ],
    rules=[KitchenRules]
)
