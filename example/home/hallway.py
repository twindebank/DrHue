from drhue.entities.lights import Lights
from drhue.entities.room import Room
from drhue.entities.sensor import Sensor

hallway = Room(
    name="Hallway",
    devices=[
        Lights("Hallway"),
        Sensor("Hallway sensor")
    ]
)
