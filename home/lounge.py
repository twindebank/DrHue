import drhue.home as home


# lounge = Room(
#     name='Lounge',
#
# )

class Lounge(home.Room):
    name = 'Lounge'
    lights = home.Lights("Lounge")
    sensor = home.Sensor("Lounge sensor")
    google_home = home.GoogleHome("Lounge speaker")
    chromecast = home.Chromecast("Telly")
    vaccuum = home.Vacuum("Boopy")

    def apply_rules(self):
        # set brightness and timeout here depending on tiem of day and ambient light levels

        if self.sensor.motion_detected():
            self.lights.turn_on()
