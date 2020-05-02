from drhue.entities.google import GoogleHome
from drhue.entities.room import Room

office = Room(
    name="Office",
    devices=[GoogleHome("Office speaker")]
)
