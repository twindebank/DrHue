from flask import Flask
from loguru import logger


def start_server():
    logger.info("Starting webserver...")
    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return 'Running!'

    app.run(port=8080, host='0.0.0.0')
