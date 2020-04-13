import drhue.home as home


class LoungeLights(home.Lights):
    name = "Lounge"


class LoungeSensor(home.Sensor):
    name = "Lounge sensor"


class LoungeSpeaker(home.GoogleHome):
    name = "Lounge speaker"


class Chromecast(home.Chromecast):
    name = "Telly"


class Boopy(home.Vacuum):
    name = "boopy"


class Lounge(home.Room):
    name = 'Lounge'
    device_classes = [
        LoungeLights,
        LoungeSensor,
        LoungeSpeaker,
        Chromecast,
        Boopy
    ]

    def apply_rules(self):
        # set brightness and timeout here depending on tiem of day and ambient light levels

        if self.sensor.motion:
            self.lights.on = True
