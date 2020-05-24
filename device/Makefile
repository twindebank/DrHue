venv:
	pyenv virtualenv 3.7.7 cloud-iot
	pyenv local cloud-iot

install-deps:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install
	pip install

generate-creds:
	openssl req -x509 -newkey rsa:2048 -keyout cloud_iot_private.pem -nodes -out cloud_iot.pub

fetch-google-creds:
	wget https://pki.google.com/roots.pem