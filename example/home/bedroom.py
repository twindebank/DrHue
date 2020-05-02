from drhue.entities.lights import Lights
from drhue.entities.room import Room

bedroom = Room(
    name="Bedroom",
    devices=[Lights("Bedroom")]
)
