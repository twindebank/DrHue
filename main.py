import time

from drhue.bridge import get_bridge
from drhue.home import Room, Lights, Sensor, GoogleHome, Chromecast, Vaccuum, Home
from home.my_home import MyHome


def init_rooms():
    front_door = Room(
        name="Front Door",
        is_exit=True
    )
    kitchen = Room(
        name="kitchen",
        lights=Lights("Kitchen"),
        sensor=Sensor("Kitchen sensor")
    )
    lounge = Room(
        name="Lounge",
        lights=Lights("Lounge"),
        sensor=Sensor("Lounge sensor"),
        google_home=GoogleHome("Lounge speaker"),
        chromecast=Chromecast("Telly"),
        vaccuum=Vaccuum("Boopy")
    )
    back_door = Room(
        name="Back Door",
        is_exit=True
    )
    hallway = Room(
        name="Hallway",
        lights=Lights("Hallway"),
        sensor=Sensor("Hallway sensor")
    )
    office = Room(
        name="Office",
        google_home=GoogleHome("Office speaker")
    )
    toilet = Room(
        name="toilet"
    )
    bedroom = Room(
        name="Bedroom",
        lights=Lights("Bedroom")
    )

    front_door >> kitchen >> lounge
    lounge >> back_door
    lounge >> hallway
    hallway >> office
    hallway >> toilet
    hallway >> bedroom

    rooms = [
        front_door,
        kitchen,
        lounge,
        back_door,
        hallway,
        office,
        toilet,
        bedroom
    ]
    return rooms


def run_main_loop():
    # init bridge
    # init light groups and sensors
    # pass bridge and resources to home init
    # ensure consistency
    bridge = get_bridge()
    home = MyHome(bridge=bridge)
    while True:
        home.update()
        home.run_rules()
        home.apply_rules()
        home.commit()
        time.sleep(1)


if __name__ == '__main__':
    run_main_loop()
