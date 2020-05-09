from flask import Flask, Response
from loguru import logger
from path import Path


def start_server():
    logger.info("Starting webserver...")
    app = Flask(__name__)

    @app.route('/')
    def main():
        log = Path('log.log').read_text()
        recent_first = '\n'.join(reversed(log.split('\n')))
        return Response(recent_first, mimetype='text/plain')

    app.run(port=8080, host='0.0.0.0')
