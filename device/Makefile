venv:
	pyenv virtualenv 3.7.7 cloud-iot
	pyenv local cloud-iot

install-deps:
	pip install --upgrade pip
	pip install -r requirements.txt

generate-creds:
	mkdir -p creds
	openssl req -x509 -newkey rsa:2048 -keyout creds/cloud_iot_private.pem -nodes -out creds/cloud_iot.pub

fetch-google-creds:
	wget https://pki.google.com/roots.pem creds/roots.pem