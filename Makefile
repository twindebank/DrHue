run:
	screen -dmS drhue python -m example.main

attach:
	screen -d -r drhue

list:
	screen -list
