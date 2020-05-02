from drhue.entities.lights import Lights
from drhue.entities.room import Room
from drhue.entities.sensor import Sensor

kitchen = Room(
    name="kitchen",
    devices=[
        Lights(name="Kitchen"),
        Sensor(name="Kitchen sensor")
    ]
)
