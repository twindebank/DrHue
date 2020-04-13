from drhue.home import Home
from home.lounge import Lounge


#
# def init_rooms():
#     front_door = Room(
#         name="Front Door",
#         is_exit=True
#     )
#     kitchen = Room(
#         name="kitchen",
#         lights=Lights("Kitchen"),
#         sensor=Sensor("Kitchen sensor")
#     )
#     lounge = Room(
#         name="Lounge",
#         lights=Lights("Lounge"),
#         sensor=Sensor("Lounge sensor"),
#         google_home=GoogleHome("Lounge speaker"),
#         chromecast=Chromecast("Telly"),
#         vaccuum=Vaccuum("Boopy")
#     )
#     back_door = Room(
#         name="Back Door",
#         is_exit=True
#     )
#     hallway = Room(
#         name="Hallway",
#         lights=Lights("Hallway"),
#         sensor=Sensor("Hallway sensor")
#     )
#     office = Room(
#         name="Office",
#         google_home=GoogleHome("Office speaker")
#     )
#     toilet = Room(
#         name="toilet"
#     )
#     bedroom = Room(
#         name="Bedroom",
#         lights=Lights("Bedroom")
#     )
#
#     front_door >> kitchen >> lounge
#     lounge >> back_door
#     lounge >> hallway
#     hallway >> office
#     hallway >> toilet
#     hallway >> bedroom
#
#     rooms = [
#         front_door,
#         kitchen,
#         lounge,
#         back_door,
#         hallway,
#         office,
#         toilet,
#         bedroom
#     ]
#     return rooms


class MyHome(Home):
    name = "My home"
    room_definitions = [Lounge]

    # do all the fun state tracking in this class/base class
    def run_rules(self):
        pass
