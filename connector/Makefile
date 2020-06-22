venv:
	pyenv virtualenv 3.7.7 connector
	pyenv local connector

deploy:
	gcloud functions deploy pubsub_to_bq \
	   --runtime "python37" \
	   --entry-point=main \
	   --trigger-topic rpi \
	   --region europe-west1 \

