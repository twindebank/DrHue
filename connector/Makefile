venv:
	pyenv virtualenv 3.7.7 connector
	pyenv local connector

deploy:
	gcloud functions deploy pubsub_to_bq \
	   --runtime "python37" \
	   --entry-point=pubsub_to_bq \
	   --trigger-topic rpi \
	   --region europe-west1 \
	   --set-env-vars dataset=home,table=rpi