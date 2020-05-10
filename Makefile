run-foreground:
	python -m example.main

run:
	screen -dmS drhue python -m example.main

attach:
	screen -d -r drhue

list:
	screen -list

kill:
	killall screen

venv:
	pyenv virtualenv 3.7.7 drhue
	pyenv local drhue
	pip install -r requirements.txt

rm-venv:
	pyenv uninstall drhue

cleandb:
	rm state.json
